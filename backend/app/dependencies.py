# backend/app/dependencies.py
from typing import Optional, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from backend.indexing_and_retrieval.retrieval.storage import FAISSStorage
from backend.agent.dspy_modules.dspy_config import initialize_dspy, get_dspy_status
from backend.agent.dspy_modules.simple_modules import create_dspy_planner, create_dspy_synthesizer, create_dspy_verifier, create_dspy_retrieval_decider

class VectorStoreManager:
    _instance: Optional['VectorStoreManager'] = None
    _vectorstore: Optional[FAISS] = None
    _embedding_function: Optional[SentenceTransformerEmbeddings] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """Initialize vector store once at startup"""
        if self._vectorstore is None:
            storage = FAISSStorage()
            self._vectorstore = storage.store_chunks_to_faiss()
            self._embedding_function = storage.embedding_function
            print("✅ Vector store initialized successfully")
    
    def shutdown(self):
        """Shutdown vector store on shutdown"""
        if self._vectorstore is not None:
            
            self._vectorstore = None
            self._embedding_function = None
            print("✅ Vector store shutdown successfully")

    def get_vectorstore(self) -> FAISS:
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self._vectorstore
    
    def get_embedding_function(self):
        return self._embedding_function

class DSPyManager:
    """Simple DSPy manager for the application"""
    _instance: Optional['DSPyManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self.planner = None
        self.synthesizer = None
        self.verifier = None
        self.retrieval_decider = None
        self.enabled = False
    
    def initialize(self, enable_dspy: bool = True) -> bool:
        """Initialize DSPy system"""
        try:
            success = initialize_dspy(enable_dspy)
            if success:
                self.planner = create_dspy_planner()
                self.synthesizer = create_dspy_synthesizer()
                self.verifier = create_dspy_verifier()
                self.retrieval_decider = create_dspy_retrieval_decider()
                self.enabled = True
                print("DSPy system initialized successfully")
            else:
                print("DSPy not available, using fallback modules")
                self.planner = create_dspy_planner()  # Will use fallback internally
                self.synthesizer = create_dspy_synthesizer()
                self.verifier = create_dspy_verifier()
                self.retrieval_decider = create_dspy_retrieval_decider()
                self.enabled = False
            return True
        except Exception as e:
            print(f"DSPy initialization failed: {e}")
            self.enabled = False
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get DSPy status"""
        return {
            **get_dspy_status(),
            "modules_loaded": self.planner is not None,
            "enabled": self.enabled
        }
    
    def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Analyze query using DSPy or fallback"""
        if self.planner:
            return self.planner.analyze_query(query, context)
        return {"method": "none", "success": False, "error": "No planner available"}
    
    def generate_response(self, query: str, context: str, mental_models: str, query_type: str = "general") -> Dict[str, Any]:
        """Generate response using DSPy or fallback"""
        if self.synthesizer:
            return self.synthesizer.generate_response(query, context, mental_models, query_type)
        return {"method": "none", "success": False, "error": "No synthesizer available"}
    
    def verify_response(self, query: str, response: str, context: str, query_type: str = "general") -> Dict[str, Any]:
        """Verify response using DSPy or fallback"""
        if self.verifier:
            return self.verifier.verify_response(query, response, context, query_type)
        return {"method": "none", "success": False, "error": "No verifier available"}
    
    def decide_retrieval(self, query: str, conversation_context: str = "") -> Dict[str, Any]:
        """Decide whether retrieval is needed using DSPy or fallback"""
        if self.retrieval_decider:
            return self.retrieval_decider.should_retrieve(query, conversation_context)
        return {"method": "none", "success": False, "error": "No retrieval decider available"}


# Global instances
vector_store_manager = VectorStoreManager()
dspy_manager = DSPyManager()


def initialize_dependencies(dspy_config_options: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
    """Initialize all application dependencies"""
    results = {}
    
    # Initialize vector store
    try:
        vector_store_manager.initialize()
        results['vector_store'] = True
    except Exception as e:
        print(f"Vector store initialization failed: {e}")
        results['vector_store'] = False
    
    # Initialize DSPy
    try:
        enable_dspy = dspy_config_options.get('enable_dspy', True) if dspy_config_options else True
        results['dspy'] = dspy_manager.initialize(enable_dspy)
    except Exception as e:
        print(f"DSPy initialization failed: {e}")
        results['dspy'] = False
    
    return results


def shutdown_dependencies():
    """Shutdown all dependencies"""
    try:
        vector_store_manager.shutdown()
        print("All dependencies shut down successfully")
    except Exception as e:
        print(f"Error during shutdown: {e}")


def get_dependencies_status() -> Dict[str, Any]:
    """Get status of all dependencies"""
    return {
        "vector_store": {
            "initialized": vector_store_manager._vectorstore is not None
        },
        "dspy": dspy_manager.get_status()
    }