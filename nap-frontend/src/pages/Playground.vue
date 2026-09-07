<template>
  <t-layout class="h-full w-full">
    <t-aside width="304px" class="border-r border-nap-border bg-nap-surface flex flex-col">
      <div class="p-4 pb-3">
        <t-button size="large" block :style="{ borderRadius: '9999px' }" @click="newConversation">
          <template #icon><t-icon name="add" /></template>
          新建会话
        </t-button>
      </div>
      <div class="flex-1 min-h-0 overflow-y-auto px-3 pb-3">
        <p class="px-1 pb-2 text-xs text-nap-text-tertiary select-none">最近会话</p>
        <div v-for="conv in conversations" :key="conv.id" class="conversation-item"
          :class="currentConvId === conv.id ? 'conversation-item-active' : ''" @click="selectConversation(conv.id)">
          <t-icon name="chat" size="15" />
          <span class="flex-1 truncate text-sm font-medium">{{ conv.title }}</span>
          <t-icon v-if="currentConvId === conv.id" name="check" size="14" class="flex-shrink-0" />
        </div>
        <t-empty v-if="conversations.length === 0" class="py-10">
          <template #description>
            <p class="text-sm text-nap-text-secondary">还没有会话</p>
          </template>
        </t-empty>
      </div>
    </t-aside>

    <t-layout>
      <t-header class="h-14 border-b border-nap-border flex items-center justify-between px-6 bg-nap-surface">
        <t-space :size="12">
          <t-select v-model="selectedAgentId" :options="agentOptions" placeholder="选择智能体" class="w-48" size="small" />
          <StatusBadge v-if="selectedAgent" :status="selectedAgent.status" />
        </t-space>
        <t-space :size="8">
          <t-button size="small" variant="text" @click="showActivity = !showActivity">
            <template #icon><t-icon name="list" /></template>
          </t-button>
          <t-button size="small" variant="text" @click="clearChat">
            <template #icon><t-icon name="delete" /></template>
          </t-button>
        </t-space>
      </t-header>

      <t-layout>
        <t-content class="chat-content">
          <div class="flex-1 overflow-y-auto p-6 space-y-4">
            <t-space v-for="msg in messages" :key="msg.id" class="w-full"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'" :style="{ 'display': 'flex' }">
              <t-avatar v-if="msg.role !== 'user'" :icon="'robot'" size="small"
                class="bg-nap-primary/20 text-nap-primary" />
              <div class="max-w-[70%] rounded-2xl px-4 py-3 text-sm"
                :class="msg.role === 'user' ? 'bg-nap-primary text-white rounded-br-md' : 'bg-nap-surface border border-nap-border text-nap-text rounded-bl-md'">
                <div v-html="renderMarkdown(msg.content)" />
                <div v-if="msg.toolCalls && msg.toolCalls.length > 0" class="mt-3 space-y-2">
                  <ToolCallCard v-for="tc in msg.toolCalls" :key="tc.id" :tool-call="tc" />
                </div>
              </div>
            </t-space>

            <t-space v-if="chatStore.isStreaming" class="w-full" :style="{ 'display': 'flex' }">
              <t-avatar :icon="'robot'" size="small" class="bg-nap-primary/20 text-nap-primary" />
              <div
                class="bg-nap-surface border border-nap-border rounded-2xl rounded-bl-md px-4 py-3 text-sm text-nap-text">
                <div v-if="chatStore.streamingContent" v-html="renderMarkdown(chatStore.streamingContent)" />
                <span v-else class="inline-block w-2 h-4 bg-nap-primary animate-pulse" />
              </div>
            </t-space>

            <t-empty v-if="messages.length === 0 && !chatStore.isStreaming" class="py-20">
              <template #description>
                <h3 class="text-lg font-medium text-nap-text">开始一段对话</h3>
                <p class="text-sm text-nap-text-secondary mt-1">选择一个智能体并发送消息</p>
              </template>
              <template #image>
                <t-icon name="chat" size="48" class="text-nap-primary" />
              </template>
            </t-empty>
          </div>

          <div class="p-4 border-t border-nap-border">
            <div class="flex items-end gap-3">
              <t-textarea v-model="inputMessage" :autosize="{ minRows: 1, maxRows: 5 }" placeholder="输入你的消息..."
                class="flex-1" @keydown.enter.exact.prevent="sendMessage" />
              <t-button :disabled="!inputMessage.trim() || chatStore.isStreaming" :loading="chatStore.isStreaming"
                @click="sendMessage">
                <template #icon><t-icon :name="chatStore.isStreaming ? 'stop' : 'send'" /></template>
              </t-button>
            </div>
          </div>
        </t-content>

        <t-aside v-if="showActivity" width="320px"
          class="border-l border-nap-border bg-nap-surface overflow-y-auto activity-panel">
          <t-card :bordered="false" size="small">
            <template #title><span class="text-nap-text">执行活动</span></template>
            <t-space direction="vertical" size="16" style="width: 100%">
              <div v-for="span in traceSpans" :key="span.id" class="space-y-2">
                <div class="flex items-center gap-2 text-sm">
                  <t-icon :name="getSpanIcon(span.type)" class="text-nap-text-secondary" />
                  <span class="text-nap-text">{{ span.name }}</span>
                  <span class="text-xs text-nap-text-secondary ml-auto">{{ span.duration }}ms</span>
                </div>
                <div class="ml-6 text-xs text-nap-text-secondary border-l-2 border-nap-border pl-3">
                  <p><strong>输入:</strong> {{ JSON.stringify(span.input).slice(0, 100) }}</p>
                  <p class="mt-1"><strong>输出:</strong> {{ JSON.stringify(span.output).slice(0, 100) }}</p>
                </div>
              </div>
            </t-space>
          </t-card>
        </t-aside>
      </t-layout>
    </t-layout>
  </t-layout>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ToolCallCard from '@/components/chat/ToolCallCard.vue'
