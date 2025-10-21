"""
Verifier Node for Charlie Munger RAG Agent
Validates response quality and determines if retry is needed
"""

import time
import re
from typing import Dict, List, Any, Literal
from backend.agent.graph.state import MungerState, add_execution_trace, add_error, add_warning, can_retry
from backend.agent.llm.client import LLMClient
from backend.app.dependencies import dspy_manager


class ResponseVerifier:
    """Validates response quality and factual accuracy"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        
        # Quality criteria for Munger-style responses
        self.quality_criteria = {
            "factual_accuracy": {
                "weight": 0.3,
                "description": "Response is factually accurate and grounded in Munger's actual views"
            },
            "style_consistency": {
                "weight": 0.25,
                "description": "Response matches Munger's communication style"
            },
            "completeness": {
                "weight": 0.2,
                "description": "Response adequately addresses the user's question"
            },
            "practical_value": {
                "weight": 0.15,
                "description": "Response provides actionable insights"
            },
            "mental_model_application": {
                "weight": 0.1,
                "description": "Response appropriately applies relevant mental models"
            }
        }
    
    def check_factual_accuracy(self, response: str, context: str) -> Dict[str, Any]:
        """Check if response is factually accurate using LLM"""
        try:
            accuracy_prompt = f"""
            Evaluate the factual accuracy of this response about Charlie Munger's views and principles.
            
            RESPONSE TO EVALUATE:
            {response}
            
            SOURCE CONTEXT:
            {context[:1000]}...
            
            Rate the factual accuracy on a scale of 0-10, where:
            - 10: Completely accurate and well-grounded in Munger's actual views
            - 7-9: Mostly accurate with minor inaccuracies
            - 4-6: Somewhat accurate but with notable issues
            - 1-3: Mostly inaccurate or speculative
            - 0: Completely inaccurate or fabricated
            
            Provide your rating and a brief explanation.
            Format: RATING: X/10 | EXPLANATION: [your explanation]
            """
            
            llm_response = self.llm_client.get_response([
                {"role": "user", "content": accuracy_prompt}
            ])
            
            # Parse rating from response
            rating_match = re.search(r'RATING:\s*(\d+)/10', llm_response)
            rating = int(rating_match.group(1)) if rating_match else 5
            
            explanation_match = re.search(r'EXPLANATION:\s*(.+)', llm_response)
            explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided"
            
            return {
                "score": rating / 10.0,
                "explanation": explanation,
                "raw_response": llm_response
            }
            
        except Exception as e:
            return {
                "score": 0.5,  # Default neutral score
                "explanation": f"Accuracy check failed: {str(e)}",
                "raw_response": ""
            }
    
    def check_style_consistency(self, response: str) -> Dict[str, Any]:
        """Check if response matches Munger's communication style"""
        style_indicators = {
            "direct_language": ["direct", "straightforward", "clear"],
            "practical_focus": ["practical", "actionable", "useful"],
            "humility": ["uncertain", "complex", "difficult", "don't know"],
            "analogies": ["like", "similar to", "analogous", "example"],
            "multidisciplinary": ["psychology", "economics", "business", "science"]
        }
        
        response_lower = response.lower()
        style_scores = {}
        
        for style, keywords in style_indicators.items():
            score = sum(1 for keyword in keywords if keyword in response_lower)
            style_scores[style] = min(1.0, score / 3.0)  # Normalize to 0-1
        
        # Check for Munger-specific phrases
        munger_phrases = [
            "circle of competence", "mental models", "inversion", "base rates",
            "second order thinking", "confirmation bias", "opportunity cost"
        ]
        
        munger_score = sum(1 for phrase in munger_phrases if phrase in response_lower)
        munger_score = min(1.0, munger_score / 2.0)  # Normalize
        
        overall_score = (sum(style_scores.values()) + munger_score) / (len(style_scores) + 1)
        
        return {
            "score": overall_score,
            "style_breakdown": style_scores,
            "munger_phrases_found": munger_score
        }
    
    def check_completeness(self, response: str, query: str) -> Dict[str, Any]:
        """Check if response adequately addresses the user's question"""
        try:
            completeness_prompt = f"""
            Evaluate how well this response addresses the user's question.
            
            USER QUESTION:
            {query}
            
            RESPONSE:
            {response}
            
            Rate completeness on a scale of 0-10, where:
            - 10: Completely addresses all aspects of the question
            - 7-9: Addresses most aspects with minor gaps
            - 4-6: Addresses some aspects but misses important parts
            - 1-3: Barely addresses the question
            - 0: Doesn't address the question at all
            
            Provide your rating and identify any gaps.
            Format: RATING: X/10 | GAPS: [any gaps you identified]
            """
            
            llm_response = self.llm_client.get_response([
                {"role": "user", "content": completeness_prompt}
            ])
            
            # Parse rating
            rating_match = re.search(r'RATING:\s*(\d+)/10', llm_response)
            rating = int(rating_match.group(1)) if rating_match else 5
            
            gaps_match = re.search(r'GAPS:\s*(.+)', llm_response)
            gaps = gaps_match.group(1).strip() if gaps_match else "No gaps identified"
            
            return {
                "score": rating / 10.0,
                "gaps": gaps,
                "raw_response": llm_response
            }
            
        except Exception as e:
            return {
                "score": 0.5,
                "gaps": f"Completeness check failed: {str(e)}",
                "raw_response": ""
            }
    
    def check_practical_value(self, response: str) -> Dict[str, Any]:
        """Check if response provides actionable insights"""
        practical_indicators = [
            "should", "recommend", "suggest", "consider", "avoid", "focus on",
            "steps", "process", "framework", "checklist", "guidelines"
        ]
        
        response_lower = response.lower()
        practical_count = sum(1 for indicator in practical_indicators if indicator in response_lower)
        
        # Check for specific actionable language
        actionable_patterns = [
            r"you should", r"it's important to", r"make sure to", r"be careful",
            r"the key is", r"focus on", r"avoid", r"consider"
        ]
        
        actionable_count = sum(1 for pattern in actionable_patterns if re.search(pattern, response_lower))
        
        # Calculate score
        score = min(1.0, (practical_count + actionable_count) / 5.0)
        
        return {
            "score": score,
            "practical_indicators": practical_count,
            "actionable_patterns": actionable_count
        }
    
    def check_mental_model_application(self, response: str, applicable_models: List[str]) -> Dict[str, Any]:
        """Check if response appropriately applies mental models"""
        if not applicable_models:
            return {"score": 1.0, "models_applied": [], "explanation": "No mental models required"}
        
        response_lower = response.lower()
        models_applied = []
        
        for model in applicable_models:
            if model in response_lower:
                models_applied.append(model)
        
        # Calculate score based on how many models were applied
        application_score = len(models_applied) / len(applicable_models)
        
        return {
            "score": application_score,
            "models_applied": models_applied,
            "models_missing": [model for model in applicable_models if model not in models_applied]
        }
    
    def calculate_overall_quality(self, verification_results: Dict[str, Any]) -> float:
        """Calculate overall quality score from verification results"""
        total_score = 0
        total_weight = 0
        
        for criterion, weight_info in self.quality_criteria.items():
            if criterion in verification_results:
                score = verification_results[criterion]["score"]
                weight = weight_info["weight"]
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5


