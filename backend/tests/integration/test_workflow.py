"""
Simple Test Script for Charlie Munger RAG Agent
Run one query through the workflow
"""

import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

def test_simple_query():
    """Test with a simple query using the basic workflow"""
    
    try:
        print("🚀 Starting Munger RAG Test...")
        
        # Import after path setup
        from backend.agent.graph.workflow import get_workflow, execute_workflow
        
        # Test query
        query = "What would Charlie Munger say about AI as a technology benefiting buisnesses?"
        print(f"📝 Query: {query}")
        
        # Get simple workflow (no verification for now)
        print("📋 Creating simple workflow...")
        workflow = get_workflow("simple")
        print("✅ Workflow created")
        
        # Execute
        print("🎭 Executing workflow...")
        start_time = time.time()
        
        result = execute_workflow(workflow, query)
        
        execution_time = time.time() - start_time
        print(f"⏱️ Completed in {execution_time:.2f} seconds")
        
        # Print results
        print("\n" + "="*50)
        print("📊 RESULTS")
        print("="*50)
        
        print(f"Current Step: {result.get('current_step', 'unknown')}")
        print(f"Query Type: {result.get('query_type', 'unknown')}")
        print(f"Complexity: {result.get('query_complexity', 'unknown')}")
        
        # Documents retrieved
        raw_docs = len(result.get('raw_retrieved_docs', []))
        reranked_docs = len(result.get('reranked_docs', []))
        print(f"Documents: {raw_docs} → {reranked_docs} (after reranking)")
        
        # Response
        response = result.get('generated_response', 'No response generated')
        print(f"\n💬 RESPONSE:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        # Errors
        errors = result.get('errors', [])
        if errors:
            print(f"\n❌ ERRORS:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("\n✅ No errors!")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_step_by_step():
    """Test each node individually for debugging"""
    
    try:
        print("🔍 Testing individual nodes...")
        
        # Import components
        from backend.agent.graph.state import create_initial_state
        from backend.agent.graph.nodes.planner import planner_node
        from backend.agent.graph.nodes.retriever import retriever_node
        from backend.agent.graph.nodes.synthesizer import synthesizer_node
        
        query = "What is Munger's inversion principle?"
        print(f"📝 Query: {query}")
        
        # Create initial state
        state = create_initial_state(query)
        
        # Test Planner
        print("\n1️⃣ Testing Planner...")
        state = planner_node(state)
        print(f"   ✅ Planner: {state.get('query_type')} ({state.get('query_complexity')})")
        
        # Test Retriever
        print("\n2️⃣ Testing Retriever...")
        state = retriever_node(state)
        print(f"   ✅ Retriever: {len(state.get('reranked_docs', []))} documents")
        
        # Test Synthesizer
        print("\n3️⃣ Testing Synthesizer...")
        state = synthesizer_node(state)
        response = state.get('generated_response', '')
        print(f"   ✅ Synthesizer: {len(response.split())} words generated")
        
        print(f"\n💬 FINAL RESPONSE:")
        print(response[:200] + "..." if len(response) > 200 else response)
        
        return state
        
    except Exception as e:
        print(f"❌ Step-by-step test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🎯 Choose test mode:")
    print("1. Simple workflow test")
    print("2. Step-by-step node testing")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        result = test_step_by_step()
    else:
        result = test_simple_query()
    
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")