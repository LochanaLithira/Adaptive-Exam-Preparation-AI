from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from utils.config import get_database, COLLECTIONS
import logging
import os
import json
import pymongo.errors

# Import API configuration
from utils.api_config import PERFORMANCE_TRACKER_PORT, verify_services_status

# Import LLM service
from services.llm_service import generate_explanation

# Configure logging - only log to console, not to files
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("performance_tracker")
logger.info("Logging to console only")

app = FastAPI(title="Performance Tracker Agent")

# Log when the server starts
logger.info("Performance Tracker Agent starting up")

# -----------------------------
# MongoDB connection
# -----------------------------
db = get_database()
if db is None:
    logger.error("MongoDB connection failed. Check MongoDB connection settings.")
    raise Exception("MongoDB connection failed")
    
# Log successful connection
logger.info("MongoDB connection established successfully")

# Verify MongoDB connection with a ping test
try:
    # Ping the database to verify connection is working
    db.command('ping')
    logger.info("MongoDB connection successful! Database connection verified.")
    
    # Get database information for debugging
    db_stats = db.command("dbStats")
    logger.info(f"Connected to MongoDB database: {db.name}")
    logger.info(f"Database contains {db_stats.get('collections', 'unknown')} collections")
    
    # Check if the quiz_results collection exists
    if COLLECTIONS["quiz_results"] in db.list_collection_names():
        logger.info(f"Collection '{COLLECTIONS['quiz_results']}' exists in database")
    else:
        logger.warning(f"Collection '{COLLECTIONS['quiz_results']}' does not exist yet - it will be created automatically")
    
except pymongo.errors.ConnectionFailure as e:
    logger.error(f"MongoDB server not available. Error: {str(e)}")
    raise Exception(f"MongoDB server not available: {str(e)}")
except Exception as e:
    logger.error(f"Error verifying MongoDB connection: {str(e)}")
    raise Exception(f"Error verifying MongoDB connection: {str(e)}")

# Get collection for quiz results
results_col = db[COLLECTIONS["quiz_results"]]

# -----------------------------
# Function to test database writes
# -----------------------------
def test_database_write():
    """Test function to verify database write capability"""
    try:
        test_doc = {
            "test": True,
            "timestamp": logging.Formatter().converter(),
            "message": "Database write test"
        }
        result = results_col.insert_one(test_doc)
        if result.acknowledged:
            logger.info(f"Database write test successful. Test document ID: {result.inserted_id}")
            # Clean up test document
            results_col.delete_one({"_id": result.inserted_id})
            return True
        else:
            logger.error("Database write test failed: insertion not acknowledged")
            return False
    except Exception as e:
        logger.error(f"Database write test failed: {str(e)}", exc_info=True)
        return False

# Run database write test at startup
if test_database_write():
    logger.info("SUCCESS: Database connectivity and write permissions confirmed")
else:
    logger.error("ERROR: Database write test failed - check MongoDB permissions and connection")

# -----------------------------
# Pydantic model for input
# -----------------------------
class QuizResult(BaseModel):
    user_id: str  # Changed from int to str to handle MongoDB ObjectIds
    quiz_id: int
    topic: str
    answers: dict           # {"Q1": "A"}
    correct_answers: dict   # {"Q1": "B"}
    questions_text: dict    # {"Q1": "What is 2+2?"}

# -----------------------------
# Core MCQ evaluation function
# -----------------------------
def evaluate_mcq(answers: dict, correct_answers: dict):
    score = 0
    wrong_questions = {}

    for q_id, student_ans in answers.items():
        correct_ans = correct_answers.get(q_id)
        if student_ans == correct_ans:
            score += 1
        else:
            wrong_questions[q_id] = correct_ans

    total = len(correct_answers)
    accuracy = (score / total) * 100
    feedback = f"You scored {score}/{total} ({accuracy:.2f}%)."
    if wrong_questions:
        feedback += f" Review questions: {', '.join(wrong_questions.keys())}"

    return score, total, accuracy, feedback, wrong_questions

# -----------------------------
# Generate LLM explanations
# -----------------------------
def generate_feedback_with_llm(answers, correct_answers, questions_text):
    explanations = {}
    for q_id, student_ans in answers.items():
        correct_ans = correct_answers.get(q_id)
        if student_ans != correct_ans:
            question_text = questions_text.get(q_id, "")
            explanations[q_id] = generate_explanation(question_text, student_ans, correct_ans)
    return explanations

