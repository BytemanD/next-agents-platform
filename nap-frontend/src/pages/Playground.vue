<template>
  <t-row style="height: 100%; overflow-y: auto;" :gutter="6">
    <t-col :span="2" style="height: 100%;">
      <t-aside class="p-2 border-rounded-4 h-full flex flex-col min-h-0" style="min-width: 220px">
        <t-select label="智能体：" v-model="agentStore.selectedAgentId" :options="agentOptions" placeholder="选择智能体">
        </t-select>
        <!-- <t-divider></t-divider> -->
        <t-space class="flex justify-between mt-8">
          <p class="px-1 pb-2 text-grey">最近会话</p>
          <t-space :size="4">
            <t-button variant="text" @click="fetchSessions" size="small">
              <template #icon><t-icon name="refresh" /></template>
            </t-button>
            <t-button variant="text" size="small" :style="{ borderRadius: '9999px' }" @click="newConversation">
              <template #icon><t-icon name="add" /></template>
            </t-button>
          </t-space>
        </t-space>
        <t-empty v-if="conversations.length === 0" class="py-10">
          <template #description>
            <p class="text-sm text-nap-text-secondary">还没有会话</p>
          </template>
        </t-empty>
        <t-list v-else class="conversation-list flex-1 min-h-0 overflow-y-auto">
          <t-list-item v-for="session in conversations" :key="session.uuid" class="cursor-pointer rounded-2"
            :class="{ 'conversation-item-active': currentConvId === session.uuid }"
            @click="selectConversation(session.uuid)">
            <t-list-item-meta>
              <template #description>
                <span class="conversation-title">{{ session.title }}</span>
              </template>
            </t-list-item-meta>
            <template #action>
              <t-popconfirm
                theme="warning"
                content="确定删除该会话吗？删除后不可恢复。"
                placement="bottom-right"
                @confirm="deleteConversation(session.uuid)"
                @click.stop
              >
                <t-link @click.stop theme="danger" hover="color"><t-icon name="close"></t-icon></t-link>
              </t-popconfirm>
          </template>
          </t-list-item>
        </t-list>
      </t-aside>
    </t-col>
    <t-col :span="10" style="height: 100%; padding: 40px;">
      <div class="relative h-full flex flex-col min-h-0">
        <t-chatbot v-if="agentStore.selectedAgentId"
          :chat-service-config="chatServiceConfig" :message-props="messageItemProps" ref="chatRef"
          :sender-props="senderProps"
          class="flex-1 min-h-0 min-w-0" @message-change="onMessageChange">
          <template #sender-footer-prefix>
            <t-space class="flex j">
              <t-button shape="round" variant="outline">深度思考</t-button>
              <!-- 选择模型 -->
              <t-select label="模型：" v-model="selectedModel" :options="modelOptions" placeholder="选择模型" class="border-rounded-10"
                clearable>
              </t-select>
              <!-- 选择工具 -->
              <t-select v-model="selectedTools" :options="toolOptions" placeholder="无" multiple label="工具:" :min-collapsed-num="1">

              </t-select>
            </t-space>
          </template>
          <template #sender-footer-suffix>
          </template>
        </t-chatbot>

        <div v-if="agentStore.selectedAgentId && !hasMessages" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none welcome">
          <div class="welcome-glow welcome-glow-1"></div>
          <div class="welcome-glow welcome-glow-2"></div>
          <div class="flex flex-col items-center gap-4 relative z-10">
            <div class="welcome-logo-wrap">
              <span class="welcome-logo-ring"></span>
              <AppLogo size="large" :show-text="false" />
            </div>
            <h1 class="welcome-title text-2xl font-semibold">你好，有什么我能帮你的吗？</h1>
            <p class="text-sm text-nap-muted">选择右侧会话继续，或直接提问开始一段新对话</p>

            <div class="welcome-suggestions pointer-events-auto">
              <button
                v-for="s in welcomeSuggestions"
                :key="s"
                class="welcome-chip"
                @click="useSuggestion(s)"
              >
                <t-icon name="chat" size="14" />
                {{ s }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </t-col>
  </t-row>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { API, TOKEN_KEY } from '@/api'
import { useAgentStore } from '@/stores/agent'
import { useChatStore, type ChatStoreMessage, type ChatChunk } from '@/stores/chat'
import AppLogo from '@/components/common/AppLogo.vue'
import type { Session, SessionMessage } from '@/types'
import { ChatServiceConfig, type AIMessageContent, type SSEChunkData } from '@tdesign-vue-next/chat'
import {
  Chatbot as TChatbot,
} from '@tdesign-vue-next/chat';

const agentStore = useAgentStore()
const chatStore = useChatStore()

function messageItemProps(msg: any) {
  return {
    variant: msg?.role === 'user' ? 'base' as const : undefined,
    chatContentProps: { thinking: { collapsed: true, animation: 'moving' as const } },
  }
}

const chatServiceConfig = computed<ChatServiceConfig>(() => ({
  // 对话服务地址
  endpoint: agentStore.selectedAgentId
    ? `/api/v1/agents/${agentStore.selectedAgentId}/chat`
    : '',
  // 开启流式传输
  stream: true,
  onRequest: (params) => {
    chatStore.activeRequestKey = currentKey.value
    chatStore.setDraft(currentKey.value, '')
    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
      },
      body: JSON.stringify({
        // 改成你后端要的格式
        query: params.prompt,        // 默认可能是 messages 数组
        model: selectedModel.value || undefined,
        session: currentConvId.value || undefined,
        tools: selectedTools.value,
      }),
    };
  },

  // 解析后端返回的数据，转换为组件所需格式
  onMessage: (chunk: SSEChunkData): AIMessageContent => {
    const rest = chunk.data as { type?: string; msg?: string };
    const msg = rest?.msg || '';
    let content: AIMessageContent
    if (rest?.type === 'thinking') {
      content = { type: 'thinking', data: { text: msg, title: '深度思考' }, status: 'streaming' };
    } else {
      content = { type: 'markdown', data: msg, status: 'streaming' };
    }
    const key = chatStore.activeRequestKey || currentKey.value
    chatStore.upsertStreamContent(key, content as ChatStoreMessage['content'][number])
    return content;
  },

  onComplete: (isAborted?: boolean) => {
    const el = (chatRef.value as any)?.$el ?? chatRef.value
    const messageStore = el?.provide?.chatEngine?.messageStore
    if (messageStore) {
      const ai = messageStore.messages.filter((m: any) => m.role === 'assistant').pop()
      if (ai?.content?.length) {
        const status = isAborted ? 'stop' : 'complete'
        messageStore.updateMultipleContents(
          ai.id,
          ai.content.map((c: any) => (c.type === 'thinking' ? { ...c, status } : c))
        )
      }
    }
    const key = chatStore.activeRequestKey || currentKey.value
    chatStore.finalizeStream(key, !!isAborted)
    chatStore.activeRequestKey = null
    snapshotCurrentToStore()
    if (!currentConvId.value) {
      fetchSessions().then(() => {
        if (!currentConvId.value) {
          const top = conversations.value[0]
          if (top?.uuid) {
            currentConvId.value = top.uuid
            const agentId = agentStore.selectedAgentId
            if (agentId) {
              chatStore.bindNewToSession(agentId, top.uuid)
              chatStore.setDraft(chatStore.keyFor(top.uuid, agentId), '')
            }
          }
        }
      })
    }
  },
}))

