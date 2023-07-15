<template>
  <n-spin :show="loading">
    <template #description>Loading Form</template>
    <n-dialog-provider>
      <NSpace vertical :size="12">
        <n-card :size="`${viewport.isGreaterOrEquals('md') ? 'huge' : 'small'}`" :bordered="false">
          <template #header>
            <n-grid :cols="4">
              <n-gi :span="3">
                <n-text style="display: flex; align-items: center">
                  <img src="@/public/logo.svg" height="40" alt="NLP" />
                  Auto-GPT
                </n-text>
              </n-gi>
              <n-gi v-if="!viewport.isGreaterOrEquals('md')">
                <n-space align="end" justify="end">
                  <n-button v-if="tab === 1" style="font-size: 36px" text @click="tab = 2">
                    <n-icon>
                      <document-edit24-regular></document-edit24-regular>
                    </n-icon>
                  </n-button>
                  <n-button v-else style="font-size: 36px" text @click="tab = 1">
                    <n-icon>
                      <run24-regular></run24-regular>
                    </n-icon>
                  </n-button>
                </n-space>
              </n-gi>
            </n-grid>
          </template>
          <template v-if="viewport.isGreaterOrEquals('md') || tab === 1">
            <n-form ref="formRef" :model="model" :rules="rules" :disabled="bot?.is_active">
              <n-grid x-gap="12" y-gap="12" :cols="4" item-responsive responsive="screen">
                <n-gi :style="`${viewport.isLessThan('md') ? 'height: 25vh' : ''}`" span="4 m:3">
                  <n-space justify="center">
                    <n-grid x-gap="12" y-gap="6" :cols="12" item-responsive responsive="screen">
                      <n-gi style="order: 1" span="12 m:11">
                        <n-grid :cols="4" item-responsive responsive="screen">
                          <n-gi v-if="viewport.isGreaterOrEquals('md')" span="2">
                            <div style="position: relative; width: 100%; height: 100%">
                              <span style="position: absolute; bottom: 0; left: 0">
                                Enter ONE AI Goal or upload an ai_settings file:
                              </span>
                            </div>
                          </n-gi>
                          <n-gi v-else span="1">
                            <div style="position: relative; width: 100%; height: 100%">
                              <span style="position: absolute; bottom: 0; left: 0">AI Goal:</span>
                            </div>
                          </n-gi>
                          <n-gi span="3 m:2">
                            <n-space justify="end">
                              <n-form-item
                                path="ai_settings"
                                :rule="requiredIfNot('ai_goal')"
                                :show-feedback="false"
                                :show-label="false"
                              >
                                <n-upload :custom-request="parseAiSettings" :show-file-list="false">
                                  <n-tag
                                    v-if="model.ai_settings"
                                    size="small"
                                    closable
                                    round
                                    @close="model.ai_settings = null"
                                  >
                                    {{ model.ai_settings.ai_name }}
                                  </n-tag>
                                  <n-button>Upload File</n-button>
                                </n-upload>
                              </n-form-item>
                            </n-space>
                          </n-gi>
                        </n-grid>
                      </n-gi>
                      <n-gi style="order: 2" span="12 m:11">
                        <n-form-item
                          path="ai_goal"
                          :rule="requiredIfNot('ai_settings')"
                          :show-feedback="false"
                          :show-label="false"
                        >
                          <n-input v-model:value="model.ai_goal"></n-input>
                        </n-form-item>
                      </n-gi>
                      <n-gi :style="`order: ${viewport.isGreaterOrEquals('md') ? 3 : 4}`" span="3 m:1">
                        <n-button v-if="bot && bot.is_active" type="error" style="width: 100%" @click="stop">
                          Stop
                        </n-button>
                        <n-button v-else type="success" style="width: 100%" @click="submit">Start</n-button>
                      </n-gi>
                      <n-gi :style="`order: ${viewport.isGreaterOrEquals('md') ? 4 : 3}`" span="9 m:11">
                        <n-grid x-gap="12" y-gap="12" :cols="10" item-responsive responsive="screen">
                          <n-gi span="6 m:2">
                            <n-form-item label-placement="left" :show-feedback="false">
                              <n-tooltip trigger="hover">
                                <template #trigger>
                                  <n-icon size="24px"><lightning /></n-icon>
                                </template>
                                Fast Engine
                              </n-tooltip>
                              <n-select v-model:value="model.fast_engine" :options="llmEngineOptions"></n-select>
                            </n-form-item>
                          </n-gi>
                          <n-gi span="4 m:2">
                            <n-select v-model:value="model.fast_tokens" :options="fastTokensOptions"></n-select>
                          </n-gi>
                          <n-gi span="6 m:2">
                            <n-form-item label-placement="left" :show-feedback="false">
                              <n-tooltip trigger="hover">
                                <template #trigger>
                                  <n-icon size="24px"><brain-circuit24-filled /></n-icon>
                                </template>
                                Smart Engine
                              </n-tooltip>
                              <n-select v-model:value="model.smart_engine" :options="llmEngineOptions"></n-select>
                            </n-form-item>
                          </n-gi>
                          <n-gi span="4 m:2">
                            <n-select v-model:value="model.smart_tokens" :options="smartTokensOptions"></n-select>
                          </n-gi>
                          <n-gi v-if="viewport.isGreaterOrEquals('md')" span="2">
                            <n-form-item label-placement="left">
                              <n-icon size="24px"><image-outline /></n-icon>
                              <n-select v-model:value="model.image_size" :options="imageSizeOptions"></n-select>
                            </n-form-item>
                          </n-gi>
                        </n-grid>
                      </n-gi>
                    </n-grid>
                  </n-space>
                </n-gi>
                <n-gi v-if="viewport.isGreaterOrEquals('md')" span="1">
                  <n-card title="Enabled plugins:">
                    <n-space>
                      <n-tag v-for="(item, i) of enabledPlugins" :key="i" size="small" round>
                        {{ item }}
                      </n-tag>
                    </n-space>
                  </n-card>
                </n-gi>
              </n-grid>
              <n-grid x-gap="12" y-gap="12" :cols="4" item-responsive responsive="screen">
                <n-gi span="4 m:3">
                  <log-viewer ref="logViewerRef" :log="log"></log-viewer>
                </n-gi>
                <n-gi v-if="viewport.isGreaterOrEquals('md')" span="1">
                  <n-list style="height: 160px">
                    <n-list-item>
                      <n-thing>
                        <n-upload :custom-request="uploadWorkspaceFile" :show-file-list="false" multiple>
                          <n-upload-dragger>
                            <div style="margin-bottom: 12px">
                              <n-icon size="48" :depth="3">
                                <archive />
                              </n-icon>
                            </div>
                            <n-text style="font-size: 16px">Click or drag a file to this area to upload</n-text>
                          </n-upload-dragger>
                        </n-upload>
                      </n-thing>
                    </n-list-item>
                  </n-list>
                  <n-list style="height: 440px; overflow: auto">
                    <template v-if="workspacePath !== ''">
                      <n-list-item
                        style="cursor: pointer"
                        @click="fetchWorkspaceFiles(workspacePath.split('/').slice(0, -1).join('/'))"
                      >
                        <n-thing :title="'/..'"></n-thing>
                      </n-list-item>
                    </template>
                    <n-list-item
                      v-for="(item, i) in workspaceFiles"
                      :key="i"
                      :style="`cursor: ${item.is_dir ? 'pointer' : 'auto'}`"
                      @click="item.is_dir ? fetchWorkspaceFiles(item.path) : () => {}"
                    >
                      <n-grid :cols="3">
                        <n-gi :span="2">
                          <n-thing>
                            <template #header>
                              {{ `${item.is_dir ? '/' : ''}${item.name}` }}
                              <template v-if="item.size">
                                <span style="font-size: 10px; font-weight: normal">({{ item.size }})</span>
                              </template>
                            </template>
                          </n-thing>
                        </n-gi>
                        <n-gi>
                          <n-space justify="end">
                            <n-button
                              v-if="!item.is_dir && isPreviewSupported(item.name)"
                              circle
                              @click.stop="loadPreview(item.path)"
                            >
                              <template #icon>
                                <n-icon>
                                  <search />
                                </n-icon>
                              </template>
                            </n-button>
                            <n-button circle @click.stop="downloadFile(item.path)">
                              <template #icon>
                                <n-icon>
                                  <download />
                                </n-icon>
                              </template>
                            </n-button>
                            <n-popconfirm
                              v-model:show="item.show"
                              @positive-click.stop="deleteWorkspaceFile(item.path)"
                            >
                              <template #trigger>
                                <n-button circle type="error" @click.stop="item.show = !!item.show">
                                  <template #icon>
                                    <n-icon>
                                      <close />
                                    </n-icon>
                                  </template>
                                </n-button>
                              </template>
                              Are you sure you want to delete this file?
                            </n-popconfirm>
                          </n-space>
                        </n-gi>
                      </n-grid>
                    </n-list-item>
                  </n-list>
                </n-gi>
                <n-gi span="4 m:3">
                  <n-grid v-if="bot && bot.is_active && bot.runs_left === 0" x-gap="12" y-gap="12" :cols="1">
                    <n-gi>
                      <n-space justify="center">
                        <n-button type="error" @click="stop">No</n-button>
                        <n-button type="success" @click="continueBot">Yes</n-button>
                        <n-select v-model:value="yesCount" style="width: 100px" :options="yesCountOptions"></n-select>
                      </n-space>
                    </n-gi>
                  </n-grid>
                </n-gi>
                <n-gi v-if="viewport.isGreaterOrEquals('md')" span="1">
                  <n-grid x-gap="12" y-gap="12" :cols="2">
                    <n-gi>
                      <n-button style="width: 100%" type="info" @click="downloadFile()">Download all</n-button>
                    </n-gi>
                    <n-gi>
                      <n-popconfirm @positive-click="clearWorkspace()">
                        <template #trigger>
                          <n-button style="width: 100%" type="warning">Clear</n-button>
                        </template>
                        Are you sure you want to clear ALL workspace files?
                      </n-popconfirm>
                    </n-gi>
                  </n-grid>
                </n-gi>
              </n-grid>
            </n-form>
          </template>
          <template v-else>
            <n-grid :cols="1">
              <n-gi>
                <n-card style="height: 20vh; overflow: auto" title="Enabled plugins:">
                  <n-space>
                    <n-tag v-for="(item, i) of enabledPlugins" :key="i" size="small" round>
                      {{ item }}
                    </n-tag>
                  </n-space>
                </n-card>
              </n-gi>
              <n-gi>
                <n-list style="height: 17vh">
                  <n-list-item>
                    <n-thing>
                      <n-upload :custom-request="uploadWorkspaceFile" :show-file-list="false" multiple>
                        <n-upload-dragger>
                          <div style="margin-bottom: 12px">
                            <n-icon size="24" :depth="3">
                              <archive />
                            </n-icon>
                          </div>
                          <n-text style="font-size: 12px">Click or drag a file to this area to upload</n-text>
                        </n-upload-dragger>
                      </n-upload>
                    </n-thing>
                  </n-list-item>
                </n-list>
                <n-list style="height: 40vh; overflow: auto; margin-bottom: 10px">
                  <template v-if="workspacePath !== ''">
                    <n-list-item
                      style="cursor: pointer"
                      @click="fetchWorkspaceFiles(workspacePath.split('/').slice(0, -1).join('/'))"
                    >
                      <n-thing :title="'/..'"></n-thing>
                    </n-list-item>
                  </template>
                  <n-list-item
                    v-for="(item, i) in workspaceFiles"
                    :key="i"
                    :style="`cursor: ${item.is_dir ? 'pointer' : 'auto'}`"
                    @click="item.is_dir ? fetchWorkspaceFiles(item.path) : () => {}"
                  >
                    <n-grid :cols="3">
                      <n-gi :span="2">
                        <n-thing>
                          <template #header>
                            {{ `${item.is_dir ? '/' : ''}${item.name}` }}
                            <template v-if="item.size">
                              <span style="font-size: 10px; font-weight: normal">({{ item.size }})</span>
                            </template>
                          </template>
                        </n-thing>
                      </n-gi>
                      <n-gi>
                        <n-space justify="end">
                          <n-button
                            v-if="!item.is_dir && isPreviewSupported(item.name)"
                            circle
                            size="small"
                            @click.stop="loadPreview(item.path)"
                          >
                            <template #icon>
                              <n-icon>
                                <search />
                              </n-icon>
                            </template>
                          </n-button>
                          <n-button circle size="small" @click.stop="downloadFile(item.path)">
                            <template #icon>
                              <n-icon>
                                <download />
                              </n-icon>
                            </template>
                          </n-button>
                          <n-popconfirm v-model:show="item.show" @positive-click.stop="deleteWorkspaceFile(item.path)">
                            <template #trigger>
                              <n-button circle type="error" size="small" @click.stop="item.show = !!item.show">
                                <template #icon>
                                  <n-icon>
                                    <close />
                                  </n-icon>
                                </template>
                              </n-button>
                            </template>
                            Are you sure you want to delete this file?
                          </n-popconfirm>
                        </n-space>
                      </n-gi>
                    </n-grid>
                  </n-list-item>
                </n-list>
              </n-gi>
              <n-gi>
                <n-grid x-gap="12" y-gap="12" :cols="2">
                  <n-gi>
                    <n-button style="width: 100%" type="info" @click="downloadFile()">Download all</n-button>
                  </n-gi>
                  <n-gi>
                    <n-popconfirm @positive-click="clearWorkspace()">
                      <template #trigger>
                        <n-button style="width: 100%" type="warning">Clear</n-button>
                      </template>
                      Are you sure you want to clear ALL workspace files?
                    </n-popconfirm>
                  </n-gi>
                </n-grid>
              </n-gi>
            </n-grid>
          </template>
        </n-card>
      </NSpace>
      <n-modal v-model:show="previewConfig.show" :on-update:show="closePreview" display-directive="show">
        <n-card
          style="max-width: 1000px"
          :bordered="false"
          :size="`${viewport.isGreaterOrEquals('md') ? 'huge' : 'medium'}`"
          role="dialog"
          aria-modal="true"
        >
          <template #header-extra>
            <n-button text @click="previewConfig.show = false">
              <n-icon size="18px">
                <close />
              </n-icon>
            </n-button>
          </template>
          <template #header>
            <span>
              {{ `Preview: ${previewConfig.name}` }}
            </span>
          </template>
          <pre v-if="!!previewConfig.text"><code v-html='previewConfig.text'></code></pre>
          <img
            v-else-if="!!previewConfig.imageURL"
            style="max-width: 900px"
            :src="previewConfig.imageURL"
            alt="Preview not available"
          />
        </n-card>
      </n-modal>
    </n-dialog-provider>
  </n-spin>
