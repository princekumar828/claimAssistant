import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "sample_data")
    CLAIMS_CSV = os.path.join(DATA_DIR, "claims.csv")
    
    INDEX_DIR = os.path.join(BASE_DIR, "indexing_storage")
    INDEX_FILE = os.path.join(INDEX_DIR, "faiss.index")
    METADATA_FILE = os.path.join(INDEX_DIR, "metadata.pkl")
    
    # Model Config
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_TYPE = os.getenv("LLM_TYPE", "gemini") # Options: mock, openai, gpt4all, gemini
    
    # OpenAI Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Gemini Config
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-1.5-flash"
    
    # GPT4All Config
    GPT4ALL_MODEL = "orca-mini-3b-gguf2-q4_0.gguf" # Small, fast model
    
    # App Config
    HOST = "0.0.0.0"
    PORT = 8000

settings = Settings()

# Ensure directories
if not os.path.exists(settings.INDEX_DIR):
    os.makedirs(settings.INDEX_DIR)
