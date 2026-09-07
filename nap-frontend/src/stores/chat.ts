import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message } from '@/types'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<any[]>([])
  const currentConversationId = ref<string | null>(null)
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const streamingContent = ref('')

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function updateStreamingContent(content: string) {
    streamingContent.value = content
  }

  function clearMessages() {
    messages.value = []
    streamingContent.value = ''
  }

  function startStreaming() {
    isStreaming.value = true
    streamingContent.value = ''
  }

  function stopStreaming() {
    isStreaming.value = false
    if (streamingContent.value) {
      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: streamingContent.value,
        timestamp: new Date().toISOString()
      })
      streamingContent.value = ''
    }
  }

  return {
    conversations,
    currentConversationId,
    messages,
    isStreaming,
    streamingContent,
    addMessage,
    updateStreamingContent,
    clearMessages,
    startStreaming,
    stopStreaming
  }
})
