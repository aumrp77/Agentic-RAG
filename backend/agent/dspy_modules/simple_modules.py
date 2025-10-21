"""
Simple DSPy modules for Charlie Munger RAG Agent
Minimal implementation with fallback support
"""

from typing import Dict, Any, List
from .dspy_config import DSPY_AVAILABLE, dspy, is_dspy_ready


# DSPy Signatures (only if DSPy is available)
if DSPY_AVAILABLE:
    class RetrievalDecision(dspy.Signature):
        """Decide whether external retrieval is needed for a query for the Munger RAG Agent which is a conversational agent that answers questions based on Charlie Munger's knowledge.
        
        The RAG Agent would be like a user askign questions to Charlie Munger.
        The query is a question or request from the user.
        The conversation_context is the recent conversation history if available.
        The needs_retrieval is a boolean indicating whether external retrieval is needed.
        The reasoning is a chain-of-thought reasoning for the retrieval decision.
        The query_category is a category of the query.
        The confidence is a confidence in the decision.
        """
        query = dspy.InputField(desc="User's question or request")
        conversation_context = dspy.InputField(desc="Recent conversation history if available")
        
        needs_retrieval = dspy.OutputField(desc="Does this query need external document retrieval? Answer: yes, no, or minimal")
        reasoning = dspy.OutputField(desc="Chain-of-thought reasoning for the retrieval decision")
        query_category = dspy.OutputField(desc="Category: memory, simple_fact, conversational, munger_knowledge")
        confidence = dspy.OutputField(desc="Confidence in decision (0-10)")

    class ContextAnalyzer(dspy.Signature):
        """Analyze retrieved context for relevance and key insights"""
        query = dspy.InputField(desc="User's question")
        raw_context = dspy.InputField(desc="Raw retrieved context from documents")
        key_insights = dspy.OutputField(desc="Most relevant insights from the context")
        context_quality = dspy.OutputField(desc="Quality assessment: high, medium, low")
        missing_elements = dspy.OutputField(desc="What important information might be missing")

    class QueryAnalyzer(dspy.Signature):
        """Analyze user queries with context awareness"""
        query = dspy.InputField(desc="User's question")
        context_insights = dspy.InputField(desc="Key insights from retrieved context")
        query_type = dspy.OutputField(desc="Type: quote, explanation, mental_model, story, decision_framework, general")
        complexity = dspy.OutputField(desc="Complexity: simple, moderate, complex")
        mental_models = dspy.OutputField(desc="Relevant mental models (comma-separated)")
        context_sufficiency = dspy.OutputField(desc="Is context sufficient: yes, partial, no")

    class MungerConversationGenerator(dspy.Signature):
        """Generate responses as if you ARE Charlie Munger speaking directly to the person"""
        query = dspy.InputField(desc="The person's question to you (Charlie Munger)")
        key_insights = dspy.InputField(desc="Relevant insights from your knowledge and experiences")
        mental_models = dspy.InputField(desc="Mental models to apply")
        query_type = dspy.InputField(desc="Type of question being asked")
        
        response = dspy.OutputField(desc="""Respond as Charlie Munger speaking directly to this person. Use:
        - First person ('I think', 'In my experience', 'I've learned')
        - Direct address ('you', 'your situation')
        - Personal anecdotes and examples from your life
        - Characteristic humility ('I could be wrong', 'This is just my view')
        - Practical wisdom with specific actionable advice
        - Your signature analogies and comparisons
        - Reference to your partnership with Warren when relevant
        - Acknowledgment of complexity and nuance""")

    class ResponseRefiner(dspy.Signature):
        """Refine response to enhance Munger's conversational authenticity"""
        original_response = dspy.InputField(desc="Initial response as Munger")
        query_context = dspy.InputField(desc="Original question and context")
        
        refined_response = dspy.OutputField(desc="""Enhance the response to make it more authentically Munger:
        - Add more personal touches and direct engagement
        - Include characteristic phrases
        - Ensure practical applicability
        - Add appropriate self-deprecation or humility
        - Make it feel like a genuine conversation""")

    class QualityChecker(dspy.Signature):
        """Check response quality focusing on conversational authenticity"""
        query = dspy.InputField(desc="Original question")
        response = dspy.InputField(desc="Munger's response")
        context = dspy.InputField(desc="Source context")
        
        authenticity_score = dspy.OutputField(desc="How authentic does this sound as Munger? (0-10)")
        conversational_score = dspy.OutputField(desc="How natural is the conversation? (0-10)")
        practical_value = dspy.OutputField(desc="How actionable is the advice? (0-10)")
        suggestions = dspy.OutputField(desc="Specific suggestions to improve authenticity")


