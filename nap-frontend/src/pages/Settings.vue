<template>
  <t-tabs :value="activeTab" @change="activeTab = $event" class="settings-tabs">
    <t-tab-panel value="api" label="模型">
      <t-row :gutter="16">
        <t-col v-for="endpoint in apiEndpoints" :key="endpoint.uuid" :xs="24" :sm="12" :md="8" :xl="6">
          <t-card :title="endpoint.name || endpoint.base_url" size="small" :bordered="true">
            <t-descriptions :column="1" size="small" tableLayout="auto">
              <t-descriptions-item label="地址">{{ endpoint.base_url }}</t-descriptions-item>
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
              <t-button size="small" variant="outline" @click="handleEdit(endpoint)">编辑</t-button>
              <t-popconfirm content="确认删除该模型？" @confirm="handleDelete(endpoint)">
                <t-button theme="danger" size="small" variant="text">删除</t-button>
              </t-popconfirm>
            </template>
          </t-card>
        </t-col>
        <t-col :xs="24" :sm="12" :md="8" :xl="6">
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

  <t-dialog
    v-model:visible="createVisible"
    :header="editingUuid ? '编辑模型' : '添加模型'"
    :confirm-btn="{ content: editingUuid ? '保存' : '创建', loading: submitting }"
    @confirm="handleCreate"
  >
    <t-form ref="formRef" :data="createForm" :rules="formRules" label-align="top">
      <t-form-item label="名称" name="name">
        <t-input v-model="createForm.name" placeholder="OpenAI" clearable />
      </t-form-item>
      <t-form-item label="Base URL" name="base_url">
        <t-input v-model="createForm.base_url" placeholder="https://api.openai.com/v1" clearable />
      </t-form-item>
      <t-form-item label="API Key" name="api_key">
        <t-input v-model="createForm.api_key" placeholder="sk-..." type="password" clearable />
      </t-form-item>
      <t-form-item label="模型（用逗号分隔）" name="models">
        <t-input v-model="createForm.modelsText" placeholder="gpt-4o, deepseek-v4, kimi" clearable />
      </t-form-item>
    </t-form>
  </t-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'

interface APIEndpoint {
  uuid: string
  name: string
  base_url: string
  api_key: string
  models: string[]
}

const activeTab = ref('api')

const apiEndpoints = ref<APIEndpoint[]>([])
const listLoading = ref(false)

const maskKey = (key: string) =>
  key.length > 8 ? `${key.slice(0, 4)}...${key.slice(-4)}` : '••••••••'

async function fetchLLMs() {
  listLoading.value = true
  try {
    const data = await API.fetchLLMs<{ llms: APIEndpoint[] }>()
    apiEndpoints.value = data.llms || []
  } catch {
    MessagePlugin.error('加载模型列表失败')
  } finally {
    listLoading.value = false
  }
}

onMounted(fetchLLMs)

const createVisible = ref(false)
const submitting = ref(false)
const editingUuid = ref('')
const formRef = ref()
const createForm = ref({ name: '', base_url: '', api_key: '', modelsText: '' })

const formRules = {
  base_url: [{ required: true, message: '请填写 Base URL', type: 'error' }],
  api_key: [{ required: true, message: '请填写 API Key', type: 'error' }]
}

function handleAddKey() {
  editingUuid.value = ''
  createForm.value = { name: '', base_url: '', api_key: '', modelsText: '' }
  createVisible.value = true
}

function handleEdit(endpoint: APIEndpoint) {
  editingUuid.value = endpoint.uuid
  createForm.value = {
    name: endpoint.name,
    base_url: endpoint.base_url,
    api_key: endpoint.api_key,
    modelsText: endpoint.models.join(', ')
  }
  createVisible.value = true
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const models = createForm.value.modelsText
      .split(/[,，]/)
      .map((s) => s.trim())
      .filter(Boolean)
    const payload = {
      name: createForm.value.name,
      base_url: createForm.value.base_url,
      api_key: createForm.value.api_key,
      models
    }
    if (editingUuid.value) {
      await API.updateLLM(editingUuid.value, payload)
      MessagePlugin.success('更新成功')
    } else {
      await API.createLLM(payload)
      MessagePlugin.success('创建成功')
    }
    createVisible.value = false
    fetchLLMs()
  } catch {
    MessagePlugin.error(editingUuid.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(endpoint: APIEndpoint) {
  try {
    await API.deleteLLM(endpoint.uuid)
    MessagePlugin.success('删除成功')
    fetchLLMs()
  } catch {
    MessagePlugin.error('删除失败')
  }
}

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