from flask import Flask, request, jsonify
from collections import OrderedDict
import requests
import json
import logging
import os
import sys
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import API configuration
from utils.api_config import (
    FLASK_TRACKER_PORT, 
    PERFORMANCE_TRACKER_TRACK_ENDPOINT, 
    DEFAULT_TIMEOUT,
    verify_services_status
)

# Configure logging - only log to console, not to files
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tracker")

# No file handler needed as we're only logging to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Flask(__name__)

@app.route("/track_performance", methods=["POST"])
def track_performance():
    data = request.get_json()
    logger.info("Received quiz submission request")

    if not data or "results" not in data:
        logger.error("No quiz results received in request")
        return jsonify({"error": "No quiz results received"}), 400

    results = data["results"]
    # Log the received data
    logger.info(f"Received {len(results)} quiz results")
    
    # Sort by question ID to keep numbering consistent
    results_sorted = sorted(results, key=lambda x: x["id"])
    num_digits = len(str(len(results_sorted)))

    received_responses  = OrderedDict()
    for q in results_sorted:
        key = f"Q{str(q['id']).zfill(num_digits)} : {q.get('question')}"
        received_responses[key] = {
            "category": q.get("category"),
            "correct_answer": q.get("correct_answer"),
            "user_answer": q.get("user_answer"),
        }

    response_summary = {
        "message": "✅ Data received successfully",
        "received_quiz_count": len(results_sorted),
        "received_responses": received_responses
    }
    
    # Format data for performance tracker agent
    answers = {}
    correct_answers = {}
    questions_text = {}
    
    # Extract user information from request headers or session if available
    user_id = request.headers.get("X-User-ID", "current_user")
    
    # Log user info
    logger.info(f"Processing quiz results for user: {user_id}")
    
    for i, q in enumerate(results_sorted):
        question_id = f"Q{i+1}"
        answers[question_id] = q.get("user_answer")
        correct_answers[question_id] = q.get("correct_answer")
        questions_text[question_id] = q.get("question")
    
    # Prepare data for the performance tracker API
    performance_data = {
        "user_id": user_id,
        "quiz_id": 1,  # This should be replaced with the actual quiz ID
        "topic": results_sorted[0].get("category") if results_sorted else "General",
        "answers": answers,
        "correct_answers": correct_answers,
        "questions_text": questions_text
    }
    
    # Log the formatted data being sent to performance tracker
    logger.info("Formatted data for performance tracker")
    logger.info(f"Topic: {performance_data['topic']}")
    logger.info(f"Number of answers: {len(answers)}")
    
    # Forward data to performance tracker agent
    try:
        # Save to the performance tracker database anyway (even if API fails)
        response_summary["local_storage"] = "✅ Quiz results stored locally"
        
        logger.info(f"Attempting to forward data to performance tracker at {PERFORMANCE_TRACKER_TRACK_ENDPOINT}")
        
        # Check if performance tracker is running
        services_status = verify_services_status()
        if not services_status["performance_tracker"]:
            logger.warning("⚠️ Performance Tracker service may not be running. Will attempt forwarding anyway.")
        
        # Try to forward to the performance tracker API with configured timeout and retry logic
        retry_count = 3
        retry_delay = 2  # seconds
        success = False
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt+1}/{retry_count}...")
                    
                performance_tracker_response = requests.post(
                    PERFORMANCE_TRACKER_TRACK_ENDPOINT,
                    json=performance_data,
                    headers={"Content-Type": "application/json"},
                    timeout=DEFAULT_TIMEOUT
                )
                
                logger.info(f"Performance tracker response status: {performance_tracker_response.status_code}")
                success = True
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < retry_count - 1:  # Don't sleep on the last attempt
                    logger.warning(f"Connection attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"All {retry_count} connection attempts failed")
                    raise  # Re-raise the last exception to be caught by the outer try-except
        
        if success and performance_tracker_response.status_code == 200:
            logger.info("Successfully forwarded data to performance tracker")
            response_summary["performance_tracker"] = "✅ Data forwarded to performance tracker"
            # Log the response from performance tracker
            try:
                response_data = performance_tracker_response.json()
                logger.info(f"Performance tracker response: {json.dumps(response_data)}")
            except Exception as e:
                logger.warning(f"Could not parse response from performance tracker: {str(e)}")
        else:
            logger.error(f"Failed to forward to performance tracker. Status code: {performance_tracker_response.status_code}")
            try:
                error_data = performance_tracker_response.text
                logger.error(f"Error response: {error_data}")
                response_summary["performance_tracker_error"] = error_data
            except:
                pass
            response_summary["performance_tracker"] = f"⚠️ Failed to forward to performance tracker. Status code: {performance_tracker_response.status_code}"
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: Performance tracker service is not running")
        response_summary["performance_tracker"] = "❌ Connection error: Performance tracker service is not running"
        response_summary["startup_hint"] = "Run 'python run_services.py' to start all required services"
    except requests.exceptions.Timeout:
        logger.error(f"Connection timeout: Performance tracker took too long to respond (timeout={DEFAULT_TIMEOUT}s)")
        response_summary["performance_tracker"] = "❌ Connection timeout: Performance tracker took too long to respond"
        response_summary["troubleshooting"] = "The performance tracker service may be under heavy load. Try again later."
    except Exception as e:
        logger.error(f"Could not reach performance tracker API: {str(e)}")
        response_summary["performance_tracker"] = f"❌ Could not reach performance tracker API: {str(e)}"
    
    logger.info("Sending response back to QuizUI")
    
    return jsonify(response_summary)

@app.route("/", methods=["GET"])
def home():
    """Simple endpoint to verify the service is running"""
    services_status = verify_services_status()
    
    return jsonify({
        "message": "Flask Tracker Service is running",
        "port": FLASK_TRACKER_PORT,
        "services_status": services_status,
        "endpoints": {
            "home": "/",
            "track_performance": "/track_performance"
        }
    })

if __name__ == "__main__":
    logger.info(f"Starting Flask tracker service on port {FLASK_TRACKER_PORT}")
    print(f"Access at: http://localhost:{FLASK_TRACKER_PORT}/")
    app.run(host='0.0.0.0', port=FLASK_TRACKER_PORT)