import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # --- Core Application Settings ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # --- MongoDB Settings ---
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/smart_task_manager'
    
    # --- JWT Settings ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # --- AI Settings (Using Gemini) ---
    # The key is primarily used in ai_service.py but listed here for completeness/config access
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')