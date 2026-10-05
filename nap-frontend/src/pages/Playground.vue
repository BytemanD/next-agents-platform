<template>
  <t-row style="height: 100%; overflow-y: auto;" :gutter="6">
    <t-col :span="2" style="height: 100%;">
      <t-aside class="p-2 border-rounded-4 h-full flex flex-col min-h-0" style="min-width: 220px">
        <t-select label="智能体:" v-model="agentStore.selectedAgentId" :options="agentOptions" placeholder="选择智能体">
        </t-select>
        <!-- <t-divider>最近会话</t-divider> -->
        <t-space class="flex justify-between mt-4">
          <t-text theme="secondary" style="font-size: xx-small;">最近会话</t-text>
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
        <t-list v-else class=" flex-1 min-h-0 overflow-y-auto">
          <t-list-item v-for="session in conversations" :key="session.uuid"
            class="cursor-pointer rounded-2 conversation-list-item  my-1"
            :class="{ 'conversation-item-active': currentConvId === session.uuid }"
            @click="selectConversation(session.uuid)">
            <t-list-item-meta>
              <template #description>
                <t-text theme="primary">{{ session.title }}</t-text>
              </template>
            </t-list-item-meta>
            <template #action>
              <t-popconfirm theme="warning" content="确定删除该会话吗？删除后不可恢复。" placement="bottom-right"
                @confirm="deleteConversation(session.uuid)" @click.stop>
                <!-- <span class="session-action">sdfsdf</span> -->
                <t-link @click.stop theme="danger" hover="color" class="session-action">
                  <t-icon name="close" color="danger"></t-icon>
                </t-link>
              </t-popconfirm>
              <!-- <t-link @click.stop theme="danger"><t-icon name="close"></t-icon></t-link> -->
              <!-- <t-link theme="danger" hover="color"><t-icon name="close"></t-icon></t-link> -->
            </template>
          </t-list-item>
        </t-list>
      </t-aside>
    </t-col>
    <t-col :span="10" style="height: 100%; padding: 40px;">
      <div class="relative h-full flex flex-col min-h-0">
        <t-chatbot v-if="agentStore.selectedAgentId" :chat-service-config="chatServiceConfig"
          :message-props="messageItemProps" ref="chatRef" :sender-props="senderProps" class="flex-1 min-h-0 min-w-0"
          @message-change="onMessageChange">
          <template #sender-footer-prefix>
            <t-space>
              <!-- <t-button shape="round" variant="outline">深度思考</t-button> -->
              <select-button icon="earth" v-if="agentStore.enableWebSearch()"
                v-model="enableWebSearch">联网搜索</select-button>
              <!-- 选择工具 -->
              <t-select v-model="selectedTools" :options="agentStore.toolOptions" placeholder="无" multiple label="工具:"
                :min-collapsed-num="1">
              </t-select>
              <!-- 选择MCP -->
              <t-select v-model="selectedMcps" :options="agentStore.mcpOptions" placeholder="无" multiple label="MCP:"
                :min-collapsed-num="1">
              </t-select>
              <!-- 选择模型 -->
              <t-select label="模型：" v-model="selectedModel" :options="modelOptions" placeholder="选择模型"
                class="border-rounded-10" clearable>
              </t-select>
            </t-space>
          </template>
        </t-chatbot>

        <div v-if="agentStore.selectedAgentId && !hasMessages"
          class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none welcome">
          <div class="flex flex-col items-center gap-4 relative">
            <div class="welcome-logo-wrap">
              <span class="welcome-logo-ring"></span>
              <AppLogo size="large" :show-text="false" />
            </div>
            <h1 class="welcome-title text-2xl font-semibold">你好，有什么我能帮你的吗？</h1>
            <p class="text-sm text-nap-muted">选择右侧会话继续，或直接提问开始一段新对话</p>

            <div class="welcome-suggestions pointer-events-auto">
              <button v-for="s in welcomeSuggestions" :key="s" class="welcome-chip" @click="useSuggestion(s)">
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
import { API, getToken } from '@/api'
import { useAgentStore } from '@/stores/agent'
import { useChatStore, type ChatStoreMessage, type ChatChunk } from '@/stores/chat'
import AppLogo from '@/components/common/AppLogo.vue'
import type { Session, SessionMessage } from '@/types'
import { ChatServiceConfig, type AIMessageContent, type SSEChunkData } from '@tdesign-vue-next/chat'
import { Chatbot as TChatbot } from '@tdesign-vue-next/chat';
import SelectButton from '@/components/common/SelectButton.vue'

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
  onRequest: async (params) => {
    chatStore.activeRequestKey = currentKey.value
    chatStore.setDraft(currentKey.value, '')
    const token = await getToken()
    const attachments = await resolveSendingFileKeys()
    // 上传没拿到文件，但已在聊天里显示附件时，作为空处理
    const attachmentKeys = attachments.filter(Boolean)
    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        // 改成你后端要的格式
        query: params.prompt,        // 默认可能是 messages 数组
        model: selectedModel.value || undefined,
        session: currentConvId.value || undefined,
        tools: enableWebSearch.value
          ? [...selectedTools.value, agentStore.webSearchTool]
          : selectedTools.value,
        mcp_uuids: selectedMcps.value,
        attachments: attachmentKeys,
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
    } else if (rest?.type === 'error') {
      content = { type: 'text', data: msg, status: 'error' };
    } else {
      content = { type: 'markdown', data: msg, status: 'streaming' };
    }
    const key = chatStore.activeRequestKey || currentKey.value
    chatStore.upsertStreamContent(key, content as ChatStoreMessage['content'][number])
    return content;
  },

  onError: () => {
    const el = (chatRef.value as any)?.$el ?? chatRef.value
    const messageStore = el?.provide?.chatEngine?.messageStore
    if (messageStore) {
      const ai = messageStore.messages.filter((m: any) => m.role === 'assistant').pop()
      if (ai?.id) {
        messageStore.setMessageStatus(ai.id, 'error')
        messageStore.updateMultipleContents(
          ai.id,
          ai.content.map((c: any) => (c.status ? { ...c, status: 'error' } : c))
        )
      }
    }
    const key = chatStore.activeRequestKey || currentKey.value
    chatStore.finalizeStream(key, false)
    chatStore.activeRequestKey = null
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

const uploadRawFiles = ref<{ key: string; raw: File }[]>([])
const uploadTasks = new Map<string, Promise<string | null>>()
const sendingFileKeys = ref<string[]>([])
const pendingAttachments = ref<{ key: string; name: string; size?: number; fileType?: string; fileKey?: string }[]>([])

const senderProps = computed(() => ({
  value: chatStore.getDraft(currentKey.value),
  onChange: (e: any) => {
    chatStore.setDraft(currentKey.value, e?.detail ?? '')
  },
  actions: ['uploadAttachment', 'send'],
  attachmentsProps: { items: pendingAttachments.value },
  onFileSelect: (e: any) => {
    const files = Array.isArray(e?.detail) ? e.detail : (e?.target?.files || [])
    const items = Array.from(files as File[]).map((f) => ({
      key: `${f.name}-${f.size}-${f.lastModified}`,
      name: f.name,
      size: f.size,
      fileType: f.type?.split('/')[0] || undefined,
    }))
    pendingAttachments.value = [...pendingAttachments.value, ...items]
    uploadRawFiles.value = [...uploadRawFiles.value, ...items.map((it, i) => ({ key: it.key, raw: (files as File[])[i] }))]
    items.forEach((it) => {
      uploadTasks.set(it.key, uploadAttachment(it))
    })
  },
  onFileRemove: (e: any) => {
    const rest = Array.isArray(e?.detail) ? e.detail : []
    pendingAttachments.value = rest
    const keys = new Set(rest.map((r: any) => r?.key))
    uploadRawFiles.value = uploadRawFiles.value.filter((r) => keys.has(r.key))
  },
  onSend: (e: any) => {
    const detailAtts = e?.detail?.attachments
    const atts = Array.isArray(detailAtts) ? detailAtts : pendingAttachments.value
    sendingFileKeys.value = (atts as any[])
      .map((a: any) => a?.key)
      .filter((k: unknown): k is string => typeof k === 'string' && !!k)
    pendingAttachments.value = []
    uploadRawFiles.value = []
  },
}))

async function uploadAttachment(item: { key: string; name: string; fileKey?: string }): Promise<string | null> {
  const file = findRawFile(item)
  if (!file) return null
  try {
    const data = await API.uploadAttachment<{ attachment: { uuid: string; name: string } }>(file)
    const idx = pendingAttachments.value.findIndex((a) => a.key === item.key)
    if (idx >= 0) pendingAttachments.value[idx] = { ...item, fileKey: data.attachment.uuid }
    return data.attachment.uuid
  } catch {
    pendingAttachments.value = pendingAttachments.value.filter((a) => a.key !== item.key)
    uploadRawFiles.value = uploadRawFiles.value.filter((r) => r.key !== item.key)
    MessagePlugin.error(`附件「${item.name}」上传失败`)
    return null
  }
}

async function resolveSendingFileKeys(): Promise<string[]> {
  const fileKeys: string[] = []
  for (const key of sendingFileKeys.value) {
    const task = uploadTasks.get(key)
    if (task) {
      const fk = await task
      if (fk) fileKeys.push(fk)
    }
  }
  sendingFileKeys.value = []
  return fileKeys
}

function findRawFile(item: { key: string }): File | undefined {
  const el = uploadRawFiles.value.find((f) => f.key === item.key)
  return el?.raw
}

function onMessageChange(e: any) {
  const detail = e.detail ?? e
  hasMessages.value = Array.isArray(detail) ? detail.length > 0 : true
}

const selectedModel = ref('')
const selectedTools = ref<string[]>([])
const selectedMcps = ref<string[]>([])

const enableWebSearch = ref(false)

// 联网搜索由独立开关控制，不计入工具下拉
function applyAgentTools() {
  const tools = Object.keys(agentStore.selectedAgent?.tools || {})
  enableWebSearch.value = tools.includes(agentStore.webSearchTool)
  selectedTools.value = tools.filter(t => t !== agentStore.webSearchTool)
  selectedMcps.value = [...(agentStore.selectedAgent?.mcp_uuids || [])]
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
  if (agentStore.selectedAgentId) {
    selectedModel.value = ''
    applyAgentTools()
    await nextTick()
    restoreKeyDisplay(currentKey.value)
    fetchSessions()
  }
})

watch(() => agentStore.selectedAgentId, async (_id, oldId) => {
  snapshotCurrentToStore(oldId)
  selectedModel.value = ''
  currentConvId.value = null
  applyAgentTools()
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
  background: var(--bg-100);
  /* color: var(--td-brand-color); */
  /* color: white; */
}


.conversation-item-active :deep(.t-text) {
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

.conversation-title:hover {
  color: white;
}

/* .conversation-list :deep(.t-list-item .t-link) {
  opacity: 0;
  transition: opacity 0.15s ease;
} */

/* .conversation-list :deep(.t-list-item:hover .t-link) {
  opacity: 1;
}

.conversation-list :deep(.t-list-item:hover .t-button) {
  opacity: 1;
} */


.session-action {
  opacity: 0;
}

.conversation-list-item:hover .session-action {
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

  0%,
  100% {
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

  0%,
  100% {
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