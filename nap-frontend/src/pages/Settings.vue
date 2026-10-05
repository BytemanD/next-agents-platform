<template>
  <t-tabs :value="activeTab" @change="activeTab = $event" class="settings-tabs">
    <t-tab-panel value="llm" label="模型">
      <settings-llm></settings-llm>
    </t-tab-panel>
    <t-tab-panel value="mcp" label="MCP">
      <settings-mcp></settings-mcp>
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
          <p class="text-sm text-nap-text-secondary">Hand it over and take a nap</p>
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
import SettingsMcp from './SettingsMCP.vue'
import SettingsLlm from './SettingsLLM.vue'

const activeTab = ref('llm')

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
</script>

<style scoped>
.settings-tabs {
  position: sticky;
  background: transparent !important;
  /* padding-top: 2px; */
}

:deep(.t-tab-panel) {
  padding: 10px 10px;
}
</style>