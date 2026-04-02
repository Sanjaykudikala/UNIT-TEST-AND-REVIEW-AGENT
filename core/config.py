import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Vector DB Settings
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    
    # Default Paths (Can be overridden by CLI)
    REPO_PATH = os.getenv("REPO_PATH", "./commons-text")
    OUTPUT_DIR = "./output"

settings = Settings()
