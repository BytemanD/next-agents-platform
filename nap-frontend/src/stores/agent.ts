import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
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
  const loading = ref(false)

  const activeAgents = computed(() => agents.value.filter(a => a.status === 'active'))
  const draftAgents = computed(() => agents.value.filter(a => a.status === 'draft'))

  async function fetchAgents() {
    loading.value = true
    try {
      const { data } = await axios.get('/api/v1/agents')
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
    } finally {
      loading.value = false
    }
  }

  function setCurrentAgent(agent: Agent | null) {
    currentAgent.value = agent
  }

  return {
    agents,
    currentAgent,
    loading,
    activeAgents,
    draftAgents,
    fetchAgents,
    setCurrentAgent
  }
})