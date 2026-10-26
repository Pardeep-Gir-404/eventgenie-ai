import os
from typing import List
from dotenv import load_dotenv

# Load local .env from backend directory and workspace root
base_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_env_path = os.path.join(base_backend_dir, ".env")
root_env_path = os.path.join(os.path.dirname(base_backend_dir), ".env")

if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path, override=True)
if os.path.exists(root_env_path):
    load_dotenv(root_env_path, override=False)
load_dotenv()

class Settings:
    APP_NAME: str = "EventGenie AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def GEMINI_API_KEY(self) -> str:
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        
    @property
    def GEMINI_MODEL(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Firestore Configuration (Optional)
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    FIRESTORE_DATABASE_ID: str = os.getenv("FIRESTORE_DATABASE_ID", "(default)")
    USE_FIRESTORE: bool = bool(os.getenv("USE_FIRESTORE", "false").lower() in ("true", "1", "yes"))
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    
    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and not self.GEMINI_API_KEY.startswith("your_"))

settings = Settings()
