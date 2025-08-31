import hashlib
import sqlite3
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
import json
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AuthManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "data/users.db"
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                profile_data TEXT DEFAULT '{}'
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> tuple[str, str]:
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        """Verify a password against its hash"""
        test_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return test_hash == hashed_password
    
    def create_user(self, username: str, email: str, password: str, full_name: str) -> tuple[bool, str]:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                conn.close()
                if existing_user[0] == username:
                    return False, f"Username '{username}' already exists. Please choose a different username."
                else:
                    return False, f"Email '{email}' already exists. Please use a different email address."
            
            # Hash password and create user
            password_hash, salt = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, full_name))
            
            conn.commit()
            conn.close()
            return True, "Account created successfully!"
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data if successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, full_name, profile_data
                FROM users 
                WHERE (username = ? OR email = ?) AND is_active = TRUE
            ''', (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                conn.close()
                return None
            
            # Verify password
            user_id, db_username, email, password_hash, salt, full_name, profile_data = user_data
            if not self.verify_password(password, password_hash, salt):
                conn.close()
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'id': user_id,
                'username': db_username,
                'email': email,
                'full_name': full_name,
                'profile_data': json.loads(profile_data) if profile_data else {}
            }
        except Exception as e:
            return None
    
    def create_session(self, user_id: int, expiry_hours: int = 24) -> str:
        """Create a new session for a user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expiry_hours)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            conn.close()
            return session_token
        except Exception as e:
            return ""
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user data if valid"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.full_name, u.profile_data, s.expires_at
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.is_active = TRUE AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, username, email, full_name, profile_data, expires_at = result
                return {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'full_name': full_name,
                    'profile_data': json.loads(profile_data) if profile_data else {}
                }
            return None
        except Exception as e:
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Invalidate a user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

# Streamlit session state management
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def login_required(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.warning("Please log in to access this page.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def check_authentication():
    """Check if user is authenticated and session is valid"""
    auth_manager = AuthManager()
    
    if st.session_state.get('session_token'):
        user_data = auth_manager.validate_session(st.session_state.session_token)
        if user_data:
            st.session_state.authenticated = True
            st.session_state.user_data = user_data
            return True
    
    # Clear invalid session
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.session_token = None
    return False