import axios from 'axios'
import {
  StartChatRequest,
  ContinueChatRequest,
  ChatSession,
  SystemStatus,
  SessionStatus,
  ConversationHistory,
} from '../types/chat'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000, // Increased to 2 minutes for complex RAG processing
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    return response
  },
  (error) => {
    console.error('Response error:', error)
    
    // Handle timeout errors specifically
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      const message = 'Mr. Munger is taking longer than usual to think. This can happen with complex questions that require deep analysis. Please try asking a simpler question or try again.'
      return Promise.reject(new Error(message))
    }
    
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export const chatApi = {
  // Get system status
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await api.get('/chat/status')
    return response.data
  },

  // Start a new chat session
  async startChat(request: StartChatRequest): Promise<ChatSession> {
    const response = await api.post('/chat/start', request)
    return response.data
  },

  // Continue existing chat session
  async continueChat(sessionId: string, message: string): Promise<ChatSession> {
    const request: ContinueChatRequest = {
      session_id: sessionId,
      message,
    }
    const response = await api.post('/chat/continue', request)
    return response.data
  },

  // Get session status
  async getSessionStatus(sessionId: string): Promise<SessionStatus> {
    const response = await api.get(`/chat/session/${sessionId}/status`)
    return response.data
  },

  // Get conversation history
  async getConversationHistory(sessionId: string): Promise<ConversationHistory> {
    const response = await api.get(`/chat/session/${sessionId}/history`)
    return response.data
  },

  // Clear session
  async clearSession(sessionId: string): Promise<{ message: string }> {
    const response = await api.delete(`/chat/session/${sessionId}`)
    return response.data
  },

  // Health check
  async healthCheck(): Promise<{ message: string; status: string }> {
    const response = await api.get('/health')
    return response.data
  },
}

export default api
