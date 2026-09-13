import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { API } from '@/api'
import type { Agent } from '@/types'

interface AgentAPI {
  uuid: string
  name: string
  description: string
  instruction: string
  llm: string
  status: string
  tools: string[]
  created_at: string
  updated_at: string
}

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const selectedAgentId = ref<string | null>(null)
  const selectedAgentModels = ref<string[]>([])
  const loading = ref(false)

  const activeAgents = computed(() => agents.value.filter(a => a.status === 'active'))
  const draftAgents = computed(() => agents.value.filter(a => a.status === 'draft'))

  const selectedAgent = computed(() =>
    agents.value.find(a => a.id === selectedAgentId.value) || null
  )

  async function fetchAgents() {
    loading.value = true
    try {
      const data = await API.fetchAgents<{ agents: AgentAPI[] }>()
      agents.value = (data.agents || []).map((a: AgentAPI) => ({
        id: a.uuid,
        name: a.name,
        description: a.description,
        avatar: '',
        model: a.llm,
        status: a.status === 'active' ? 'active' : a.status === 'draft' ? 'draft' : 'error',
        tools: a.tools || [],
        systemPrompt: a.instruction,
        createdAt: a.created_at,
        updatedAt: a.updated_at
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

  return {
    agents,
    currentAgent,
    selectedAgentId,
    selectedAgentModels,
    loading,
    activeAgents,
    draftAgents,
    selectedAgent,
    fetchAgents,
    setCurrentAgent
  }
})