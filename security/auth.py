import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
import json
import sys
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, ConnectionFailure

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_database, COLLECTIONS

class AuthManager:
    def __init__(self):
        # Lazy initialization - don't connect to DB until needed
        self.db = None
        self.users_collection = None
        self.sessions_collection = None
        self.connection_error = None
        self._initialized = False
    
    def _ensure_connection(self):
        """Ensure database connection is established"""
        if not self._initialized:
            try:
                self.db = get_database()
                if self.db is None:
                    raise ConnectionError("Failed to connect to MongoDB database")
                self.users_collection = self.db[COLLECTIONS["users"]]
                self.sessions_collection = self.db[COLLECTIONS["sessions"]]
                self._initialized = True
                # Initialize database indexes after connection is established
                self._init_indexes()
            except Exception as e:
                self.connection_error = str(e)
                self._initialized = False
                # Show user-friendly error
                if hasattr(st, 'error'):
                    st.error("🔌 Database connection issue. Please check your internet connection and try again.")
        return self._initialized
    
    def _init_indexes(self):
        """Initialize the MongoDB collections with indexes (internal method)"""
        if not self._initialized:
            return
            
        try:
            # Create unique indexes for users collection (only if they don't exist)
            try:
                self.users_collection.create_index("username", unique=True)
            except Exception:
                pass  # Index already exists
            
            try:
                self.users_collection.create_index("email", unique=True)
            except Exception:
                pass  # Index already exists
            
            # Create indexes for sessions collection (only if they don't exist)
            try:
                self.sessions_collection.create_index("session_token", unique=True)
            except Exception:
                pass  # Index already exists
            
            try:
                self.sessions_collection.create_index("user_id")
            except Exception:
                pass  # Index already exists
            
        except Exception:
            pass  # Index creation failed, but it's not critical
    
    def is_connected(self):
        """Check if database connection is available"""
        return self._ensure_connection()

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, user_doc: dict) -> bool:
        """Verify password against hash - supports both old and new formats"""
        try:
            # New format: password field contains "salt:hash"
            if "password" in user_doc and ":" in user_doc["password"]:
                hashed = user_doc["password"]
                salt, password_hash = hashed.split(":", 1)
                return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
            
            # Old format: separate password_hash and salt fields
            elif "password_hash" in user_doc and "salt" in user_doc:
                salt = user_doc["salt"]
                password_hash = user_doc["password_hash"]
                return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
            
            return False
        except (ValueError, KeyError):
            return False
    
    def create_user(self, username: str, email: str, password: str, full_name: str = None) -> tuple[bool, str]:
        """Create a new user account"""
        if not self._ensure_connection():
            return False, "Database connection failed. Please try again later."
        
        try:
            # Check if user already exists
            if self.users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
                return False, "Username or email already exists."
            
            # Create user document
            user_doc = {
                "username": username,
                "email": email,
                "password": self.hash_password(password),
                "full_name": full_name or username,
                "created_at": datetime.now(),
                "is_active": True,
                "last_login": None
            }
            
            # Insert user
            result = self.users_collection.insert_one(user_doc)
            if result.inserted_id:
                return True, "Account created successfully! Please log in."
            else:
                return False, "Failed to create account. Please try again."
                
        except DuplicateKeyError:
            return False, "Username or email already exists."
        except Exception as e:
            return False, "An error occurred while creating your account. Please try again."
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful"""
        if not self._ensure_connection():
            return None
        
        try:
            # Find user by username or email
            user = self.users_collection.find_one({
                "$or": [
                    {"username": username},
                    {"email": username}
                ],
                "is_active": {"$in": [True, "True"]}
            })
            
            if not user:
                return None
            
            # Verify password (pass full user document for backward compatibility)
            if not self.verify_password(password, user):
                return None
            
            # Update last login
            self.users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.now()}}
            )
            
            # Convert ObjectId to string for JSON serialization
            user["_id"] = str(user["_id"])
            return user
            
        except Exception:
            return None
    
    def create_session(self, user_id: str, expiry_hours: int = 24) -> Optional[str]:
        """Create a session for authenticated user"""
        if not self._ensure_connection():
            return None
        
        try:
            session_token = secrets.token_urlsafe(32)
            session_doc = {
                "session_token": session_token,
                "user_id": user_id,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=expiry_hours),
                "is_active": True
            }
            
            result = self.sessions_collection.insert_one(session_doc)
            if result.inserted_id:
                return session_token
            return None
            
        except Exception:
            return None
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data if valid"""
        if not self._ensure_connection():
            return None
        
        try:
            # Find active session
            session = self.sessions_collection.find_one({
                "session_token": session_token,
                "is_active": True,
                "expires_at": {"$gt": datetime.now()}
            })
            
            if not session:
                return None
            
            # Get user data
            user = self.users_collection.find_one({
                "_id": ObjectId(session["user_id"]),
                "is_active": True
            })
            
            if user:
                user["_id"] = str(user["_id"])
                return user
            
            return None
            
        except Exception:
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by invalidating session"""
        if not self._ensure_connection():
            return False
        
        try:
            result = self.sessions_collection.update_one(
                {"session_token": session_token},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        if not self._ensure_connection():
            return
        
        try:
            result = self.sessions_collection.delete_many({
                "expires_at": {"$lt": datetime.now()}
            })
        except Exception:
            pass


# Session management functions
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def check_authentication() -> bool:
    """Check if user is authenticated and session is valid"""
    init_session_state()
    
    # If not marked as authenticated, return False
    if not st.session_state.authenticated:
        return False
    
    # If no session token, return False
    if not st.session_state.session_token:
        st.session_state.authenticated = False
        st.session_state.user_data = None
        return False
    
    try:
        # Validate session with database
        auth_manager = AuthManager()
        if not auth_manager.is_connected():
            return False
        
        user_data = auth_manager.validate_session(st.session_state.session_token)
        if user_data:
            st.session_state.user_data = user_data
            return True
        else:
            # Session invalid, clear authentication
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.session_token = None
            return False
            
    except Exception:
        return False


def login_required(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.error("🔒 Please log in to access this page.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper
