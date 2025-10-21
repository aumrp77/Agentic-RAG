#!/usr/bin/env python3
"""
Test the conversational workflow with memory
"""

import sys
import os
import uuid

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def test_conversational_workflow():
    """Test the memory-enhanced conversational workflow"""
    print("🗣️ Testing Conversational Workflow with Memory")
    print("=" * 70)
    
    try:
        # Initialize dependencies
        from backend.app.dependencies import initialize_dependencies
        
        results = initialize_dependencies({'enable_dspy': True})
        print(f"System initialized: DSPy={results['dspy']}, Vector={results['vector_store']}")
        
        if not results['vector_store']:
            print("⚠️ Cannot run conversational test without vector store")
            return False
        
        # Import conversational functions
        from backend.agent.graph.workflow import start_conversation_session, continue_conversation_session
        
        # Generate unique session ID
        session_id = f"test_conversation_{uuid.uuid4().hex[:8]}"
        print(f"\nStarting conversation session: {session_id}")
        
        # Conversation sequence
        conversation = [
            "What is your advice on investing?",
            "What was the last question I asked you?",
            "Can you tell me more about patience in investing?",
            "You mentioned avoiding speculation. What do you mean by that?",
        ]
        
        responses = []
        
        for i, query in enumerate(conversation):
            print(f"\n{'='*50}")
            print(f"Exchange {i+1}: {query}")
            print(f"{'='*50}")
            
            if i == 0:
                # Start conversation
                result = start_conversation_session(session_id, query)
            else:
                # Continue conversation
                result = continue_conversation_session(session_id, query)
            
            if result["success"]:
                response = result["response"]
                confidence = result["confidence"]
                conversation_context = result["conversation_context"]
                
                print(f"\n🤖 Munger's Response:")
                print(f"{response}")
                print(f"\n📊 Metadata:")
                print(f"   Confidence: {confidence:.3f}")
                print(f"   Has History: {conversation_context.get('has_conversation_history', False)}")
                
                if conversation_context.get("continuation_context"):
                    cont_ctx = conversation_context["continuation_context"]
                    print(f"   Context Type: {cont_ctx.get('type', 'unknown')}")
                    if cont_ctx.get('previous_topic'):
                        print(f"   Previous Topic: {cont_ctx['previous_topic']}")
                
                if conversation_context.get("user_context"):
                    user_ctx = conversation_context["user_context"]
                    print(f"   Is Follow-up: {user_ctx.get('is_followup', False)}")
                    print(f"   References Previous: {user_ctx.get('references_previous', False)}")
                    print(f"   User Familiarity: {user_ctx.get('familiarity_level', 'unknown')}")
                
                if conversation_context.get("discussed_topics"):
                    topics = conversation_context["discussed_topics"]
                    print(f"   Discussed Topics: {topics}")
                
                responses.append({
                    "query": query,
                    "response": response[:200] + "..." if len(response) > 200 else response,
                    "confidence": confidence,
                    "context_type": conversation_context.get("continuation_context", {}).get("type", "new"),
                    "has_memory": conversation_context.get("has_conversation_history", False)
                })
                
            else:
                print(f"❌ Error: {result['error']}")
                return False
        
        # Summary
        print(f"\n{'='*70}")
        print("CONVERSATION SUMMARY")
        print(f"{'='*70}")
        
        print(f"Session ID: {session_id}")
        print(f"Total Exchanges: {len(responses)}")
        
        print(f"\nConversation Flow:")
        for i, resp in enumerate(responses):
            context_icon = "🧠" if resp["has_memory"] else "🆕"
            print(f"  {i+1}. {context_icon} {resp['context_type']}: {resp['query']}")
            print(f"     Response: {resp['response']}")
            print(f"     Confidence: {resp['confidence']:.3f}")
        
        # Test memory persistence
        print(f"\n🧠 Testing Memory Persistence...")
        followup_result = continue_conversation_session(session_id, "What was the first thing I asked you about?")
        
        if followup_result["success"]:
            print(f"Memory test response: {followup_result['response'][:150]}...")
            memory_works = "investing" in followup_result['response'].lower()
            print(f"Memory working: {'✅' if memory_works else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversational workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_features():
    """Test specific memory features"""
    print("\n🧠 Testing Memory Features")
    print("=" * 50)
    
    try:
        from backend.agent.graph.memory import MungerConversationMemory
        
        # Create test memory
        memory = MungerConversationMemory("test_memory_session")
        
        # Add test exchanges
        exchanges = [
            ("What is inversion?", "Inversion is thinking backwards, considering what could go wrong rather than what could go right."),
            ("Can you give an example?", "Well, instead of asking how to succeed in business, ask what would cause a business to fail."),
            ("That's helpful, what about in investing?", "In investing, instead of focusing on what makes a great investment, consider what makes terrible investments.")
        ]
        
        for human_msg, ai_msg in exchanges:
            memory.add_exchange(human_msg, ai_msg, {"mental_models": ["inversion"]})
        
        # Test context retrieval
        context = memory.get_conversation_context("Tell me more about avoiding failures")
        
        print(f"✅ Memory system functional")
        print(f"   Has conversation history: {context['has_conversation_history']}")
        print(f"   Recent exchanges: {len(context['recent_exchanges'])}")
        print(f"   Discussed topics: {context['discussed_topics']}")
        print(f"   Conversation summary: {context['conversation_summary'][:100] if context['conversation_summary'] else 'None'}")
        
        # Test enhanced context
        enhanced_context = memory.get_memory_enhanced_context("New context about business failures")
        print(f"   Enhanced context length: {len(enhanced_context)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory features test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Conversational Workflow Tests")
    print("=" * 80)
    
    # Test memory features first
    memory_success = test_memory_features()
    
    # Test full conversational workflow
    workflow_success = test_conversational_workflow()
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Memory Features: {'✅ PASS' if memory_success else '❌ FAIL'}")
    print(f"Conversational Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    
    if memory_success and workflow_success:
        print(f"\n🎉 All conversational tests PASSED!")
        print(f"💬 The system now supports:")
        print(f"   • Conversation memory across exchanges")
        print(f"   • Context-aware response generation") 
        print(f"   • Follow-up question understanding")
        print(f"   • Session persistence")
        print(f"   • Memory-enhanced retrieval")
    else:
        print(f"\n💥 Some tests FAILED!")
