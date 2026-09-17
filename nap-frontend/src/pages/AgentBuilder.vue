<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <t-space size="12">
        <t-button variant="outline" @click="$router.back()">
          <template #icon><t-icon name="arrow-left" /></template>
        </t-button>
        <div>
          <h1 class="text-2xl font-bold text-nap-text">{{ isEdit ? '编辑智能体' : '创建智能体' }}</h1>
          <p class="text-nap-text-secondary mt-1">配置你的智能体行为与能力</p>
        </div>
      </t-space>
      <t-space size="12">
        <t-button @click="handleSave('active')">保存</t-button>
      </t-space>
    </div>

    <t-row :gutter="[24, 24]">
      <t-col :xs="12" :lg="4">
        <t-space direction="vertical" size="24" style="width: 100%">
          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">基本信息</span></template>
            <t-row :gutter="16">
              <t-col :xs="24" :sm="12">
                <t-form-item label="智能体名称">
                  <t-input v-model="form.name" placeholder="例如：研究助理" />
                </t-form-item>
              </t-col>
              <t-col :xs="24" :sm="12">
                <t-form-item label="模型">
                  <t-select v-model="form.model" :options="modelOptions" placeholder="选择模型" />
                </t-form-item>
              </t-col>
            </t-row>
            <t-form-item label="描述">
              <t-textarea v-model="form.description" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="这个智能体是做什么的？" />
            </t-form-item>
          </t-card>

          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">参数设置</span></template>
            <t-row :gutter="16">
              <t-col :xs="24" :sm="12">
                <t-form-item label="温度" label-align="left" :label-width="72">
                  <t-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-step />
                </t-form-item>
              </t-col>
              <t-col :xs="24" :sm="12">
                <t-form-item label="最大 Token 数" label-align="left" :label-width="96">
                  <t-input-number v-model="form.maxTokens" :min="256" :max="128000" :step="256" theme="normal" />
                </t-form-item>
              </t-col>
            </t-row>
          </t-card>
        </t-space>
      </t-col>

      <t-col :xs="12" :lg="4">
        <t-card :bordered="true" class="settings-card h-full">
          <template #title><span class="text-nap-text">系统提示词</span></template>
          <t-textarea v-model="form.systemPrompt" :autosize="{ minRows: 10, maxRows: 20 }"
            placeholder="你是一位乐于助人的助理..." class="font-mono text-sm" />
          <p class="text-xs text-nap-text-secondary mt-2">定义智能体的性格、知识和行为规则。</p>
        </t-card>
      </t-col>

      <t-col :xs="12" :lg="4">
        <t-space direction="vertical" size="24" style="width: 100%">
          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">工具</span></template>
            <template #description><span class="text-nap-text-secondary">选择这个智能体可以使用的工具</span></template>
            <t-space direction="vertical" :size="8" style="width: 100%">
              <div v-for="tool in availableTools" :key="tool.id"
                class="flex items-center justify-between p-3 rounded-lg border border-nap-border hover:border-nap-primary/30 transition-colors cursor-pointer"
                :class="form.tools.includes(tool.id) ? 'border-nap-primary/50 bg-nap-primary/5' : ''"
                @click="toggleTool(tool.id)">
                <div class="flex items-center gap-3">
                  <t-icon :name="tool.icon" class="text-nap-text-secondary" />
                  <div>
                    <p class="text-sm font-medium text-nap-text">{{ tool.name }}</p>
                    <p class="text-xs text-nap-text-secondary">{{ tool.description }}</p>
                  </div>
                </div>
                <t-checkbox :checked="form.tools.includes(tool.id)" />
              </div>
            </t-space>
          </t-card>

          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">知识库</span></template>
            <template #description><span class="text-nap-text-secondary">关联知识源</span></template>
            <t-select v-model="form.knowledgeBaseIds" multiple :options="knowledgeOptions" placeholder="选择知识库" />
          </t-card>
        </t-space>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'

const route = useRoute()
const isEdit = computed(() => !!route.params.id)

const form = ref({
  name: '',
  description: '',
  model: null as string | null,
  systemPrompt: '',
  temperature: 0.7,
  maxTokens: 4096,
  tools: [] as string[],
  knowledgeBaseIds: [] as string[]
})

const modelOptions = ref<{ label: string; value: string }[]>([])
const knowledgeOptions = ref<{ label: string; value: string }[]>([])

function defaultForm() {
  return {
    name: '',
    description: '',
    model: null as string | null,
    systemPrompt: '',
    temperature: 0.7,
    maxTokens: 4096,
    tools: [] as string[],
    knowledgeBaseIds: [] as string[]
  }
}

async function fetchLLMs() {
  try {
    const data = await API.fetchLLMs<{ llms: { uuid: string; name: string; base_url: string }[] }>()
    modelOptions.value = (data.llms || []).map(
      (llm) => ({
        label: llm.name || llm.base_url,
        value: llm.uuid
      })
    )
  } catch {
    MessagePlugin.error('加载模型列表失败')
  }
}

async function fetchKnowledgeBases() {
  try {
    const data = await API.fetchKnowledgeBases()
    knowledgeOptions.value = (data.items || []).map(
      (kb) => ({ label: kb.name, value: kb.uuid })
    )
  } catch {
    knowledgeOptions.value = []
  }
}

async function fetchAgent(agentUuid: string) {
  try {
    const agent = await API.fetchAgent<{
      uuid: string
      name: string
      description: string
      instruction: string
      llm: string
      status: string
      tools: string[]
    }>(agentUuid)
    const f = defaultForm()
    f.name = agent.name
    f.description = agent.description
    f.systemPrompt = agent.instruction
    f.model = agent.llm || null
    f.tools = agent.tools || []
    form.value = f
  } catch {
    MessagePlugin.error('加载智能体失败')
  }
}

const availableTools = [
  { id: 'retrival', name: '知识库检索', description: '从知识库检索相关内容', icon: 'search' }
]

function toggleTool(toolId: string) {
  const idx = form.value.tools.indexOf(toolId)
  if (idx >= 0) {
    form.value.tools.splice(idx, 1)
  } else {
    form.value.tools.push(toolId)
  }
}

async function handleSave(status: string) {
  const payload = {
    name: form.value.name,
    description: form.value.description,
    instruction: form.value.systemPrompt,
    llm: form.value.model || '',
    status,
    tools: form.value.tools
  }
  try {
    if (route.params.id) {
      await API.updateAgent(route.params.id as string, payload)
      MessagePlugin.success('更新成功')
    } else {
      await API.createAgent(payload)
      MessagePlugin.success('创建成功')
    }
  } catch {
    MessagePlugin.error(route.params.id ? '更新失败' : '创建失败')
  }
}

onMounted(() => {
  fetchLLMs()
  fetchKnowledgeBases()
  if (isEdit.value) {
    fetchAgent(route.params.id as string)
  }
})
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}
</style>