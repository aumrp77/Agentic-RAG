"""
Synthesizer Node for Charlie Munger RAG Agent
Generates Munger-style responses using retrieved context and mental models
"""

import time
from typing import Dict, List, Any
from backend.agent.graph.state import MungerState, add_execution_trace, add_error, get_context_for_synthesis, get_mental_models_context
from backend.agent.llm.client import LLMClient
from backend.app.dependencies import dspy_manager


class MungerSynthesizer:
    """Generates responses in Charlie Munger's characteristic style"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        
        # Munger's communication style characteristics
        self.style_guidelines = {
            "directness": "Be direct and straightforward, avoid jargon",
            "practicality": "Focus on practical wisdom and actionable insights",
            "analogies": "Use clear analogies and examples from everyday life",
            "humility": "Show intellectual humility and acknowledge uncertainty",
            "multidisciplinary": "Draw connections across different fields",
            "simplicity": "Explain complex ideas in simple terms",
            "honesty": "Be brutally honest about limitations and failures"
        }
    
    def build_context_prompt(self, state: MungerState) -> str:
        """Build comprehensive context prompt for response generation"""
        query = state["user_query"]
        query_type = state.get("query_type", "general")
        
        # Get context from retrieved documents
        context = get_context_for_synthesis(state, max_docs=3)
        
        # Get mental models context
        mental_models_context = get_mental_models_context(state)
        
        # Build base prompt
        prompt_parts = [
            "You are Charlie Munger. Answer this question in your characteristic style:",
            "",
            f"QUESTION: {query}",
            "",
            "RELEVANT INFORMATION:",
            context,
            ""
        ]
        
        # Add mental models context if available
        if mental_models_context:
            prompt_parts.extend([
                mental_models_context,
                ""
            ])
        
        # Add style-specific instructions
        prompt_parts.extend(self._get_style_instructions(query_type))
        
        return "\n".join(prompt_parts)
    
    def _get_style_instructions(self, query_type: str) -> List[str]:
        """Get style-specific instructions based on query type"""
        base_instructions = [
            "STYLE REQUIREMENTS:",
            "- Use clear, direct language without unnecessary complexity",
            "- Be practical and focus on actionable wisdom",
            "- Include specific examples or analogies when helpful",
            "- Show intellectual humility and acknowledge what you don't know",
            "- Draw connections across different fields when relevant",
            "- Be brutally honest about limitations and potential failures",
            ""
        ]
        
        type_specific = {
            "quote": [
                "QUOTE-SPECIFIC INSTRUCTIONS:",
                "- If the user wants a direct quote, provide the exact words",
                "- If no exact quote exists, explain what Munger would likely say",
                "- Always provide context for any quotes you give",
                ""
            ],
            "explanation": [
                "EXPLANATION-SPECIFIC INSTRUCTIONS:",
                "- Break down complex concepts into understandable parts",
                "- Use analogies to make abstract ideas concrete",
                "- Explain the 'why' behind principles, not just the 'what'",
                ""
            ],
            "mental_model": [
                "MENTAL MODEL-SPECIFIC INSTRUCTIONS:",
                "- Clearly explain the mental model and its purpose",
                "- Provide concrete examples of how to apply it",
                "- Show how it connects to other mental models",
                "- Give practical steps for implementation",
                ""
            ],
            "story": [
                "STORY-SPECIFIC INSTRUCTIONS:",
                "- Use specific examples and case studies",
                "- Make stories relatable and memorable",
                "- Extract the key lesson from each story",
                "- Connect stories to broader principles",
                ""
            ],
            "decision_framework": [
                "DECISION FRAMEWORK-SPECIFIC INSTRUCTIONS:",
                "- Provide a clear step-by-step process",
                "- Include checklists or decision trees when helpful",
                "- Address common biases and how to avoid them",
                "- Give practical tools for implementation",
                ""
            ]
        }
        
        instructions = base_instructions.copy()
        if query_type in type_specific:
            instructions.extend(type_specific[query_type])
        
        instructions.extend([
            "RESPONSE FORMAT:",
            "- Start with a direct answer to the question",
            "- Provide supporting reasoning and examples",
            "- Include relevant mental models or frameworks",
            "- End with practical takeaways or next steps",
            ""
        ])
        
        return instructions
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using LLM"""
        try:
            response = self.llm_client.get_response([
                {"role": "user", "content": prompt}
            ])
            return response.strip()
        except Exception as e:
            raise Exception(f"Response generation failed: {str(e)}")
    
    def calculate_confidence_score(self, response: str, context: str) -> float:
        """Calculate confidence score for the generated response"""
        # Simple heuristics for confidence scoring
        score_factors = []
        
        # Length factor (too short or too long reduces confidence)
        word_count = len(response.split())
        if 50 <= word_count <= 500:
            score_factors.append(1.0)
        elif word_count < 50:
            score_factors.append(0.5)
        else:
            score_factors.append(0.8)
        
        # Uncertainty indicators (reduce confidence)
        uncertainty_words = ["maybe", "perhaps", "might", "could", "possibly", "unclear"]
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        uncertainty_factor = max(0.3, 1.0 - (uncertainty_count * 0.1))
        score_factors.append(uncertainty_factor)
        
        # Specificity indicators (increase confidence)
        specificity_words = ["specifically", "exactly", "precisely", "definitely", "certainly"]
        specificity_count = sum(1 for word in specificity_words if word in response.lower())
        specificity_factor = min(1.0, 0.7 + (specificity_count * 0.1))
        score_factors.append(specificity_factor)
        
        # Context utilization (check if response uses the provided context)
        context_words = set(context.lower().split())
        response_words = set(response.lower().split())
        overlap = len(context_words.intersection(response_words))
        context_factor = min(1.0, overlap / 20.0)  # Normalize
        score_factors.append(context_factor)
        
        # Calculate final confidence score
        confidence = sum(score_factors) / len(score_factors)
        return min(1.0, max(0.0, confidence))
    
    def extract_sources(self, state: MungerState) -> List[str]:
        """Extract source information for citations"""
        sources = []
        docs = state.get("reranked_docs", [])[:3]  # Top 3 sources
        
        for i, doc in enumerate(docs, 1):
            # Safely access metadata
            doc_metadata = doc.metadata or {}
            chunk_id = doc_metadata.get("chunk_id", f"chunk_{i}")
            parent_doc_id = doc_metadata.get("parent_doc_id", "unknown_source")
            score = doc_metadata.get("rerank_score", 0)
            
            source_info = f"Source {i}: {parent_doc_id} (Chunk {chunk_id}, Score: {score:.3f})"
            sources.append(source_info)
        
        return sources