class SimpleDSPyRetrievalDecider:
    """DSPy-powered intelligent retrieval decision maker"""
    
    def __init__(self):
        if DSPY_AVAILABLE and is_dspy_ready():
            self.retrieval_decider = dspy.ChainOfThought(RetrievalDecision)
            self.dspy_enabled = True
        else:
            self.dspy_enabled = False
    
    def should_retrieve(self, query: str, conversation_context: str = "") -> Dict[str, Any]:
        """Decide whether external retrieval is needed using DSPy Chain-of-Thought"""
        
        if self.dspy_enabled:
            try:
                decision = self.retrieval_decider(
                    query=query,
                    conversation_context=conversation_context or "No previous conversation"
                )
                
                # Primary DSPy result
                dspy_result = {
                    "method": "dspy",
                    "needs_retrieval": decision.needs_retrieval.lower() in ["yes", "minimal"],
                    "retrieval_level": decision.needs_retrieval.lower(),  # yes, no, minimal
                    "reasoning": decision.reasoning,
                    "query_category": decision.query_category,
                    "confidence": float(decision.confidence) / 10.0,
                    "success": True
                }
                
                # Use DSPy result if confidence is reasonable
                if dspy_result["confidence"] > 0.5:
                    return dspy_result
                
                print(f"DSPy confidence low ({dspy_result['confidence']:.2f}), using fallback")
                
            except Exception as e:
                print(f"DSPy retrieval decision failed: {e}")
        
        # Fallback to rule-based decision only if DSPy fails or has low confidence
        return self._fallback_decision(query, conversation_context)
    
    def _fallback_decision(self, query: str, conversation_context: str = "") -> Dict[str, Any]:
        """Rule-based fallback for retrieval decision"""
        query_lower = query.lower()
        
        # Memory/conversation queries - no retrieval needed
        memory_indicators = [
            "last question", "previous", "what did i ask", "earlier", "before",
            "exact question", "just asked", "what was my", "my question",
            "conversation", "memory", "history", "asked you", "you said",
            "just ask", "i ask", "did i ask", "what did i"
        ]
        
        if any(indicator in query_lower for indicator in memory_indicators):
            return {
                "method": "fallback",
                "needs_retrieval": False,
                "retrieval_level": "no",
                "reasoning": "Query is about conversation memory/history",
                "query_category": "memory",
                "confidence": 0.9,
                "success": True
            }
        
        # Simple conversational queries - minimal or no retrieval
        simple_conversational = [
            "hello", "hi", "thanks", "thank you", "bye", "goodbye",
            "how are you", "who are you", "what's your name"
        ]
        
        if any(phrase in query_lower for phrase in simple_conversational):
            return {
                "method": "fallback",
                "needs_retrieval": False,
                "retrieval_level": "no",
                "reasoning": "Simple conversational query",
                "query_category": "conversational",
                "confidence": 0.8,
                "success": True
            }
        
        # Very short queries might not need full retrieval
        if len(query.split()) <= 3:
            return {
                "method": "fallback",
                "needs_retrieval": True,
                "retrieval_level": "minimal",
                "reasoning": "Short query might need limited context",
                "query_category": "simple_fact",
                "confidence": 0.6,
                "success": True
            }
        
        # Default: assume retrieval is needed for Munger knowledge questions
        return {
            "method": "fallback",
            "needs_retrieval": True,
            "retrieval_level": "yes",
            "reasoning": "Complex query likely needs Munger knowledge retrieval",
            "query_category": "munger_knowledge",
            "confidence": 0.7,
            "success": True
        }


