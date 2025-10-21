"""
Simple Conversational Memory for Charlie Munger RAG Agent
Uses LangChain ConversationBufferMemory for conversation history and summary
"""

from typing import Dict, List
from langchain.schema import BaseMessage
from langchain.memory import ConversationBufferMemory
import json
import os
from datetime import datetime, timedelta


class MungerConversationMemory:
    """Simple memory system for Munger conversations using LangChain ConversationBufferMemory"""
    
    def __init__(self, session_id: str, max_token_limit: int = 2000):
        self.session_id = session_id
        self.max_token_limit = max_token_limit
        
        # Use LangChain's ConversationBufferMemory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Load existing memory if available
        self._load_session_memory()
    
    def add_exchange(self, human_message: str, ai_response: str):
        """Add a complete exchange to memory"""
        self.memory.save_context(
            {"input": human_message},
            {"output": ai_response}
        )
        self._save_session_memory()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get conversation history messages"""
        memory_variables = self.memory.load_memory_variables({})
        return memory_variables.get("chat_history", [])
    
    def get_conversation_summary(self) -> str:
        """Get a simple summary of the conversation"""
        memory_variables = self.memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        if len(chat_history) < 2:
            return ""
        
        exchange_count = len(chat_history) // 2
        return f"Conversation with {exchange_count} exchanges"
    
    def get_conversation_context(self, query: str) -> Dict:
        """Get conversation context for compatibility with existing workflow"""
        memory_variables = self.memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        has_history = len(chat_history) > 0
        
        # Format recent exchanges
        recent_exchanges = []
        for i in range(0, len(chat_history), 2):
            if i + 1 < len(chat_history):
                human_msg = chat_history[i].content if hasattr(chat_history[i], 'content') else str(chat_history[i])
                ai_msg = chat_history[i + 1].content if hasattr(chat_history[i + 1], 'content') else str(chat_history[i + 1])
                recent_exchanges.append({
                    "human": human_msg,
                    "ai": ai_msg[:150] + "..." if len(ai_msg) > 150 else ai_msg
                })
        
        return {
            "has_conversation_history": has_history,
            "conversation_summary": self.get_conversation_summary(),
            "recent_exchanges": recent_exchanges[-3:],  # Last 3 exchanges
            "user_context": {"is_followup": False, "references_previous": False},
            "continuation_context": {"type": "new_topic"}
        }
    
    def get_memory_enhanced_context(self, current_context: str) -> str:
        """Enhance current retrieval context with recent conversation memory"""
        memory_variables = self.memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        
        if not chat_history:
            return current_context
        
        # Get recent context from last exchange
        recent_context = ""
        if len(chat_history) >= 2:
            last_messages = chat_history[-2:]
            human_msg = last_messages[0].content if hasattr(last_messages[0], 'content') else str(last_messages[0])
            ai_msg = last_messages[1].content if hasattr(last_messages[1], 'content') else str(last_messages[1])
            recent_context = f"Previous Q: {human_msg}\nMunger's response: {ai_msg[:200]}..."
        
        if recent_context:
            return f"Previous conversation context:\n{recent_context}\n\nCurrent context:\n{current_context}"
        else:
            return current_context
    
    def clear_memory(self):
        """Clear conversation memory for this session"""
        self.memory.clear()
        self._remove_session_file()
    
    def _save_session_memory(self):
        """Save conversation memory to persistent storage"""
        import os
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "indexing_and_retrieval", "storage", "conversation_memory")
        os.makedirs(memory_dir, exist_ok=True)
        
        # Extract messages from LangChain memory using proper API
        memory_variables = self.memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        
        serialized_history = []
        for msg in chat_history:
            serialized_history.append({
                "type": msg.__class__.__name__,
                "content": msg.content if hasattr(msg, 'content') else str(msg)
            })
        
        memory_data = {
            "session_id": self.session_id,
            "chat_history": serialized_history,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(f"{memory_dir}/{self.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2)
    
    def _load_session_memory(self):
        """Load existing conversation memory from storage"""
        import os
        memory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "indexing_and_retrieval", "storage", "conversation_memory", f"{self.session_id}.json")
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
            
            # Restore chat history to LangChain memory
            chat_history = memory_data.get("chat_history", [])
            for msg_data in chat_history:
                msg_type = msg_data.get("type", "HumanMessage")
                content = msg_data.get("content", "")
                
                if msg_type == "HumanMessage":
                    self.memory.chat_memory.add_user_message(content)
                elif msg_type == "AIMessage":
                    self.memory.chat_memory.add_ai_message(content)
    
    def _remove_session_file(self):
        """Remove saved session file"""
        import os
        memory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "indexing_and_retrieval", "storage", "conversation_memory", f"{self.session_id}.json")
        if os.path.exists(memory_file):
            os.remove(memory_file)


class ConversationMemoryManager:
    """Global manager for conversation memory sessions"""
    
    def __init__(self):
        self._sessions: Dict[str, MungerConversationMemory] = {}
    
    def get_session_memory(self, session_id: str) -> MungerConversationMemory:
        """Get or create memory for a session"""
        if session_id not in self._sessions:
            self._sessions[session_id] = MungerConversationMemory(session_id)
        return self._sessions[session_id]
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Cleanup old conversation sessions based on file timestamps"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        import os
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", "indexing_and_retrieval", "storage", "conversation_memory")
        
        if not os.path.exists(memory_dir):
            return
        
        sessions_to_remove = []
        for session_id in list(self._sessions.keys()):
            memory_file = f"{memory_dir}/{session_id}.json"
            if os.path.exists(memory_file):
                file_time = datetime.fromtimestamp(os.path.getmtime(memory_file))
                if file_time < cutoff_time:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in self._sessions:
                del self._sessions[session_id]


# Global memory manager instance
memory_manager = ConversationMemoryManager()
