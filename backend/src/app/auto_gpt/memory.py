from __future__ import annotations

import copy
import dataclasses
import json
from pathlib import Path
from typing import Any

import orjson

from autogpt.config import Config
from autogpt.llm.base import Message
from autogpt.llm.providers.openai import OPEN_AI_CHAT_MODELS
from autogpt.llm.utils import count_string_tokens
from autogpt.logs import logger
from autogpt.memory.message_history import MessageHistory

from app.auto_gpt.utilities import extract_json_from_response

EMBED_DIM = 1536
SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_NON_STR_KEYS
GPT_CACHE = ".gpt_cache"


@dataclasses.dataclass
class CachedMessageHistory(MessageHistory):
    filename: Path = Path("")

    def __post_init__(self) -> None:
        cfg = Config()
        workspace_path = Path(cfg.workspace_path)
        self.filename = workspace_path / GPT_CACHE / f"{cfg.memory_index}-history.json"

        if self.filename.exists():
            with self.filename.open("rb") as f:
                data = orjson.loads(f.read())
                self.messages = [Message(**mes) for mes in data.get("messages", [])]
                self.summary = data.get("summary", self.summary)
                self.last_trimmed_index = data.get("last_trimmed_index", self.last_trimmed_index)
        else:
            self.filename.parent.mkdir(exist_ok=True, parents=True)
            with self.filename.open("w+b") as f:
                f.write(b"{}")

    def build_dict(self):
        return {
            "messages": self.messages,
            "summary": self.summary,
            "last_trimmed_index": self.last_trimmed_index,
        }

    def flush(self) -> None:
        with open(self.filename, "wb") as f:
            f.write(orjson.dumps(self.build_dict(), option=SAVE_OPTIONS))

    def append(self, message: Message) -> None:
        super().append(message)
        self.flush()

    def update_running_summary(self, new_events: list[Message]) -> Message:
        """
        This function takes a list of dictionaries representing new events and combines them with the current summary,
        focusing on key and potentially important information to remember. The updated summary is returned in a message
        formatted in the 1st person past tense.

        Args:
            new_events (List[Dict]): A list of dictionaries containing the latest events to be added to the summary.

        Returns:
            str: A message containing the updated summary of actions, formatted in the 1st person past tense.

        Example:
            new_events = [{"event": "entered the kitchen."}, {"event": "found a scrawled note with the number 7"}]
            update_running_summary(new_events)
            # Returns: "This reminds you of these events from your past: \nI entered the kitchen and found a scrawled note saying 7."
        """
        cfg = Config()

        if not new_events:
            return self.summary_message()

        # Create a copy of the new_events list to prevent modifying the original list
        new_events = copy.deepcopy(new_events)

        # Replace "assistant" with "you". This produces much better first person past tense results.
        for event in new_events:
            if event.role.lower() == "assistant":
                event.role = "you"

                # Remove "thoughts" dictionary from "content"
                try:
                    content_dict = extract_json_from_response(event.content)
                    if "thoughts" in content_dict:
                        del content_dict["thoughts"]
                    event.content = json.dumps(content_dict)
                except json.JSONDecodeError as e:
                    logger.error(f"Error: Invalid JSON: {e}")
                    if cfg.debug_mode:
                        logger.error(f"{event.content}")

            elif event.role.lower() == "system":
                event.role = "your computer"

            # Delete all user messages
            elif event.role == "user":
                new_events.remove(event)

        # Summarize events and current summary in batch to a new running summary

        # Assume an upper bound length for the summary prompt template, i.e. Your task is to create a concise running summary...., in summarize_batch func
        # TODO make this default dynamic
        prompt_template_length = 100
        max_tokens = OPEN_AI_CHAT_MODELS.get(cfg.fast_llm_model).max_tokens
        summary_tlength = count_string_tokens(str(self.summary), cfg.fast_llm_model)
        batch = []
        batch_tlength = 0

        # TODO Can put a cap on length of total new events and drop some previous events to save API cost, but need to think thru more how to do it without losing the context
        for event in new_events:
            event_tlength = count_string_tokens(str(event), cfg.fast_llm_model)

            if batch_tlength + event_tlength > max_tokens - prompt_template_length - summary_tlength:
                # The batch is full. Summarize it and start a new one.
                self.summarize_batch(batch, cfg)
                summary_tlength = count_string_tokens(str(self.summary), cfg.fast_llm_model)
                batch = [event]
                batch_tlength = event_tlength
            else:
                batch.append(event)
                batch_tlength += event_tlength

        if batch:
            # There's an unprocessed batch. Summarize it.
            self.summarize_batch(batch, cfg)

        return self.summary_message()


class CachedAgents:
    """A class that stores the memory in a local file"""

    def __init__(self, cfg) -> None:
        """Initialize a class instance

        Args:
            cfg: Config object

        Returns:
            None
        """
        workspace_path = Path(cfg.workspace_path)
        self.filename = workspace_path / GPT_CACHE / f"{cfg.memory_index}-agents.json"

        self.data = {}

        if self.filename.exists():
            with self.filename.open("rb") as f:
                self.data = {int(k): v for k, v in orjson.loads(f.read()).items()}
        else:
            self.filename.parent.mkdir(exist_ok=True, parents=True)
            with self.filename.open("w+b") as f:
                f.write(b"{}")

    def __setitem__(self, key, value):
        self.add(key, value)

    def __getitem__(self, key):
        return self.data[key]

    def flush(self) -> None:
        with open(self.filename, "wb") as f:
            f.write(orjson.dumps(self.data, option=SAVE_OPTIONS))

    def add(self, key: int, agent: tuple) -> None:
        self.data[key] = agent
        self.flush()

    def get(self, key: int, default: Any = None) -> tuple | None:
        return self.data.get(key, default)

    def delete(self, key: int) -> None:
        del self.data[key]

    def items(self):
        return self.data.items()
