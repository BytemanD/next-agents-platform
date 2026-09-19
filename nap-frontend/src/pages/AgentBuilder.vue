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
        <t-button :loading="saving" @click="handleSave('active')">保存</t-button>
      </t-space>
    </div>

    <t-row :gutter="[12, 12]">
      <t-col :xs="12" :lg="4">
        <t-card size="small" class="my-2" title="基本信息">
          <t-form>
            <t-form-item label="名称" name="name">
              <t-input placeholder="例如：研究助理" v-model="form.name" />
            </t-form-item>
            <t-form-item label="模型提供商" name="llm">
              <t-select v-model="form.llm" :options="modelOptions" placeholder="选择模型" />
            </t-form-item>
            <t-form-item label="描述">
              <t-textarea v-model="form.description" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="这个智能体是做什么的？" />
            </t-form-item>
            <t-divider>参数设置</t-divider>
            <t-form-item label="温度">
              <t-slider v-model="form.config.temperature" :min="0" :max="2" :step="0.1" show-step />
            </t-form-item>
            <t-form-item label="最大 Token 数">
              <t-input-number v-model="form.config.max_tokens" :min="256" :max="128000" :step="256" theme="normal" />
            </t-form-item>
          </t-form>
        </t-card>
      </t-col>

      <t-col :xs="12" :lg="4">
        <t-card size="small" class="my-2">
          <template #title>知识库</template>
          <template #description>关联知识源</template>
          <t-select v-model="form.knowledge_bases" multiple :options="knowledgeOptions" placeholder="选择知识库" />
        </t-card>
        <t-card size="small" class="my-2">
          <template #title>工具</template>
          <template #description>选择这个智能体可以使用的工具</template>
          <t-list size="small">
            <t-list-item
              v-for="tool in availableTools" :key="tool.name" size="small"
              :class="form.tools.includes(tool.id) ? 'border-nap-primary/50 bg-nap-primary/5' : ''"
              class="rounded-lg">
              <template #content>
                <t-list-item-meta :title="tool.name">
                  <template #image>
                    <t-icon :name="tool.icon" class="ml-3 mt-3" size="30" />
                  </template>
                  <template #description>
                    <t-text :content="tool.description" :ellipsis="{ row: 2, expandable: true, collapsible: true }" />
                  </template>
                </t-list-item-meta>
              </template>
              <template #action>
                <t-checkbox :checked="form.tools.includes(tool.id)" @change="toggleTool(tool.id)" />
              </template>
            </t-list-item>
          </t-list>
        </t-card>
      </t-col>

      <t-col :xs="12" :lg="4">
        <t-card size="small" class="my-2" title="系统提示词" subtitle="定义智能体的性格、知识和行为规则。">
          <t-textarea v-model="form.instruction" :autosize="{ minRows: 10, maxRows: 20 }" placeholder="你是一位乐于助人的助理..."
            class="font-mono text-sm" />
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'

interface AgentForm {
  name: string
  description: string
  llm: string
  instruction: string
  status: string
  config: { temperature: number; max_tokens: number }
  knowledge_bases: string[]
  tools: string[]
}

const route = useRoute()
const isEdit = computed(() => !!route.params.id)

const form = ref<AgentForm>(defaultForm())
const saving = ref(false)

function defaultForm(): AgentForm {
  return {
    name: '',
    description: '',
    llm: '',
    instruction: '',
    status: 'draft',
    config: { temperature: 0.7, max_tokens: 4096 },
    knowledge_bases: [],
    tools: []
  }
}

const modelOptions = ref<{ label: string; value: string }[]>([])
const knowledgeOptions = ref<{ label: string; value: string }[]>([])
const availableTools = ref<ToolItem[]>([])

interface ToolItem {
  id: string
  name: string
  description: string
  icon: string
}

const TOOL_ICONS: Record<string, string> = {
  search: 'search',
  listing: 'list',
  tool: 'tool'
}

interface BackendTool {
  name: string
  description: string
  extras?: { title?: string; type?: string }
}

async function fetchTools() {
  try {
    const data = await API.fetchTools<{ tools: BackendTool[] }>()
    availableTools.value = (data.tools || []).map((tool) => ({
      id: tool.name,
      name: tool.extras?.title || tool.name,
      description: tool.description,
      icon: TOOL_ICONS[tool.extras?.type || ''] || 'tool'
    }))
  } catch {
    availableTools.value = []
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
    const agent = await API.fetchAgent<AgentForm & { uuid: string }>(agentUuid)
    form.value = {
      name: agent.name || '',
      description: agent.description || '',
      llm: agent.llm || '',
      instruction: agent.instruction || '',
      status: agent.status || 'draft',
      config: {
        temperature: agent.config?.temperature ?? 1,
        max_tokens: agent.config?.max_tokens ?? null
      },
      knowledge_bases: agent.knowledge_bases || [],
      tools: agent.tools || []
    }
  } catch {
    MessagePlugin.error('加载智能体失败')
  }
}

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
    instruction: form.value.instruction,
    llm: form.value.llm,
    status,
    config: form.value.config,
    knowledge_bases: form.value.knowledge_bases,
    tools: form.value.tools
  }
  saving.value = true
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
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchLLMs()
  fetchKnowledgeBases()
  fetchTools()
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