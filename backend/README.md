# Domainly.ai Backend

A professional multi-domain AI assistant backend powered by FastAPI and Google Gemini API. It handles system prompt orchestration and references domain-specific knowledge bases using a lightweight local JSON file database.

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
   ```

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
