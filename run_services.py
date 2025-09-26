"""
Service Launcher for Adaptive Exam Preparation AI
Starts all required services in separate processes
"""

import os
import sys
import subprocess
import time
from utils.api_config import (
    FLASK_TRACKER_PORT,
    PERFORMANCE_TRACKER_PORT,
    verify_services_status
)

def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_python_executable():
    """Get the path to the Python executable in the virtual environment"""
    if sys.platform == 'win32':
        if os.path.exists(".venv\\Scripts\\python.exe"):
            return os.path.abspath(".venv\\Scripts\\python.exe")
    else:
        if os.path.exists(".venv/bin/python"):
            return os.path.abspath(".venv/bin/python")
    
    # If we couldn't find the venv Python, return the current executable
    return sys.executable

def activate_venv_cmd():
    """Get command to activate virtual environment based on platform"""
    if sys.platform == 'win32':
        # Check if .venv directory exists
        if os.path.exists(".venv"):
            return ".venv\\Scripts\\activate"
        # Otherwise try to use the conda environment
        return "conda activate adaptive-exam-prep-ai"
    else:
        if os.path.exists(".venv"):
            return "source .venv/bin/activate"
        return "conda activate adaptive-exam-prep-ai"
        
def get_python_executable():
    """Get the correct Python executable for the current environment"""
    # Try to find virtual environment Python
    if os.path.exists(".venv"):
        if sys.platform == 'win32':
            venv_python = os.path.abspath(os.path.join(".venv", "Scripts", "python.exe"))
            if os.path.exists(venv_python):
                return venv_python
        else:
            venv_python = os.path.abspath(os.path.join(".venv", "bin", "python"))
            if os.path.exists(venv_python):
                return venv_python
                
    # If we can't find venv Python, use the current executable
    return sys.executable

def start_performance_tracker():
    """Start the Performance Tracker Agent"""
    # Check if already running
    if is_port_in_use(PERFORMANCE_TRACKER_PORT):
        print(f"⚠️ Port {PERFORMANCE_TRACKER_PORT} is already in use - Performance Tracker may already be running")
        return
    
    print("Starting Performance Tracker Agent...")
    
    # Get the Python executable from the virtual environment
    python_exe = get_python_executable()
    
    # Use the Python executable to run uvicorn directly
    if sys.platform == 'win32':
        cmd = f'"{python_exe}" -m uvicorn agents.performance_tracker_agent:app --reload --port {PERFORMANCE_TRACKER_PORT}'
        print(f"Running command: {cmd}")
        subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
    else:
        cmd = f'"{python_exe}" -m uvicorn agents.performance_tracker_agent:app --reload --port {PERFORMANCE_TRACKER_PORT}'
        print(f"Running command: {cmd}")
        subprocess.Popen(f'gnome-terminal -- bash -c "{cmd}; exec bash"', shell=True)
    
    print(f"Performance Tracker started on port {PERFORMANCE_TRACKER_PORT}")

def start_flask_tracker():
    """Start the Flask Tracker Service"""
    # Check if already running
    if is_port_in_use(FLASK_TRACKER_PORT):
        print(f"⚠️ Port {FLASK_TRACKER_PORT} is already in use - Flask Tracker may already be running")
        return
    
    script_path = "services/tracker.py"
    service_name = "Flask Tracker"
    
    print(f"Starting {service_name} Service...")
    
    # Get the Python executable from the virtual environment
    python_exe = get_python_executable()
    script_abs_path = os.path.abspath(script_path)
    
    print(f"Using Python: {python_exe}")
    print(f"Running script: {script_abs_path}")
    
    # Start in a new window using appropriate command for the platform
    if sys.platform == 'win32':
        cmd = f'"{python_exe}" "{script_abs_path}"'
        subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
    else:
        cmd = f'"{python_exe}" "{script_abs_path}"'
        subprocess.Popen(f'gnome-terminal -- bash -c "{cmd}; exec bash"', shell=True)
    
    print(f"{service_name} started on port {FLASK_TRACKER_PORT}")

