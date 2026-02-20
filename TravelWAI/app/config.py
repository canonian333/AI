# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
    MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    
    # PRODUCTION GRADE: Centralized Model Selection
    # Update this single string when models are decommissioned
    # Switched to llama3-70b-8192
    MODEL_NAME = "llama-3.3-70b-versatile"
    SMALL_MODEL_NAME = "llama-3.1-8b-instant" 

    @classmethod
    def validate(cls):
        required = ["GROQ_API_KEY", "SERPAPI_API_KEY", "INTERNAL_API_KEY", "MONGO_CONNECTION_STRING", "LANGCHAIN_API_KEY"]
        for key in required:
            if not getattr(cls, key):
                raise ValueError(f"CRITICAL: Missing environment variable: {key}")