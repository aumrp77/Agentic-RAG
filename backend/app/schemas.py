"""
API Data Transfer Objects (DTOs) and Schemas
Defines the HTTP contract between frontend and backend
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response schema"""
    message: str
    status: str

class RootResponse(BaseModel):
    """Root endpoint response schema"""
    message: str
    status: str

class ChatMessage(BaseModel):
    """Chat message schema"""
    content: str
    role: str = "user"
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response schema"""
    content: str
    role: str = "assistant"
    timestamp: Optional[str] = None

# Enhanced schemas for conversational workflow
class StartChatRequest(BaseModel):
    """Request to start a new chat session"""
    message: str
    session_id: Optional[str] = None

class ContinueChatRequest(BaseModel):
    """Request to continue existing chat session"""
    message: str
    session_id: str

class ThinkingStatus(BaseModel):
    """Status update for thinking process"""
    status: str  # "thinking", "planning", "retrieving", "synthesizing", "verifying"
    message: str
    step: Optional[str] = None

class ChatSessionResponse(BaseModel):
    """Response for chat session"""
    success: bool
    session_id: str
    response: str
    confidence: float
    thinking_steps: Optional[List[ThinkingStatus]] = None
    conversation_context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = datetime.now().isoformat()

class SessionStatusResponse(BaseModel):
    """Response for session status"""
    session_id: str
    conversation_count: int
    duration: str
    memory_entries: int
    last_activity: str

class ConversationHistory(BaseModel):
    """Conversation history response"""
    session_id: str
    history: List[Dict[str, str]]
    summary: Optional[str] = None

class SystemStatusResponse(BaseModel):
    """System initialization status"""
    initialized: bool
    vector_store: bool
    dspy: bool
    memory: bool
    error: Optional[str] = None
