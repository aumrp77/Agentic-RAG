# backend/retrieval/rerank.py - ENHANCED VERSION
from backend.indexing_and_retrieval.retrieval.retrieval import Retrieval
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from typing import List, Optional
from langchain.schema import Document

class Rerank:
    def __init__(self, user_query: str, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.user_query = user_query
        self.cross_encoder = HuggingFaceCrossEncoder(model_name=model_name)
        # ✅ CHANGE: Don't create Retrieval here - accept docs instead

    def rerank_documents(self, documents: List[Document], top_k: Optional[int] = None) -> List[Document]:
        """✅ NEW: Rerank provided documents instead of retrieving new ones"""
        if not documents:
            return []
        
        try:
            # Score each chunk using the cross encoder
            for chunk in documents:
                # Ensure metadata exists
                if chunk.metadata is None:
                    chunk.metadata = {}
                
                score = self.cross_encoder.score([[self.user_query, chunk.page_content]])[0]
                chunk.metadata["rerank_score"] = float(score)
            
            # Sort chunks by rerank score in descending order
            documents.sort(key=lambda x: (x.metadata or {}).get("rerank_score", 0), reverse=True)
            
            # Return top_k if specified
            if top_k is not None:
                return documents[:top_k]
            return documents
            
        except Exception as e:
            print(f"Reranking failed: {e}")
            return documents  # Return original docs if reranking fails

    def rerank(self, top_k: Optional[int] = None):  # ✅ MODIFY: add top_k parameter
        """Legacy method - retrieves then reranks"""
        retrieval = Retrieval(self.user_query)
        retrieved_chunks = retrieval.get_retrieval()
        return self.rerank_documents(retrieved_chunks, top_k)
    
    def get_rerank(self, top_k: Optional[int] = None):
        return self.rerank(top_k)

if __name__ == "__main__":
    rerank = Rerank("What is Munger's inversion principle and how does he apply it in speeches?")
    print(rerank.get_rerank())