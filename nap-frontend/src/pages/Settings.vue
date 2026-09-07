<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-nap-text">设置</h1>
      <p class="text-sm text-nap-text-secondary mt-1">配置你的工作区</p>
    </div>

    <t-tabs
      theme="tag"
      :value="activeTab"
      @change="activeTab = $event"
      class="settings-tabs"
    >
      <t-tab-panel value="api" label="API 密钥">
        <t-card :bordered="true">
          <div class="settings-panel">
            <t-space direction="vertical" :size="16" style="width: 100%">
              <div
                v-for="key in apiKeys"
                :key="key.name"
                class="flex items-center justify-between p-3.5 rounded-xl border border-nap-border hover:border-nap-primary/40 transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg bg-nap-accent-soft flex items-center justify-center flex-shrink-0">
                    <t-icon name="key" class="text-nap-primary" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-nap-text">{{ key.name }}</p>
                    <p class="text-xs text-nap-text-secondary font-mono mt-0.5">{{ key.masked }}</p>
                  </div>
                </div>
                <t-space :size="8">
                  <t-button theme="default" size="small" variant="outline">编辑</t-button>
                  <t-button theme="danger" size="small" variant="text">删除</t-button>
                </t-space>
              </div>
              <t-button theme="primary" variant="dashed" block @click="handleAddKey">
                <template #icon><t-icon name="add" /></template>
                添加 API 密钥
              </t-button>
            </t-space>
          </div>
        </t-card>
      </t-tab-panel>

      <t-tab-panel value="appearance" label="外观">
        <t-card :bordered="true">
          <div class="settings-panel">
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
          </div>
        </t-card>
      </t-tab-panel>

      <t-tab-panel value="notification" label="通知">
        <t-card :bordered="true">
          <div class="settings-panel">
            <t-space direction="vertical" :size="4" style="width: 100%">
              <div
                v-for="notif in notifications"
                :key="notif.key"
                class="flex items-center justify-between py-4 px-2 border-b border-nap-border last:border-b-0"
              >
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
            </t-space>
          </div>
        </t-card>
      </t-tab-panel>

      <t-tab-panel value="about" label="关于">
        <t-card :bordered="true">
          <div class="settings-panel">
            <div class="flex items-center gap-4 mb-6">
              <div
                class="w-14 h-14 rounded-2xl bg-nap-gradient flex items-center justify-center text-white text-2xl font-bold shadow-[0_8px_24px_rgba(79,70,229,0.3)]"
                style="font-family: var(--font-display)"
              >
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
                <span class="text-nap-text">下一代智能体平台</span>
              </div>
              <div class="flex justify-between py-3 text-sm">
                <span class="text-nap-text-secondary">技术栈</span>
                <span class="text-nap-text">Vue 3 · TDesign · Vite</span>
              </div>
            </div>
          </div>
        </t-card>
      </t-tab-panel>
    </t-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('api')

const apiKeys = ref([
  { name: 'OpenAI', masked: 'sk-...xxxx' },
  { name: 'Anthropic', masked: 'sk-ant-...xxxx' },
  { name: '自定义端点', masked: 'https://...xxxx' }
])

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
.settings-tabs :deep(.t-tabs__nav) {
  position: sticky;
  top: 0;
  z-index: 5;
  background: var(--nap-page);
  padding-top: 2px;
}

.settings-tabs :deep(.t-tabs__nav-wrap) {
  background: transparent;
}

.settings-tabs :deep(.t-tabs__content-inner) {
  padding-top: 20px;
}

.settings-panel {
  padding: 4px 0;
}
</style>