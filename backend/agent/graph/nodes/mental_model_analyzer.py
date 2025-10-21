"""
Mental Model Analyzer Node for Charlie Munger RAG Agent
Identifies and applies relevant mental models to enhance responses
"""

import time
from typing import Dict, List, Any
from backend.agent.graph.state import MungerState, add_execution_trace, add_warning
from backend.agent.llm.client import LLMClient


class MentalModelAnalyzer:
    """Analyzes content and identifies applicable mental models"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        
        # Comprehensive mental models database
        self.mental_models_db = {
            "inversion": {
                "description": "Thinking about problems backwards - what would cause failure?",
                "keywords": ["inversion", "opposite", "reverse", "failure", "avoid"],
                "examples": ["What would cause this to fail?", "How can we avoid disaster?"],
                "munger_quote": "All I want to know is where I'm going to die, so I'll never go there."
            },
            "base_rates": {
                "description": "Using statistical probabilities and base rates in decision making",
                "keywords": ["probability", "statistics", "odds", "base rate", "likelihood"],
                "examples": ["What's the statistical probability?", "What do the base rates tell us?"],
                "munger_quote": "The first rule is that you can't really know anything if you just remember isolated facts."
            },
            "opportunity_cost": {
                "description": "Considering what you give up when making a choice",
                "keywords": ["opportunity cost", "trade-off", "alternative", "cost", "benefit"],
                "examples": ["What's the cost of this choice?", "What are we giving up?"],
                "munger_quote": "The opportunity cost of capital is the return on the next best alternative."
            },
            "second_order_thinking": {
                "description": "Thinking about the consequences of consequences",
                "keywords": ["second order", "consequence", "unintended", "cascade", "ripple"],
                "examples": ["What happens after what happens?", "What are the unintended consequences?"],
                "munger_quote": "You have to think about the second and third order effects."
            },
            "circle_of_competence": {
                "description": "Staying within areas of expertise and knowledge",
                "keywords": ["competence", "expertise", "knowledge", "skill", "ability"],
                "examples": ["Is this within my expertise?", "Do I understand this well enough?"],
                "munger_quote": "Know your circle of competence, and stick within it."
            },
            "confirmation_bias": {
                "description": "Tendency to search for information that confirms existing beliefs",
                "keywords": ["bias", "confirmation", "prejudice", "belief", "assumption"],
                "examples": ["Am I only seeing what I want to see?", "What evidence contradicts my view?"],
                "munger_quote": "The human mind is a lot like the human egg, and the human egg has a shut-off device."
            },
            "anchoring": {
                "description": "Over-reliance on first piece of information received",
                "keywords": ["anchor", "reference", "starting point", "initial", "first"],
                "examples": ["Am I anchored to the first number I heard?", "What's my reference point?"],
                "munger_quote": "The first impression is often wrong."
            },
            "availability_heuristic": {
                "description": "Overestimating probability of events that come easily to mind",
                "keywords": ["availability", "recency", "salient", "memorable", "vivid"],
                "examples": ["Is this just the most recent example?", "Am I overestimating because it's memorable?"],
                "munger_quote": "The availability heuristic is a mental shortcut that relies on immediate examples."
            },
            "representativeness": {
                "description": "Judging probability by similarity to stereotypes",
                "keywords": ["representative", "typical", "stereotype", "pattern", "similar"],
                "examples": ["Does this fit the typical pattern?", "Am I stereotyping here?"],
                "munger_quote": "The representativeness heuristic leads to systematic errors."
            },
            "loss_aversion": {
                "description": "Feeling losses more strongly than equivalent gains",
                "keywords": ["loss", "gain", "risk", "aversion", "pain"],
                "examples": ["Am I avoiding losses more than seeking gains?", "What's the pain of being wrong?"],
                "munger_quote": "Losses loom larger than gains."
            }
        }
    
    def identify_applicable_models(self, query: str, context: str) -> List[str]:
        """Identify which mental models are most applicable to the query and context"""
        applicable_models = []
        
        # Combine query and context for analysis
        full_text = f"{query} {context}".lower()
        
        # Score each mental model based on keyword matches and relevance
        model_scores = {}
        for model_name, model_info in self.mental_models_db.items():
            score = 0
            
            # Keyword matching
            for keyword in model_info["keywords"]:
                if keyword in full_text:
                    score += 1
            
            # Check for model-specific patterns
            if model_name == "inversion" and any(word in full_text for word in ["avoid", "prevent", "failure"]):
                score += 2
            elif model_name == "base_rates" and any(word in full_text for word in ["probability", "statistics", "odds"]):
                score += 2
            elif model_name == "opportunity_cost" and any(word in full_text for word in ["choice", "decision", "trade"]):
                score += 2
            
            if score > 0:
                model_scores[model_name] = score
        
        # Sort by score and return top models
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        applicable_models = [model for model, score in sorted_models[:3]]  # Top 3 models
        
        return applicable_models
    
    def get_model_explanations(self, models: List[str]) -> Dict[str, str]:
        """Get detailed explanations for applicable mental models"""
        explanations = {}
        
        for model in models:
            if model in self.mental_models_db:
                model_info = self.mental_models_db[model]
                explanation = f"{model_info['description']} Example: {model_info['examples'][0]}"
                explanations[model] = explanation
        
        return explanations
    
    def generate_application_notes(self, query: str, models: List[str], context: str) -> List[str]:
        """Generate notes on how to apply mental models to the specific query"""
        notes = []
        
        for model in models:
            if model in self.mental_models_db:
                model_info = self.mental_models_db[model]
                
                # Generate specific application note using LLM
                try:
                    application_prompt = f"""
                    How would Charlie Munger apply the {model} mental model to answer this question?
                    
                    Question: {query}
                    Context: {context[:500]}...
                    
                    Mental Model: {model_info['description']}
                    Example: {model_info['examples'][0]}
                    
                    Provide a brief 1-2 sentence note on how to apply this model.
                    """
                    
                    response = self.llm_client.get_response([
                        {"role": "user", "content": application_prompt}
                    ])
                    
                    notes.append(f"{model}: {response.strip()}")
                    
                except Exception as e:
                    # Fallback to generic application
                    notes.append(f"{model}: Consider {model_info['description']}")
        
        return notes


def mental_model_analyzer_node(state: MungerState) -> MungerState:
    """
    Main mental model analyzer node that identifies and prepares mental models for application
    """
    start_time = time.time()
    
    try:
        query = state["user_query"]
        context = "\n".join([doc.page_content for doc in state.get("reranked_docs", [])[:3]])
        
        # Skip if not needed
        if not requires_mental_models(state):
            state["current_step"] = "mental_models_skipped"
            return state
        
        analyzer = MentalModelAnalyzer()
        
        # Step 1: Identify applicable models
        print("🧠 Analyzing mental models...")
        applicable_models = analyzer.identify_applicable_models(query, context)
        
        # Combine with previously identified models
        all_models = list(set(state.get("identified_mental_models", []) + applicable_models))
        state["applicable_mental_models"] = all_models
        
        # Step 2: Get model explanations
        explanations = analyzer.get_model_explanations(all_models)
        state["mental_model_explanations"] = explanations
        
        # Step 3: Generate application notes
        application_notes = analyzer.generate_application_notes(query, all_models, context)
        state["model_application_notes"] = application_notes
        
        # Update state
        state["current_step"] = "mental_models_analyzed"
        
        # Add execution trace
        duration = time.time() - start_time
        add_execution_trace(state, "mental_model_analyzer", {
            "timestamp": start_time,
            "duration": duration,
            "models_identified": len(all_models),
            "models": all_models,
            "application_notes": len(application_notes)
        })
        
        print(f"✅ Mental Models: {len(all_models)} models identified - {', '.join(all_models)}")
        
    except Exception as e:
        error_msg = f"Mental model analysis failed: {str(e)}"
        state["errors"].append(error_msg)
        state["current_step"] = "mental_model_analysis_failed"
        print(f"❌ Mental Model Analyzer error: {error_msg}")
    
    return state


def requires_mental_models(state: MungerState) -> bool:
    """Check if mental model analysis is needed"""
    query_type = state.get("query_type")
    identified_models = state.get("identified_mental_models", [])
    
    # Always analyze for these query types
    if query_type in ["mental_model", "decision_framework", "general"]:
        return True
    
    # Analyze if mental models were detected in planning
    if len(identified_models) > 0:
        return True
    
    return False


def get_mental_models_context(state: MungerState) -> str:
    """Get formatted mental models context for response generation"""
    models = state.get("applicable_mental_models", [])
    explanations = state.get("mental_model_explanations", {})
    notes = state.get("model_application_notes", [])
    
    if not models:
        return ""
    
    context_parts = ["MENTAL MODELS TO APPLY:"]
    
    for model in models:
        if model in explanations:
            context_parts.append(f"- {model.upper()}: {explanations[model]}")
    
    if notes:
        context_parts.append("\nAPPLICATION NOTES:")
        for note in notes:
            context_parts.append(f"- {note}")
    
    return "\n".join(context_parts)


def get_model_application_prompt(state: MungerState) -> str:
    """Generate prompt section for mental model application"""
    models_context = get_mental_models_context(state)
    
    if not models_context:
        return ""
    
    return f"""
    
{models_context}

When answering, make sure to:
1. Apply the relevant mental models naturally in your response
2. Use specific examples that illustrate the models
3. Show how Munger would think through this problem using these frameworks
4. Be practical and actionable in your application
"""