</template>

<script setup lang="ts">
import { FormInst, FormItemRule, FormRules, UploadCustomRequestOptions, useNotification } from 'naive-ui';
import hljs from 'highlight.js';
import { cloneDeep, isArray, isPlainObject, last } from 'lodash-es';
import { Archive, Close, Download, ImageOutline, Search } from '@vicons/ionicons5';
import { Lightning } from '@vicons/carbon';
import { BrainCircuit24Filled, DocumentEdit24Regular, Run24Regular } from '@vicons/fluent';
import {
  AiSettingsSchema,
  BotFormSchema,
  BotSchema,
  GPT35Tokens,
  GPT4Tokens,
  gpt35TokensOptions,
  gpt4TokensOptions,
  ImageSize,
  imageSizeOptions,
  LLMEngine,
  llmEngineOptions,
  WorkspaceFileEnrichedSchema,
  yesCountOptions,
} from '@/interfaces/';
import LogViewer from '@/components/LogViewer.vue';

const oneName = 'single goal';
const oneRole =
  'You are a powerful GPT Agent that will work to achieve any goal you are tasked with provided it is not illegal or unethical';

const notify = useNotification();
const viewport = useViewport();
const tab = ref(1);

const loading = ref(false);
const bot: Ref<BotSchema | null> = ref(null);
const log = ref('');
const yesCount: Ref<number> = ref(5);
const enabledPlugins: Ref<string[]> = ref([]);
const workspaceFiles: Ref<WorkspaceFileEnrichedSchema[]> = ref([]);
const apiManager = useApiManager();
const config = useRuntimeConfig();
const previewConfig: Ref<{ show: boolean; name: string; text?: string; imageURL?: string; isDoc?: boolean }> = ref({
  show: false,
  name: '',
});