class SimpleDSPyPlanner:
    """Context-aware DSPy query planner with enhanced processing"""
    
    def __init__(self):
        if DSPY_AVAILABLE and is_dspy_ready():
            self.context_analyzer = dspy.ChainOfThought(ContextAnalyzer)
            self.query_analyzer = dspy.ChainOfThought(QueryAnalyzer)
            self.retrieval_decider = SimpleDSPyRetrievalDecider()
            self.dspy_enabled = True
        else:
            self.retrieval_decider = SimpleDSPyRetrievalDecider()  # Still use fallback logic
            self.dspy_enabled = False
    
    def decide_retrieval(self, query: str, conversation_context: str = "") -> Dict[str, Any]:
        """Decide whether retrieval is needed for this query"""
        return self.retrieval_decider.should_retrieve(query, conversation_context)
    
    def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Analyze query using context-aware DSPy processing or fallback"""
        if self.dspy_enabled:
            try:
                # Stage 1: Analyze context for key insights
                if context:
                    context_analysis = self.context_analyzer(
                        query=query,
                        raw_context=context
                    )
                    key_insights = context_analysis.key_insights
                    context_quality = context_analysis.context_quality
                    missing_elements = context_analysis.missing_elements
                else:
                    key_insights = "Limited context available"
                    context_quality = "low"
                    missing_elements = "Comprehensive context needed"
                
                # Stage 2: Analyze query with context insights
                query_analysis = self.query_analyzer(
                    query=query,
                    context_insights=key_insights
                )
                
                return {
                    "method": "dspy",
                    "query_type": query_analysis.query_type,
                    "complexity": query_analysis.complexity,
                    "mental_models": [model.strip() for model in query_analysis.mental_models.split(",") if model.strip()],
                    "context_quality": context_quality,
                    "context_sufficiency": query_analysis.context_sufficiency,
                    "key_insights": key_insights,
                    "missing_elements": missing_elements,
                    "success": True
                }
            except Exception as e:
                print(f"DSPy planner failed: {e}")
        
        # Fallback logic
        return self._fallback_analyze(query)
    
    def _fallback_analyze(self, query: str) -> Dict[str, Any]:
        """Simple rule-based fallback"""
        query_lower = query.lower()
        
        # Simple keyword-based classification
        if any(word in query_lower for word in ["said", "quote", "mentioned"]):
            query_type = "quote"
        elif any(word in query_lower for word in ["story", "example", "anecdote"]):
            query_type = "story"
        elif any(word in query_lower for word in ["principle", "model", "concept"]):
            query_type = "mental_model"
        elif any(word in query_lower for word in ["how", "approach", "evaluate"]):
            query_type = "decision_framework"
        else:
            query_type = "general"
        
        # Simple complexity assessment
        complexity = "complex" if len(query.split()) > 15 else "moderate" if len(query.split()) > 8 else "simple"
        
        return {
            "method": "fallback",
            "query_type": query_type,
            "complexity": complexity,
            "mental_models": [],
            "success": True
        }


class SimpleDSPySynthesizer:
    """Context-aware DSPy synthesizer for authentic Munger conversations"""
    
    def __init__(self):
        if DSPY_AVAILABLE and is_dspy_ready():
            self.context_analyzer = dspy.ChainOfThought(ContextAnalyzer)
            self.conversation_generator = dspy.ChainOfThought(MungerConversationGenerator)
            self.response_refiner = dspy.ChainOfThought(ResponseRefiner)
            self.dspy_enabled = True
        else:
            self.dspy_enabled = False
    
    def generate_response(self, query: str, context: str, mental_models: str, query_type: str = "general") -> Dict[str, Any]:
        """Generate authentic Munger conversation using context-aware processing"""
        if self.dspy_enabled:
            try:
                # Stage 1: Extract key insights from context
                context_analysis = self.context_analyzer(
                    query=query,
                    raw_context=context
                )
                key_insights = context_analysis.key_insights
                
                # Stage 2: Generate response as Munger speaking directly
                conversation_result = self.conversation_generator(
                    query=query,
                    key_insights=key_insights,
                    mental_models=mental_models,
                    query_type=query_type
                )
                
                # Stage 3: Refine for authenticity and conversational flow
                refined_result = self.response_refiner(
                    original_response=conversation_result.response,
                    query_context=f"Question: {query}\nContext Quality: {context_analysis.context_quality}"
                )
                
                # Calculate confidence based on context quality and completeness
                confidence = self._calculate_confidence(
                    context_analysis.context_quality,
                    context_analysis.missing_elements,
                    len(refined_result.refined_response.split())
                )
                
                return {
                    "method": "dspy",
                    "response": refined_result.refined_response,
                    "confidence_score": confidence,
                    "context_quality": context_analysis.context_quality,
                    "key_insights_used": key_insights,
                    "success": True
                }
            except Exception as e:
                print(f"DSPy synthesizer failed: {e}")
        
        # Fallback logic
        return self._fallback_generate(query, context, mental_models, query_type)
    
    def _calculate_confidence(self, context_quality: str, missing_elements: str, response_length: int) -> float:
        """Calculate confidence based on context quality and response completeness"""
        base_confidence = 0.85
        
        # Adjust for context quality
        if context_quality == "high":
            quality_boost = 0.1
        elif context_quality == "medium":
            quality_boost = 0.0
        else:  # low
            quality_boost = -0.15
        
        # Adjust for response completeness
        length_boost = min(0.05, (response_length - 50) / 1000)  # Bonus for detailed responses
        
        # Adjust for missing information
        missing_penalty = -0.05 if "missing" in missing_elements.lower() else 0.0
        
        final_confidence = max(0.3, min(0.95, base_confidence + quality_boost + length_boost + missing_penalty))
        return round(final_confidence, 3)
    
    def _fallback_generate(self, query: str, context: str, mental_models: str, query_type: str) -> Dict[str, Any]:
        """Fallback with authentic Munger conversational style"""
        # Create more conversational, first-person responses even in fallback
        if query_type == "quote":
            response = f"Well, you're asking about something I've talked about before. Let me share what I remember thinking about this...\n\n{context[:400]}\n\nNow, I could be wrong about the exact words, but that captures the essence of my thinking on this matter."
        elif query_type == "story":
            response = f"That's an interesting question. Let me tell you about something from my experience that might help...\n\n{context[:400]}\n\nI've learned that these kinds of examples often teach us more than abstract principles."
        elif query_type == "mental_model":
            response = f"Ah, that's one of my favorite topics. In my experience, this mental model has been incredibly useful...\n\n{context[:400]}\n\nYou know, I've found that understanding these concepts intellectually is one thing, but applying them consistently is quite another."
        else:
            response = f"That's a thoughtful question. Based on what I've learned over the years...\n\n{context[:400]}\n\nOf course, every situation is different, and you'll need to think through how this applies to your specific circumstances."
        
        return {
            "method": "fallback",
            "response": response,
            "confidence_score": 0.6,  # Lower confidence for fallback
            "context_quality": "medium",
            "success": True
        }


class SimpleDSPyVerifier:
    """Context-aware verifier focusing on conversational authenticity"""
    
    def __init__(self):
        if DSPY_AVAILABLE and is_dspy_ready():
            self.quality_checker = dspy.ChainOfThought(QualityChecker)
            self.dspy_enabled = True
        else:
            self.dspy_enabled = False
    
    def verify_response(self, query: str, response: str, context: str, query_type: str = "general") -> Dict[str, Any]:
        """Verify response quality focusing on conversational authenticity"""
        if self.dspy_enabled:
            try:
                result = self.quality_checker(
                    query=query,
                    response=response,
                    context=context
                )
                
                # Calculate composite score from multiple dimensions
                authenticity_score = float(result.authenticity_score) / 10.0
                conversational_score = float(result.conversational_score) / 10.0
                practical_score = float(result.practical_value) / 10.0
                
                # Weighted average emphasizing authenticity and conversation
                overall_score = (
                    authenticity_score * 0.4 +
                    conversational_score * 0.4 +
                    practical_score * 0.2
                )
                
                return {
                    "method": "dspy",
                    "overall_quality_score": round(overall_score, 3),
                    "authenticity_score": round(authenticity_score, 3),
                    "conversational_score": round(conversational_score, 3),
                    "practical_value_score": round(practical_score, 3),
                    "quality_level": "high_quality" if overall_score > 0.75 else "medium_quality" if overall_score > 0.5 else "low_quality",
                    "suggestions": result.suggestions,
                    "success": True
                }
            except Exception as e:
                print(f"DSPy verifier failed: {e}")
        
        # Fallback logic
        return self._fallback_verify(query, response, context)
    
    def _fallback_verify(self, query: str, response: str, context: str) -> Dict[str, Any]:
        """Fallback verification focusing on conversational authenticity"""
        response_lower = response.lower()
        
        # Check for conversational authenticity markers
        first_person_indicators = ["i think", "i've learned", "in my experience", "i believe", "i remember"]
        authenticity_score = sum(1 for phrase in first_person_indicators if phrase in response_lower) / len(first_person_indicators)
        
        # Check for conversational flow
        conversation_indicators = ["well", "you know", "let me tell you", "that's interesting", "ah,", "now,"]
        conversational_score = sum(1 for phrase in conversation_indicators if phrase in response_lower) / len(conversation_indicators)
        
        # Check for practical value
        practical_indicators = ["practical", "useful", "apply", "specific", "actionable", "example"]
        practical_score = sum(1 for phrase in practical_indicators if phrase in response_lower) / len(practical_indicators)
        
        # Check for humility/uncertainty (Munger characteristic)
        humility_indicators = ["could be wrong", "might be", "seems to me", "i think", "perhaps"]
        humility_score = sum(1 for phrase in humility_indicators if phrase in response_lower) / len(humility_indicators)
        
        # Check basic quality metrics
        response_length = len(response.split())
        has_context_overlap = len(set(response_lower.split()) & set(context.lower().split())) > 5
        addresses_query = len(set(query.lower().split()) & set(response_lower.split())) > 2
        
        # Calculate composite scores
        authenticity = min(1.0, (authenticity_score + humility_score) / 2)
        conversation = min(1.0, conversational_score + (0.2 if response_length > 50 else 0))
        practical = min(1.0, practical_score + (0.3 if has_context_overlap else 0) + (0.2 if addresses_query else 0))
        
        # Overall score emphasizing authenticity and conversation
        overall_score = (authenticity * 0.4 + conversation * 0.4 + practical * 0.2)
        
        # Generate suggestions based on what's missing
        suggestions = []
        if authenticity < 0.5:
            suggestions.append("Add more first-person perspective and personal experience")
        if conversation < 0.5:
            suggestions.append("Use more conversational phrases and natural flow")
        if practical < 0.5:
            suggestions.append("Include more practical examples and actionable advice")
        
        suggestion_text = "; ".join(suggestions) if suggestions else "Response shows good conversational authenticity"
        
        return {
            "method": "fallback",
            "overall_quality_score": round(overall_score, 3),
            "authenticity_score": round(authenticity, 3),
            "conversational_score": round(conversation, 3),
            "practical_value_score": round(practical, 3),
            "quality_level": "high_quality" if overall_score > 0.75 else "medium_quality" if overall_score > 0.5 else "low_quality",
            "suggestions": suggestion_text,
            "success": True
        }


# Convenience functions for easy access
def create_dspy_retrieval_decider() -> SimpleDSPyRetrievalDecider:
    """Create a DSPy retrieval decider instance"""
    return SimpleDSPyRetrievalDecider()


def create_dspy_planner() -> SimpleDSPyPlanner:
    """Create a DSPy planner instance"""
    return SimpleDSPyPlanner()


def create_dspy_synthesizer() -> SimpleDSPySynthesizer:
    """Create a DSPy synthesizer instance"""
    return SimpleDSPySynthesizer()


def create_dspy_verifier() -> SimpleDSPyVerifier:
    """Create a DSPy verifier instance"""
    return SimpleDSPyVerifier()
