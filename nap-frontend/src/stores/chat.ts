import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ChatChunk {
  type: string
  data: unknown
  status?: string
  id?: string
}

export interface ChatStoreMessage {
  id: string
  role: string
  status?: string
  datetime?: string
  content: ChatChunk[]
}

export interface SessionChatState {
  messages: ChatStoreMessage[]
  draft: string
}

const MAX_TOTAL_MESSAGES = 400

/** 引擎 messageStore 是 immer 产物（深度 frozen），写入 store 前必须先深拷贝为可变更对象 */
function cloneMessages(messages: ChatStoreMessage[]): ChatStoreMessage[] {
  try {
    return structuredClone(messages)
  } catch {
    return JSON.parse(JSON.stringify(messages))
  }
}

export const useChatStore = defineStore('chat', () => {
  const recs = ref<Record<string, SessionChatState>>({})
  const activeRequestKey = ref<string | null>(null)

  function keyFor(sessionId: string | null, agentId: string): string {
    return sessionId ? `s:${sessionId}` : `n:${agentId || ''}`
  }

  function ensure(key: string): SessionChatState {
    if (!recs.value[key]) {
      recs.value[key] = { messages: [], draft: '' }
    }
    return recs.value[key]
  }

  function getMessages(key: string): ChatStoreMessage[] {
    return ensure(key).messages
  }

  /** 给引擎的 setMessages 用：深拷贝一份，避免引擎(immer)原地 freeze 我们 store 里的对象 */
  function getMessagesForEngine(key: string): ChatStoreMessage[] {
    return cloneMessages(getMessages(key))
  }

  function setMessages(key: string, messages: ChatStoreMessage[]) {
    ensure(key).messages = cloneMessages(messages).slice(-MAX_TOTAL_MESSAGES)
  }

  function getDraft(key: string): string {
    return ensure(key).draft
  }

  function setDraft(key: string, draft: string) {
    ensure(key).draft = draft
  }

  function removeSession(sessionId: string) {
    delete recs.value[`s:${sessionId}`]
  }

  function bindNewToSession(agentId: string, sessionId: string) {
    const from = keyFor(null, agentId)
    const to = keyFor(sessionId, agentId)
    if (recs.value[from]) {
      recs.value[to] = recs.value[from]
      delete recs.value[from]
    }
  }

  function upsertStreamContent(key: string, chunk: ChatChunk) {
    const state = ensure(key)
    const msgs = state.messages
    const nextStatus = chunk.status || 'streaming'
    const mergeLast = (last: ChatChunk | undefined, incoming: ChatChunk): ChatChunk => {
      if (last && last.type === incoming.type) {
        const ld = last.data as any
        const cd = incoming.data as any
        if (typeof ld === 'string' && typeof cd === 'string') {
          return { ...last, data: ld + cd, status: nextStatus }
        }
        if (ld && cd && typeof ld.text === 'string' && typeof cd.text === 'string') {
          return { ...last, data: { ...ld, text: ld.text + cd.text }, status: nextStatus }
        }
      }
      return { ...incoming, status: nextStatus }
    }
    for (let i = msgs.length - 1; i >= 0; i -= 1) {
      const m = msgs[i]
      if (m.role !== 'assistant') continue
      const arr = m.content
      const last = arr[arr.length - 1]
      const nextContent = last && last.type === chunk.type
        ? arr.slice(0, -1).concat([mergeLast(last, chunk)])
        : arr.concat([{ ...chunk, status: nextStatus }])
      state.messages = msgs.slice(0, i).concat([{ ...m, content: nextContent }], msgs.slice(i + 1))
      return
    }
    state.messages = msgs.concat([{
      id: `pending-${msgs.length}-${Date.now()}`,
      role: 'assistant',
      status: nextStatus,
      content: [{ ...chunk, status: nextStatus }],
    }])
  }

  function finalizeStream(key: string, aborted = false) {
    const state = ensure(key)
    const msgs = state.messages
    const status = aborted ? 'stop' : 'complete'
    for (let i = msgs.length - 1; i >= 0; i -= 1) {
      const m = msgs[i]
      if (m.role !== 'assistant') continue
      const content = m.content.map((c, idx, arr) => {
        if (idx === arr.length - 1 && c.status && c.status !== 'error') {
          return { ...c, status }
        }
        return c
      })
      state.messages = msgs.slice(0, i).concat([{ ...m, status, content }], msgs.slice(i + 1))
      return
    }
  }

  return {
    recs,
    activeRequestKey,
    keyFor,
    getMessages,
    getMessagesForEngine,
    setMessages,
    getDraft,
    setDraft,
    removeSession,
    bindNewToSession,
    upsertStreamContent,
    finalizeStream,
  }
})