const rules: FormRules = {
  required: {
    required: true,
    trigger: 'blur',
  },
  requiredAny: {
    validator(rule: FormItemRule, value: string) {
      if (!value) {
        // @ts-ignore
        return new Error(`${rule.field} is required`);
      }
      return true;
    },
  },
  requiredNumber: {
    required: true,
    trigger: 'blur',
    type: 'number',
  },
};

const formRef = ref<FormInst | null>(null);
const value: BotFormSchema = {
  smart_tokens: GPT4Tokens.t8000,
  fast_tokens: GPT35Tokens.t4000,
  smart_engine: LLMEngine.GPT_4,
  fast_engine: LLMEngine.GPT_3_5_TURBO,
  image_size: ImageSize.s512,
  ai_settings: null,
  ai_goal: '',
};
const model = ref(value);
const logViewerRef = ref<LogViewer | null>(null);
const workspacePath: Ref<string> = ref('');

function requiredIfNot(field: keyof BotFormSchema): FormItemRule {
  return {
    validator(rule: FormItemRule, value: string) {
      if (!value && !model.value[field]) {
        // @ts-ignore
        return new Error(`${rule.field} is required`);
      }
      return true;
    },
  };
}

const fastTokensOptions = computed(() => {
  if ([LLMEngine.GPT_3_5_TURBO, LLMEngine.GPT_3_5_TURBO_16K].includes(model.value.fast_engine)) {
    return gpt35TokensOptions;
  } else {
    return gpt4TokensOptions;
  }
});

