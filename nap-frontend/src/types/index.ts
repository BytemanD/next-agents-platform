export interface Agent {
  id: string
  name: string
  description: string
  avatar: string
  model: string
  status: 'active' | 'draft' | 'error'
  tools: string[]
  systemPrompt?: string
  temperature?: number
  maxTokens?: number
  knowledgeBaseIds?: string[]
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
  active: number
  created_at: string
  updated_at: string
}

export interface KnowledgeItem {
  uuid: string
  knowledge: string
  name: string
  size: number
  path: string | null
  status: string
  created_at: string
  updated_at: string
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
