import { LLMEngine, ImageSize, GPT35Tokens, GPT4Tokens } from '@/interfaces/enums';

export interface AiSettingsSchema {
  ai_goals: string[];
  ai_name: string;
  ai_role: string;
  api_budget?: number | null;
}

export interface BaseBotSchema {
  smart_tokens: GPT4Tokens;
  fast_tokens: GPT35Tokens;
  smart_engine: LLMEngine;
  fast_engine: LLMEngine;
  image_size: ImageSize;
  ai_settings: AiSettingsSchema | null;
}

export interface BotInCreateSchema extends BaseBotSchema {
  ai_settings: AiSettingsSchema;
}

export interface BotSchema extends BaseBotSchema {
  ai_settings: AiSettingsSchema;
  is_active: boolean;
  is_failed: boolean;
  runs_left: number;
}

export interface BotFormSchema extends BaseBotSchema {
  ai_goal: string;
}

export interface WorkspaceFileSchema {
  name: string;
  path: string;
  is_dir: boolean;
  mime_type: string | null;
  size: string | null;
}

export interface WorkspaceFileEnrichedSchema extends WorkspaceFileSchema {
  show: boolean;
}
