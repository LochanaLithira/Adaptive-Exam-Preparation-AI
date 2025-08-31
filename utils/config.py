"""
Configuration settings for the Adaptive Exam Preparation AI
"""

import os
from pathlib import Path

from pymongo import MongoClient
import streamlit as st
import socket

# ==============================
# Base directory
# ==============================
BASE_DIR = Path(__file__).parent.parent

# ==============================
# MongoDB Settings
# ==============================
# MongoDB Connection URL
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb+srv://lithi0301:1XXDdlzvPBQvNaJo@adaptive-exam-preparati.o5h3ewc.mongodb.net/?retryWrites=true&w=majority&appName=Adaptive-Exam-Preparation-AI&ssl=true"
)

DATABASE_NAME = os.getenv("DATABASE_NAME", "adaptive_exam_prep_ai")

# Fallback to local MongoDB
FALLBACK_MONGODB_URL = "mongodb://localhost:27017/"

# ==============================
# Utility functions
# ==============================
def test_internet_connection():
    """Test basic internet connectivity"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# ==============================
# MongoDB Collections
# ==============================
COLLECTIONS = {
    "users": "users",
    "sessions": "user_sessions",
    "quizzes": "quizzes",
    "quiz_results": "quiz_results",
    "study_plans": "study_plans",
    "performance_data": "performance_data"
}

# ==============================
# Database connection helper
# ==============================
def get_mongodb_client():
    """Get MongoDB client connection"""

    if not test_internet_connection():
        return None

    # Try primary MongoDB Atlas connection
    try:
        client = MongoClient(
            MONGODB_URL,
            connectTimeoutMS=20000,
            serverSelectionTimeoutMS=20000,
            socketTimeoutMS=25000,
            maxPoolSize=10,
            retryWrites=True,
            w="majority"
        )
        # Test connection
        client.admin.command("ping", maxTimeMS=15000)
        return client
    except Exception:
        pass

    # If Atlas fails, try local MongoDB as fallback
    try:
        client = MongoClient(FALLBACK_MONGODB_URL)
        client.admin.command("ping")
        return client
    except Exception:
        pass

    return None

# ==============================
# Database caching for Streamlit
# ==============================
@st.cache_resource
def get_database():
    """Get database instance with caching and error handling"""
    try:
        client = get_mongodb_client()
        if client:
            return client[DATABASE_NAME]
        return None
    except Exception:
        return None

# ==============================
# Other App Settings
# ==============================
SESSION_EXPIRY_HOURS = 24
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-this")

PASSWORD_MIN_LENGTH = 8
BCRYPT_ROUNDS = 12

APP_NAME = "Adaptive Exam Preparation AI"
APP_VERSION = "1.0.0"

STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