def start_streamlit_app():
    """Start the Streamlit Application"""
    print("Starting Streamlit Application...")
    venv_cmd = activate_venv_cmd()
    cmd = f"{venv_cmd} && streamlit run app.py"
    
    # Start in a new window using appropriate command for the platform
    if sys.platform == 'win32':
        subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
    else:
        subprocess.Popen(f'gnome-terminal -- bash -c "{cmd}; exec bash"', shell=True)
    
    print("Streamlit Application started")

def check_services_status(retry=10, wait=2):
    """Check if all services are running"""
    print("\nChecking services status...")
    
    for i in range(retry):
        # On first and last iteration, use verbose mode for detailed diagnostics
        verbose = (i == 0 or i == retry - 1)
        status = verify_services_status(verbose=verbose)
        
        all_running = all(status.values())
        if all_running:
            print("✅ All services are running:")
        else:
            print("⚠️ Service status:")
        
        for service, running in status.items():
            icon = "✅" if running else "❌"
            print(f"{icon} {service}")
            
            # If service isn't running on last retry, suggest manual start
            if not running and i == retry - 1:
                if service == "flask_tracker":
                    print("   Try starting manually: python services/tracker.py")
                elif service == "performance_tracker":
                    print("   Try starting manually: uvicorn agents.performance_tracker_agent:app --reload --port 8001")
                elif service == "streamlit_app":
                    print("   Try starting manually: streamlit run app.py")
        
        if all_running:
            break
            
        if i < retry - 1:
            print(f"Waiting {wait} seconds before checking again (attempt {i+1}/{retry})...")
            time.sleep(wait)
    
    return status

def ensure_flask_home_route():
    """Ensure Flask tracker has a home route for health checks"""
    flask_file = "services/tracker.py"
    
    try:
        with open(flask_file, 'r') as f:
            content = f.read()
            
        # Check if home route already exists
        if '@app.route("/", methods=["GET"])' in content:
            print("Flask home route already exists - skipping update")
            return True
            
        # Add home route before the if __name__ == "__main__": line
        if 'if __name__ == "__main__":' in content:
            updated_content = content.replace(
                'if __name__ == "__main__":',
                '@app.route("/", methods=["GET"])\n'
                'def home():\n'
                '    """Simple endpoint to verify the service is running"""\n'
                '    return jsonify({\n'
                '        "status": "ok",\n'
                '        "message": "Flask Tracker Service is running"\n'
                '    })\n\n'
                'if __name__ == "__main__":'
            )
            
            with open(flask_file, 'w') as f:
                f.write(updated_content)
                
            print("Added health check route to Flask tracker")
            return True
    except Exception as e:
        print(f"Warning: Could not update Flask tracker: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== STARTING ADAPTIVE EXAM PREPARATION AI SERVICES =====\n")
    
    # Ensure Flask has a home route for health checks
    ensure_flask_home_route()
    
    # Kill any processes that might be using our ports
    if sys.platform == 'win32':
        try:
            os.system(f"taskkill /F /IM streamlit.exe")
            os.system(f"taskkill /F /IM uvicorn.exe") 
            print("Killed any existing processes that might conflict with our services")
        except:
            pass
    
    # Start all services
    start_performance_tracker()
    time.sleep(3)  # Give more time between starting services
    
    start_flask_tracker()
    time.sleep(3)
    
    start_streamlit_app()
    time.sleep(5)
    
    # Check if services are running with more retries and longer wait time
    check_services_status(retry=15, wait=3)
    
    print("\n===== SERVICE ACCESS INFORMATION =====")
    print("Flask Tracker API: http://localhost:5000/")
    print("Performance Tracker API: http://localhost:8001/ping")
    print("Performance Tracker API Docs: http://localhost:8001/docs")
    print("Streamlit Application: http://localhost:8501")
    
    print("\n===== SERVICE MANAGEMENT =====")
    print("1. If services aren't running, check terminal windows for error messages")
    print("2. To stop services, close the terminal windows or press Ctrl+C in each window")
    print("3. To restart services, run this script again")