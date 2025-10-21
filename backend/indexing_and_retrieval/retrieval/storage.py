from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from backend.indexing_and_retrieval.indexing import Ingest
from backend.agent.graph.state import Chunk
from langchain.schema import Document
from typing import List
import os

class FAISSStorage:
    def __init__(self):
        self.embedding_function = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        
    def store_chunks_to_faiss(self):
        """Ingest documents and create FAISS vectorstore"""
        # Check if FAISS index already exists
        import os
        faiss_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "indexing_and_retrieval", "storage", "faiss_db")
        if os.path.exists(faiss_path):
            self.vectorstore = FAISS.load_local(faiss_path, self.embedding_function, allow_dangerous_deserialization=True)
            return self.vectorstore
            
        # Do ingestion directly here
        ingest = Ingest()
        
        # Try to load existing chunks first, ingest only if needed
        try:
            chunks_data = ingest.load_chunks()
            ingest.chunks = [Chunk(**chunk) for chunk in chunks_data]
        except FileNotFoundError:
            # No chunks.json exists, need to ingest
            ingest.ingest()
        
        chunks = ingest.get_chunks()
        
        # Convert to LangChain Document format (required by FAISS)
        langchain_docs = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk.text,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "parent_doc_id": chunk.parent_doc_id,
                    "token_count": chunk.token_count
                }
            )
            langchain_docs.append(doc)
        
        # Let FAISS handle all the embedding
        self.vectorstore = FAISS.from_documents(
            documents=langchain_docs,
            embedding=self.embedding_function
        )
        
        # Save the FAISS index for future use
        self.vectorstore.save_local(faiss_path)
        return self.vectorstore
    
    def get_vectorstore(self):
        if self.vectorstore is None:
            self.store_chunks_to_faiss()
        return self.vectorstore