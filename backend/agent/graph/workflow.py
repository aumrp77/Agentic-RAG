"""
LangGraph Workflow for Charlie Munger RAG Agent
Combines all workflow types with conversation memory and web interface support
"""

import time
from typing import Dict, Any, Callable, Optional
from langgraph.graph import StateGraph, END
from backend.agent.graph.state import MungerState, create_initial_state, increment_retry, can_retry
from backend.agent.graph.memory import memory_manager
from backend.agent.graph.nodes.planner import planner_node
from backend.agent.graph.nodes.retriever import retriever_node
from backend.agent.graph.nodes.mental_model_analyzer import mental_model_analyzer_node, requires_mental_models
from backend.agent.graph.nodes.synthesizer import synthesizer_node
from backend.agent.graph.nodes.verifier import verifier_node

# Global thinking status callback (for web interface)
_thinking_status_callback: Optional[Callable[[str, str, str], None]] = None

def set_thinking_status_callback(callback: Optional[Callable[[str, str, str], None]]):
    """Set global callback for thinking status updates"""
    global _thinking_status_callback
    _thinking_status_callback = callback

def update_thinking_status(status: str, message: str, step: str = None):
    """Update thinking status if callback is set"""
    if _thinking_status_callback:
        _thinking_status_callback(status, message, step)


# Enhanced Conversational Nodes
def memory_context_node(state: MungerState) -> MungerState:
    """
    Enhanced context node that incorporates conversation memory
    """
    update_thinking_status("thinking", "Mr. Munger is accessing his memory...", "memory_context")
    
    session_id = state.get("session_id", "default")
    user_query = state["user_query"]
    
    # Get conversation memory
    conv_memory = memory_manager.get_session_memory(session_id)
    print(f"🧠 Memory Context: {conv_memory.get_conversation_summary()}")
    
    # Get conversation context
    conversation_context = conv_memory.get_conversation_context(user_query)
    
    # Update state with memory context
    state["conversation_context"] = conversation_context
    state["has_conversation_history"] = conversation_context["has_conversation_history"]
    state["conversation_summary"] = conversation_context["conversation_summary"]
    state["recent_exchanges"] = conversation_context["recent_exchanges"]
    state["user_context"] = conversation_context["user_context"]
    state["continuation_context"] = conversation_context["continuation_context"]
    
    # Mark step
    state["current_step"] = "memory_context_loaded"
    
    has_history = conversation_context["has_conversation_history"]
    if has_history:
        update_thinking_status("thinking", "Mr. Munger is reviewing our conversation...", "memory_loaded")
        print("🧠 Memory Context: Continuing conversation")
        context_type = conversation_context["continuation_context"]["type"]
        print(f"   Context Type: {context_type}")
        if context_type == "followup":
            print(f"   Following up on: {conversation_context['continuation_context'].get('previous_topic', 'previous discussion')}")
    else:
        update_thinking_status("thinking", "Mr. Munger is preparing to think about your question...", "memory_loaded")
        print("🧠 Memory Context: New conversation")
    
    return state