# -----------------------------
# FastAPI POST endpoint
# -----------------------------
@app.post("/track")
async def track_performance(data: QuizResult, request: Request):
    try:
        # Log the received request
        logger.info(f"Received performance tracking request for user {data.user_id}")
        logger.info(f"Quiz topic: {data.topic}, Quiz ID: {data.quiz_id}")
        logger.info(f"Number of answers: {len(data.answers)}")
        
        # No need for raw request logging in production
        
        # Validate the data
        if not data.answers or not data.correct_answers or not data.questions_text:
            error_msg = "Missing required quiz data (answers, correct_answers, or questions_text)"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info("Evaluating quiz results...")
        # Evaluate MCQs
        score, total, accuracy, feedback, wrong_questions = evaluate_mcq(
            data.answers, data.correct_answers
        )
        
        logger.info(f"Evaluation complete: {score}/{total} ({accuracy:.2f}%)")
        
        # Generate explanations for wrong answers using LLM
        logger.info(f"Generating explanations for {len(wrong_questions)} wrong answers")
        try:
            explanations = generate_feedback_with_llm(
                data.answers, data.correct_answers, data.questions_text
            )
            logger.info(f"Generated {len(explanations)} explanations")
        except Exception as e:
            logger.error(f"Error generating explanations: {str(e)}")
            explanations = {"error": f"Failed to generate explanations: {str(e)}"}

        # Prepare result
        result = {
            "score": score,
            "total": total,
            "accuracy": accuracy,
            "feedback": feedback,
            "wrong_questions": wrong_questions,
            "explanations": explanations
        }

        # Save to MongoDB
        try:
            logger.info("Saving results to MongoDB...")
            
            # Debug: Print database and collection information
            db_name = db.name
            col_name = results_col.name
            logger.info(f"Using database: {db_name}, collection: {col_name}")
            
            # Create document to insert
            document = {
                "user_id": data.user_id,
                "quiz_id": data.quiz_id,
                "topic": data.topic,
                "answers": data.answers,
                "correct_answers": data.correct_answers,  # Store correct answers for reference
                "result": result,
                "timestamp": logging.Formatter().converter()  # Add timestamp
            }
            
            # Debug: Log the document structure before insertion
            logger.info(f"Attempting to insert document with structure: user_id={data.user_id}, quiz_id={data.quiz_id}, topic={data.topic}, answers count={len(data.answers)}")
            
            # Use insert_one with explicit write concern to ensure proper write operations
            insert_result = results_col.insert_one(
                document, 
                bypass_document_validation=False
            )
            
            if insert_result.acknowledged:
                logger.info(f"Results saved to MongoDB with ID: {insert_result.inserted_id}")
                # Add the MongoDB ID to the result
                result["_id"] = str(insert_result.inserted_id)
                result["db_save_status"] = "success"
            else:
                logger.error("MongoDB insert was not acknowledged!")
                result["db_save_status"] = "not_acknowledged"
                
        except pymongo.errors.PyMongoError as pme:
            # Specific MongoDB errors handling
            logger.error(f"MongoDB error: {str(pme)}")
            logger.error(f"Error type: {type(pme).__name__}")
            result["db_save_error"] = f"MongoDB error: {str(pme)}"
            result["db_save_status"] = "error"
            
        except Exception as db_error:
            # Catch-all for other errors
            logger.error(f"Failed to save to MongoDB: {str(db_error)}", exc_info=True)
            logger.error(f"Error type: {type(db_error).__name__}")
            # Continue execution to return the result even if DB save fails
            result["db_save_error"] = str(db_error)
            result["db_save_status"] = "error"

        # Add timestamp and debug info to result
        result["timestamp"] = str(logging.Formatter().converter())
        result["debug_info"] = {
            "log_file": os.path.abspath("performance_tracker_debug.log"),
            "timestamp": logging.Formatter().converter()
        }
        
        # Create an appropriate status based on database operations
        status = "success"
        if "db_save_error" in result:
            status = "partial_success"
            logger.warning("Returning partial success response (had database errors)")
        else:
            logger.info("Returning success response")
            
        return {
            "status": status, 
            "data": result
        }

    except Exception as e:
        logger.error(f"Error processing performance tracking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
        
# -----------------------------
# Test endpoint to verify service is running
# -----------------------------
@app.get("/ping")
def ping():
    """Simple endpoint to verify the service is running"""
    logger.info("Ping received")
    return {"status": "ok", "message": "Performance Tracker Agent is running"}
    
# -----------------------------
# Test endpoint to verify database connection
# -----------------------------
# Test endpoints have been removed for production
