import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Agent } from '@/types'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const loading = ref(false)

  const activeAgents = computed(() => agents.value.filter(a => a.status === 'active'))
  const draftAgents = computed(() => agents.value.filter(a => a.status === 'draft'))

  async function fetchAgents() {
    loading.value = true
    try {
      // TODO: replace with actual API call
      agents.value = [
        {
          id: '1',
          name: '研究助理',
          description: '协助进行研究和文献综述',
          avatar: '',
          model: 'gpt-4o',
          status: 'active',
          tools: ['web_search', 'file_read'],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        },
        {
          id: '2',
          name: '代码评审员',
          description: '审查代码并提供改进建议',
          avatar: '',
          model: 'claude-3.5-sonnet',
          status: 'active',
          tools: ['code_review', 'file_read'],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        },
        {
          id: '3',
          name: '数据分析师',
          description: '分析数据并生成报告',
          avatar: '',
          model: 'gpt-4o',
          status: 'draft',
          tools: ['code_exec', 'file_write'],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
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