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
  mcp_uuids: string[]
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

interface AvailableMcp {
  uuid: string
  name: string
  url: string
}

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const selectedAgentId = ref<string | null>(null)
  const selectedAgentModels = ref<string[]>([])
  const loading = ref(false)
  const availableTools = ref<AvailableTool[]>([])
  const availableMcps = ref<AvailableMcp[]>([])

  const activeAgents = computed(() => agents.value.filter(a => a.status === 'active'))
  const draftAgents = computed(() => agents.value.filter(a => a.status === 'draft'))

  const selectedAgent = computed(() =>
    agents.value.find(a => a.id === selectedAgentId.value) || null
  )

  // 后端 detail 接口只回该 agent 已启用的工具，这里再排掉联网搜索
  // （它由对话框里的独立开关控制，不出现在工具下拉中）
  const toolOptions = computed(() =>
    availableTools.value
      .filter(t => t.id !== WEB_SEARCH_TOOL)
      .map(t => ({ label: t.name, value: t.id }))
  )

  // 同理，detail 只回该 agent 已关联的 MCP
  const mcpOptions = computed(() =>
    availableMcps.value.map(m => ({ label: m.name || m.url, value: m.uuid }))
  )

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
        mcp_uuids: a.mcp_uuids || [],
      }))
      if (!selectedAgentId.value && agents.value.length > 0) {
        selectedAgentId.value = agents.value[0].id
      }
    } finally {
      loading.value = false
    }
  }

  // 按当前 agent 拉取工具 / MCP / 模型元信息，一次请求覆盖三者
  async function fetchAgentDetail(uuid: string) {
    try {
      const data = await API.fetchAgentDetail<{
        llm: { uuid: string; name: string; base_url: string; models: string[] }
        tools: ToolAPI[]
        mcps: { uuid: string; name: string; url: string }[]
      }>(uuid)
      availableTools.value = (data.tools || []).map(t => ({
        id: t.name,
        name: t.extras?.title || t.name,
        description: t.description
      }))
      availableMcps.value = data.mcps || []
      selectedAgentModels.value = data.llm?.models || []
    } catch {
      availableTools.value = []
      availableMcps.value = []
      selectedAgentModels.value = []
    }
  }

  watch(selectedAgentId, (id) => {
    selectedAgentModels.value = []
    availableTools.value = []
    availableMcps.value = []
    if (!id) return
    fetchAgentDetail(id)
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
    mcpOptions,
    webSearchTool: WEB_SEARCH_TOOL,
    fetchAgents,
    fetchAgentDetail,
    setCurrentAgent,
    enableWebSearch
  }
})