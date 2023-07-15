"""The application entry point.  Can be invoked by a CLI or any other front end application."""
import logging
import sys
from pathlib import Path
from typing import Optional

from colorama import Fore, Style

from autogpt.agent import AgentManager
from autogpt.config.ai_config import AIConfig
from autogpt.llm.api_manager import ApiManager
from autogpt.setup import prompt_user
from autogpt.utils import clean_input
from autogpt.config.config import Config, ConfigBuilder, check_openai_api_key
from autogpt.configurator import create_config
from autogpt.logs import logger
from autogpt.memory.vector import get_memory
from autogpt.models.command_registry import CommandRegistry
from autogpt.prompts.prompt import DEFAULT_TRIGGERING_PROMPT
from autogpt.utils import (
    get_current_git_branch,
    get_latest_bulletin,
    get_legal_warning,
    markdown_to_ansi_style,
)
from autogpt.workspace import Workspace

from app.auto_gpt.api_manager import CachedApiManager
from app.auto_gpt.agent import AgentStandalone
from app.auto_gpt.install_plugin_deps import install_plugin_dependencies
from app.auto_gpt.memory import CachedAgents, CachedMessageHistory
from app.auto_gpt.plugins import scan_plugins


COMMAND_CATEGORIES = [
    "autogpt.commands.execute_code",
    "autogpt.commands.file_operations",
    "autogpt.commands.web_search",
    "autogpt.commands.web_selenium",
    "autogpt.app",
    "autogpt.commands.task_statuses",
]