def synthesizer_node(state: MungerState) -> MungerState:
    """
    Main synthesizer node that generates Munger-style responses
    Enhanced with DSPy intelligence while maintaining fallback compatibility
    """
    start_time = time.time()
    
    try:
        # Check if we have sufficient context
        if not state.get("reranked_docs"):
            add_error(state, "No context available for synthesis", "synthesizer")
            state["current_step"] = "synthesis_failed"
            return state
        
        print("Generating Munger-style response...")
        
        # Prepare data for both DSPy and fallback approaches
        query = state["user_query"]
        context = get_context_for_synthesis(state)
        mental_models = get_mental_models_context(state)
        query_type = state.get("query_type", "general")
        
        # Try DSPy-enhanced synthesis first
        try:
            dspy_synthesis = dspy_manager.generate_response(
                query, context, mental_models, query_type
            )
            
            if dspy_synthesis.get("success", False) and dspy_synthesis.get("method") == "dspy":
                # Use DSPy results
                response = dspy_synthesis.get("response", "")
                confidence = dspy_synthesis.get("confidence_score", 0.85)
                synthesis_method = "dspy"
                
                print(f"Synthesis (DSPy): {len(response.split())} words, confidence: {confidence:.3f}")
                
            else:
                raise Exception("DSPy synthesis not available, using fallback")
                
        except Exception as dspy_error:
            # Fallback to original LLM-based synthesis
            synthesizer = MungerSynthesizer()
            prompt = synthesizer.build_context_prompt(state)
            response = synthesizer.generate_response(prompt)
            confidence = synthesizer.calculate_confidence_score(response, context)
            synthesis_method = "fallback"
            
            print(f"Synthesis (Fallback): {len(response.split())} words, confidence: {confidence:.3f}")
        
        # Common processing for both paths
        state["generated_response"] = response
        state["response_confidence"] = confidence
        state["synthesis_method"] = synthesis_method
        
        # Extract sources for citations (using original synthesizer)
        synthesizer = MungerSynthesizer()
        sources = synthesizer.extract_sources(state)
        state["sources_used"] = sources
        
        # Update state
        state["current_step"] = "synthesized"
        
        # Add execution trace
        duration = time.time() - start_time
        add_execution_trace(state, "synthesizer", {
            "timestamp": start_time,
            "duration": duration,
            "response_length": len(response.split()),
            "confidence_score": confidence,
            "sources_count": len(sources),
            "query_type": query_type,
            "method": synthesis_method
        })
        
    except Exception as e:
        error_msg = f"Synthesis failed: {str(e)}"
        add_error(state, error_msg, "synthesizer")
        state["current_step"] = "synthesis_failed"
        print(f"❌ Synthesizer error: {error_msg}")
    
    return state


def get_response_quality_indicators(state: MungerState) -> Dict[str, Any]:
    """Get quality indicators for the generated response"""
    response = state.get("generated_response", "")
    confidence = state.get("response_confidence", 0)
    
    indicators = {
        "word_count": len(response.split()),
        "confidence_score": confidence,
        "has_examples": any(word in response.lower() for word in ["example", "for instance", "such as"]),
        "has_analogies": any(word in response.lower() for word in ["like", "similar to", "analogous"]),
        "mentions_mental_models": any(model in response.lower() for model in state.get("applicable_mental_models", [])),
        "acknowledges_uncertainty": any(word in response.lower() for word in ["uncertain", "unclear", "complex"]),
        "provides_practical_advice": any(word in response.lower() for word in ["should", "recommend", "suggest", "consider"])
    }
    
    return indicators


def should_enhance_response(state: MungerState) -> bool:
    """Determine if response needs enhancement"""
    confidence = state.get("response_confidence", 0)
    word_count = len(state.get("generated_response", "").split())
    
    # Enhance if confidence is low or response is too short
    return confidence < 0.6 or word_count < 30


def get_enhancement_suggestions(state: MungerState) -> List[str]:
    """Get suggestions for response enhancement"""
    suggestions = []
    indicators = get_response_quality_indicators(state)
    
    if not indicators["has_examples"]:
        suggestions.append("Add specific examples or case studies")
    
    if not indicators["has_analogies"]:
        suggestions.append("Include analogies to make concepts clearer")
    
    if not indicators["mentions_mental_models"]:
        suggestions.append("Apply relevant mental models more explicitly")
    
    if not indicators["acknowledges_uncertainty"]:
        suggestions.append("Acknowledge limitations or uncertainties")
    
    if not indicators["provides_practical_advice"]:
        suggestions.append("Provide more actionable recommendations")
    
    return suggestions