const currentConvId = ref<string | null>(null)
const chatRef = ref<any>(null)
const hasMessages = ref(false)

const currentKey = computed(() =>
  chatStore.keyFor(currentConvId.value, agentStore.selectedAgentId || '')
)

function getEngineMessages(): ChatStoreMessage[] | null {
  const el = (chatRef.value as any)?.$el ?? chatRef.value
  const msgs = el?.provide?.chatEngine?.messageStore?.messages
  if (Array.isArray(msgs)) return msgs
  return el?.chatMessageValue && Array.isArray(el.chatMessageValue) ? el.chatMessageValue : null
}

function snapshotCurrentToStore(agentId?: string | null) {
  if (!chatRef.value) return
  const msgs = getEngineMessages()
  const key = chatStore.keyFor(currentConvId.value, agentId ?? (agentStore.selectedAgentId || ''))
  if (msgs) chatStore.setMessages(key, msgs)
}

function restoreKeyDisplay(key: string) {
  if (!chatRef.value) return
  const ref = chatRef.value
  if (chatStore.getMessages(key).length) {
    ref.setMessages?.(chatStore.getMessagesForEngine(key), 'replace')
  } else {
    ref.clearMessages?.()
  }
  hasMessages.value = chatStore.getMessages(key).length > 0
}

