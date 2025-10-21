"""
API Routes for Charlie Munger RAG Agent
Contains all HTTP endpoints and their handlers
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket

from backend.app.schemas import (
    StartChatRequest, ContinueChatRequest, ChatSessionResponse,
    SessionStatusResponse, ConversationHistory, SystemStatusResponse
)
from backend.agent.graph.workflow import start_conversation_session, continue_conversation_session
from backend.agent.graph.memory import memory_manager
from backend.app.dependencies import initialize_dependencies, get_dependencies_status, shutdown_dependencies

# Create the main API router
router = APIRouter()

# Global state for system initialization
_system_initialized = False
_initialization_start_time = None

class SessionManager:
    """Simple session manager for tracking active sessions"""
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str = None) -> str:
        if not session_id:
            session_id = f"web_session_{uuid.uuid4().hex[:8]}"
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "conversation_count": 0
        }
        return session_id
    
    def update_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
            self.sessions[session_id]["conversation_count"] += 1
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        duration = datetime.now() - session["created_at"]
        memory_entries = len(memory_manager.get_session_memory(session_id).get_conversation_history())
        
        return {
            "session_id": session_id,
            "conversation_count": session["conversation_count"],
            "duration": str(duration),
            "memory_entries": memory_entries,
            "last_activity": session["last_activity"].isoformat()
        }

# Global session manager
session_manager = SessionManager()

async def initialize_system_if_needed():
    """Initialize system dependencies if not already done"""
    global _system_initialized, _initialization_start_time
    
    if not _system_initialized:
        _initialization_start_time = datetime.now()
        print("🚀 Initializing Charlie Munger RAG System for web interface...")
        
        results = initialize_dependencies()
        
        if not results.get('vector_store'):
            raise HTTPException(
                status_code=500, 
                detail="Vector store initialization failed - retrieval won't work"
            )
        
        _system_initialized = True
        print("✅ System initialized successfully for web interface!")
    
    return True

# Basic endpoints
@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Personal AI Assistant API", "status": "ready"}

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"message": "Charlie Munger RAG Agent", "status": "ready"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        pass

# Chat endpoints
@router.get("/chat/status")
async def get_system_status() -> SystemStatusResponse:
    """Get system initialization status"""
    global _system_initialized
    
    if _system_initialized:
        status = get_dependencies_status()
        return SystemStatusResponse(
            initialized=True,
            vector_store=status["vector_store"]["initialized"],
            dspy=status["dspy"]["enabled"],
            memory=True
        )
    else:
        return SystemStatusResponse(
            initialized=False,
            vector_store=False,
            dspy=False,
            memory=False
        )

@router.post("/chat/start")
async def start_chat(request: StartChatRequest) -> ChatSessionResponse:
    """Start a new chat session with Charlie Munger"""
    
    # Initialize system if needed
    await initialize_system_if_needed()
    
    # Create or use provided session ID
    session_id = session_manager.create_session(request.session_id)
    
    try:
        # Process the conversation with thinking status
        import time
        start_time = time.time()
        print(f"🚀 Starting conversation processing for session {session_id}")
        
        result = start_conversation_session(request.message, session_id)
        
        processing_time = time.time() - start_time
        print(f"⏱️ Conversation processing completed in {processing_time:.2f} seconds")
        
        if result.get("success"):
            session_manager.update_session(session_id)
            
            return ChatSessionResponse(
                success=True,
                session_id=session_id,
                response=result.get("response", "I'm having trouble thinking right now."),
                confidence=result.get("confidence", 0.0),
                thinking_steps=result.get("thinking_steps", []),
                conversation_context=result.get("conversation_context", {}),
                timestamp=datetime.now().isoformat()
            )
        else:
            error_msg = result.get("error", "Unknown error occurred")
            return ChatSessionResponse(
                success=False,
                session_id=session_id,
                response="",
                confidence=0.0,
                error=error_msg,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.post("/chat/continue")
async def continue_chat(request: ContinueChatRequest) -> ChatSessionResponse:
    """Continue an existing chat session"""
    
    # Ensure system is initialized
    if not _system_initialized:
        raise HTTPException(status_code=400, detail="System not initialized. Start a new chat first.")
    
    try:
        # Process the conversation with thinking status
        import time
        start_time = time.time()
        print(f"🚀 Continuing conversation processing for session {request.session_id}")
        
        result = continue_conversation_session(request.session_id, request.message)
        
        processing_time = time.time() - start_time
        print(f"⏱️ Conversation processing completed in {processing_time:.2f} seconds")
        
        if result.get("success"):
            session_manager.update_session(request.session_id)
            
            return ChatSessionResponse(
                success=True,
                session_id=request.session_id,
                response=result.get("response", "I'm having trouble thinking right now."),
                confidence=result.get("confidence", 0.0),
                thinking_steps=result.get("thinking_steps", []),
                conversation_context=result.get("conversation_context", {}),
                timestamp=datetime.now().isoformat()
            )
        else:
            error_msg = result.get("error", "Unknown error occurred")
            return ChatSessionResponse(
                success=False,
                session_id=request.session_id,
                response="",
                confidence=0.0,
                error=error_msg,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/chat/session/{session_id}/status")
async def get_session_status(session_id: str) -> SessionStatusResponse:
    """Get status of a specific session"""
    try:
        status = session_manager.get_session_status(session_id)
        return SessionStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/chat/session/{session_id}/history")
async def get_conversation_history(session_id: str) -> ConversationHistory:
    """Get conversation history for a session"""
    try:
        memory = memory_manager.get_session_memory(session_id)
        history = memory.get_conversation_history()
        summary = memory.get_conversation_summary()
        
        # Format history for API response
        formatted_history = []
        for i in range(0, len(history), 2):
            if i + 1 < len(history):
                human_msg = history[i].content
                ai_msg = history[i + 1].content
                formatted_history.append({
                    "role": "user",
                    "content": human_msg,
                    "timestamp": history[i].additional_kwargs.get("timestamp", "")
                })
                formatted_history.append({
                    "role": "assistant", 
                    "content": ai_msg,
                    "timestamp": history[i + 1].additional_kwargs.get("timestamp", "")
                })
        
        return ConversationHistory(
            session_id=session_id,
            history=formatted_history,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.delete("/chat/session/{session_id}")
async def clear_session(session_id: str) -> Dict[str, str]:
    """Clear conversation memory for a session"""
    try:
        memory = memory_manager.get_session_memory(session_id)
        memory.clear_memory()
        
        # Reset session counter
        if session_id in session_manager.sessions:
            session_manager.sessions[session_id]["conversation_count"] = 0
        
        return {"message": f"Session {session_id} cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@router.post("/chat/shutdown")
async def shutdown_system() -> Dict[str, str]:
    """Shutdown system dependencies (admin endpoint)"""
    global _system_initialized
    
    try:
        shutdown_dependencies()
        _system_initialized = False
        return {"message": "System shutdown successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during shutdown: {str(e)}")