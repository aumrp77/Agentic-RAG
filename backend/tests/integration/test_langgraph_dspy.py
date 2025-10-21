#!/usr/bin/env python3
"""
Test the DSPy-enhanced LangGraph workflow
"""

import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def test_workflow_integration():
    """Test the complete DSPy-enhanced workflow"""
    print("🚀 Testing DSPy-Enhanced LangGraph Workflow")
    print("=" * 60)
    
    try:
        # Initialize dependencies first
        from backend.app.dependencies import initialize_dependencies
        
        dspy_config = {
            'enable_dspy': True,
            'model_name': 'gpt-4-turbo-preview',
            'fallback_on_error': True,
            'auto_train': False
        }
        
        print("Initializing dependencies...")
        results = initialize_dependencies(dspy_config)
        
        print(f"Vector Store: {'✅' if results['vector_store'] else '❌'}")
        print(f"DSPy System: {'✅' if results['dspy'] else '❌'}")
        
        if not results['vector_store']:
            print("⚠️ Cannot run workflow without vector store")
            return False
        
        # Test individual nodes
        print("\n" + "=" * 60)
        print("Testing Individual Nodes")
        print("=" * 60)
        
        # Test planner node
        from backend.agent.graph.nodes.planner import planner_node
        from backend.agent.graph.state import create_initial_state
        
        test_query = "What is Munger's inversion principle?"
        print(f"\nQuery: {test_query}")
        
        # Create initial state
        state = create_initial_state(test_query, "test_session")
        
        # Test planner
        print("\n--- Testing Planner Node ---")
        start_time = time.time()
        state = planner_node(state)
        planner_time = time.time() - start_time
        
        print(f"Planner completed in {planner_time:.2f}s")
        print(f"Planning method: {state.get('planning_method', 'unknown')}")
        print(f"Query type: {state.get('query_type', 'unknown')}")
        print(f"Complexity: {state.get('query_complexity', 'unknown')}")
        print(f"Mental models: {state.get('identified_mental_models', [])}")
        
        if state.get("current_step") != "planned":
            print("❌ Planner failed")
            return False
        
        # Test retrieval (simplified)
        print("\n--- Testing Retrieval (Mock) ---")
        from backend.indexing_and_retrieval.retrieval.storage import FAISSStorage
        storage = FAISSStorage()
        vectorstore = storage.store_chunks_to_faiss()
        
        # Simple retrieval
        retrieval_results = vectorstore.similarity_search(test_query, k=5)
        state["raw_retrieved_docs"] = retrieval_results
        state["reranked_docs"] = retrieval_results[:3]  # Mock reranking
        state["current_step"] = "retrieved"
        
        print(f"Retrieved {len(retrieval_results)} documents")
        
        # Test synthesizer
        print("\n--- Testing Synthesizer Node ---")
        from backend.agent.graph.nodes.synthesizer import synthesizer_node
        
        start_time = time.time()
        state = synthesizer_node(state)
        synthesizer_time = time.time() - start_time
        
        print(f"Synthesizer completed in {synthesizer_time:.2f}s")
        print(f"Synthesis method: {state.get('synthesis_method', 'unknown')}")
        response = state.get("generated_response", "")
        print(f"Response length: {len(response.split())} words")
        print(f"Confidence: {state.get('response_confidence', 0):.3f}")
        
        if state.get("current_step") != "synthesized":
            print("❌ Synthesizer failed")
            return False
        
        # Test verifier
        print("\n--- Testing Verifier Node ---")
        from backend.agent.graph.nodes.verifier import verifier_node
        
        start_time = time.time()
        state = verifier_node(state)
        verifier_time = time.time() - start_time
        
        print(f"Verifier completed in {verifier_time:.2f}s")
        print(f"Verification method: {state.get('verification_method', 'unknown')}")
        print(f"Quality score: {state.get('response_quality_score', 0):.3f}")
        print(f"Quality level: {state.get('quality_level', 'unknown')}")
        
        # Final results
        print("\n" + "=" * 60)
        print("WORKFLOW RESULTS")
        print("=" * 60)
        
        total_time = planner_time + synthesizer_time + verifier_time
        print(f"Total processing time: {total_time:.2f}s")
        
        # Show method usage
        methods_used = {
            "Planning": state.get('planning_method', 'unknown'),
            "Synthesis": state.get('synthesis_method', 'unknown'), 
            "Verification": state.get('verification_method', 'unknown')
        }
        
        print("\nMethods Used:")
        for component, method in methods_used.items():
            icon = "🧠" if method == "dspy" else "⚙️" if method == "fallback" else "❓"
            print(f"  {component}: {icon} {method}")
        
        # Show response preview
        response = state.get("generated_response", "")
        print(f"\nResponse Preview:")
        print(f"  {response[:100]}..." if len(response) > 100 else f"  {response}")
        
        # Check for errors
        errors = state.get("errors", [])
        if errors:
            print(f"\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")
        
        # Success criteria
        dspy_used = any(method == "dspy" for method in methods_used.values())
        fallback_works = any(method == "fallback" for method in methods_used.values())
        
        print(f"\n🎯 Integration Assessment:")
        print(f"  DSPy Enhancement: {'✅' if dspy_used else '❌'}")
        print(f"  Fallback Support: {'✅' if fallback_works else '❌'}")
        print(f"  Workflow Complete: {'✅' if response else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_workflow_integration()
    if success:
        print("\n🎉 DSPy-Enhanced LangGraph Integration: SUCCESS!")
    else:
        print("\n💥 DSPy-Enhanced LangGraph Integration: FAILED!")
