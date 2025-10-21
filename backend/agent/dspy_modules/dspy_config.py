"""
DSPy Configuration using existing LLMClient
Simple integration that wraps our OpenAI client for DSPy usage
"""

import os
from typing import List, Dict, Any, Optional
from backend.agent.llm.client import LLMClient

# Try to import DSPy, fallback gracefully if not available
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None


if DSPY_AVAILABLE:
    class DSPyLLMAdapter(dspy.LM):
        """Adapter to make our LLMClient compatible with DSPy"""
        
        def __init__(self, llm_client: LLMClient, model: str = "gpt-4-turbo-preview"):
            super().__init__(model=model)
            self.provider = "custom"
            self.history = []
            self.llm_client = llm_client
        
        def basic_request(self, prompt: str, **kwargs) -> str:
            """Handle communication with our LLMClient"""
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.get_response(messages)
                
                # Store in history for DSPy tracking
                self.history.append({
                    "prompt": prompt,
                    "response": response,
                    "kwargs": kwargs,
                })
                
                return response if response else ""
            except Exception as e:
                print(f"LLM call failed: {e}")
                return ""
        
        def __call__(self, prompt: str = None, messages: List[Dict[str, str]] = None, only_completed: bool = True, return_sorted: bool = False, **kwargs) -> List[str]:
            """DSPy interface for generating completions"""
            # Handle both prompt and messages format
            if prompt is not None:
                response = self.basic_request(prompt, **kwargs)
            elif messages is not None:
                # Convert messages to a single prompt
                prompt_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
                response = self.basic_request(prompt_text, **kwargs)
            else:
                return [""]
            return [response]
        
        def generate(self, prompt: str, **kwargs) -> List[str]:
            """Alternative interface for DSPy"""
            return self(prompt, **kwargs)
else:
    # Fallback class when DSPy is not available
    class DSPyLLMAdapter:
        def __init__(self, llm_client: LLMClient):
            self.llm_client = llm_client
            self.model = "gpt-4-turbo-preview"
        
        def __call__(self, prompt: str, **kwargs) -> List[str]:
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.get_response(messages)
                return [response] if response else [""]
            except Exception as e:
                print(f"LLM call failed: {e}")
                return [""]


class DSPyConfig:
    """Centralized DSPy configuration manager"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.dspy_lm = None
        self.configured = False
        self.available = DSPY_AVAILABLE
    
    def initialize(self, enable_dspy: bool = True) -> bool:
        """Initialize DSPy with our LLM client"""
        if not enable_dspy:
            print("DSPy disabled by configuration")
            self.configured = False
            return False
            
        if not DSPY_AVAILABLE:
            print("DSPy not available - install with: pip install dspy-ai")
            return False
        
        try:
            # Create adapter for our LLM client
            self.dspy_lm = DSPyLLMAdapter(self.llm_client)
            
            # Configure DSPy to use our adapter (DSPy 3.x uses dspy.configure)
            dspy.configure(lm=self.dspy_lm)
            
            self.configured = True
            print("DSPy configured with existing LLMClient")
            return True
            
        except Exception as e:
            print(f"DSPy configuration failed: {e}")
            self.configured = False
            return False
    
    def is_ready(self) -> bool:
        """Check if DSPy is ready to use"""
        return self.available and self.configured
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        return {
            "available": self.available,
            "configured": self.configured,
            "ready": self.is_ready(),
            "adapter_type": "LLMClient" if self.configured else None
        }


# Global DSPy configuration instance
dspy_config = DSPyConfig()


def initialize_dspy(enable_dspy: bool = True) -> bool:
    """Initialize DSPy system"""
    return dspy_config.initialize(enable_dspy)


def is_dspy_ready() -> bool:
    """Check if DSPy is ready to use"""
    return dspy_config.is_ready()


def get_dspy_status() -> Dict[str, Any]:
    """Get DSPy status"""
    return dspy_config.get_status()
