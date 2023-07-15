from __future__ import annotations

from pathlib import Path

import orjson

from autogpt.config import Config
from autogpt.llm.api_manager import ApiManager


SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_NON_STR_KEYS
GPT_CACHE = ".gpt_cache"


class CachedApiManager(ApiManager):
    def load_config(self, config: Config):
        self.config = config

    @classmethod
    def cast(cls, some_a: ApiManager):
        """Cast an A into a MyA."""
        assert isinstance(some_a, ApiManager)
        some_a.__class__ = cls
        assert isinstance(some_a, CachedApiManager)
        return some_a

    def build_dict(self) -> dict[str, float]:
        return dict(
            total_prompt_tokens=self.total_prompt_tokens,
            total_completion_tokens=self.total_completion_tokens,
            total_cost=self.total_cost,
            total_budget=self.total_budget,
        )

    def restore(self):
        workspace_path = Path(self.config.workspace_path)
        filename = workspace_path / GPT_CACHE / f"{self.config.memory_index}-budget.json"
        if filename.exists():
            with filename.open("rb") as f:
                d = orjson.loads(f.read())
            self.total_prompt_tokens = d.get("total_prompt_tokens", 0)
            self.total_completion_tokens = d.get("total_completion_tokens", 0)
            self.total_cost = d.get("total_cost", 0)
            self.total_budget = d.get("total_budget", 0)
        else:
            filename.parent.mkdir(exist_ok=True, parents=True)
            self.flush()

    def flush(self):
        with open(Path(self.config.workspace_path) / GPT_CACHE / f"{self.config.memory_index}-budget.json", "wb") as f:
            f.write(orjson.dumps(self.build_dict(), option=SAVE_OPTIONS))

    def update_cost(self, prompt_tokens, completion_tokens, model):
        """
        Update the total cost, prompt tokens, and completion tokens.

        Args:
        prompt_tokens (int): The number of tokens used in the prompt.
        completion_tokens (int): The number of tokens used in the completion.
        model (str): The model used for the API call.
        """
        super().update_cost(prompt_tokens, completion_tokens, model)
        self.flush()
