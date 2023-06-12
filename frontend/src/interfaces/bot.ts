import { LLMEngine, ImageSize, FastTokens, SmartTokens } from '@/interfaces/enums';

export interface AiSettingsSchema {
  ai_goals: string[];
  ai_name: string;
  ai_role: string;
}

export interface BaseBotSchema {
  smart_tokens: SmartTokens;
  fast_tokens: FastTokens;
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

export interface BotFormSchema extends BaseBotSchema {}

export interface WorkspaceFileSchema {
  name: string;
  path: string;
  is_dir: boolean;
  mime_type: string | null;
}

export interface WorkspaceFileEnrichedSchema extends WorkspaceFileSchema {
  show: boolean;
}
