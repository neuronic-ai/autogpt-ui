import { LLMEngine, ImageSize, FastTokens, SmartTokens, YesCount } from '@/interfaces/enums';

export const yesCountOptions = Object.values(YesCount)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: value }));
export const llmEngineOptions = Object.values(LLMEngine).map((value) => ({ value, label: value }));
export const imageSizeOptions = Object.values(ImageSize)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value}` }));
export const fastTokensOptions = Object.values(FastTokens)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value}` }));
export const smartTokensOptions = Object.values(SmartTokens)
  .filter((value) => typeof value === 'number')
  .map((value) => ({ value, label: `${value}` }));
