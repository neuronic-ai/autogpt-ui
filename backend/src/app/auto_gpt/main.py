"""The application entry point.  Can be invoked by a CLI or any other front end application."""
import logging
import sys
from pathlib import Path

from colorama import Fore, Style

# from webdriver_manager.firefox import GeckoDriverManager

from autogpt.agent import AgentManager
from autogpt.config.ai_config import AIConfig
from autogpt.llm.api_manager import ApiManager
from autogpt.setup import prompt_user
from autogpt.utils import clean_input
from autogpt.commands.command import CommandRegistry
from autogpt.config import Config, check_openai_api_key
from autogpt.configurator import create_config
from autogpt.logs import logger
from autogpt.memory.vector import get_memory
from autogpt.plugins import scan_plugins
from autogpt.prompts.prompt import DEFAULT_TRIGGERING_PROMPT
from autogpt.utils import get_current_git_branch, get_latest_bulletin, markdown_to_ansi_style
from autogpt.workspace import Workspace

from app.auto_gpt.api_manager import CachedApiManager
from app.auto_gpt.agent import AgentStandalone
from app.auto_gpt.install_plugin_deps import install_plugin_dependencies
from app.auto_gpt.memory import CachedAgents, CachedMessageHistory


COMMAND_CATEGORIES = [
    "autogpt.commands.analyze_code",
    "autogpt.commands.audio_text",
    "autogpt.commands.execute_code",
    "autogpt.commands.file_operations",
    "autogpt.commands.git_operations",
    "autogpt.commands.google_search",
    "autogpt.commands.image_gen",
    "autogpt.commands.improve_code",
    "autogpt.commands.web_selenium",
    "autogpt.commands.write_tests",
    "autogpt.app",
    "autogpt.commands.task_statuses",
]


def construct_main_ai_config(skip_print: bool) -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    cfg = Config()

    config = AIConfig.load(cfg.ai_settings_file)
    if not skip_print:
        if cfg.skip_reprompt and config.ai_name:
            logger.typewriter_log("Name :", Fore.GREEN, config.ai_name)
            logger.typewriter_log("Role :", Fore.GREEN, config.ai_role)
            logger.typewriter_log("Goals:", Fore.GREEN, f"{config.ai_goals}")
            logger.typewriter_log(
                "API Budget:",
                Fore.GREEN,
                "infinite" if config.api_budget <= 0 else f"${config.api_budget}",
            )
        elif config.ai_name:
            logger.typewriter_log(
                "Welcome back! ",
                Fore.GREEN,
                f"Would you like me to return to being {config.ai_name}?",
                speak_text=True,
            )
            should_continue = clean_input(
                f"""Continue with the last settings?
                    Name:  {config.ai_name}
                    Role:  {config.ai_role}
                    Goals: {config.ai_goals}
                    API Budget: {"infinite" if config.api_budget <= 0 else f"${config.api_budget}"}
                    Continue ({cfg.authorise_key}/{cfg.exit_key}): """
            )
            if should_continue.lower() == cfg.exit_key:
                config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(cfg.ai_settings_file)

    # set the total api budget
    api_manager = ApiManager()
    CachedApiManager.cast(api_manager)
    api_manager.set_total_budget(config.api_budget)
    api_manager.restore()

    if not skip_print:
        # Agent Created, print message
        logger.typewriter_log(
            config.ai_name,
            Fore.LIGHTBLUE_EX,
            "has been created with the following details:",
            speak_text=True,
        )
        # Print the ai config details
        # Name
        logger.typewriter_log("Name:", Fore.GREEN, config.ai_name, speak_text=False)
        # Role
        logger.typewriter_log("Role:", Fore.GREEN, config.ai_role, speak_text=False)
        # Goals
        logger.typewriter_log("Goals:", Fore.GREEN, "", speak_text=False)
        for goal in config.ai_goals:
            logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)
    if api_manager.get_total_budget() > 0 and api_manager.get_total_cost() > 0:
        remaining_budget = api_manager.get_total_budget() - api_manager.get_total_cost()
        logger.typewriter_log("Remaining budget: ", Fore.GREEN, f"${remaining_budget:.8f}")
        if remaining_budget <= 0:
            logger.typewriter_log("Budget exceeded, exit immediately", Fore.RED)
            sys.exit(1)
    # manager = GeckoDriverManager()
    # logger.typewriter_log("Gecko driver path: ", Fore.GREEN, f"{manager.install()}")
    return config