const smartTokensOptions = computed(() => {
  if ([LLMEngine.GPT_3_5_TURBO, LLMEngine.GPT_3_5_TURBO_16K].includes(model.value.smart_engine)) {
    return gpt35TokensOptions;
  } else {
    return gpt4TokensOptions;
  }
});

async function stop(e?: MouseEvent) {
  if (e) {
    e.preventDefault();
  }
  await apiManager.stopBot();
  await reFetch(true);
}

async function deleteWorkspaceFile(name: string) {
  await apiManager.deleteWorkspaceFile(name);
  await fetchWorkspaceFiles(workspacePath.value);
}

async function fetchWorkspaceFiles(path: string) {
  workspacePath.value = path;
  workspaceFiles.value = (await apiManager.listWorkspaceFiles(workspacePath.value)).map((item) => ({
    ...item,
    show: workspaceFiles.value.filter((item2) => item.path === item2.path && item2.show).length > 0,
  }));
}

async function clearWorkspace() {
  await apiManager.clearWorkspace();
  await reFetch(true);
}

async function parseAiSettings(options: UploadCustomRequestOptions) {
  const parsedSettings = await apiManager.parseAiSettings(options.file.file!);
  if (parsedSettings) {
    model.value.ai_settings = parsedSettings;
  }
  options.onFinish();
}

