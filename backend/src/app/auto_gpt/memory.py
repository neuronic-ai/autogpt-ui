from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

import orjson

from autogpt.config import Config
from autogpt.llm.base import Message
from autogpt.memory.message_history import MessageHistory

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