def run_auto_gpt(
    continuous: bool,
    continuous_limit: int,
    ai_settings: str,
    prompt_settings: str,
    skip_reprompt: bool,
    speak: bool,
    debug: bool,
    gpt3only: bool,
    gpt4only: bool,
    memory_type: str,
    browser_name: str,
    allow_downloads: bool,
    skip_news: bool,
    workspace_directory: str,
    install_plugin_deps: bool,
    max_cache_size: int,
):
    # Configure logging before we do anything else.
    logger.set_level(logging.DEBUG if debug else logging.INFO)
    logger.speak_mode = speak

    cfg = Config()
    # TODO: fill in llm values here
    check_openai_api_key()
    create_config(
        cfg,
        continuous,
        continuous_limit,
        "",
        prompt_settings,
        False,
        speak,
        debug,
        gpt3only,
        gpt4only,
        memory_type,
        browser_name,
        allow_downloads,
        skip_news,
    )
    cfg.skip_reprompt = skip_reprompt
    cfg.ai_settings_file = ai_settings

    if not cfg.skip_news:
        motd, is_new_motd = get_latest_bulletin()
        if motd:
            motd = markdown_to_ansi_style(motd)
            for motd_line in motd.split("\n"):
                logger.info(motd_line, "NEWS:", Fore.GREEN)
            if is_new_motd and not cfg.chat_messages_enabled:
                input(
                    Fore.MAGENTA
                    + Style.BRIGHT
                    + "NEWS: Bulletin was updated! Press Enter to continue..."
                    + Style.RESET_ALL
                )

        git_branch = get_current_git_branch()
        if git_branch and git_branch != "stable":
            logger.typewriter_log(
                "WARNING: ",
                Fore.RED,
                f"You are running on `{git_branch}` branch " "- this is not a supported branch.",
            )
        if sys.version_info < (3, 10):
            logger.typewriter_log(
                "WARNING: ",
                Fore.RED,
                "You are running on an older version of Python. "
                "Some people have observed problems with certain "
                "parts of Auto-GPT with this version. "
                "Please consider upgrading to Python 3.10 or higher.",
            )

    if install_plugin_deps:
        install_plugin_dependencies()

    if workspace_directory is None:
        workspace_directory = Path(__file__).parent / "auto_gpt_workspace"
    else:
        workspace_directory = Path(workspace_directory)
    workspace_directory = Workspace.make_workspace(workspace_directory)
    cfg.workspace_path = str(workspace_directory)

    # HACK: doing this here to collect some globals that depend on the workspace.
    file_logger_path = workspace_directory / "file_logger.txt"
    if not file_logger_path.exists():
        with file_logger_path.open(mode="w", encoding="utf-8") as f:
            f.write("File Operation Logger ")

    cfg.file_logger_path = str(file_logger_path)

    cfg.set_plugins(scan_plugins(cfg, cfg.debug_mode))
    # Create a CommandRegistry instance and scan default folder
    command_registry = CommandRegistry()
    logger.debug(f"The following command categories are disabled: {cfg.disabled_command_categories}")
    enabled_command_categories = [x for x in COMMAND_CATEGORIES if x not in cfg.disabled_command_categories]

    logger.debug(f"The following command categories are enabled: {enabled_command_categories}")

    for command_category in enabled_command_categories:
        command_registry.import_commands(command_category)

    agent = AgentStandalone(
        ai_name=None,
        memory=None,
        next_action_count=0,
        command_registry=command_registry,
        config=None,
        system_prompt=None,
        triggering_prompt=DEFAULT_TRIGGERING_PROMPT,
        workspace_directory=workspace_directory,
    )
    message_history = CachedMessageHistory(agent)
    while message_history.filename.stat().st_size >= max_cache_size:
        logger.typewriter_log("Truncating cache...")
        message_history.messages[:] = message_history.messages[(len(message_history.messages) // 4) or 1 :]
        message_history.flush()
    AgentManager().agents = CachedAgents(cfg)

    # add chat plugins capable of report to logger
    if cfg.chat_messages_enabled:
        for plugin in cfg.plugins:
            if hasattr(plugin, "can_handle_report") and plugin.can_handle_report():
                logger.info(f"Loaded plugin into logger: {plugin.__class__.__name__}")
                logger.chat_plugins.append(plugin)

    try:
        last_assistant_reply = next(filter(lambda x: x.role == "assistant", reversed(message_history.messages))).content
    except StopIteration:
        last_assistant_reply = None

    ai_name = ""
    ai_config = construct_main_ai_config(bool(last_assistant_reply))
    ai_config.command_registry = command_registry

    # add chat plugins capable of report to logger
    if cfg.chat_messages_enabled:
        for plugin in cfg.plugins:
            if hasattr(plugin, "can_handle_report") and plugin.can_handle_report():
                logger.info(f"Loaded plugin into logger: {plugin.__class__.__name__}")
                logger.chat_plugins.append(plugin)

    # Initialize memory and make sure it is empty.
    # this is particularly important for indexing and referencing pinecone memory
    memory = get_memory(cfg, init=True)
    if not last_assistant_reply:
        logger.typewriter_log("Using memory of type:", Fore.GREEN, f"{memory.__class__.__name__}")
        logger.typewriter_log("Using Browser:", Fore.GREEN, cfg.selenium_web_browser)
    system_prompt = ai_config.construct_full_prompt()
    if cfg.debug_mode:
        logger.typewriter_log("Prompt:", Fore.GREEN, system_prompt)

    agent.ai_name = ai_name
    agent.config = ai_config
    agent.history = message_history
    agent.memory = memory
    agent.system_prompt = system_prompt
    agent.process_next_interaction(last_assistant_reply)