const senderProps = computed(() => ({
  value: chatStore.getDraft(currentKey.value),
  onChange: (e: any) => {
    chatStore.setDraft(currentKey.value, e?.detail ?? '')
  },
}))

function onMessageChange(e: any) {
  const detail = e.detail ?? e
  hasMessages.value = Array.isArray(detail) ? detail.length > 0 : true
}

const selectedModel = ref('')
const selectedTools = ref<string[]>([])

const toolOptions = computed(() =>
  availableTools.value.map(t => ({ label: t.name, value: t.id }))
)

const availableTools = ref<{ id: string; name: string }[]>([])

async function fetchTools() {
  try {
    const data = await API.fetchTools<{ tools: { name: string; description: string; detail?: string; extras?: { title?: string; type?: string } }[] }>()
    availableTools.value = (data.tools || []).map(t => ({
      id: t.name,
      name: t.extras?.title || t.name
    }))
  } catch {
    availableTools.value = []
  }
}

const welcomeSuggestions = [
  '帮我总结这份文档的重点',
  '用 Python 写一段数据分析脚本',
  '解释这段代码的含义',
]

const modelOptions = computed(() =>
  agentStore.selectedAgentModels.map(m => ({ label: m, value: m }))
)

const conversations = ref<Session[]>([])
const agentOptions = computed(() =>
  agentStore.agents.map(a => ({ label: a.name, value: a.id }))
)
function newConversation() {
  snapshotCurrentToStore()
  currentConvId.value = null
  restoreKeyDisplay(currentKey.value)
}

async function useSuggestion(text: string) {
  if (!chatRef.value?.addPrompt) return
  chatRef.value.addPrompt(text, true)
}

async function selectConversation(id: string) {
  if (id === currentConvId.value) return
  snapshotCurrentToStore()
  currentConvId.value = id
  const key = currentKey.value
  if (chatStore.getMessages(key).length === 0) {
    try {
      const { messages } = await API.fetchSessionMessages<{ messages: SessionMessage[] }>(id)
      chatStore.setMessages(key, convertMessages(messages))
    } catch {
      MessagePlugin.error('加载会话消息失败')
    }
  }
  restoreKeyDisplay(key)
}

function convertMessages(messages: SessionMessage[]): ChatStoreMessage[] {
  return messages.map(msg => {
    let role: 'user' | 'assistant' | 'system'
    if (msg.type === 'ai') role = 'assistant'
    else if (msg.type === 'system' || msg.type === 'system-text') role = 'system'
    else role = 'user'

    const content: ChatChunk[] = []
    if (msg.thinking) {
      content.push({
        type: 'thinking',
        status: 'complete',
        data: { text: msg.thinking, title: '深度思考' },
      })
    }
    const data = msg.content ?? ''
    if (role === 'assistant') content.push({ type: 'markdown', data })
    else content.push({ type: 'text', data })

    return { id: msg.id, role, content }
  }) as ChatStoreMessage[]
}


async function deleteConversation(id: string) {
  try {
    await API.deleteSession(id)
    MessagePlugin.success('会话已删除')
    chatStore.removeSession(id)
    if (currentConvId.value === id) {
      currentConvId.value = null
      hasMessages.value = false
      chatRef.value?.clearMessages()
    }
    await fetchSessions()
  } catch {
    MessagePlugin.error('删除会话失败')
  }
}

async function fetchSessions() {
  if (!agentStore.selectedAgentId) {
    conversations.value = []
    return
  }
  try {
    const data = await API.fetchSessions<{ sessions: Session[] }>(agentStore.selectedAgentId)
    conversations.value = data.sessions || []
  } catch {
    conversations.value = []
    MessagePlugin.error('加载会话列表失败')
  }
}

