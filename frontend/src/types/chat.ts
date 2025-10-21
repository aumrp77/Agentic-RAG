export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
  confidence?: number
  thinkingSteps?: ThinkingStep[]
}

export interface ThinkingStep {
  status: string
  message: string
  step?: string
  timestamp?: number
}

export interface ChatSession {
  success: boolean
  session_id: string
  response: string
  confidence: number
  thinking_steps?: ThinkingStep[]
  conversation_context?: any
  error?: string
  timestamp: string
}

export interface StartChatRequest {
  message: string
  session_id?: string
}

export interface ContinueChatRequest {
  message: string
  session_id: string
}

export interface SystemStatus {
  initialized: boolean
  vector_store: boolean
  dspy: boolean
  memory: boolean
  error?: string
}

export interface SessionStatus {
  session_id: string
  conversation_count: number
  duration: string
  memory_entries: number
  last_activity: string
}

export interface ConversationHistory {
  session_id: string
  history: Array<{
    role: string
    content: string
    timestamp: string
  }>
  summary?: string
}
