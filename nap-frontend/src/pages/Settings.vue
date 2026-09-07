<template>
  <t-tabs :value="activeTab" @change="activeTab = $event" class="settings-tabs">
    <t-tab-panel value="api" label="模型">
      <t-row>
        <t-col :xs="12" :sm="12" :md="6" :xl="4" v-for="endpoint in apiEndpoints" :key="endpoint.base_url"
          :bordered="true" size="small" style="padding: 4px">
          <t-card :title="endpoint.name" size="small">
            <t-descriptions :column="1" size="" tableLayout="auto">
              <t-descriptions-item label="地址" labelStyle="width: 20px;">{{ endpoint.base_url }}</t-descriptions-item>
              <t-descriptions-item label="密钥">{{ maskKey(endpoint.api_key) }}</t-descriptions-item>
              <t-descriptions-item label="模型">
                <t-space :size="4">
                  <t-tag v-for="model in endpoint.models" :key="model" variant="light" size="small">
                    {{ model }}
                  </t-tag>
                </t-space>
              </t-descriptions-item>
            </t-descriptions>
            <template #actions>
              <t-button size="small" variant="outline">编辑</t-button>
              <t-button theme="danger" size="small" variant="text">删除</t-button>
            </template>
          </t-card>
          <t-card></t-card>
        </t-col>
        <t-col :xs="12" :sm="12" :md="6" :xl="4">
          <t-button variant="dashed" block @click="handleAddKey">
            <template #icon><t-icon name="add" /></template>
            添加模型
          </t-button>
        </t-col>
      </t-row>
    </t-tab-panel>

    <t-tab-panel value="appearance" label="外观" class="panel">
      <t-row :gutter="16">
        <t-col :xs="24" :sm="12">
          <t-form-item label="主题" tips="全局主题目前固定在浅色">
            <t-select v-model="settings.theme" :options="themeOptions" />
          </t-form-item>
        </t-col>
        <t-col :xs="24" :sm="12">
          <t-form-item label="语言">
            <t-select v-model="settings.language" :options="languageOptions" />
          </t-form-item>
        </t-col>
      </t-row>
    </t-tab-panel>

    <t-tab-panel value="notification" label="通知" class="panel">
      <div v-for="notif in notifications" :key="notif.key"
        class="flex items-center justify-between py-4 px-2 border-b border-nap-border last:border-b-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-nap-surface-hover flex items-center justify-center flex-shrink-0">
            <t-icon :name="notif.icon" class="text-nap-text-secondary" />
          </div>
          <div>
            <p class="text-sm font-medium text-nap-text">{{ notif.label }}</p>
            <p class="text-xs text-nap-text-secondary mt-0.5">{{ notif.description }}</p>
          </div>
        </div>
        <t-switch v-model="notif.enabled" />
      </div>
    </t-tab-panel>

    <t-tab-panel value="about" label="关于" class="panel">
      <div class="flex items-center gap-4 mb-6">
        <div
          class="w-14 h-14 rounded-2xl bg-nap-gradient flex items-center justify-center text-white text-2xl font-bold shadow-[0_8px_24px_rgba(79,70,229,0.3)]"
          style="font-family: var(--font-display)">
          N
        </div>
        <div>
          <p class="text-lg font-semibold text-nap-text" style="font-family: var(--font-display)">NAP</p>
          <p class="text-sm text-nap-text-secondary">把任务交给我们，安心打个盹</p>
        </div>
      </div>
      <div class="space-y-0 divide-y divide-nap-border">
        <div class="flex justify-between py-3 text-sm">
          <span class="text-nap-text-secondary">版本</span>
          <span class="text-nap-text tabular">0.1.0</span>
        </div>
        <div class="flex justify-between py-3 text-sm">
          <span class="text-nap-text-secondary">平台</span>
          <span class="text-nap-text">Next Agents Platform</span>
        </div>
        <div class="flex justify-between py-3 text-sm">
          <span class="text-nap-text-secondary">技术栈</span>
          <span class="text-nap-text">Vue 3 · TDesign · Vite</span>
        </div>
      </div>
    </t-tab-panel>
  </t-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('api')

const apiEndpoints = ref([
  {
    name: 'OpenAI',
    base_url: 'https://api.openai.com/v1',
    api_key: 'sk-xxxxxxxxxxxxxxxxxxxxxxxx',
    models: ['gpt-4o', 'gpt-4o-mini']
  },
  {
    name: 'Anthropic',
    base_url: 'https://api.anthropic.com/v1',
    api_key: 'sk-ant-xxxxxxxxxxxxxxxx',
    models: ['claude-sonnet-4', 'claude-opus-4']
  },
  {
    name: '自定义端点',
    base_url: 'https://localhost:8000/v1',
    api_key: 'local-xxxxxxxxxxxxxxxx',
    models: ['deepseek-v4', 'kimi', 'qwen2.5']
  }
])

const maskKey = (key: string) =>
  key.length > 8 ? `${key.slice(0, 4)}...${key.slice(-4)}` : '••••••••'

const settings = ref({
  theme: 'light',
  language: 'zh'
})

const themeOptions = [
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' },
  { label: '跟随系统', value: 'system' }
]

const languageOptions = [
  { label: '中文', value: 'zh' },
  { label: 'English', value: 'en' },
  { label: '日本語', value: 'ja' }
]

const notifications = ref([
  { key: 'task_complete', label: '任务完成', description: '智能体完成任务时通知', icon: 'check-circle', enabled: true },
  { key: 'error_alert', label: '错误提醒', description: '智能体出错时通知', icon: 'alert-circle', enabled: true },
  { key: 'weekly_report', label: '周报', description: '每周收到使用量汇总', icon: 'chart-bar', enabled: false }
])

function handleAddKey() {
  console.log('添加 API 密钥')
}
</script>

<style scoped>
.settings-tabs {
  position: sticky;
  background: transparent !important;
  /* padding-top: 2px; */
}

.settings-api {
  display: flex;
  flex-direction: column;
  /* gap: 16px; */
}



:deep(.t-tab-panel) {
  padding: 10px 10px;
}
</style>