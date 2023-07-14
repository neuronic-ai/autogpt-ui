import { LLMEngine, ImageSize, GPT35Tokens, GPT4Tokens, YesCount } from '@/interfaces/enums';

export const yesCountOptions = Object.values(YesCount)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: value }));
export const llmEngineOptions = Object.values(LLMEngine).map((value) => ({
  value,
  label: value,
}));
export const imageSizeOptions = Object.values(ImageSize)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value}x${value}` }));
export const gpt35TokensOptions = Object.values(GPT35Tokens)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value} Tokens` }));
export const gpt4TokensOptions = Object.values(GPT4Tokens)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value} Tokens` }));