def enhanced_planner_node(state: MungerState) -> MungerState:
    """
    Enhanced planner that considers conversation context and decides on retrieval
    """
    update_thinking_status("planning", "Mr. Munger is analyzing your question...", "planning")
    
    from backend.app.dependencies import dspy_manager
    
    user_query = state["user_query"]
    conversation_context = state.get("conversation_context", {})
    
    # Create enhanced context for planning
    context_parts = []
    
    # Add conversation summary if available
    if conversation_context.get("conversation_summary"):
        context_parts.append(f"Conversation summary: {conversation_context['conversation_summary']}")
    
    # Add recent exchanges context
    if conversation_context.get("recent_exchanges"):
        recent_context = "; ".join([
            f"Previous: {ex['human']} -> {ex['ai'][:100]}..." 
            for ex in conversation_context["recent_exchanges"][-2:]
        ])
        context_parts.append(f"Recent context: {recent_context}")
    
    # Add user context
    user_ctx = conversation_context.get("user_context", {})
    if user_ctx.get("is_followup"):
        context_parts.append("This appears to be a follow-up question")
    if user_ctx.get("references_previous"):
        context_parts.append("User is referencing previous conversation")
    
    # Format conversation context for retrieval decision
    conv_context_str = "; ".join(context_parts) if context_parts else ""
    
    # STEP 1: Decide whether retrieval is needed using DSPy CoT
    retrieval_decision = dspy_manager.decide_retrieval(user_query, conv_context_str)
    state["retrieval_decision"] = retrieval_decision
    
    # Handle case where DSPy manager isn't available - use fallback logic
    if not retrieval_decision.get("success", False):
        from backend.agent.dspy_modules.simple_modules import SimpleDSPyRetrievalDecider
        fallback_decider = SimpleDSPyRetrievalDecider()
        retrieval_decision = fallback_decider.should_retrieve(user_query, conv_context_str)
        state["retrieval_decision"] = retrieval_decision
    
    state["needs_retrieval"] = retrieval_decision.get("needs_retrieval", True)
    state["retrieval_level"] = retrieval_decision.get("retrieval_level", "yes")
    
    # Enhanced planning with conversation awareness
    from backend.agent.graph.nodes.planner import QueryPlanner
    planner = QueryPlanner()
    
    # Modify query type based on conversation context
    base_type = planner.classify_query_type(user_query)
    continuation_context = conversation_context.get("continuation_context", {})
    
    if continuation_context.get("type") == "followup":
        state["query_type"] = base_type
        state["conversational_enhancement"] = "followup"
    elif continuation_context.get("type") == "pivot":
        state["query_type"] = base_type
        state["conversational_enhancement"] = "pivot"
    else:
        state["query_type"] = base_type
        state["conversational_enhancement"] = "new_topic"
    
    state["query_complexity"] = planner.analyze_query_complexity(user_query)
    state["identified_mental_models"] = planner.detect_mental_models(user_query)
    state["planning_method"] = "conversational"
    
    # Print enhanced planning info
    retrieval_info = f"retrieval: {state['retrieval_level']}" if state["needs_retrieval"] else "no retrieval"
    print(f"Planner (Conversational): {base_type} query ({state.get('conversational_enhancement')}) - {retrieval_info}")
    
    needs_retrieval = state.get("needs_retrieval", True)
    if needs_retrieval:
        update_thinking_status("planning", "Mr. Munger is deciding what knowledge to retrieve...", "retrieval_planned")
    else:
        update_thinking_status("planning", "Mr. Munger will answer from his general knowledge...", "no_retrieval_needed")
    
    if retrieval_decision.get("reasoning"):
        print(f"   Reasoning: {retrieval_decision['reasoning']}")
    
    # Set planning metadata
    state["query_intent"] = f"Conversational {state.get('query_type', 'general')} query"
    state["current_step"] = "planned_with_memory_and_retrieval_decision"
    
    return state


def enhanced_retriever_node(state: MungerState) -> MungerState:
    """
    Enhanced retriever that incorporates conversation memory
    """
    update_thinking_status("retrieving", "Mr. Munger is searching through his knowledge base...", "retrieval")
    
    session_id = state.get("session_id", "default")
    conv_memory = memory_manager.get_session_memory(session_id)
    
    # Run standard retrieval first
    state = retriever_node(state)
    
    if state.get("current_step") == "retrieved":
        # Enhance context with conversation memory
        reranked_docs = state.get("reranked_docs", [])
        if reranked_docs:
            update_thinking_status("retrieving", f"Mr. Munger found {len(reranked_docs)} relevant pieces of knowledge...", "retrieval_complete")
            # Safely extract content from documents
            current_context = "\n".join([
                doc.page_content for doc in reranked_docs 
                if doc and hasattr(doc, 'page_content')
            ])
            enhanced_context = conv_memory.get_memory_enhanced_context(current_context)
            
            # Update state with enhanced context
            state["memory_enhanced_context"] = enhanced_context
            state["retrieval_method"] = "memory_enhanced"
            
            print("🔍 Retrieval enhanced with conversation memory")
        else:
            update_thinking_status("retrieving", "Mr. Munger couldn't find specific documents but will use his general knowledge...", "retrieval_empty")
            print("🔍 No documents to enhance with memory")
    
    return state