def construct_main_ai_config(
    config: Config,
    name: Optional[str] = None,
    role: Optional[str] = None,
    goals: tuple[str] = tuple(),
    skip_print: bool = False,
) -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    ai_config = AIConfig.load(config.ai_settings_file)

    # Apply overrides
    if name:
        ai_config.ai_name = name
    if role:
        ai_config.ai_role = role
    if goals:
        ai_config.ai_goals = list(goals)

    if not skip_print:
        if (
            all([name, role, goals])
            or config.skip_reprompt
            and all([ai_config.ai_name, ai_config.ai_role, ai_config.ai_goals])
        ):
            logger.typewriter_log("Name :", Fore.GREEN, ai_config.ai_name)
            logger.typewriter_log("Role :", Fore.GREEN, ai_config.ai_role)
            logger.typewriter_log("Goals:", Fore.GREEN, f"{ai_config.ai_goals}")
            logger.typewriter_log(
                "API Budget:",
                Fore.GREEN,
                "infinite" if ai_config.api_budget <= 0 else f"${ai_config.api_budget}",
            )
        elif all([ai_config.ai_name, ai_config.ai_role, ai_config.ai_goals]):
            logger.typewriter_log(
                "Welcome back! ",
                Fore.GREEN,
                f"Would you like me to return to being {ai_config.ai_name}?",
                speak_text=True,
            )
            should_continue = clean_input(
                config,
                f"""Continue with the last settings?
                    Name:  {ai_config.ai_name}
                    Role:  {ai_config.ai_role}
                    Goals: {ai_config.ai_goals}
                    API Budget: {"infinite" if ai_config.api_budget <= 0 else f"${ai_config.api_budget}"}
                    Continue ({config.authorise_key}/{config.exit_key}): """,
            )
            if should_continue.lower() == config.exit_key:
                ai_config = AIConfig()

    if any([not ai_config.ai_name, not ai_config.ai_role, not ai_config.ai_goals]):
        ai_config = prompt_user(config)
        ai_config.save(config.ai_settings_file)

    if config.restrict_to_workspace:
        logger.typewriter_log(
            "NOTE:All files/directories created by this agent can be found inside its workspace at:",
            Fore.YELLOW,
            f"{config.workspace_path}",
        )
    # set the total api budget
    api_manager = ApiManager()
    CachedApiManager.cast(api_manager)
    api_manager.set_total_budget(ai_config.api_budget)
    api_manager.load_config(config)
    api_manager.restore()

    if not skip_print:
        # Agent Created, print message
        logger.typewriter_log(
            ai_config.ai_name,
            Fore.LIGHTBLUE_EX,
            "has been created with the following details:",
            speak_text=True,
        )

        # Print the ai_config details
        # Name
        logger.typewriter_log("Name:", Fore.GREEN, ai_config.ai_name, speak_text=False)
        # Role
        logger.typewriter_log("Role:", Fore.GREEN, ai_config.ai_role, speak_text=False)
        # Goals
        logger.typewriter_log("Goals:", Fore.GREEN, "", speak_text=False)
        for goal in ai_config.ai_goals:
            logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)

    return ai_config


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
    workspace_directory: str | Path,
    install_plugin_deps: bool,
    max_cache_size: int,
    ai_name: Optional[str] = None,
    ai_role: Optional[str] = None,
    ai_goals: tuple[str] = tuple(),
):
    # Configure logging before we do anything else.
    logger.set_level(logging.DEBUG if debug else logging.INFO)

    config = ConfigBuilder.build_config_from_env()
    # HACK: This is a hack to allow the config into the logger without having to pass it around everywhere
    # or import it directly.
    logger.config = config

    # TODO: fill in llm values here
    check_openai_api_key(config)

    create_config(
        config,
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
    config.skip_reprompt = skip_reprompt
    config.ai_settings_file = ai_settings

    if config.continuous_mode:
        for line in get_legal_warning().split("\n"):
            logger.warn(markdown_to_ansi_style(line), "LEGAL:", Fore.RED)

    if not config.skip_news:
        motd, is_new_motd = get_latest_bulletin()
        if motd:
            motd = markdown_to_ansi_style(motd)
            for motd_line in motd.split("\n"):
                logger.info(motd_line, "NEWS:", Fore.GREEN)
            if is_new_motd and not config.chat_messages_enabled:
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
    config.workspace_path = str(workspace_directory)

    # HACK: doing this here to collect some globals that depend on the workspace.
    Workspace.build_file_logger_path(config, workspace_directory)

    config.plugins = scan_plugins(config, config.debug_mode)
    # Create a CommandRegistry instance and scan default folder
    command_registry = CommandRegistry()

    logger.debug(f"The following command categories are disabled: {config.disabled_command_categories}")
    enabled_command_categories = [x for x in COMMAND_CATEGORIES if x not in config.disabled_command_categories]

    logger.debug(f"The following command categories are enabled: {enabled_command_categories}")

    for command_category in enabled_command_categories:
        command_registry.import_commands(command_category)

    # Unregister commands that are incompatible with the current config
    incompatible_commands = []
    for command in command_registry.commands.values():
        if callable(command.enabled) and not command.enabled(config):
            command.enabled = False
            incompatible_commands.append(command)

    for command in incompatible_commands:
        command_registry.unregister(command)
        logger.debug(
            f"Unregistering incompatible command: {command.name}, "
            f"reason - {command.disabled_reason or 'Disabled by current config.'}"
        )

    message_history = CachedMessageHistory.load_from_file(None, config)
    while message_history.filename.stat().st_size >= max_cache_size:
        logger.typewriter_log("Truncating cache...")
        message_history.messages[:] = message_history.messages[(len(message_history.messages) // 4) or 1 :]
        message_history.flush()
    AgentManager(config).agents = CachedAgents(config)

    try:
        last_assistant_reply = next(filter(lambda x: x.role == "assistant", reversed(message_history.messages)))
    except StopIteration:
        last_assistant_reply = None

    ai_config = construct_main_ai_config(
        config, name=ai_name, role=ai_role, goals=ai_goals, skip_print=bool(last_assistant_reply)
    )
    ai_config.command_registry = command_registry
    ai_name = ai_config.ai_name

    # add chat plugins capable of report to logger
    if config.chat_messages_enabled:
        for plugin in config.plugins:
            if hasattr(plugin, "can_handle_report") and plugin.can_handle_report():
                logger.info(f"Loaded plugin into logger: {plugin.__class__.__name__}")
                logger.chat_plugins.append(plugin)

    # Initialize memory and make sure it is empty.
    # this is particularly important for indexing and referencing pinecone memory
    memory = get_memory(config)
    memory.clear()
    if not last_assistant_reply:
        logger.typewriter_log("Using memory of type:", Fore.GREEN, f"{memory.__class__.__name__}")
        logger.typewriter_log("Using Browser:", Fore.GREEN, config.selenium_web_browser)
    system_prompt = ai_config.construct_full_prompt(config)
    if config.debug_mode:
        logger.typewriter_log("Prompt:", Fore.GREEN, system_prompt)

    agent = AgentStandalone(
        ai_name=ai_name,
        memory=memory,
        next_action_count=0,
        command_registry=command_registry,
        ai_config=ai_config,
        config=config,
        system_prompt=system_prompt,
        triggering_prompt=DEFAULT_TRIGGERING_PROMPT,
        workspace_directory=workspace_directory,
    )
    message_history.agent = agent
    agent.history = message_history
    agent.process_next_interaction(last_assistant_reply)
