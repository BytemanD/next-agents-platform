import axios from 'axios'
import type { KnowledgeBase, KnowledgeDetail, KnowledgeItem, KnowledgeTodo } from '@/types'

export const TOKEN_KEY = 'nap_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

const AUTH_EXCLUDE: Array<[string, string]> = [
  ['post', '/api/v1/auth/login'],
  ['post', '/api/v1/users']
]

axios.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()
  const url = config.url || ''
  const excluded = AUTH_EXCLUDE.some(([m, u]) => method === m && url.startsWith(u))
  if (!excluded) {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export interface AgentPayload {
  name: string
  description: string
  instruction: string
  llm: string
  status: string
  config?: { temperature: number; max_tokens: number }
  knowledge_bases?: string[]
  tools: string[]
}

export interface LLMPayload {
  name: string
  base_url: string
  api_key: string
  models: string[]
}

export interface KnowledgeBasePayload {
  name: string
  description: string
  active: boolean
}

export class Api {
  // ---------- Auth ----------
  async login<T = unknown>(username: string, password: string) {
    const { data } = await axios.post<T>('/api/v1/auth/login', { username, password })
    return data
  }

  async register<T = unknown>(username: string, password: string, email?: string) {
    const { data } = await axios.post<T>('/api/v1/users', { username, password, email })
    return data
  }

  async fetchUserMe<T = unknown>() {
    const { data } = await axios.get<T>('/api/v1/users/me')
    return data
  }

  // ---------- Agents ----------
  async fetchAgents<T = unknown>() {
    const { data } = await axios.get('/api/v1/agents')
    return data as T
  }

  async fetchAgent<T = unknown>(uuid: string) {
    const { data } = await axios.get(`/api/v1/agents/${uuid}`)
    return data as T
  }

  async createAgent<T = unknown>(payload: AgentPayload) {
    const { data } = await axios.post('/api/v1/agents', payload)
    return data as T
  }

  async updateAgent<T = unknown>(uuid: string, payload: Partial<AgentPayload>) {
    const { data } = await axios.put(`/api/v1/agents/${uuid}`, payload)
    return data as T
  }

  async deleteAgent<T = unknown>(uuid: string) {
    const { data } = await axios.delete(`/api/v1/agents/${uuid}`)
    return data as T
  }

  // ---------- Sessions ----------
  async fetchSessions<T = unknown>(agentUuid: string) {
    const { data } = await axios.get('/api/v1/sessions', { params: { agent: agentUuid } })
    return data as T
  }

  async deleteSession<T = unknown>(uuid: string) {
    const { data } = await axios.delete(`/api/v1/sessions/${uuid}`)
    return data as T
  }

  async fetchSessionMessages<T = unknown>(uuid: string) {
    const { data } = await axios.get(`/api/v1/sessions/${uuid}/messages`)
    return data as T
  }

  // ---------- LLMs ----------
  async fetchLLMs<T = unknown>() {
    const { data } = await axios.get('/api/v1/llms')
    return data as T
  }

  async fetchLLM<T = unknown>(uuid: string) {
    const { data } = await axios.get(`/api/v1/llms/${uuid}`)
    return data as T
  }

  async createLLM<T = unknown>(payload: LLMPayload) {
    const { data } = await axios.post('/api/v1/llms', payload)
    return data as T
  }

  async updateLLM<T = unknown>(uuid: string, payload: Partial<LLMPayload>) {
    const { data } = await axios.put(`/api/v1/llms/${uuid}`, payload)
    return data as T
  }

  async deleteLLM<T = unknown>(uuid: string) {
    const { data } = await axios.delete(`/api/v1/llms/${uuid}`)
    return data as T
  }

  // ---------- Knowledge bases ----------
  async fetchKnowledgeBases() {
    const { data } = await axios.get<{ items: KnowledgeBase[] }>('/api/v1/knowledge-bases')
    return data
  }

  async fetchKbStats(uuid: string) {
    const { data } = await axios.get<{ total: number }>(`/api/v1/knowledge-bases/${uuid}/stats`)
    return data
  }

  async createKnowledgeBase<T = unknown>(payload: KnowledgeBasePayload) {
    const { data } = await axios.post('/api/v1/knowledge-bases', payload)
    return data as T
  }

  async deleteKnowledgeBase<T = unknown>(uuid: string) {
    const { data } = await axios.delete(`/api/v1/knowledge-bases/${uuid}`)
    return data as T
  }

  // ---------- Knowledges (documents) ----------
  async fetchKbKnowledges(kbId: string) {
    const { data } = await axios.get<{ items: KnowledgeItem[] }>(`/api/v1/knowledge-bases/${kbId}/knowledges`)
    return data
  }

  async fetchKnowledges() {
    const { data } = await axios.get<{ items: KnowledgeItem[] }>('/api/v1/knowledges')
    return data
  }

  async fetchKnowledgeDetail<T = KnowledgeDetail>(uuid: string) {
    const { data } = await axios.get<T>(`/api/v1/knowledges/${uuid}`)
    return data
  }

  async fetchKnowledgeTodos<T = KnowledgeTodo>(uuid: string) {
    const { data } = await axios.get<{ items: T[] }>(`/api/v1/knowledges/${uuid}/todos`)
    return data
  }

  async uploadKbFile(kbId: string, file: File) {
    const form = new FormData()
    form.append('file', file)
    const { data } = await axios.post(`/api/v1/knowledge-bases/${kbId}/knowledges/file`, form)
    return data
  }

  async deleteKnowledge<T = unknown>(uuid: string) {
    const { data } = await axios.delete(`/api/v1/knowledges/${uuid}`)
    return data as T
  }

  // ---------- Monitoring ----------
  async fetchTokenUsage<T = unknown>(days = 7, agentUuid?: string) {
    const { data } = await axios.get<T>('/api/v1/monitoring/token-usage', {
      params: { days, agent_uuid: agentUuid || undefined }
    })
    return data
  }

  // ---------- Tools ----------
  async fetchTools<T = unknown>() {
    const { data } = await axios.get<T>('/api/v1/tools')
    return data
  }
}

export const API = new Api()