async function uploadWorkspaceFile(options: UploadCustomRequestOptions) {
  await apiManager.uploadWorkspaceFile(options.file.file!);
  options.onFinish();
  await fetchWorkspaceFiles(workspacePath.value);
}

async function continueBot() {
  await apiManager.continueBot(yesCount.value);
  await reFetch(true);
}

function downloadFile(name?: string) {
  const url = new URL(`api/v1/bots/workspace/get`, config.public.apiBase || 'http://dummy');
  if (name) {
    url.searchParams.append('name', name);
  }
  url.searchParams.append('v', `${Date.now()}`);
  const a = document.createElement('a');
  const href = url.href.replace('http://dummy', '');
  a.href = href;
  a.download = href.split('/').pop()!;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

async function loadPreview(name: string) {
  const url = `${config.public.apiBase}/api/v1/bots/workspace/get`;
  const response = await useFetch(url, {
    params: { name },
    headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache', Expires: '0' },
  });
  const content = response.data.value;
  previewConfig.value.name = name;
  if (typeof content === 'string') {
    previewConfig.value.text = hljs.highlightAuto(content).value;
  } else if (isPlainObject(content) || isArray(content)) {
    previewConfig.value.text = hljs.highlightAuto(JSON.stringify(content)).value;
  } else if (content instanceof Blob) {
    if (content.type.includes('image')) {
      previewConfig.value.imageURL = URL.createObjectURL(content);
    } else if (content.type === 'application/javascript') {
      previewConfig.value.text = hljs.highlightAuto(await content.text()).value;
    }
  }
  previewConfig.value.show = true;
}

function closePreview(value: boolean) {
  if (!value) {
    previewConfig.value.show = false;
    nextTick(() => {
      previewConfig.value.name = '';
      previewConfig.value.text = undefined;
      previewConfig.value.imageURL = undefined;
    });
  }
}

function isPreviewSupported(name: string) {
  return [
    'txt',
    'text',
    'csv',
    'conf',
    'cnf',
    'sql',
    'html',
    'php',
    'js',
    'css',
    'png',
    'jpg',
    'jpeg',
    'gif',
    'py',
    'json',
    'sh',
    'yaml',
    'toml',
  ].includes(last(name.toLowerCase().split('.'))!);
}

function submit(e: MouseEvent) {
  e.preventDefault();
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      const existingAlgoFinder = await apiManager.getBot();
      if (existingAlgoFinder && existingAlgoFinder.is_active) {
        notify.warning({
          content: 'Test has already been submitted, to cancel it press Stop',
          duration: 10000,
        });
        return false;
      }
      notify.destroyAll();
      let aiSettings = model.value.ai_settings;
      if (!aiSettings) {
        aiSettings = {
          ai_name: oneName,
          ai_role: oneRole,
          ai_goals: [model.value.ai_goal],
          api_budget: 3,
        };
      }
      bot.value = await apiManager.putBot({
        image_size: model.value.image_size,
        smart_engine: model.value.smart_engine,
        smart_tokens: model.value.smart_tokens,
        fast_engine: model.value.fast_engine,
        fast_tokens: model.value.fast_tokens,
        ai_settings: aiSettings,
      });
    }
  });
}