def conversational_synthesizer_node(state: MungerState) -> MungerState:
    """
    Enhanced synthesizer for conversational flow
    """
    update_thinking_status("synthesizing", "Mr. Munger is formulating his response...", "synthesis")
    
    user_query = state["user_query"]
    conversation_context = state.get("conversation_context", {})
    
    # Check if user is asking about conversation history/memory
    is_memory_question = any(word in user_query.lower() for word in [
        "last question", "previous", "what did i ask", "earlier", "before", 
        "exact question", "just asked", "what was my", "my question", 
        "conversation", "memory", "history", "asked you"
    ])
    
    if is_memory_question:
        # For memory questions, use ONLY conversation history as context
        recent_exchanges = conversation_context.get("recent_exchanges", [])
        
        if recent_exchanges:
            # Build a clear conversation history context
            conversation_history = []
            for i, ex in enumerate(recent_exchanges, 1):
                conversation_history.append(f"Exchange {i}:")
                conversation_history.append(f"  You asked: '{ex['human']}'")
                conversation_history.append(f"  I responded: {ex['ai']}")
                conversation_history.append("")
            
            memory_context = "\n".join(conversation_history)
            
            # Find the most recent NON-memory question
            previous_exchange = None
            for ex in reversed(recent_exchanges):
                if not any(word in ex['human'].lower() for word in [
                    "previous", "last question", "what did i ask", "my question", 
                    "asked you", "conversation", "history"
                ]):
                    previous_exchange = ex
                    break
            
            if previous_exchange:
                conversational_prompt = f"""You are Charlie Munger. The user is asking about our conversation history.

User's current question: {user_query}

Our conversation history:
{memory_context}

Your most recent question (before asking about history) was: "{previous_exchange['human']}"
I responded with: {previous_exchange['ai'][:200]}{"..." if len(previous_exchange['ai']) > 200 else ""}

Please answer their question about our conversation history accurately. Reference the specific question and response above."""
            else:
                conversational_prompt = f"""You are Charlie Munger. The user is asking about our conversation history.

User's current question: {user_query}

Our conversation history:
{memory_context}

Please answer their question about our conversation history accurately. Reference the questions and responses from our exchange above."""
        else:
            conversational_prompt = f"""You are Charlie Munger. The user is asking about our conversation history.

User's current question: {user_query}

However, we haven't had any previous conversation yet - this appears to be our first exchange.

Please let them know that we're just starting our conversation and there's no previous history to reference."""
            
        synthesis_context = "Memory-based response"
        
    else:
        # For non-memory questions, use the regular RAG context with conversation enhancement
        if state.get("needs_retrieval", True):
            # Normal retrieval case
            context = state.get("memory_enhanced_context") or "\n".join([
                doc.page_content for doc in state.get("reranked_docs", [])
            ])
        else:
            # No retrieval case - use general Munger knowledge
            context = "Drawing from my general knowledge and experience without specific document retrieval."
        
        # Add conversation-specific context for synthesis
        synthesis_context = context
        
        # Add conversation flow context
        continuation_context = conversation_context.get("continuation_context", {})
        user_context = conversation_context.get("user_context", {})
        
        if continuation_context.get("type") == "followup":
            synthesis_context += "\n\nConversation context: This is a follow-up to previous discussion about {}.".format(continuation_context.get('previous_topic', 'the topic'))
        elif continuation_context.get("type") == "pivot":
            synthesis_context += "\n\nConversation context: Pivoting from previous discussion to explore a different angle."
        elif user_context.get("references_previous"):
            synthesis_context += "\n\nConversation context: User is referencing something from our previous conversation."
        
        # Add user familiarity context
        familiarity = user_context.get("familiarity_level", "unknown")
        if familiarity == "high":
            synthesis_context += "\n\nUser context: This person is familiar with my concepts and mental models."
        elif familiarity == "low":
            synthesis_context += "\n\nUser context: This person may be new to my thinking - provide clear explanations."
        
        # Create conversational prompt
        conversational_prompt = """You are Charlie Munger in a continuing conversation. 
        
Current question: {}

Context: {}

Conversation flow: {}

Respond as if you're having a natural conversation, referencing previous exchanges when relevant, and maintaining the flow of discussion.""".format(
            user_query,
            synthesis_context,
            continuation_context.get('type', 'new_topic')
        )
    
    # Enhanced conversational synthesis
    from backend.agent.graph.nodes.synthesizer import MungerSynthesizer
    
    synthesizer = MungerSynthesizer()
    response = synthesizer.generate_response(conversational_prompt)
    
    state["generated_response"] = response
    
    # Set confidence based on query type and retrieval usage
    if is_memory_question:
        confidence = 0.85
        method = "memory_based"
    elif state.get("needs_retrieval", True):
        confidence = 0.75  # Standard RAG confidence
        method = "conversational_with_retrieval"
    else:
        confidence = 0.65  # Lower confidence for general knowledge without retrieval
        method = "conversational_general"
    
    state["response_confidence"] = confidence
    state["synthesis_method"] = method
    
    if response:
        update_thinking_status("synthesizing", "Mr. Munger has crafted his wisdom for you...", "synthesis_complete")
    else:
        update_thinking_status("synthesizing", "Mr. Munger is having difficulty formulating a response...", "synthesis_failed")
    
    retrieval_status = "Memory-based" if is_memory_question else ("RAG-enhanced" if state.get("needs_retrieval", True) else "General knowledge")
    print(f"Synthesis (Conversational): {retrieval_status} response generated")
    
    # Extract sources and update state
    state["sources_used"] = [] if is_memory_question else []
    state["current_step"] = "synthesized_conversational"
    
    return state


