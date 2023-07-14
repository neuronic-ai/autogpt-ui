import { FetchError } from 'ofetch';
import { useNotification } from 'naive-ui';
import {
  ApiError,
  AiSettingsSchema,
  BotSchema,
  LogResponse,
  BotInCreateSchema,
  WorkspaceFileSchema,
  YesCount,
} from '@/interfaces';

interface ApiManager {
  putBot(v: BotInCreateSchema): Promise<BotSchema | null>;
  getBot(): Promise<BotSchema | null>;
  getEnabledPlugins(): Promise<string[]>;
  listWorkspaceFiles(path?: string | null): Promise<WorkspaceFileSchema[]>;
  deleteWorkspaceFile(name: string): Promise<void>;
  uploadWorkspaceFile(file: File | Blob): Promise<void>;
  clearWorkspace(): Promise<void>;
  parseAiSettings(file: File | Blob): Promise<AiSettingsSchema | null>;
  continueBot(count: YesCount): Promise<void>;
  stopBot(): Promise<void>;
  getBotLog(): Promise<string>;
}

export const useApiManager = function () {
  const config = useRuntimeConfig();
  const notify = useNotification();

  // @ts-ignore
  function onResponseError({ response }) {
    if (response.status && [401, 403].includes(response.status)) {
      navigateTo(`https://${window.location.hostname}/auth/`, { external: true });
    }
  }

  async function stopBot(): Promise<void> {
    await useFetch(`${config.public.apiBase}/api/v1/bots/stop`, {
      onResponseError,
    });
  }

  async function continueBot(count: YesCount): Promise<void> {
    await useFetch(`${config.public.apiBase}/api/v1/bots/continue`, {
      onResponseError,
      params: { count },
    });
  }

  async function deleteWorkspaceFile(name: string): Promise<void> {
    await useFetch(`${config.public.apiBase}/api/v1/bots/workspace`, {
      method: 'delete',
      params: { name },
      onResponseError,
    });
  }

  async function parseAiSettings(file: File | Blob): Promise<AiSettingsSchema | null> {
    const formData = new FormData();
    formData.append('file', file);
    const { data, error } = await useFetch<AiSettingsSchema, FetchError<ApiError>, string, 'post'>(
      `${config.public.apiBase}/api/v1/bots/parse-settings`,
      {
        method: 'post',
        body: formData,
        onResponseError,
      },
    );
    if (error.value) {
      notify.error({
        content: error.value?.data?.detail || 'Unknown error occurred',
      });
    }
    return data.value as AiSettingsSchema;
  }

  async function uploadWorkspaceFile(file: File | Blob): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);
    const { error } = await useFetch<null, FetchError<ApiError>, string, 'post'>(
      `${config.public.apiBase}/api/v1/bots/workspace`,
      {
        method: 'post',
        body: formData,
        onResponseError,
      },
    );
    if (error.value) {
      notify.error({
        content: error.value?.data?.detail || 'Unknown error occurred',
      });
    }
  }

  async function clearWorkspace(): Promise<void> {
    await useFetch(`${config.public.apiBase}/api/v1/bots/workspace/clear`, {
      onResponseError,
    });
  }

  async function listWorkspaceFiles(path?: string | null): Promise<WorkspaceFileSchema[]> {
    return (
      (
        await useFetch<WorkspaceFileSchema[]>(`${config.public.apiBase}/api/v1/bots/workspace`, {
          params: { path },
          onResponseError,
        })
      ).data.value || []
    );
  }

  async function putBot(v: BotInCreateSchema): Promise<BotSchema | null> {
    const notification = notify.info({
      content: `Creating bot...`,
    });
    const { data, error } = await useFetch<BotSchema, FetchError<ApiError>, string, 'post'>(
      `${config.public.apiBase}/api/v1/bots/`,
      {
        method: 'post',
        body: v,
        onResponseError,
      },
    );
    if (error.value) {
      notify.error({
        content: error.value?.data?.detail || 'Unknown error occurred',
      });
    } else if ((data.value as BotSchema).is_failed) {
      notification.destroy();
      notify.error({
        content: `Failed to create bot, check logs`,
        duration: 3000,
      });
    } else {
      notification.destroy();
      notify.success({
        content: `Successfully created bot`,
        duration: 3000,
      });
    }
    return data.value as BotSchema;
  }

  async function getBot(): Promise<BotSchema | null> {
    try {
      return (
        await useFetch<BotSchema>(`${config.public.apiBase}/api/v1/bots/`, {
          onResponseError,
        })
      ).data.value as BotSchema;
    } catch (err) {
      return null;
    }
  }

  async function getEnabledPlugins(): Promise<string[]> {
    try {
      return (
        await useFetch<string[]>(`${config.public.apiBase}/api/v1/bots/enabled-plugins`, {
          onResponseError,
        })
      ).data.value as string[];
    } catch (err) {
      return [];
    }
  }

  async function getBotLog(): Promise<string> {
    try {
      return (
        (
          await useFetch<LogResponse>(`${config.public.apiBase}/api/v1/bots/log`, {
            onResponseError,
          })
        ).data.value?.text || ''
      );
    } catch (err) {
      return '';
    }
  }

  return {
    putBot,
    getBot,
    getEnabledPlugins,
    stopBot,
    continueBot,
    getBotLog,
    deleteWorkspaceFile,
    listWorkspaceFiles,
    uploadWorkspaceFile,
    clearWorkspace,
    parseAiSettings,
  } as ApiManager;
};