import { useChatStore } from '@/stores/chat'
import { useAgentStore } from '@/stores/agent'
import type { TraceSpan } from '@/types'

const chatStore = useChatStore()
const agentStore = useAgentStore()

const chatContainer = ref<HTMLElement>()
const inputMessage = ref('')
const selectedAgentId = ref<string | null>(null)
const showActivity = ref(false)
const currentConvId = ref<string | null>(null)

const conversations = ref([
  { id: '1', title: '量子计算研究' },
  { id: '2', title: 'API 代码评审' },
  { id: '3', title: '数据分析报告' }
])

const messages = computed(() => chatStore.messages)

const selectedAgent = computed(() =>
  agentStore.agents.find(a => a.id === selectedAgentId.value)
)

const agentOptions = computed(() =>
  agentStore.agents.map(a => ({ label: a.name, value: a.id }))
)

const traceSpans = ref<TraceSpan[]>([
  { id: '1', name: 'LLM 调用', type: 'llm', duration: 1200, input: { prompt: '你好' }, output: { response: '你好，有什么可以帮你？' }, status: 'success' },
  { id: '2', name: '联网搜索', type: 'tool', duration: 800, input: { query: '量子计算' }, output: { results: 5 }, status: 'success' },
  { id: '3', name: '知识检索', type: 'retrieval', duration: 300, input: { query: '量子' }, output: { chunks: 3 }, status: 'success' }
])

function renderMarkdown(content: string) {
  return content
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-nap-surface-hover border border-nap-border rounded-lg p-3 my-2 overflow-x-auto text-[13px]"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-nap-surface-hover px-1.5 py-0.5 rounded text-nap-primary">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

function getSpanIcon(type: string) {
  switch (type) {
    case 'llm': return 'bolt'
    case 'tool': return 'code'
    case 'retrieval': return 'search'
    default: return 'database'
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function sendMessage() {
  if (!inputMessage.value.trim() || chatStore.isStreaming) return

  chatStore.addMessage({
    id: crypto.randomUUID(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date().toISOString()
  })

  inputMessage.value = ''

  chatStore.startStreaming()
  scrollToBottom()

  setTimeout(() => {
    chatStore.updateStreamingContent('我理解你的请求了，让我来处理...')
    scrollToBottom()
  }, 500)

  setTimeout(() => {
    chatStore.updateStreamingContent('我理解你的请求了，让我来处理。\n\n以下是我的发现：')
    scrollToBottom()
  }, 1000)

  setTimeout(() => {
    chatStore.updateStreamingContent('我理解你的请求了，让我来处理。\n\n以下是我的发现：\n\n**关键要点：**\n1. 第一点，包含一些细节\n2. 第二点，包含重要信息\n3. 第三点，总结结论')
    scrollToBottom()
  }, 1500)

  setTimeout(() => {
    chatStore.stopStreaming()
    scrollToBottom()
  }, 2000)
}

function newConversation() {
  currentConvId.value = null
  chatStore.clearMessages()
}

function selectConversation(id: string) {
  currentConvId.value = id
  chatStore.clearMessages()
}

function clearChat() {
  chatStore.clearMessages()
}

onMounted(() => {
  agentStore.fetchAgents()
  if (agentStore.agents.length > 0) {
    selectedAgentId.value = agentStore.agents[0].id
  }
})
</script>

<style scoped>
.conversation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  margin-bottom: 2px;
  cursor: pointer;
  color: var(--nap-muted);
  transition: background-color 0.18s ease, color 0.18s ease;
}

.conversation-item:hover {
  background: var(--td-bg-color-container-hover);
  color: var(--nap-ink);
}

.conversation-item-active,
.conversation-item-active:hover {
  background: var(--td-brand-color-light);
  color: var(--td-brand-color);
}

.conversation-item-active :deep(.t-icon) {
  color: var(--td-brand-color);
}

.chat-content {
  display: flex;
  flex-direction: column;
  background: transparent;
}
</style>