def enhanced_verifier_node(state: MungerState) -> MungerState:
    """
    Enhanced verifier considering conversational quality
    """
    update_thinking_status("verifying", "Mr. Munger is reviewing his response for quality...", "verification")
    
    # Run standard verification
    state = verifier_node(state)
    
    # Add conversational quality assessment
    conversation_context = state.get("conversation_context", {})
    response = state.get("generated_response", "")
    
    # Check for conversational elements
    conversational_quality = assess_conversational_quality(response, conversation_context)
    state["conversational_quality_score"] = conversational_quality
    
    # Adjust overall quality based on conversational elements
    base_quality = state.get("response_quality_score", 0.5)
    enhanced_quality = (base_quality * 0.7) + (conversational_quality * 0.3)
    state["enhanced_quality_score"] = enhanced_quality
    
    if enhanced_quality > 0.7:
        update_thinking_status("verifying", "Mr. Munger is satisfied with his response quality...", "verification_passed")
    else:
        update_thinking_status("verifying", "Mr. Munger has some concerns about his response quality...", "verification_warning")
    
    print(f"Verification: Enhanced quality {enhanced_quality:.3f} (conv: {conversational_quality:.3f})")
    
    return state


def memory_update_node(state: MungerState) -> MungerState:
    """
    Update conversation memory with the current exchange
    """
    update_thinking_status("thinking", "Mr. Munger is committing this exchange to memory...", "memory_update")
    
    session_id = state.get("session_id", "default")
    user_query = state["user_query"]
    ai_response = state.get("generated_response", "")
    
    if ai_response:
        # Get conversation memory
        conv_memory = memory_manager.get_session_memory(session_id)
        
        # Add exchange to memory
        conv_memory.add_exchange(user_query, ai_response)
        
        print(f"💾 Conversation memory updated for session {session_id}")
    
    update_thinking_status("complete", "Mr. Munger has finished thinking and is ready to respond.", "complete")
    
    state["current_step"] = "memory_updated"
    return state


def assess_conversational_quality(response: str, conversation_context: Dict) -> float:
    """
    Assess the conversational quality of the response
    """
    score = 0.5  # Base score
    response_lower = response.lower()
    
    # Check for conversational continuity
    continuation_type = conversation_context.get("continuation_context", {}).get("type")
    
    if continuation_type == "followup":
        # Should reference or build on previous discussion
        if any(word in response_lower for word in ["as i mentioned", "building on", "continuing", "further"]):
            score += 0.2
    elif continuation_type == "pivot":
        # Should acknowledge the shift
        if any(word in response_lower for word in ["different angle", "another way", "alternatively"]):
            score += 0.2
    
    # Check for personal engagement
    if any(phrase in response_lower for phrase in ["you're asking", "your question", "your situation"]):
        score += 0.15
    
    # Check for conversational flow
    if any(phrase in response_lower for phrase in ["well", "now", "let me", "you know"]):
        score += 0.1
    
    # Check for memory reference
    if conversation_context.get("has_conversation_history"):
        if any(phrase in response_lower for phrase in ["we discussed", "earlier", "previously"]):
            score += 0.15
    
    return min(1.0, score)


# Workflow Creation Functions

