import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-in-production'
    THEME = os.environ.get('THEME') or 'default'
    MONGO_URI = os.environ.get('MONGO_URI')
    API_KEY = os.environ.get('GEMINI_API_KEY')  # Google GenAI API Key
