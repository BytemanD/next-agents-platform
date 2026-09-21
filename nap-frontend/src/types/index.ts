export interface Agent {
  id: string
  uuid: string
  name: string
  description: string
  llm: string
  instruction?: string
  status: 'active' | 'draft' | 'error'
  config: Object
  knowledge_bases: string[]
  tools: string[]

  createdAt: string
  updatedAt: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  toolCalls?: ToolCall[]
  feedback?: 'positive' | 'negative'
}

export interface ToolCall {
  id: string
  name: string
  input: Record<string, any>
  output: any
  duration: number
  status: 'pending' | 'running' | 'completed' | 'error'
}

export interface Conversation {
  id: string
  agentId: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

export interface Session {
  uuid: string
  user: string
  agent: string
  title: string
  created_at: string
  updated_at: string
}

export interface SessionMessage {
  id: string
  type: string
  content: string | null
  thinking: string | null
}

export interface KnowledgeDocument {
  id: string
  name: string
  type: string
  size: number
  status: 'processing' | 'ready' | 'error'
  chunks: number
  createdAt: string
}

export interface KnowledgeBase {
  uuid: string
  name: string
  description: string
  active: boolean
  created_at: string
  updated_at: string
}

export interface KnowledgeItem {
  uuid: string
  knowledge: string
  creator: string
  name: string
  size: number
  path: string | null
  status: number
  created_at: string
  updated_at: string
}

export interface KnowledgeEnrichment {
  keywords: string[]
  summary: string
}

export interface KnowledgeDetail extends KnowledgeItem {
  enrichment: KnowledgeEnrichment | null
}

export interface KnowledgeTodo {
  id: string
  knowlwdge_uuid: string
  name: string
  status: string
  detail: string
  created_at: string
  updated_at: string
}

export const KNOWLEDGE_STATUS: Record<number, string> = {
  // 0: '排队中',
  // 1: '保存中',
  // 2: '已保存',
  // 3: '解析中',
  // 4: '已解析',
  // 5: '解析失败',
  // 100: '删除中',
  // 101: '已删除'
}

export interface Trace {
  id: string
  agentId: string
  conversationId: string
  status: 'success' | 'error' | 'running'
  tokens: number
  cost: number
  duration: number
  spans: TraceSpan[]
  createdAt: string
}

export interface TraceSpan {
  id: string
  name: string
  type: 'llm' | 'tool' | 'retrieval' | 'chain'
  duration: number
  tokens?: number
  input: any
  output: any
  status: 'success' | 'error'
}

export interface DashboardStats {
  totalAgents: number
  activeAgents: number
  totalConversations: number
  totalDocuments: number
  totalTokens: number
  totalCost: number
}

export interface NavItem {
  label: string
  path: string
  icon: string
  featured?: boolean
}
