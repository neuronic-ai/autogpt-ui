import json
from colorama import Fore, Style

from autogpt.agent.agent import Agent
from autogpt.app import execute_command, extract_command
from autogpt.json_utils.utilities import extract_json_from_response, validate_json
from autogpt.llm.chat import chat_with_ai
from autogpt.llm.utils import count_string_tokens
from autogpt.log_cycle.log_cycle import (
    FULL_MESSAGE_HISTORY_FILE_NAME,
    NEXT_ACTION_FILE_NAME,
)
from autogpt.logs import logger, print_assistant_thoughts, remove_ansi_escape
from autogpt.speech import say_text
from autogpt.spinner import Spinner


class AgentStandalone(Agent):
    def execute_command(self, command_name: str, arguments: dict, user_input: str):
        # Execute command
        if command_name is not None and command_name.lower().startswith("error"):
            result = f"Could not execute command: {arguments}"
        elif command_name == "human_feedback":
            result = f"Human feedback: {user_input}"
        else:
            for plugin in self.config.plugins:
                if not plugin.can_handle_pre_command():
                    continue
                command_name, arguments = plugin.pre_command(command_name, arguments)
            command_result = execute_command(
                command_name=command_name,
                arguments=arguments,
                agent=self,
            )
            result = f"Command {command_name} returned: " f"{command_result}"

            result_tlength = count_string_tokens(str(command_result), self.config.smart_llm)
            memory_tlength = count_string_tokens(str(self.history.summary_message()), self.config.smart_llm)
            if result_tlength + memory_tlength + 600 > self.smart_token_limit:
                result = f"Failure: command {command_name} returned too much output. \
                    Do not execute this command again with the same arguments."

            for plugin in self.config.plugins:
                if not plugin.can_handle_post_command():
                    continue
                result = plugin.post_command(command_name, result)
            if self.next_action_count > 0:
                self.next_action_count -= 1

        # Check if there's a result from the command append it to the message
        # history
        if result is not None:
            self.history.add("system", result, "action_result")
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, result)
        else:
            self.history.add("system", "Unable to execute command", "action_result")
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, "Unable to execute command")

    def process_next_interaction(self, last_assistant_reply: str | None):
        self.cycle_count = 0
        command_name = None
        arguments = None

        self.cycle_count += 1
        self.log_cycle_handler.log_count_within_cycle = 0
        self.log_cycle_handler.log_cycle(
            self.ai_config.ai_name,
            self.created_at,
            self.cycle_count,
            [m.raw() for m in self.history],
            FULL_MESSAGE_HISTORY_FILE_NAME,
        )

        # Send message to AI, get response
        if not last_assistant_reply:
            # Send message to AI, get response
            with Spinner("Thinking... ", plain_output=self.config.plain_output):
                assistant_reply = chat_with_ai(
                    self.config,
                    self,
                    self.system_prompt,
                    self.triggering_prompt,
                    self.smart_token_limit,
                    self.config.smart_llm,
                )
        else:
            assistant_reply = last_assistant_reply

        try:
            assistant_reply_json = extract_json_from_response(assistant_reply.content)
            validate_json(assistant_reply_json, self.config)
        except json.JSONDecodeError as e:
            logger.error(f"Exception while validating assistant reply JSON: {e}")
            assistant_reply_json = {}

        for plugin in self.config.plugins:
            if not plugin.can_handle_post_planning():
                continue
            assistant_reply_json = plugin.post_planning(assistant_reply_json)

        # Print Assistant thoughts
        if assistant_reply_json != {}:
            # Get command name and arguments
            try:
                if not last_assistant_reply:
                    print_assistant_thoughts(self.ai_name, assistant_reply_json, self.config)
                command_name, arguments = extract_command(assistant_reply_json, assistant_reply, self.config)
                if self.config.speak_mode:
                    say_text(f"I want to execute {command_name}", self.config)

                arguments = self._resolve_pathlike_command_args(arguments)

            except Exception as e:
                logger.error("Error: \n", str(e))
        self.log_cycle_handler.log_cycle(
            self.ai_config.ai_name,
            self.created_at,
            self.cycle_count,
            assistant_reply_json,
            NEXT_ACTION_FILE_NAME,
        )

        if not last_assistant_reply:
            # First log new-line so user can differentiate sections better in console
            logger.typewriter_log("\n")
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {Fore.CYAN}{remove_ansi_escape(command_name)}{Style.RESET_ALL}  "
                f"ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}",
            )

            logger.info(
                f"Enter '{self.config.authorise_key}' to authorise command, "
                f"'{self.config.authorise_key} -N' to run N continuous commands, "
                f"'{self.config.exit_key}' to exit program, or enter feedback for "
                f"{self.ai_name}..."
            )
        else:
            # if command_name is not None:
            self.execute_command(command_name, arguments, "")
            self.process_next_interaction(None)
