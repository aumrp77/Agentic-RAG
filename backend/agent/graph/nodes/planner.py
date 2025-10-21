"""
Planner Node for Charlie Munger RAG Agent
Analyzes user queries and determines optimal strategy for response generation
"""

import re
import time
from typing import Dict, Any
from backend.agent.graph.state import MungerState, add_execution_trace, add_warning
from backend.agent.llm.client import LLMClient
from backend.app.dependencies import dspy_manager


class QueryPlanner:
    """Advanced query analysis and planning for Munger-style responses"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        
        # Mental models keywords for detection
        self.mental_model_keywords = {
            "inversion": ["inversion", "invert", "opposite", "reverse thinking"],
            "base_rates": ["base rate", "statistical", "probability", "odds"],
            "opportunity_cost": ["opportunity cost", "trade-off", "alternative"],
            "second_order_thinking": ["second order", "consequence", "unintended"],
            "circle_of_competence": ["competence", "expertise", "knowledge"],
            "confirmation_bias": ["bias", "confirmation", "prejudice"],
            "anchoring": ["anchor", "reference point", "starting point"],
            "availability_heuristic": ["availability", "recency", "salient"],
            "representativeness": ["representative", "typical", "stereotype"]
        }
        
        # Query type patterns
        self.query_patterns = {
            "quote": [
                r"what did.*munger.*say",
                r"quote.*munger",
                r"munger.*said",
                r"munger.*quote",
                r"exact words"
            ],
            "explanation": [
                r"explain.*munger",
                r"how does.*munger.*think",
                r"what is.*principle",
                r"why.*munger"
            ],
            "mental_model": [
                r"mental model",
                r"inversion",
                r"base rate",
                r"opportunity cost",
                r"second order",
                r"framework"
            ],
            "story": [
                r"story.*munger",
                r"example.*munger",
                r"munger.*experience",
                r"munger.*case"
            ],
            "decision_framework": [
                r"how.*decide",
                r"decision.*process",
                r"framework.*decision",
                r"approach.*problem"
            ]
        }

    def analyze_query_complexity(self, query: str) -> str:
        """Determine query complexity based on linguistic features"""
        # Simple heuristics for complexity
        word_count = len(query.split())
        question_count = query.count('?')
        conjunction_count = len(re.findall(r'\b(and|or|but|however|although)\b', query.lower()))
        
        # Complex indicators
        complex_indicators = [
            "multiple", "several", "compare", "contrast", "relationship",
            "framework", "system", "process", "methodology"
        ]
        
        has_complex_indicators = any(indicator in query.lower() for indicator in complex_indicators)
        
        if word_count > 20 or question_count > 2 or conjunction_count > 2 or has_complex_indicators:
            return "complex"
        elif word_count > 10 or question_count > 1:
            return "moderate"
        else:
            return "simple"

    def detect_mental_models(self, query: str) -> list[str]:
        """Detect mental models mentioned or implied in the query"""
        detected_models = []
        query_lower = query.lower()
        
        for model, keywords in self.mental_model_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_models.append(model)
        
        return detected_models


    def classify_query_type(self, query: str) -> str:
        """Classify query type using pattern matching and LLM analysis"""
        query_lower = query.lower()
        
        # Pattern-based classification
        for query_type, patterns in self.query_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                return query_type
        
        # Fallback to LLM classification for ambiguous cases
        try:
            classification_prompt = f"""
            Analyze this query about Charlie Munger and classify it into one of these categories:
            - quote: User wants a direct quote or exact words from Munger
            - explanation: User wants explanation of Munger's thinking or principles
            - mental_model: User asks about specific mental models or frameworks
            - story: User wants examples, stories, or case studies
            - decision_framework: User wants guidance on decision-making process
            - general: General question about Munger's wisdom or philosophy
            
            Query: "{query}"
            
            Respond with only the category name.
            """
            
            response = self.llm_client.get_response([
                {"role": "user", "content": classification_prompt}
            ])
            
            category = response.strip().lower()
            if category in ["quote", "explanation", "mental_model", "story", "decision_framework", "general"]:
                return category
                
        except Exception as e:
            print(f"LLM classification failed: {e}")
        
        return "general"

    def determine_retrieval_strategy(self, query_type: str, complexity: str) -> Dict[str, Any]:
        """Determine optimal retrieval strategy based on query analysis"""
        strategies = {
            "quote": {
                "retrieval_count": 10,  # Reduced for faster response
                "rerank_count": 4,
                "focus": "exact_quotes",
                "prefer_sources": ["speeches", "interviews", "meetings"]
            },
            "explanation": {
                "retrieval_count": 12,  # Reduced for faster response
                "rerank_count": 5,
                "focus": "conceptual_content",
                "prefer_sources": ["books", "essays", "speeches"]
            },
            "mental_model": {
                "retrieval_count": 15,  # Reduced for faster response
                "rerank_count": 6,
                "focus": "framework_content",
                "prefer_sources": ["books", "speeches", "interviews"]
            },
            "story": {
                "retrieval_count": 12,  # Reduced for faster response
                "rerank_count": 4,
                "focus": "narrative_content",
                "prefer_sources": ["speeches", "interviews", "meetings"]
            },
            "decision_framework": {
                "retrieval_count": 18,  # Reduced for faster response
                "rerank_count": 7,
                "focus": "process_content",
                "prefer_sources": ["books", "speeches", "essays"]
            },
            "general": {
                "retrieval_count": 12,  # Reduced for faster response
                "rerank_count": 5,
                "focus": "balanced_content",
                "prefer_sources": ["all"]
            }
        }
        
        base_strategy = strategies.get(query_type, strategies["general"])
        
        # Adjust for complexity
        if complexity == "complex":
            base_strategy["retrieval_count"] = int(base_strategy["retrieval_count"] * 1.5)
            base_strategy["rerank_count"] = int(base_strategy["rerank_count"] * 1.2)
        
        return base_strategy

    def extract_query_intent(self, query: str) -> str:
        """Extract the core intent behind the query using LLM"""
        try:
            intent_prompt = f"""
            Extract the core intent from this query about Charlie Munger. 
            Focus on what the user really wants to know or understand.
            
            Query: "{query}"
            
            Provide a concise 1-2 sentence summary of the user's intent.
            """
            
            response = self.llm_client.get_response([
                {"role": "user", "content": intent_prompt}
            ])
            
            return response.strip()
            
        except Exception as e:
            print(f"Intent extraction failed: {e}")
            return f"Understand Munger's perspective on: {query}"


def planner_node(state: MungerState) -> MungerState:
    """
    Main planner node that analyzes the query and sets up the workflow strategy
    Enhanced with DSPy intelligence while maintaining fallback compatibility
    """
    start_time = time.time()
    
    try:
        query = state["user_query"]
        context = state.get("context", "")
        
        # Try DSPy-enhanced planning first
        try:
            dspy_analysis = dspy_manager.analyze_query(query, context)
            
            if dspy_analysis.get("success", False) and dspy_analysis.get("method") == "dspy":
                # Use DSPy results
                complexity = dspy_analysis.get("complexity", "moderate")
                query_type = dspy_analysis.get("query_type", "general")
                mental_models = dspy_analysis.get("mental_models", [])
                planning_method = "dspy"
                
                print(f"Planner (DSPy): {query_type} query ({complexity} complexity) - {len(mental_models)} mental models detected")
                
            else:
                raise Exception("DSPy analysis not available, using fallback")
                
        except Exception as dspy_error:
            # Fallback to original rule-based planning
            planner = QueryPlanner()
            complexity = planner.analyze_query_complexity(query)
            query_type = planner.classify_query_type(query)
            mental_models = planner.detect_mental_models(query)
            planning_method = "fallback"
            
            print(f"Planner (Fallback): {query_type} query ({complexity} complexity) - {len(mental_models)} mental models detected")
        
        # Extract intent and strategy (common to both paths)
        planner = QueryPlanner()  # Use for utility methods
        intent = planner.extract_query_intent(query)
        strategy = planner.determine_retrieval_strategy(query_type, complexity)
        
        # Update state with analysis results
        state["query_complexity"] = complexity
        state["query_type"] = query_type
        state["identified_mental_models"] = mental_models
        state["query_intent"] = intent
        state["retrieval_strategy"] = strategy
        state["planning_method"] = planning_method
        state["current_step"] = "planned"
        
        # Add execution trace
        duration = time.time() - start_time
        add_execution_trace(state, "planner", {
            "timestamp": start_time,
            "duration": duration,
            "complexity": complexity,
            "query_type": query_type,
            "mental_models_found": len(mental_models),
            "strategy": strategy,
            "method": planning_method
        })
        
    except Exception as e:
        error_msg = f"Planning failed: {str(e)}"
        state["errors"].append(error_msg)
        state["current_step"] = "planning_failed"
        print(f"Planner error: {error_msg}")
    
    return state


def should_use_mental_models(state: MungerState) -> bool:
    """Determine if mental model analysis should be performed"""
    return (
        state.get("query_type") in ["mental_model", "decision_framework", "general"] or
        len(state.get("identified_mental_models", [])) > 0
    )


def get_retrieval_params(state: MungerState) -> Dict[str, Any]:
    """Get retrieval parameters based on planning results"""
    strategy = state.get("retrieval_strategy", {})
    return {
        "k": strategy.get("retrieval_count", 20),
        "final_k": strategy.get("rerank_count", 8),
        "focus": strategy.get("focus", "balanced_content"),
        "prefer_sources": strategy.get("prefer_sources", ["all"])
    }
