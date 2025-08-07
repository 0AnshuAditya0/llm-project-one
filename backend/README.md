# HackRX Document Query System Backend

This is the FastAPI backend for the HackRX Document Query System. It processes documents (PDF, DOCX, etc.), performs semantic search using embeddings, and answers natural language questions using a free HuggingFace Transformers model (no OpenAI required).

---

## Features
- Accepts document URLs (PDF, DOCX, etc.)
- Embedding-based semantic search (FAISS, sentence-transformers)
- Local HuggingFace QA model (no API key needed)
- FastAPI endpoints for health check and question answering
- CORS enabled for frontend integration

---

## Local Setup

1. **Install Python 3.10 or 3.11** (recommended for compatibility)
2. **Create and activate a virtual environment:**
   ```sh
   python3.10 -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```sh
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
4. **Run the backend:**
   ```sh
   uvicorn main:app --reload
   ```
5. **Test health endpoint:**
   - Visit [http://localhost:8000/health](http://localhost:8000/health)
   - You should see `{ "status": "healthy", ... }`

---

## API Endpoints

- `GET /` — Welcome message
- `GET /health` — Health check
- `POST /hackrx/run` — Main document query endpoint

### Example Request
```json
POST /hackrx/run
Content-Type: application/json
{
  "documents": "<DOCUMENT_URL>",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?"
  ]
}
```

### Example Response
```json
{
  "answers": [
    "A grace period of thirty days is provided...",
    "Yes, the policy covers maternity expenses..."
  ]
}
```

---

## Deployment (Render/Heroku/Railway)

1. **Procfile** (create in backend folder):
   ```
   web: uvicorn main:app --host 0.0.0.0 --port 10000
   ```
2. **Push code to your GitHub repo.**
3. **Connect repo to Render/Heroku/Railway.**
4. **Set build/start command if needed:**
   - `pip install -r backend/requirements.txt`
   - `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
5. **Open deployed URL and check `/health` endpoint.**

---

## Notes
- Make sure your deployed backend is accessible to your frontend (CORS is enabled by default).
- For production, restrict CORS origins as needed.
- For any issues, check logs on your deployment platform.

---

## License
MIT
