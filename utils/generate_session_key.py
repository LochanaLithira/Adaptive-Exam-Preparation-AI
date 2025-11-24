#!/usr/bin/env python3
"""
Generate a secure session secret key for the Adaptive Exam Preparation AI application.
Run this script to generate a new cryptographically secure session key.
"""

import secrets
import base64

def generate_session_key():
    """Generate a cryptographically secure session key."""
    # Generate 32 bytes (256 bits) of random data
    # This is URL-safe and doesn't require special character escaping
    secret_key = secrets.token_urlsafe(32)
    return secret_key

def generate_session_key_base64():
    """Generate a base64-encoded session key."""
    secret_bytes = secrets.token_bytes(32)
    secret_key = base64.b64encode(secret_bytes).decode('utf-8')
    return secret_key

if __name__ == "__main__":
    print("Generating secure session keys...")
    print()
    
    # URL-safe key (recommended)
    url_safe_key = generate_session_key()
    print(f"URL-safe session key (recommended): {url_safe_key}")
    print(f"Length: {len(url_safe_key)} characters")
    print()
    
    # Base64 key (alternative)
    base64_key = generate_session_key_base64()
    print(f"Base64 session key (alternative): {base64_key}")
    print(f"Length: {len(base64_key)} characters")
    print()
    
    print("Copy one of these keys to your .env file:")
    print(f"SESSION_SECRET_KEY={url_safe_key}")
    print()
    print("⚠️  Important: Keep this key secret and never commit it to version control!")