import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { KnowledgeBase, KnowledgeItem } from '@/types'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const items = ref<KnowledgeItem[]>([])
  const docCounts = ref<Record<string, number>>({})
  const loading = ref(false)

  const totalSize = computed(() =>
    items.value.reduce((sum, item) => sum + item.size, 0)
  )

  const totalDocs = computed(() =>
    Object.values(docCounts.value).reduce((sum, n) => sum + n, 0)
  )

  async function fetchKnowledgeBases() {
    loading.value = true
    try {
      const { data } = await axios.get('/api/v1/knowledge-bases')
      knowledgeBases.value = data.items || []
    } finally {
      loading.value = false
    }
  }

  async function fetchDocCounts() {
    for (const kb of knowledgeBases.value) {
      try {
        const { data } = await axios.get(`/api/v1/knowledge-bases/${kb.uuid}/stats`)
        docCounts.value[kb.uuid] = data.total ?? (data as number) ?? 0
      } catch {
        docCounts.value[kb.uuid] = 0
      }
    }
  }

  async function fetchKnowledgeItems(kbId?: string) {
    loading.value = true
    try {
      const url = kbId
        ? `/api/v1/knowledge-bases/${kbId}/knowledges`
        : '/api/v1/knowledges'
      const { data } = await axios.get(url)
      items.value = data.items || []
    } finally {
      loading.value = false
    }
  }

  function itemsByBase(baseUuid: string) {
    return items.value.filter(item => item.knowledge === baseUuid)
  }

  return {
    knowledgeBases,
    items,
    docCounts,
    loading,
    totalSize,
    totalDocs,
    fetchKnowledgeBases,
    fetchDocCounts,
    fetchKnowledgeItems,
    itemsByBase
  }
})