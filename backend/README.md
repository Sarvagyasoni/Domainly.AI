# Domainly.ai Backend

A professional multi-domain AI assistant backend powered by FastAPI and Google Gemini API. It uses local retrieval-augmented generation (RAG) to select relevant passages from domain-specific knowledge bases before generating an answer.

## Setup Instructions

1. **Prerequisites**: Make sure you have Python 3.10+ installed.
2. **Create a local virtual environment**:
   ```powershell
   python -m venv .venv
   ```
3. **Activate the virtual environment**:
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure environment variables**:
   Create a `.env` file in the `backend` directory (do not commit this file to git):
   ```env
   GEMINI_API_KEY="your-gemini-api-key"
   RAG_TOP_K=3
   RAG_CHUNK_SIZE=180
   RAG_CHUNK_OVERLAP=30
   ```

## Local RAG

Knowledge documents live in `app/knowledge_base`. The backend splits the selected domain document into overlapping chunks and uses hybrid retrieval: Gemini semantic embeddings plus BM25 lexical relevance. Semantic similarity receives 70% of the default combined score and BM25 receives 30%, preserving both meaning-based and exact-term matches.

Document embeddings use `RETRIEVAL_DOCUMENT`; questions use `RETRIEVAL_QUERY`. Per-domain vectors are persisted under `app/storage/vector_indexes` and are rebuilt automatically when the knowledge text, embedding model, or vector dimensions change. If embeddings are not configured or an embedding request fails, retrieval automatically falls back to BM25.

## Conversation Database

Conversations and messages are stored in SQLite at `app/storage/domainly.db`.
The database uses separate `conversations` and `messages` tables, foreign-key
cascade deletion, UTC timestamps, lookup indexes, and WAL journaling. The
backend automatically imports the previous `conversations.json` data when the
SQLite database is first created and empty.

The frontend loads `/conversations` on startup, creates chats through the API,
and includes `chat_id` in generation requests. Completed normal and streaming
responses are therefore restored after a browser refresh.

## Running the Server

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the auto-generated documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

Execute the unit tests using Python's built-in `unittest` runner:
```bash
python -m unittest discover tests
```
