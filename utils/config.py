"""
Configuration settings for the Adaptive Exam Preparation AI
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "app.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Session settings
SESSION_EXPIRY_HOURS = 24
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-this")

# Security settings
PASSWORD_MIN_LENGTH = 8
BCRYPT_ROUNDS = 12

# Application settings
APP_NAME = "Adaptive Exam Preparation AI"
APP_VERSION = "1.0.0"

# Streamlit settings
STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Create data directory if it doesn't exist
os.makedirs(BASE_DIR / "data", exist_ok=True)