from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from backend.document_processor import AdvancedDocumentProcessor
from backend.embedding_search import AdvancedEmbeddingSearch
from backend.decision_engine import AdvancedDecisionEngine
import time
import logging

app = FastAPI(title="HackRX Document Query System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = AdvancedDocumentProcessor()
embedding_search = AdvancedEmbeddingSearch()
decision_engine = AdvancedDecisionEngine()

logging.basicConfig(level=logging.INFO)

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

@app.post("/hackrx/run", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """Main endpoint for document query processing"""
    start_time = time.time()
    
    try:
        # Step 1: Process document
        doc_data = document_processor.process_document(request.documents)
        
        # Step 2: Create embedding index
        embedding_search.create_index(doc_data['text'])
        
        # Step 3: Answer questions
        answers = []
        for question in request.questions:
            # Search for relevant chunks
            relevant_chunks = embedding_search.search(question, top_k=5)
            
            # Generate answer
            answer = decision_engine.answer_questions([question], relevant_chunks)[0]
            answers.append(answer)
        
        processing_time = time.time() - start_time
        print(f"Processing completed in {processing_time:.2f} seconds")
        
        return QueryResponse(answers=answers)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the HackRX Document Query System API. See /docs for usage."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HackRX Document Query System is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)