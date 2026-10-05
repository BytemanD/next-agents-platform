import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { API } from '@/api'
import type { Agent } from '@/types'

const WEB_SEARCH_TOOL = 'tavily_hub_search'

interface AgentAPI {
  uuid: string
  name: string
  description: string
  instruction: string
  llm: string
  status: string
  tools: Record<string, Record<string, string>>
  created_at: string
  updated_at: string
  config: string
  knowledge_bases: string[]
}

interface ToolAPI {
  name: string
  description: string
  extras?: { title?: string; type?: string }
}

interface AvailableTool {
  id: string
  name: string
  description: string
}

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const selectedAgentId = ref<string | null>(null)
  const selectedAgentModels = ref<string[]>([])
  const loading = ref(false)
  const availableTools = ref<AvailableTool[]>([])

  const activeAgents = computed(() => agents.value.filter(a => a.status === 'active'))
  const draftAgents = computed(() => agents.value.filter(a => a.status === 'draft'))

  const selectedAgent = computed(() =>
    agents.value.find(a => a.id === selectedAgentId.value) || null
  )

  // 当前智能体可用的工具选项：已注册工具 ∩ 该 agent 配置的工具
  // 联网搜索由对话框里的独立开关控制，不出现在工具下拉中
  const toolOptions = computed(() => {
    const allowed = selectedAgent.value?.tools || {}
    return availableTools.value
      .filter(t => t.id in allowed && t.id !== WEB_SEARCH_TOOL)
      .map(t => ({ label: t.name, value: t.id }))
  })

  async function fetchTools() {
    try {
      const data = await API.fetchTools<{ tools: ToolAPI[] }>()
      availableTools.value = (data.tools || []).map(t => ({
        id: t.name,
        name: t.extras?.title || t.name,
        description: t.description
      }))
    } catch {
      availableTools.value = []
    }
  }

  async function fetchAgents() {
    loading.value = true
    try {
      const data = await API.fetchAgents<{ agents: AgentAPI[] }>()
      agents.value = (data.agents || []).map((a: AgentAPI) => ({
        id: a.uuid,
        uuid: a.uuid,
        name: a.name,
        description: a.description,
        avatar: '',
        model: a.llm,
        status: a.status === 'active' ? 'active' : a.status === 'draft' ? 'draft' : 'error',
        tools: a.tools || {},
        systemPrompt: a.instruction,
        createdAt: a.created_at,
        updatedAt: a.updated_at,
        llm: a.llm,
        config: a.config,
        knowledge_bases: a.knowledge_bases,
      }))
      if (!selectedAgentId.value && agents.value.length > 0) {
        selectedAgentId.value = agents.value[0].id
      }
    } finally {
      loading.value = false
    }
  }

  watch(selectedAgentId, async (id) => {
    selectedAgentModels.value = []
    // 工具列表是全局资源，懒加载一次即可，避免每次切换 agent 重复请求
    if (!availableTools.value.length) fetchTools()
    const agent = agents.value.find(a => a.id === id)
    if (!agent?.model) return
    try {
      const data = await API.fetchLLM<{ models: string[] }>(agent.model)
      selectedAgentModels.value = data.models || []
    } catch {
      selectedAgentModels.value = []
    }
  })

  function setCurrentAgent(agent: Agent | null) {
    currentAgent.value = agent
  }
  function enableWebSearch(): boolean {
    return !!selectedAgent.value && WEB_SEARCH_TOOL in selectedAgent.value.tools
  }
  return {
    agents,
    currentAgent,
    selectedAgentId,
    selectedAgentModels,
    loading,
    activeAgents,
    draftAgents,
    selectedAgent,
    toolOptions,
    webSearchTool: WEB_SEARCH_TOOL,
    fetchAgents,
    fetchTools,
    setCurrentAgent,
    enableWebSearch
  }
})