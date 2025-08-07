from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Tuple
import json

class AdvancedEmbeddingSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
    
    def create_index(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """Create FAISS index from document text"""
        # Split text into chunks
        self.chunks = self._create_chunks(text, chunk_size, overlap)
        
        # Create embeddings
        embeddings = self.model.encode(self.chunks)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.chunk_metadata = [
            {'chunk_id': i, 'text': chunk, 'start_pos': i * (chunk_size - overlap)}
            for i, chunk in enumerate(self.chunks)
        ]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant chunks"""
        if self.index is None:
            raise ValueError("Index not created. Call create_index first.")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                results.append({
                    'text': self.chunks[idx],
                    'score': float(score),
                    'metadata': self.chunk_metadata[idx]
                })
        
        return results
    
    def _create_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks