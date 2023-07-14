from typing import Any

from pydantic import BaseModel, Field
from prisma.partials import BotInCreateSchema as _BotInCreateSchema, BotSchema as _BotSchema

from app.schemas.enums import ImageSize, EngineTokens, LLMEngine


class AiSettingsSchema(BaseModel):
    ai_goals: list[str] = Field(..., max_items=20, max_length=2000)
    ai_name: str = Field(..., max_length=30)
    ai_role: str = Field(..., max_length=1200)
    api_budget: float = Field(0.0, ge=0)


class BotSchema(_BotSchema):
    ai_settings: dict[str, Any]


class BotInCreateSchema(_BotInCreateSchema):
    fast_engine: LLMEngine = LLMEngine.GPT_3_5_TURBO
    smart_engine: LLMEngine = LLMEngine.GPT_4
    fast_tokens: EngineTokens = EngineTokens.t4000
    smart_tokens: EngineTokens = EngineTokens.t4000
    image_size: ImageSize = ImageSize.s512
    ai_settings: AiSettingsSchema


class WorkspaceFileSchema(BaseModel):
    name: str
    path: str
    is_dir: bool
    mime_type: str | None = None
    size: str | None = None
