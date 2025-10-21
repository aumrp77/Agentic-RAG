#!/usr/bin/env python3
"""
Test the fallback functionality when DSPy is disabled
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def test_fallback_workflow():
    """Test the workflow with DSPy disabled to ensure fallback works"""
    print("🔄 Testing Fallback Workflow (DSPy Disabled)")
    print("=" * 60)
    
    try:
        # Initialize dependencies with DSPy disabled
        from backend.app.dependencies import initialize_dependencies
        
        dspy_config = {
            'enable_dspy': False,  # Disable DSPy
            'model_name': 'gpt-4-turbo-preview',
            'fallback_on_error': True,
            'auto_train': False
        }
        
        print("Initializing dependencies (DSPy disabled)...")
        results = initialize_dependencies(dspy_config)
        
        print(f"Vector Store: {'✅' if results['vector_store'] else '❌'}")
        print(f"DSPy System: {'✅' if results['dspy'] else '❌ (expected)'}")
        
        # Test individual nodes with fallback
        from backend.agent.graph.nodes.planner import planner_node
        from backend.agent.graph.nodes.synthesizer import synthesizer_node
        from backend.agent.graph.nodes.verifier import verifier_node
        from backend.agent.graph.state import create_initial_state
        from backend.indexing_and_retrieval.retrieval.storage import FAISSStorage
        
        test_query = "What is compound interest?"
        state = create_initial_state(test_query, "fallback_test")
        
        print(f"\nQuery: {test_query}")
        
        # Test planner fallback
        print("\n--- Testing Planner (Fallback) ---")
        state = planner_node(state)
        print(f"Planning method: {state.get('planning_method', 'unknown')}")
        print(f"Query type: {state.get('query_type', 'unknown')}")
        
        # Mock retrieval
        storage = FAISSStorage()
        vectorstore = storage.store_chunks_to_faiss()
        retrieval_results = vectorstore.similarity_search(test_query, k=3)
        state["raw_retrieved_docs"] = retrieval_results
        state["reranked_docs"] = retrieval_results[:2]
        state["current_step"] = "retrieved"
        
        # Test synthesizer fallback
        print("\n--- Testing Synthesizer (Fallback) ---")
        state = synthesizer_node(state)
        print(f"Synthesis method: {state.get('synthesis_method', 'unknown')}")
        response = state.get("generated_response", "")
        print(f"Response length: {len(response.split())} words")
        
        # Test verifier fallback
        print("\n--- Testing Verifier (Fallback) ---")
        state = verifier_node(state)
        print(f"Verification method: {state.get('verification_method', 'unknown')}")
        print(f"Quality score: {state.get('response_quality_score', 0):.3f}")
        
        # Results
        methods_used = {
            "Planning": state.get('planning_method', 'unknown'),
            "Synthesis": state.get('synthesis_method', 'unknown'), 
            "Verification": state.get('verification_method', 'unknown')
        }
        
        print("\n" + "=" * 60)
        print("FALLBACK TEST RESULTS")
        print("=" * 60)
        
        print("Methods Used:")
        for component, method in methods_used.items():
            icon = "⚙️" if method == "fallback" else "❓"
            print(f"  {component}: {icon} {method}")
        
        # Check that all methods are fallback
        all_fallback = all(method == "fallback" for method in methods_used.values())
        workflow_complete = bool(state.get("generated_response"))
        
        print(f"\n🎯 Fallback Assessment:")
        print(f"  All Fallback Methods: {'✅' if all_fallback else '❌'}")
        print(f"  Workflow Complete: {'✅' if workflow_complete else '❌'}")
        print(f"  No Errors: {'✅' if not state.get('errors') else '❌'}")
        
        return all_fallback and workflow_complete
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fallback_workflow()
    if success:
        print("\n🎉 Fallback Workflow: SUCCESS!")
    else:
        print("\n💥 Fallback Workflow: FAILED!")
