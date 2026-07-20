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

Knowledge documents live in `app/knowledge_base`. For each chat request, the backend splits the selected domain document into overlapping chunks, ranks them with BM25 lexical relevance, and adds only the top passages to the Gemini prompt. The implementation runs locally and does not require an embedding API or vector database.

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
