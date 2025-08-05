import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class DocumentEmbedder:
    def __init__(self):
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        
    def create_embeddings(self, document_chunks: List[str]):
        """Create FAISS index from document chunks"""
        try:
            print(f"Creating embeddings for {len(document_chunks)} chunks...")
            self.chunks = document_chunks
            
            # Generate embeddings
            embeddings = self.model.encode(document_chunks, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            print(f"FAISS index created with {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
    
    def search_similar(self, query: str, k: int = 3) -> List[str]:
        """Search for most similar chunks to query"""
        try:
            if self.index is None:
                raise Exception("No embeddings index found. Call create_embeddings first.")
            
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Return relevant chunks
            relevant_chunks = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    score = scores[0][i]
                    print(f"Found relevant chunk (similarity: {score:.4f})")
                    relevant_chunks.append(chunk)
            
            return relevant_chunks
            
        except Exception as e:
            print(f"Error searching similar chunks: {str(e)}")
            raise Exception(f"Failed to search similar chunks: {str(e)}")