def create_conversational_workflow():
    """
    Create a conversational workflow that maintains memory and context
    """
    workflow = StateGraph(MungerState)
    
    # Add enhanced nodes
    workflow.add_node("memory_context", memory_context_node)
    workflow.add_node("planner", enhanced_planner_node)
    workflow.add_node("retriever", enhanced_retriever_node)
    workflow.add_node("mental_model_analyzer", mental_model_analyzer_node)
    workflow.add_node("synthesizer", conversational_synthesizer_node)
    workflow.add_node("verifier", enhanced_verifier_node)
    workflow.add_node("memory_update", memory_update_node)
    
    # Define conversational flow
    workflow.add_edge("memory_context", "planner")
    
    # Conditional: Retrieval decision
    workflow.add_conditional_edges(
        "planner",
        should_retrieve_documents,
        {
            "retrieve": "retriever",
            "skip_retrieval": "synthesizer"
        }
    )
    
    # Conditional: Mental model analysis (from retriever)
    workflow.add_conditional_edges(
        "retriever",
        should_analyze_mental_models,
        {
            "analyze": "mental_model_analyzer",
            "skip": "synthesizer"
        }
    )
    
    workflow.add_edge("mental_model_analyzer", "synthesizer")
    workflow.add_edge("synthesizer", "verifier")
    workflow.add_edge("verifier", "memory_update")
    
    # Conditional: Continue conversation or end
    workflow.add_conditional_edges(
        "memory_update",
        determine_conversation_flow,
        {
            "continue": "memory_context",  # Loop back for next query
            "end": END
        }
    )
    
    # Set entry point
    workflow.set_entry_point("memory_context")
    
    return workflow.compile()


def create_standard_workflow():
    """
    Create the standard workflow without conversation memory
    """
    workflow = StateGraph(MungerState)
    
    # Add standard nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("mental_model_analyzer", mental_model_analyzer_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("verifier", verifier_node)
    
    # Define the main flow
    workflow.add_edge("planner", "retriever")
    
    # Conditional edge: Should we analyze mental models?
    workflow.add_conditional_edges(
        "retriever",
        should_analyze_mental_models,
        {
            "analyze": "mental_model_analyzer",
            "skip": "synthesizer"
        }
    )
    
    workflow.add_edge("mental_model_analyzer", "synthesizer")
    workflow.add_edge("synthesizer", "verifier")
    
    # Conditional edge: Should we retry or end?
    workflow.add_conditional_edges(
        "verifier",
        determine_next_action,
        {
            "retry": "retriever",
            "end": END,
            "escalate": "synthesizer"
        }
    )
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    return workflow.compile()


