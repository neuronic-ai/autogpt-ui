import sys
from pathlib import Path
from typing import Any, Type

from pydantic import AnyUrl, AnyHttpUrl, BaseSettings, Field, validator, RedisDsn


AVAILABLE_PLUGINS = {
    "AutoGPTApiTools",
    "AutoGPTEmailPlugin",
    "AutoGPTTwitter",
    "AutoGPTSceneXPlugin",
    "PlannerPlugin",
    "AutoGPT_Slack",
    # "AutoGPTWebInteraction",
    "AutoGPT_YouTube",
}


class MysqlDsn(AnyUrl):
    allowed_schemes = {"mysql"}
    user_required = True


class Settings(BaseSettings):
    BASE_URL: str = ""
    API_V1_STR: str | None = None
    PROJECT_NAME: str = "Auto-gpt-UI"
    VERSION: str = "1.0.0"

    TESTING: bool = "pytest" in sys.modules

    NO_AUTH: bool = False

    SESSION_COOKIE: str = "sessionId"
    SESSION_API_URL: AnyHttpUrl = "http://localhost"
    SESSION_API_USER_PATH: str = "/user"
    SESSION_API_SESSION_PATH: str = "/session"

    WORKSPACES_DIR: Path = Field(
        "/workspaces", description="Path to workspaces directory, default value is used in docker environment"
    )
    PLUGINS_DIR: Path = Field("/plugins", description="Path to plugins directory used in Auto-GPT")

    @validator("WORKSPACES_DIR")
    def validate_workspace(cls, v: Path) -> Path:
        return v.resolve()

    PYTHON_BINARY: str = Field("python", description="Path to python binary if run outside Docker")

    TAIL_LOG_COUNT: int = Field(5000, description="Tail logs for this much rows for the UI")
    MAX_WORKSPACE_FILE_SIZE: int = Field(
        5 * 1024 * 1024, description="Max size for a workspace file to upload, 5MiB by default"
    )
    MAX_CACHE_SIZE: int = Field(
        5 * 1024 * 1024, description="Max size for a cache file before it gets truncates, 5MiB by default"
    )

    OPENAI_LOCAL_KEY: str = Field("", description="Used only if Auth is disabled")

    EXECUTE_LOCAL_COMMANDS: bool = Field(False, description="Allow shell commands execution", auto_gpt=True)

    @validator("API_V1_STR", pre=True)
    def set_api_v1_str(cls, v: str | None, values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return f"{values.get('BASE_URL') or ''}/api/v1"

    DISABLED_COMMAND_CATEGORIES: list = Field(
        default_factory=lambda: ["autogpt.commands.execute_code"],
        description="Disable specific Auto-GPT command categories",
        auto_gpt=True,
    )
    DENY_COMMANDS: list[str] = Field(default_factory=list, description="Disable specific shell commands", auto_gpt=True)
    ALLOW_COMMANDS: list[str] = Field(
        default_factory=list, description="Allow only These shell commands", auto_gpt=True
    )
    ALLOWLISTED_PLUGINS: list[str] = Field(
        default_factory=list,
        description=f"Allow only These plugins, one of: {', '.join(AVAILABLE_PLUGINS)}",
        auto_gpt=True,
    )

    DATABASE_URL: MysqlDsn = Field(
        ...,
        description="Database URL, ie: mysql://user:password@localhost:3306/auto_gpt_ui",
    )

    # @validator("DATABASE_URL")
    # def assemble_db_connection(cls, v: MysqlDsn, values: dict[str, Any]) -> str:
    #     if not values.get("TESTING"):
    #         return v
    #     return v.path

    REDIS_URL: RedisDsn = "redis://redis:6379/0"

    EMAIL_ADDRESS: str | None = Field(None, description="For Email plugin", auto_gpt=True)
    EMAIL_PASSWORD: str | None = Field(None, auto_gpt=True)
    EMAIL_SMTP_HOST: str | None = Field(None, auto_gpt=True)
    EMAIL_SMTP_PORT: int = Field(587, auto_gpt=True)
    EMAIL_IMAP_SERVER: str | None = Field(None, auto_gpt=True)
    EMAIL_MARK_AS_SEEN: bool = Field(False, auto_gpt=True)
    EMAIL_SIGNATURE: str = Field("This was sent by Auto-GPT", auto_gpt=True)
    EMAIL_DRAFT_MODE_WITH_FOLDER: str = Field("[Gmail]/Drafts", auto_gpt=True)

    TW_CONSUMER_KEY: str | None = Field(None, description="For Twitter plugin", auto_gpt=True)
    TW_CONSUMER_SECRET: str | None = Field(None, auto_gpt=True)
    TW_ACCESS_TOKEN: str | None = Field(None, auto_gpt=True)
    TW_ACCESS_TOKEN_SECRET: str | None = Field(None, auto_gpt=True)
    TW_CLIENT_ID: str | None = Field(None, auto_gpt=True)
    TW_CLIENT_ID_SECRET: str | None = Field(None, auto_gpt=True)

    SCENEX_API_KEY: str | None = Field(None, description="For SceneX plugin", auto_gpt=True)

    SLACK_BOT_TOKEN: str | None = Field(None, description="For Slack plugin", auto_gpt=True)
    SLACK_CHANNEL: str | None = Field(None, auto_gpt=True)

    YOUTUBE_API_KEY: str | None = Field(None, description="For Youtube plugin", auto_gpt=True)

    class Config:
        env_file = "env-backend.local.env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name in (
                "DISABLED_COMMAND_CATEGORIES",
                "DENY_COMMANDS",
                "ALLOW_COMMANDS",
                "ALLOWLISTED_PLUGINS",
            ):
                return list(map(str.strip, raw_val.split(",")))
            return cls.json_loads(raw_val)


settings = Settings()


def build_example_env(
    config_class: Type[BaseSettings] = Settings,
    file_name: str = "./env-backend.env.example",
    skip_=(
        "BASE_URL",
        "API_V1_STR",
        "PROJECT_NAME",
        "VERSION",
        "NO_AUTH",
        "SMTP_USE_TLS",
        "SMTP_START_TLS",
    ),
):
    skip_ = set(skip_)
    with open(file_name, "w") as f:
        for field_name, field in config_class.__fields__.items():
            if field_name in skip_:
                continue
            default_value = field.default if field.default is not None else ""
            if field.default_factory:
                default_value = field.default_factory()
            if isinstance(default_value, bool):
                default_value = int(default_value)
            if isinstance(default_value, list):
                default_value = ",".join(default_value)
            description = field.field_info.description
            if description:
                commentary = "\n# ".join(description.split("\n"))
                f.write(f"# {commentary}\n{field_name}={default_value}\n")
            else:
                f.write(f"{field_name}={default_value}\n")
