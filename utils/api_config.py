"""
API Configuration for the Adaptive Exam Preparation AI
Centralizes all API endpoint URLs, ports, and configuration
"""

import os

# ==============================
# API Services Configuration
# ==============================

# Flask tracker service (receives quiz submissions from UI)
FLASK_TRACKER_HOST = os.getenv("FLASK_TRACKER_HOST", "localhost")
FLASK_TRACKER_PORT = int(os.getenv("FLASK_TRACKER_PORT", "5000"))
FLASK_TRACKER_URL = f"http://{FLASK_TRACKER_HOST}:{FLASK_TRACKER_PORT}"
FLASK_TRACKER_ENDPOINT = f"{FLASK_TRACKER_URL}/track_performance"

# FastAPI performance tracker agent (evaluates and stores quiz results)
PERFORMANCE_TRACKER_HOST = os.getenv("PERFORMANCE_TRACKER_HOST", "localhost")
PERFORMANCE_TRACKER_PORT = int(os.getenv("PERFORMANCE_TRACKER_PORT", "8001"))
PERFORMANCE_TRACKER_URL = f"http://{PERFORMANCE_TRACKER_HOST}:{PERFORMANCE_TRACKER_PORT}"
PERFORMANCE_TRACKER_TRACK_ENDPOINT = f"{PERFORMANCE_TRACKER_URL}/track"
PERFORMANCE_TRACKER_PING_ENDPOINT = f"{PERFORMANCE_TRACKER_URL}/ping"

# Streamlit application (main UI)
STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "localhost")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_URL = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"

# ==============================
# API Timeout Configuration
# ==============================
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_API_TIMEOUT", "30"))  # 30 seconds (increased from 15)

# ==============================
# Function to verify services are running
# ==============================
def verify_services_status(verbose=False):
    """
    Checks if all required services are running
    Returns a dictionary with service status
    
    Args:
        verbose: If True, print detailed error messages
    """
    import requests
    
    status = {
        "flask_tracker": False,
        "performance_tracker": False,
        "streamlit_app": False,
    }
    
    # Check Flask Tracker
    try:
        if verbose:
            print(f"Checking Flask Tracker at {FLASK_TRACKER_URL}/...")
        response = requests.get(f"{FLASK_TRACKER_URL}/", timeout=3)
        status["flask_tracker"] = response.status_code == 200
        if verbose:
            print(f"Flask Tracker response: {response.status_code}")
    except Exception as e:
        if verbose:
            print(f"Flask Tracker error: {str(e)}")
        # Try checking if the port is open as fallback
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((FLASK_TRACKER_HOST, FLASK_TRACKER_PORT))
            s.close()
            status["flask_tracker"] = True
            if verbose:
                print("Flask Tracker port is open")
        except:
            pass
    
    # Check Performance Tracker
    try:
        if verbose:
            print(f"Checking Performance Tracker at {PERFORMANCE_TRACKER_PING_ENDPOINT}...")
        response = requests.get(PERFORMANCE_TRACKER_PING_ENDPOINT, timeout=3)
        status["performance_tracker"] = response.status_code == 200
        if verbose:
            print(f"Performance Tracker response: {response.status_code}")
    except Exception as e:
        if verbose:
            print(f"Performance Tracker error: {str(e)}")
        # Try checking if the port is open as fallback
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((PERFORMANCE_TRACKER_HOST, PERFORMANCE_TRACKER_PORT))
            s.close()
            status["performance_tracker"] = True
            if verbose:
                print("Performance Tracker port is open")
        except:
            pass
    
    # Check Streamlit (this just checks if the port is open)
    try:
        if verbose:
            print(f"Checking Streamlit at port {STREAMLIT_PORT}...")
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((STREAMLIT_HOST, STREAMLIT_PORT))
        s.close()
        status["streamlit_app"] = True
        if verbose:
            print("Streamlit port is open")
    except Exception as e:
        if verbose:
            print(f"Streamlit error: {str(e)}")
        
    return status