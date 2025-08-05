from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules (we'll create these)
from document_processor import DocumentProcessor
from embedding_search import DocumentEmbedder
from decision_engine import DecisionEngine

app = FastAPI(title="HackRX LLM Document Processor", version="1.0.0")

# Initialize components
doc_processor = DocumentProcessor()
embedder = DocumentEmbedder()
decision_engine = DecisionEngine()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

@app.get("/")
async def root():
    return {"message": "HackRX LLM Document Processor API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest):
    try:
        # Step 1: Download and process document
        print(f"Processing document: {request.documents}")
        document_text = doc_processor.download_and_process_pdf(request.documents)
        
        # Step 2: Create embeddings for document
        print("Creating document embeddings...")
        chunks = doc_processor.chunk_document(document_text)
        embedder.create_embeddings(chunks)
        
        # Step 3: Process each question
        answers = []
        for i, question in enumerate(request.questions):
            print(f"Processing question {i+1}/{len(request.questions)}: {question}")
            
            # Find relevant chunks
            relevant_chunks = embedder.search_similar(question, k=3)
            
            # Generate answer using LLM
            answer = decision_engine.generate_answer(question, relevant_chunks)
            answers.append(answer)
        
        return QueryResponse(answers=answers)
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)