async function reFetch(force?: boolean) {
  if ((bot.value && bot.value.is_active) || force) {
    const oldValue = cloneDeep(bot.value);
    bot.value = await apiManager.getBot();
    log.value = await apiManager.getBotLog();
    await fetchWorkspaceFiles(workspacePath.value);
    if (bot.value && bot.value.is_active !== oldValue?.is_active) {
      if (!bot.value.is_active) {
        if (bot.value.is_failed) {
          notify.error({
            content: 'Bot failed, check Log',
          });
        } else {
          notify.success({
            content: 'Bot finished',
          });
        }
      }
    }
  }
}

onMounted(async () => {
  loading.value = true;
  await Promise.resolve();
  const botFromDb = await apiManager.getBot();
  bot.value = botFromDb;
  if (botFromDb) {
    let aiGoal = '';
    let aiSettings: AiSettingsSchema | null = cloneDeep(botFromDb.ai_settings);
    if (botFromDb.ai_settings) {
      if (botFromDb.ai_settings.ai_name === oneName && botFromDb.ai_settings.ai_role === oneRole) {
        aiGoal = botFromDb.ai_settings.ai_goals[0];
        aiSettings = null;
      }
    }
    model.value = mergeKeepShape(model.value, { ...botFromDb, ai_goal: aiGoal });
    model.value.ai_settings = aiSettings;
    if (!botFromDb.is_active) {
      if (botFromDb.is_failed) {
        notify.error({
          content: 'Bot failed, check Log',
        });
      } else {
        notify.success({
          content: 'Bot finished',
        });
      }
    }
    log.value = await apiManager.getBotLog();
  }
  enabledPlugins.value = await apiManager.getEnabledPlugins();
  await fetchWorkspaceFiles(workspacePath.value);
  loading.value = false;
  setInterval(reFetch, 5000);
});
</script>

<style>
pre {
  white-space: pre-wrap; /* Since CSS 2.1 */
  white-space: -moz-pre-wrap; /* Mozilla, since 1999 */
  white-space: -pre-wrap; /* Opera 4-6 */
  white-space: -o-pre-wrap; /* Opera 7 */
  word-wrap: break-word; /* Internet Explorer 5.5+ */
}
</style>
