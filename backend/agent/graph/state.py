"""
Enhanced LangGraph State for Charlie Munger RAG Agent
Comprehensive state management for agentic workflow orchestration
"""

from typing import List, Dict, Optional, Literal, Any, TypedDict
from langchain.schema import Document as LCDocument
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

class Document(BaseModel):
    doc_id: str
    source_type: str | None = None
    source_name: str | None = None

class Chunk(BaseModel):
    chunk_id: str
    parent_doc_id: str
    text: str
    token_count: int

class MungerState(TypedDict):
    """Comprehensive state for Munger RAG Agent workflow using LangGraph TypedDict"""
    
    # Input & Context
    user_query: str
    conversation_history: List[BaseMessage]
    session_id: Optional[str]
    conversation_context: Optional[Dict[str, Any]]
    has_conversation_history: Optional[bool]
    conversation_summary: Optional[str]
    recent_exchanges: Optional[List[Dict[str, str]]]
    user_context: Optional[Dict[str, Any]]
    continuation_context: Optional[Dict[str, Any]]
    
    # Planning & Analysis
    query_type: Optional[Literal["quote", "explanation", "mental_model", "story", "general", "decision_framework"]]
    identified_mental_models: List[str]
    query_complexity: Optional[Literal["simple", "moderate", "complex"]]
    query_intent: Optional[str]
    
    # Retrieval Pipeline
    needs_retrieval: Optional[bool]
    retrieval_level: Optional[str]
    retrieval_decision: Optional[Dict[str, Any]]
    raw_retrieved_docs: List[LCDocument]
    reranked_docs: List[LCDocument]
    retrieval_metadata: Dict[str, Any]
    retrieval_strategy: Optional[str]
    
    # Mental Model Analysis
    applicable_mental_models: List[str]
    mental_model_explanations: Dict[str, str]
    model_application_notes: List[str]
    
    # Response Generation
    generated_response: str
    response_confidence: Optional[float]
    sources_used: List[str]
    citations: List[Dict[str, str]]
    planning_method: Optional[str]
    
    # Control Flow & Error Handling
    current_step: str
    retry_count: int
    max_retries: int
    errors: List[str]
    warnings: List[str]
    
    # Munger-Specific Features
    style_requirements: Dict[str, bool]
    munger_voice_active: bool
    analogies_used: List[str]
    practical_examples: List[str]
    
    # Quality Metrics
    response_quality_score: Optional[float]
    factual_accuracy_score: Optional[float]
    style_consistency_score: Optional[float]
    
    # Debugging & Monitoring
    execution_trace: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    debug_info: Dict[str, Any]


# Helper functions for state management
def create_initial_state(user_query: str, session_id: Optional[str] = None) -> MungerState:
    """Create initial state for a new query"""
    return MungerState(
        # Input
        user_query=user_query,
        conversation_history=[],
        session_id=session_id,
        conversation_context=None,
        has_conversation_history=None,
        conversation_summary=None,
        recent_exchanges=None,
        user_context=None,
        continuation_context=None,
        
        # Planning
        query_type=None,
        identified_mental_models=[],
        query_complexity=None,
        query_intent=None,
        
        # Retrieval
        needs_retrieval=None,
        retrieval_level=None,
        retrieval_decision=None,
        raw_retrieved_docs=[],
        reranked_docs=[],
        retrieval_metadata={},
        retrieval_strategy=None,
        planning_method=None,
        # Mental Models
        applicable_mental_models=[],
        mental_model_explanations={},
        model_application_notes=[],
        
        # Response
        generated_response="",
        response_confidence=None,
        sources_used=[],
        citations=[],

        # Control Flow
        current_step="start",
        retry_count=0,
        max_retries=3,
        errors=[],
        warnings=[],
        
        # Munger Features
        style_requirements={
            "direct_language": True,
            "practical_focus": True,
            "analogy_preference": True,
            "mental_model_integration": True
        },
        munger_voice_active=True,
        analogies_used=[],
        practical_examples=[],
        
        # Quality
        response_quality_score=None,
        factual_accuracy_score=None,
        style_consistency_score=None,
        
        # Debug
        execution_trace=[],
        performance_metrics={},
        debug_info={}
    )


def add_execution_trace(state: MungerState, step: str, details: Dict[str, Any]) -> MungerState:
    """Add execution trace entry for debugging"""
    trace_entry = {
        "step": step,
        "timestamp": details.get("timestamp"),
        "duration": details.get("duration"),
        "details": details
    }
    state["execution_trace"].append(trace_entry)
    return state


def add_error(state: MungerState, error: str, context: str = "") -> MungerState:
    """Add error to state with context"""
    error_entry = f"{error} (Context: {context})" if context else error
    state["errors"].append(error_entry)
    return state


def add_warning(state: MungerState, warning: str, context: str = "") -> MungerState:
    """Add warning to state with context"""
    warning_entry = f"{warning} (Context: {context})" if context else warning
    state["warnings"].append(warning_entry)
    return state


def increment_retry(state: MungerState) -> MungerState:
    """Increment retry count"""
    state["retry_count"] += 1
    return state


def can_retry(state: MungerState) -> bool:
    """Check if retry is allowed"""
    return state["retry_count"] < state["max_retries"]


def is_query_complex(state: MungerState) -> bool:
    """Determine if query requires complex reasoning"""
    return state.get("query_complexity") == "complex"


def requires_mental_models(state: MungerState) -> bool:
    """Check if query requires mental model application"""
    return state.get("query_type") in ["mental_model", "decision_framework", "general"]


def has_sufficient_context(state: MungerState) -> bool:
    """Check if we have enough context for response generation"""
    return len(state.get("reranked_docs", [])) >= 2


def get_top_context(state: MungerState, n: int = 3) -> str:
    """Get top N documents as context string"""
    docs = state.get("reranked_docs", [])[:n]
    return "\n\n".join([doc.page_content for doc in docs])


def get_mental_models_context(state: MungerState) -> str:
    """Get mental models context for response generation"""
    models = state.get("applicable_mental_models", [])
    explanations = state.get("mental_model_explanations", {})
    
    context_parts = []
    for model in models:
        if model in explanations:
            context_parts.append(f"{model}: {explanations[model]}")
    
    return "\n".join(context_parts)

def get_context_for_synthesis(state: MungerState, max_docs: int = 3) -> str:
    """Get formatted context for response synthesis"""
    docs = state.get("reranked_docs", [])[:max_docs]
    
    if not docs:
        return "No relevant context found."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        # Safely access metadata
        doc_metadata = doc.metadata or {}
        score = doc_metadata.get("rerank_score", 0)
        context_parts.append(f"[Source {i} (Score: {score:.3f})]\n{doc.page_content}")
    
    return "\n\n".join(context_parts)