def verifier_node(state: MungerState) -> MungerState:
    """
    Main verifier node that validates response quality and determines next steps
    Enhanced with DSPy intelligence while maintaining fallback compatibility
    """
    start_time = time.time()
    
    try:
        response = state.get("generated_response", "")
        query = state["user_query"]
        context = "\n".join([doc.page_content for doc in state.get("reranked_docs", [])[:3]])
        query_type = state.get("query_type", "general")
        
        if not response:
            add_error(state, "No response to verify", "verifier")
            state["current_step"] = "verification_failed"
            return state
        
        print("Verifying response quality...")
        
        # Try DSPy-enhanced verification first
        try:
            dspy_verification = dspy_manager.verify_response(
                query, response, context, query_type
            )
            
            if dspy_verification.get("success", False) and dspy_verification.get("method") == "dspy":
                # Use DSPy results
                overall_quality = dspy_verification.get("overall_quality_score", 0.5)
                quality_level = dspy_verification.get("quality_level", "unknown")
                verification_method = "dspy"
                
                # Map DSPy quality levels to steps
                if quality_level == "high_quality":
                    state["current_step"] = "verified_high_quality"
                    print(f"Verification (DSPy): High quality response (score: {overall_quality:.3f})")
                elif quality_level == "medium_quality":
                    state["current_step"] = "verified_acceptable"
                    print(f"Verification (DSPy): Acceptable response (score: {overall_quality:.3f})")
                else:
                    state["current_step"] = "verified_poor_quality"
                    print(f"Verification (DSPy): Poor quality response (score: {overall_quality:.3f})")
                
                # Store DSPy verification results
                state["verification_suggestions"] = dspy_verification.get("suggestions", "")
                
            else:
                raise Exception("DSPy verification not available, using fallback")
                
        except Exception as dspy_error:
            # Fallback to original comprehensive verification
            verifier = ResponseVerifier()
            applicable_models = state.get("applicable_mental_models", [])
            
            # Run all verification checks
            verification_results = {}
            
            # Factual accuracy
            accuracy_result = verifier.check_factual_accuracy(response, context)
            verification_results["factual_accuracy"] = accuracy_result
            
            # Style consistency
            style_result = verifier.check_style_consistency(response)
            verification_results["style_consistency"] = style_result
            
            # Completeness
            completeness_result = verifier.check_completeness(response, query)
            verification_results["completeness"] = completeness_result
            
            # Practical value
            practical_result = verifier.check_practical_value(response)
            verification_results["practical_value"] = practical_result
            
            # Mental model application
            model_result = verifier.check_mental_model_application(response, applicable_models)
            verification_results["mental_model_application"] = model_result
            
            # Calculate overall quality
            overall_quality = verifier.calculate_overall_quality(verification_results)
            verification_method = "fallback"
            
            # Store individual scores
            state["factual_accuracy_score"] = accuracy_result["score"]
            state["style_consistency_score"] = style_result["score"]
            state["completeness_score"] = completeness_result["score"]
            state["practical_value_score"] = practical_result["score"]
            state["mental_model_application_score"] = model_result["score"]
            
            # Determine next action based on quality
            if overall_quality >= 0.7:
                state["current_step"] = "verified_high_quality"
                print(f"Verification (Fallback): High quality response (score: {overall_quality:.3f})")
            elif overall_quality >= 0.5:
                state["current_step"] = "verified_acceptable"
                print(f"Verification (Fallback): Acceptable response (score: {overall_quality:.3f})")
            else:
                state["current_step"] = "verified_poor_quality"
                print(f"Verification (Fallback): Poor quality response (score: {overall_quality:.3f})")
        
        # Common processing for both paths
        state["response_quality_score"] = overall_quality
        state["verification_method"] = verification_method
        
        # Add execution trace
        duration = time.time() - start_time
        add_execution_trace(state, "verifier", {
            "timestamp": start_time,
            "duration": duration,
            "overall_quality": overall_quality,
            "method": verification_method
        })
        
    except Exception as e:
        error_msg = f"Verification failed: {str(e)}"
        add_error(state, error_msg, "verifier")
        state["current_step"] = "verification_failed"
        print(f"Verifier error: {error_msg}")
    
    return state


