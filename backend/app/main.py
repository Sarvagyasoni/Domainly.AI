from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.core.logging_config import setup_logging
setup_logging()
app = FastAPI(
    title="Domainly.ai",
    description="A professional multi-domain AI assistant",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(conversations_router)
@app.get("/", tags=["Home"])
def home():
    return {
        "success": True,
        "message": "Welcome to Domainly.ai — your professional AI assistant."
    }
