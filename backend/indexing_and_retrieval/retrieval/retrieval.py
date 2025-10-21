# backend/retrieval/retrieval.py - ENHANCED VERSION
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from backend.app.dependencies import vector_store_manager, VectorStoreManager
from typing import List
from langchain.schema import Document

class Retrieval:
    def __init__(self, user_query: str):
        vector_store_manager = VectorStoreManager()
        vector_store_manager.initialize()
        self.vectorstore = vector_store_manager.get_vectorstore()
        self.embedding_function = vector_store_manager.get_embedding_function()
        self.user_query = user_query

    def embed_query(self, query: str):
        return self.embedding_function.embed_query(query)

    def retrieve(self, k: int = 10) -> List[Document]:  # ✅ ADD: configurable k
        """Retrieve documents with configurable count"""
        return self.vectorstore.similarity_search(self.user_query, k=k)
    
    def retrieve_with_scores(self, k: int = 10):  # ✅ ADD: get scores too
        """Retrieve with similarity scores"""
        return self.vectorstore.similarity_search_with_score(self.user_query, k=k)
    
    def get_retrieval(self, k: int = 10):  # ✅ MODIFY: pass through k parameter
        return self.retrieve(k=k)