def should_retry(state: MungerState) -> Literal["retry", "end", "escalate"]:
    """Determine if retry is needed based on verification results"""
    quality_score = state.get("response_quality_score", 0)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    
    # If quality is very poor and we can retry
    if quality_score < 0.4 and retry_count < max_retries:
        return "retry"
    
    # If quality is poor but we've exhausted retries
    if quality_score < 0.4 and retry_count >= max_retries:
        return "escalate"
    
    # If quality is acceptable or good
    return "end"


def get_verification_summary(state: MungerState) -> Dict[str, Any]:
    """Get summary of verification results"""
    return {
        "overall_quality": state.get("response_quality_score", 0),
        "factual_accuracy": state.get("factual_accuracy_score", 0),
        "style_consistency": state.get("style_consistency_score", 0),
        "retry_count": state.get("retry_count", 0),
        "current_step": state.get("current_step", "unknown"),
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", [])
    }


def get_improvement_suggestions(state: MungerState) -> List[str]:
    """Get suggestions for improving response quality"""
    suggestions = []
    quality_score = state.get("response_quality_score", 0)
    
    if quality_score < 0.7:
        suggestions.append("Response quality could be improved")
    
    if state.get("factual_accuracy_score", 0) < 0.7:
        suggestions.append("Improve factual accuracy and grounding")
    
    if state.get("style_consistency_score", 0) < 0.7:
        suggestions.append("Better align with Munger's communication style")
    
    return suggestions