onMounted(async () => {
  await agentStore.fetchAgents()
  fetchTools()
  if (agentStore.selectedAgentId) {
    selectedModel.value = ''
    selectedTools.value = [...(agentStore.selectedAgent?.tools || [])]
    await nextTick()
    restoreKeyDisplay(currentKey.value)
    fetchSessions()
  }
})

watch(() => agentStore.selectedAgentId, async (_id, oldId) => {
  snapshotCurrentToStore(oldId)
  selectedModel.value = ''
  currentConvId.value = null
  selectedTools.value = [...(agentStore.selectedAgent?.tools || [])]
  await nextTick()
  restoreKeyDisplay(currentKey.value)
  fetchSessions()
})

watch(() => agentStore.selectedAgentModels, (models) => {
  if (models.length > 0 && !models.includes(selectedModel.value)) {
    selectedModel.value = models[0]
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

.conversation-title {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-list :deep(.t-list-item .t-link) {
  opacity: 0;
  transition: opacity 0.15s ease;
}

.conversation-list :deep(.t-list-item:hover .t-link) {
  opacity: 1;
}

.welcome {
  overflow: hidden;
}

.welcome-glow {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  animation: welcome-float 9s ease-in-out infinite;
}

.welcome-glow-1 {
  width: 420px;
  height: 420px;
  top: 18%;
  left: 24%;
  background: radial-gradient(circle, color-mix(in srgb, var(--td-brand-color) 22%, transparent), transparent 70%);
}

.welcome-glow-2 {
  width: 380px;
  height: 380px;
  bottom: 12%;
  right: 22%;
  background: radial-gradient(circle, color-mix(in srgb, var(--td-brand-color-hover) 20%, transparent), transparent 70%);
  animation-delay: -4.5s;
}

@keyframes welcome-float {
  0%, 100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(24px, -18px, 0) scale(1.08);
  }
}

.welcome-logo-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-logo-ring {
  position: absolute;
  inset: -10px;
  border-radius: 9999px;
  border: 2px solid color-mix(in srgb, var(--td-brand-color) 35%, transparent);
  animation: welcome-ring 2.6s ease-out infinite;
}

.welcome-logo-wrap::after {
  content: '';
  position: absolute;
  inset: -26px;
  border-radius: 9999px;
  background: radial-gradient(circle, color-mix(in srgb, var(--td-brand-color) 20%, transparent), transparent 68%);
  animation: welcome-pulse 2.6s ease-in-out infinite;
}

@keyframes welcome-ring {
  0% {
    transform: scale(0.7);
    opacity: 0.9;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

@keyframes welcome-pulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(0.92);
  }
  50% {
    opacity: 1;
    transform: scale(1.06);
  }
}

.welcome-title {
  background: linear-gradient(100deg, var(--td-brand-color), color-mix(in srgb, var(--td-brand-color) 40%, #fff) 55%, var(--td-brand-color));
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: welcome-title 5s linear infinite;
}

@keyframes welcome-title {
  0% {
    background-position: 0% center;
  }
  100% {
    background-position: 200% center;
  }
}

.welcome-suggestions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 26px;
  max-width: 560px;
}

.welcome-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 13px;
  color: var(--td-brand-color);
  background: var(--td-brand-color-light);
  border: 1px solid var(--td-brand-color-2);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
  animation: welcome-chip-in 0.5s ease backwards;
}

.welcome-chip:nth-child(2) {
  animation-delay: 0.1s;
}

.welcome-chip:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes welcome-chip-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px color-mix(in srgb, var(--td-brand-color) 25%, transparent);
  background: var(--td-brand-color-light-hover);
}
</style>

<style>
:root {
  --td-chat-item-primary-bg: var(--td-brand-color);
  --td-chat-item-user-text-color: #fff;
}

.t-chat__detail {
  overflow-wrap: break-word;
  word-break: break-word;
}

.t-chat__list {
  scrollbar-width: thin !important;
}

.t-chat__list::-webkit-scrollbar {
  display: block !important;
  width: 6px;
}

.t-chat__list::-webkit-scrollbar-thumb {
  border-radius: 3px;
  background: var(--td-scrollbar-color, rgba(0, 0, 0, 0.2));
}
</style>