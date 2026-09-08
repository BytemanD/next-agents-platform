import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { KnowledgeBase, KnowledgeItem } from '@/types'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const items = ref<KnowledgeItem[]>([])
  const loading = ref(false)

  const totalSize = computed(() =>
    knowledgeBases.value.reduce((sum, kb) => sum + kb.file_size, 0)
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

  async function fetchKnowledgeItems() {
    loading.value = true
    try {
      const { data } = await axios.get('/api/v1/knowledge')
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
    loading,
    totalSize,
    fetchKnowledgeBases,
    fetchKnowledgeItems,
    itemsByBase
  }
})