def create_simple_workflow():
    """
    Create a simplified workflow for testing and development
    """
    workflow = StateGraph(MungerState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Simple linear flow
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    return workflow.compile()


# Conditional Logic Functions

def should_retrieve_documents(state: MungerState) -> str:
    """
    Determine whether to retrieve documents based on the planner's decision
    """
    needs_retrieval = state.get("needs_retrieval", True)
    decision = "retrieve" if needs_retrieval else "skip_retrieval"
    print(f"🔀 Retrieval Decision: {decision}")
    return decision


def should_analyze_mental_models(state: MungerState) -> str:
    """
    Determine if mental model analysis should be performed
    """
    # Check if retriever failed
    if state.get("current_step") == "retrieval_failed":
        return "skip"
    
    # Check if we have sufficient context
    if not state.get("reranked_docs"):
        return "skip"
    
    # Check if mental models are needed
    if requires_mental_models(state):
        return "analyze"
    
    # Simple check - skip complex analysis for conversational queries
    if len(state.get("identified_mental_models", [])) > 0:
        return "analyze"
    
    return "skip"


def determine_next_action(state: MungerState) -> str:
    """
    Determine the next action after verification
    """
    current_step = state.get("current_step", "")
    quality_score = state.get("response_quality_score", 0)
    
    # If verification failed completely
    if current_step == "verification_failed":
        if can_retry(state):
            return "retry"
        else:
            return "escalate"
    
    # If response quality is poor
    if quality_score < 0.4:
        if can_retry(state):
            increment_retry(state)
            return "retry"
        else:
            return "escalate"
    
    # If response quality is acceptable or good
    return "end"


def determine_conversation_flow(state: MungerState) -> str:
    """
    Determine whether to continue conversation or end
    """
    # For now, always end after processing one exchange
    # In a real implementation, this would wait for user input
    return "end"


# Workflow Factory

def get_workflow(workflow_type: str = "conversational"):
    """
    Get workflow based on type
    
    Args:
        workflow_type: "conversational", "standard", "simple"
    """
    workflows = {
        "conversational": create_conversational_workflow,
        "standard": create_standard_workflow,
        "simple": create_simple_workflow,
    }
    
    if workflow_type not in workflows:
        raise ValueError(f"Unknown workflow type: {workflow_type}. Available: {list(workflows.keys())}")
    
    return workflows[workflow_type]()


# Session Management Functions

def start_conversation_session(initial_query: str, session_id: str, status_callback: Optional[Callable[[str, str, str], None]] = None) -> Dict[str, Any]:
    """
    Start a new conversation session with optional thinking status updates
    """
    # Set status callback if provided
    if status_callback:
        set_thinking_status_callback(status_callback)
    
    workflow = create_conversational_workflow()
    initial_state = create_initial_state(initial_query, session_id)
    
    thinking_steps = []
    
    def capture_thinking_status(status: str, message: str, step: str = None):
        thinking_steps.append({
            "status": status,
            "message": message,
            "step": step,
            "timestamp": time.time()
        })
        if status_callback:
            status_callback(status, message, step)
    
    # Set the capture callback
    set_thinking_status_callback(capture_thinking_status)
    
    try:
        final_state = workflow.invoke(initial_state)
        return {
            "success": True,
            "session_id": session_id,
            "response": final_state.get("generated_response", ""),
            "confidence": final_state.get("response_confidence", 0),
            "conversation_context": final_state.get("conversation_context", {}),
            "thinking_steps": thinking_steps,
            "state": final_state
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id,
            "thinking_steps": thinking_steps
        }
    finally:
        # Clear callback
        set_thinking_status_callback(None)


def continue_conversation_session(session_id: str, new_query: str, status_callback: Optional[Callable[[str, str, str], None]] = None) -> Dict[str, Any]:
    """
    Continue an existing conversation session with optional thinking status updates
    """
    # Set status callback if provided
    if status_callback:
        set_thinking_status_callback(status_callback)
    
    workflow = create_conversational_workflow()
    new_state = create_initial_state(new_query, session_id)
    
    thinking_steps = []
    
    def capture_thinking_status(status: str, message: str, step: str = None):
        thinking_steps.append({
            "status": status,
            "message": message,
            "step": step,
            "timestamp": time.time()
        })
        if status_callback:
            status_callback(status, message, step)
    
    # Set the capture callback
    set_thinking_status_callback(capture_thinking_status)
    
    try:
        final_state = workflow.invoke(new_state)
        return {
            "success": True,
            "session_id": session_id,
            "response": final_state.get("generated_response", ""),
            "confidence": final_state.get("response_confidence", 0),
            "conversation_context": final_state.get("conversation_context", {}),
            "thinking_steps": thinking_steps,
            "state": final_state
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id,
            "thinking_steps": thinking_steps
        }
    finally:
        # Clear callback
        set_thinking_status_callback(None)


# Legacy function names for backward compatibility
start_web_conversation_session = start_conversation_session
continue_web_conversation_session = continue_conversation_session


# Workflow execution helper
def execute_workflow(user_query: str, workflow_type: str = "conversational", session_id: str = None) -> Dict[str, Any]:
    """
    Execute a workflow with a user query
    
    Args:
        user_query: User's question
        workflow_type: Type of workflow to use
        session_id: Optional session identifier
    
    Returns:
        Final state or result after workflow execution
    """
    if workflow_type == "conversational":
        if session_id:
            return continue_conversation_session(session_id, user_query)
        else:
            import uuid
            session_id = str(uuid.uuid4())
            return start_conversation_session(user_query, session_id)
    else:
        # For non-conversational workflows
        workflow = get_workflow(workflow_type)
        initial_state = create_initial_state(user_query, session_id)
        
        try:
            final_state = workflow.invoke(initial_state)
            return {
                "success": True,
                "response": final_state.get("generated_response", ""),
                "confidence": final_state.get("response_confidence", 0),
                "state": final_state
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "state": initial_state
            }
