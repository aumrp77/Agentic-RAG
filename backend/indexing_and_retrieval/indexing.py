"""
Document Indexing and Chunking for Charlie Munger RAG Agent
Combines ingestion and chunking functionality in a single module
"""

from backend.agent.graph.state import Chunk, Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from langchain_community.document_loaders import PyPDFLoader
from typing import List
import uuid
import os
import json


class Chunker:
    """
    Chunker class for chunking documents into chunks of paragraphs, sections, quotes, etc.
    """
    
    def __init__(self, document_paths: List[str]):
        self.document_paths = document_paths
        self.document_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            separators=["\nChapter ", "\n\n", "\n", " ", ""]
        )
        self.chunks = []

    def chunk_document(self, document_path: str):
        """
        Chunk a document into chunks of paragraphs, sections, quotes, etc.
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found at {document_path}")
            
        # Load PDF and extract text content
        pdf_documents = PyPDFLoader(document_path).load_and_split()
        
        # Combine all page content into a single text string
        full_text = "\n\n".join([doc.page_content for doc in pdf_documents])
        
        source_type = document_path.split("/")[-1].split(".")[0].split("_")[1] #CharlieMunger_(Type).pdf
        document = Document(source_name=document_path, source_type=source_type, doc_id=document_path.split("/")[-1])
        
        chunks = self.document_splitter.split_text(full_text)
        
        for chunk_text in chunks:
            chunk_id = str(uuid.uuid4())
            chunk_obj = Chunk(chunk_id=chunk_id, parent_doc_id=document.doc_id, text=chunk_text, token_count=len(chunk_text.split()))
            self.chunks.append(chunk_obj)
        
        return chunks
    
    def chunk_documents(self):
        """
        Chunk all documents in the document_paths list.
        """
        for document_path in self.document_paths:
            self.chunk_document(document_path)
            
        import os
        storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "indexing_and_retrieval", "storage", "chunks.json")
        with open(storage_path, "w") as f:
            json.dump([chunk.model_dump() for chunk in self.chunks], f)
            
        return self.chunks
    
    def load_chunks(self):
        import os
        storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "indexing_and_retrieval", "storage", "chunks.json")
        with open(storage_path, "r") as f:
            self.chunks = [Chunk(**chunk) for chunk in json.load(f)]
        return self.chunks
    
    def get_chunks(self):
        return self.chunks


class Ingest:
    """
    Document ingestion orchestrator that uses Chunker for processing
    """
    def __init__(self):
        self.chunker = Chunker(["/workspaces/the-munger-talks/docs/PoorCharliesAlmanack_book.pdf"])
        print(f"Total chunks created: {len(self.chunker.chunks)}")

    def ingest(self):
        """
        Main ingestion process - chunks documents and provides sample output
        """
        self.chunker.chunk_documents()
        
        print(f"Total chunks created: {len(self.chunker.chunks)}")
        
        # Print first few chunks as a sample
        for i, chunk in enumerate(self.chunker.chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"ID: {chunk.chunk_id}")
            print(f"Token count: {chunk.token_count}")
            print(f"Text preview: {chunk.text[:200]}...")
        

    def load_chunks(self):
        """Load existing chunks from storage"""
        return self.chunker.load_chunks()
    
    def get_chunks(self):
        """Get the current chunks"""
        return self.chunker.get_chunks()
