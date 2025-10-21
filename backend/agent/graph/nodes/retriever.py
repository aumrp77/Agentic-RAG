"""
Retriever Node for Charlie Munger RAG Agent
Coordinates retrieval and reranking using existing components
"""

import time
from typing import Dict, Any, List
from langchain.schema import Document as LCDocument
from backend.agent.graph.state import MungerState, add_execution_trace, add_error, has_sufficient_context
from backend.indexing_and_retrieval.retrieval.retrieval import Retrieval
from backend.indexing_and_retrieval.retrieval.rerank import Rerank


class EnhancedRetriever:
    """Enhanced retrieval coordinator with strategy-aware retrieval"""
    
    def __init__(self):
        self.retrieval_cache = {}  # Simple cache for repeated queries
    
    def retrieve_with_strategy(self, query: str, strategy: Dict[str, Any]) -> List[LCDocument]:
        """Perform retrieval using strategy-specific parameters"""
        try:
            # Create retrieval instance
            retriever = Retrieval(query)
            
            # Get initial retrieval with strategy-based count
            retrieval_count = strategy.get("retrieval_count", 20)
            raw_docs = retriever.retrieve(k=retrieval_count)
            
            return raw_docs
            
        except Exception as e:
            print(f"Retrieval failed: {e}")
            return []
    
    def rerank_with_strategy(self, query: str, docs: List[LCDocument], strategy: Dict[str, Any]) -> List[LCDocument]:
        """Perform reranking using strategy-specific parameters"""
        try:
            if not docs:
                return []
            
            # Ensure strategy is not None
            strategy = strategy or {}
            
            # Create reranker instance and use rerank_documents method
            reranker = Rerank(query)
            final_count = strategy.get("rerank_count", 5)
            return reranker.rerank_documents(docs, final_count)
            
        except Exception as e:
            print(f"Reranking failed: {e}")
            return docs[:strategy.get("rerank_count", 8)]  # Fallback to original docs
    
    def filter_by_source_preference(self, docs: List[LCDocument], prefer_sources: List[str]) -> List[LCDocument]:
        """Filter documents based on source preferences"""
        if "all" in prefer_sources:
            return docs
        
        # This is a placeholder - in a real implementation, you'd check document metadata
        # For now, we'll return all docs since we don't have source metadata
        return docs
    
    def extract_metadata(self, docs: List[LCDocument]) -> Dict[str, Any]:
        """Extract metadata from retrieved documents"""
        if not docs:
            return {}
        
        # Safely extract scores, handling None metadata
        scores = []
        document_types = []
        total_tokens = 0
        
        for doc in docs:
            # Handle case where metadata might be None
            doc_metadata = doc.metadata or {}
            
            # Extract rerank score
            score = doc_metadata.get("rerank_score", 0)
            scores.append(score)
            
            # Extract document type
            doc_type = doc_metadata.get("source_type", "unknown")
            document_types.append(doc_type)
            
            # Extract token count
            tokens = doc_metadata.get("token_count", 0)
            total_tokens += tokens
        
        # Calculate metadata safely
        avg_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        metadata = {
            "total_documents": len(docs),
            "avg_score": avg_score,
            "score_range": {
                "min": min_score,
                "max": max_score
            },
            "document_types": list(set(document_types)),
            "total_tokens": total_tokens
        }
        
        return metadata


def retriever_node(state: MungerState) -> MungerState:
    """
    Main retriever node that coordinates retrieval and reranking
    """
    start_time = time.time()
    
    try:
        query = state["user_query"]
        strategy = state.get("retrieval_strategy") or {}
        
        # Initialize enhanced retriever
        retriever = EnhancedRetriever()
        
        # Step 1: Initial retrieval
        print(f"🔍 Retrieving documents with strategy: {strategy.get('focus', 'balanced')}")
        raw_docs = retriever.retrieve_with_strategy(query, strategy)
        state["raw_retrieved_docs"] = raw_docs
        
        if not raw_docs:
            add_error(state, "No documents retrieved", "retrieval")
            state["current_step"] = "retrieval_failed"
            return state
        
        # Step 2: Reranking
        print(f"🎯 Reranking {len(raw_docs)} documents")
        reranked_docs = retriever.rerank_with_strategy(query, raw_docs, strategy)
        state["reranked_docs"] = reranked_docs
        
        # Step 3: Source filtering (if specified)
        prefer_sources = strategy.get("prefer_sources", ["all"])
        if prefer_sources != ["all"]:
            reranked_docs = retriever.filter_by_source_preference(reranked_docs, prefer_sources)
            state["reranked_docs"] = reranked_docs
        
        # Step 4: Extract metadata
        retrieval_metadata = retriever.extract_metadata(reranked_docs)
        state["retrieval_metadata"] = retrieval_metadata
        
        # Step 5: Check if we have sufficient context
        if not has_sufficient_context(state):
            add_error(state, "Insufficient context retrieved", "retrieval")
            state["current_step"] = "insufficient_context"
            return state
        
        # Update state
        state["current_step"] = "retrieved"
        
        # Add execution trace
        duration = time.time() - start_time
        add_execution_trace(state, "retriever", {
            "timestamp": start_time,
            "duration": duration,
            "raw_count": len(raw_docs),
            "reranked_count": len(reranked_docs),
            "avg_score": retrieval_metadata.get("avg_score", 0),
            "strategy_used": strategy
        })
        
        print(f"✅ Retrieval: {len(raw_docs)} → {len(reranked_docs)} documents (avg score: {retrieval_metadata.get('avg_score', 0):.3f})")
        
    except Exception as e:
        error_msg = f"Retrieval failed: {str(e)}"
        add_error(state, error_msg, "retriever")
        state["current_step"] = "retrieval_failed"
        print(f"❌ Retrieval error: {error_msg}")
    
    return state


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


def get_top_sources(state: MungerState, n: int = 5) -> List[str]:
    """Get top N source identifiers for citations"""
    docs = state.get("reranked_docs", [])[:n]
    sources = []
    
    for doc in docs:
        # Extract source info from metadata, safely
        doc_metadata = doc.metadata or {}
        chunk_id = doc_metadata.get("chunk_id", "unknown")
        parent_doc_id = doc_metadata.get("parent_doc_id", "unknown")
        sources.append(f"{parent_doc_id}:{chunk_id}")
    
    return sources


def should_retry_retrieval(state: MungerState) -> bool:
    """Determine if retrieval should be retried"""
    # Check if we have errors and can retry
    has_retrieval_errors = any("retrieval" in error.lower() for error in state.get("errors", []))
    has_insufficient_context = state.get("current_step") == "insufficient_context"
    can_retry = state.get("retry_count", 0) < state.get("max_retries", 3)
    
    return (has_retrieval_errors or has_insufficient_context) and can_retry


def get_retrieval_quality_score(state: MungerState) -> float:
    """Calculate retrieval quality score"""
    metadata = state.get("retrieval_metadata", {})
    avg_score = metadata.get("avg_score", 0)
    doc_count = metadata.get("total_documents", 0)
    
    # Simple quality scoring
    score_factor = min(avg_score / 10.0, 1.0)  # Normalize to 0-1
    count_factor = min(doc_count / 5.0, 1.0)   # Prefer 5+ docs
    
    return (score_factor + count_factor) / 2.0
