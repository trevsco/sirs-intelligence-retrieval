import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
for directory in [UPLOADS_DIR, MODELS_DIR, LOGS_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Core RAG Parameters
    SIMILARITY_THRESHOLD: float = Field(0.0, description="Similarity threshold for vector retrieval (set to 0.0 to return all chunks)")
    CHUNK_SIZE: int = Field(512, description="Chunk size in characters")
    CHUNK_OVERLAP: int = Field(64, description="Chunk overlap in characters")
    TOP_K: int = Field(3, description="Number of top chunks to retrieve")
    
    # Models Configuration
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", description="Sentence-Transformers embedding model")
    EMBEDDING_DIM: int = Field(384, description="Embedding dimension")
    OLLAMA_MODEL: str = Field("phi4-mini", description="Ollama model for local LLM generation")
    OLLAMA_BASE_URL: str = Field("http://localhost:11434", description="Ollama base API URL")
    
    # LLM Settings
    LLM_TEMPERATURE: float = Field(0.1, description="Ollama temperature")
    LLM_MAX_TOKENS: int = Field(256, description="Maximum completion tokens")
    
    # Security & Files
    MAX_UPLOAD_SIZE_MB: int = Field(50, description="Maximum document size in MB")
    ALLOWED_EXTENSIONS: list[str] = Field(
        [".pdf", ".docx", ".txt", ".md"], 
        description="Allowed file extensions for document upload"
    )
    
    # File Paths
    BASE_DIR: Path = BASE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    MODELS_DIR: Path = MODELS_DIR
    LOGS_DIR: Path = LOGS_DIR
    DATA_DIR: Path = DATA_DIR

settings = Settings()
