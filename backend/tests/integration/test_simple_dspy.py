#!/usr/bin/env python3
"""
Simple test for the streamlined DSPy integration
Tests the configuration and basic functionality
"""

import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def test_dspy_installation():
    """Test if DSPy is installed and working"""
    print("=" * 60)
    print("Testing DSPy Installation")
    print("=" * 60)
    
    try:
        import dspy
        print(f"✅ DSPy imported successfully")
        print(f"DSPy version: {dspy.__version__}")
        return True
    except ImportError as e:
        print(f"❌ DSPy not installed: {e}")
        print("Install with: pip install dspy-ai")
        return False
    except Exception as e:
        print(f"❌ DSPy import error: {e}")
        return False


def test_llm_client():
    """Test our LLM client"""
    print("\n" + "=" * 60)
    print("Testing LLM Client")
    print("=" * 60)
    
    try:
        from backend.agent.llm.client import LLMClient
        client = LLMClient()
        print("✅ LLMClient created successfully")
        
        # Test a simple call
        messages = [{"role": "user", "content": "Say 'Hello DSPy test'"}]
        response = client.get_response(messages)
        
        if response:
            print(f"✅ LLM response: {response[:50]}...")
            return True
        else:
            print("❌ No response from LLM")
            return False
            
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False


def test_dspy_config():
    """Test DSPy configuration with our LLM client"""
    print("\n" + "=" * 60)
    print("Testing DSPy Configuration")
    print("=" * 60)
    
    try:
        from backend.agent.dspy_modules.dspy_config import dspy_config, initialize_dspy, get_dspy_status
        
        # Check initial status
        status = get_dspy_status()
        print(f"Initial DSPy available: {status['available']}")
        print(f"Initial DSPy configured: {status['configured']}")
        
        # Initialize DSPy
        success = initialize_dspy()
        print(f"DSPy initialization: {'✅ Success' if success else '❌ Failed'}")
        
        # Check final status
        final_status = get_dspy_status()
        print(f"Final DSPy status: {final_status}")
        
        return success
        
    except Exception as e:
        print(f"❌ DSPy config test failed: {e}")
        return False


def test_dspy_modules():
    """Test the simple DSPy modules"""
    print("\n" + "=" * 60)
    print("Testing DSPy Modules")
    print("=" * 60)
    
    try:
        from backend.agent.dspy_modules.simple_modules import (
            create_dspy_planner, 
            create_dspy_synthesizer, 
            create_dspy_verifier
        )
        
        # Create modules
        planner = create_dspy_planner()
        synthesizer = create_dspy_synthesizer()
        verifier = create_dspy_verifier()
        
        print("✅ All modules created successfully")
        
        # Test planner
        query = "What is inversion?"
        analysis = planner.analyze_query(query)
        print(f"✅ Planner analysis: {analysis['method']} - {analysis['query_type']}")
        
        # Test synthesizer
        response_data = synthesizer.generate_response(
            query, 
            "Context about inversion principle", 
            "inversion", 
            "mental_model"
        )
        print(f"✅ Synthesizer: {response_data['method']} - {len(response_data['response'].split())} words")
        
        # Test verifier
        verification = verifier.verify_response(
            query, 
            response_data['response'], 
            "Context about inversion"
        )
        print(f"✅ Verifier: {verification['method']} - {verification['quality_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies_integration():
    """Test the full dependencies integration"""
    print("\n" + "=" * 60)
    print("Testing Dependencies Integration")
    print("=" * 60)
    
    try:
        from backend.app.dependencies import (
            initialize_dependencies, 
            dspy_manager, 
            get_dependencies_status
        )
        
        # Initialize dependencies
        results = initialize_dependencies()
        print(f"Vector store: {'✅' if results['vector_store'] else '❌'}")
        print(f"DSPy system: {'✅' if results['dspy'] else '❌'}")
        
        # Test DSPy manager methods
        test_query = "What did Munger say about compound interest?"
        
        analysis = dspy_manager.analyze_query(test_query)
        print(f"Query analysis: {analysis['method']} - {analysis.get('query_type', 'unknown')}")
        
        response = dspy_manager.generate_response(
            test_query, 
            "Compound interest context", 
            "compound_interest"
        )
        print(f"Response generation: {response['method']} - {response.get('success', False)}")
        
        verification = dspy_manager.verify_response(
            test_query, 
            response.get('response', 'test response'), 
            "context"
        )
        print(f"Response verification: {verification['method']} - {verification.get('success', False)}")
        
        # Get detailed status
        status = get_dependencies_status()
        print(f"\nFinal system status:")
        print(f"  Vector store initialized: {status['vector_store']['initialized']}")
        print(f"  DSPy available: {status['dspy']['available']}")
        print(f"  DSPy configured: {status['dspy']['configured']}")
        print(f"  DSPy modules loaded: {status['dspy']['modules_loaded']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependencies integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Simple DSPy Integration Test")
    print("=" * 80)
    
    start_time = time.time()
    
    tests = [
        ("DSPy Installation", test_dspy_installation),
        ("LLM Client", test_llm_client),
        ("DSPy Configuration", test_dspy_config),
        ("DSPy Modules", test_dspy_modules),
        ("Dependencies Integration", test_dependencies_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"Test Summary (completed in {total_time:.2f}s)")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if not overall_success:
        print("\nTroubleshooting:")
        if not results.get("DSPy Installation", True):
            print("  - Install DSPy: pip install dspy-ai")
        if not results.get("LLM Client", True):
            print("  - Check OpenAI API key: echo $OPENAI_API_KEY")
        print("  - Check the error messages above for specific issues")


if __name__ == "__main__":
    main()
