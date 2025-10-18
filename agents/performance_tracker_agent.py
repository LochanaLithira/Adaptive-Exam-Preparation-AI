from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from utils.config import get_database, COLLECTIONS
import logging
import os
import json
import pymongo.errors
import requests

# Import API configuration
from utils.api_config import PERFORMANCE_TRACKER_PORT, verify_services_status, PLANNER_AGENT_ENDPOINT, DEFAULT_TIMEOUT

# Import LLM service
from services.llm_service import GeminiClient

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

# Initialize LLM client
llm_client = GeminiClient()

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
class QuestionDetail(BaseModel):
    question_id: str
    topic: str
    subject: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    options: dict = {}  # Dictionary containing option letters and their text

class QuizResult(BaseModel):
    user_id: str  # Changed from int to str to handle MongoDB ObjectIds
    quiz_id: int
    subject: str = "Unknown"  # Main subject area (Science, Math, English)
    questions_details: list[QuestionDetail]  # Detailed question-level data with topic mapping

# -----------------------------
# Core MCQ evaluation function (new structure)
# -----------------------------
def evaluate_mcq_detailed(questions_details: list) -> tuple:
    score = 0
    total = len(questions_details)
    wrong_questions = {}
    topic_performance = {}
    
    # Calculate overall score and topic-specific performance
    for question in questions_details:
        if question.is_correct:
            score += 1
        else:
            wrong_questions[question.question_id] = {
                "correct_answer": question.correct_answer,
                "user_answer": question.user_answer,
                "topic": question.topic
            }
        
        # Track performance by topic
        topic = question.topic
        if topic not in topic_performance:
            topic_performance[topic] = {"correct": 0, "total": 0}
        
        topic_performance[topic]["total"] += 1
        if question.is_correct:
            topic_performance[topic]["correct"] += 1
    
    accuracy = (score / total) * 100 if total > 0 else 0
    feedback = f"You scored {score}/{total} ({accuracy:.2f}%)."
    
    if wrong_questions:
        feedback += f" Review questions: {', '.join(wrong_questions.keys())}"
    
    # Add topic-specific feedback
    if topic_performance:
        feedback += "\n\nTopic Performance:"
        for topic, perf in topic_performance.items():
            topic_accuracy = (perf["correct"] / perf["total"]) * 100
            feedback += f"\n- {topic}: {perf['correct']}/{perf['total']} ({topic_accuracy:.1f}%)"

    return score, total, accuracy, feedback, wrong_questions, topic_performance

# -----------------------------
# Legacy MCQ evaluation function (for backward compatibility)
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
def generate_feedback_with_llm_detailed(questions_details: list):
    explanations = {}
    
    # Filter to get only incorrect questions
    wrong_questions = [q for q in questions_details if not q.is_correct]
    
    # If there are no wrong questions, return empty explanations
    if not wrong_questions:
        logger.info("No wrong answers to explain")
        return explanations
    
    # If there's only one wrong answer, use the original approach
    if len(wrong_questions) == 1:
        q = wrong_questions[0]
        explanations[q.question_id] = llm_client.generate_explanation(
            q.question_text, 
            q.user_answer, 
            q.correct_answer
        )
        return explanations
    
    logger.info(f"Generating explanations for {len(wrong_questions)} wrong answers using batch processing")
    
    # BATCH PROCESSING: Build one prompt for all wrong questions
    batch_prompt = "For each of the following questions, explain why the student's answer is incorrect and provide a clear explanation of the correct answer:\n\n"
    
    # Keep track of questions to map responses back correctly
    for i, question in enumerate(wrong_questions, 1):
        batch_prompt += f"Question {i}: {question.question_text}\n"
        batch_prompt += f"Student answered: {question.user_answer}\n"
        batch_prompt += f"Correct answer: {question.correct_answer}\n\n"
    
    batch_prompt += "Provide numbered explanations for each question above. Format each explanation as 'Explanation 1:', 'Explanation 2:', etc., followed by your detailed explanation."
    
    try:
        # Make a single LLM call for all questions
        logger.info("Making batch LLM call for explanations")
        response = llm_client.client.models.generate_content(
            model=llm_client.model,
            contents=batch_prompt
        )
        
        full_explanation = getattr(response, "text", None) or str(response)
        logger.info("Successfully received batch explanations from LLM")
        
        # Parse the combined response back into individual explanations
        import re
        # Use regex to split by "Explanation X:" headers
        explanation_parts = re.split(r"Explanation (\d+):", full_explanation)
        
        # The first item will be any text before the first "Explanation X:" - discard it
        if explanation_parts and explanation_parts[0].strip():
            logger.info(f"Discarded prefix text: {explanation_parts[0][:50]}...")
        
        # Process the split parts (first part is empty or intro text)
        for i in range(1, len(explanation_parts), 2):
            try:
                question_num = int(explanation_parts[i]) - 1  # Convert to zero-based index
                if 0 <= question_num < len(wrong_questions):
                    explanation_text = explanation_parts[i+1].strip()
                    question_id = wrong_questions[question_num].question_id
                    explanations[question_id] = explanation_text
                    logger.info(f"Successfully parsed explanation for question {question_id}")
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing explanation part {i}: {str(e)}")
        
        # Check if we got explanations for all wrong answers
        missing_explanations = [q.question_id for i, q in enumerate(wrong_questions) 
                               if q.question_id not in explanations]
        
        # If any explanations are missing, fall back to individual processing for those
        if missing_explanations:
            logger.warning(f"Missing explanations for {len(missing_explanations)} questions. Falling back to individual processing.")
            
            for q in wrong_questions:
                if q.question_id in missing_explanations:
                    try:
                        explanations[q.question_id] = llm_client.generate_explanation(
                            q.question_text, 
                            q.user_answer, 
                            q.correct_answer
                        )
                        logger.info(f"Generated individual explanation for question {q.question_id}")
                    except Exception as e:
                        logger.error(f"Failed to generate individual explanation: {str(e)}")
                        explanations[q.question_id] = "Could not generate explanation due to an error."
            
    except Exception as e:
        logger.error(f"Error in batch explanation generation: {str(e)}")
        
        # Fallback to individual processing if batch fails
        logger.info("Falling back to individual explanation generation for all questions")
        
        for question in wrong_questions:
            try:
                explanations[question.question_id] = llm_client.generate_explanation(
                    question.question_text, 
                    question.user_answer, 
                    question.correct_answer
                )
                logger.info(f"Generated fallback explanation for question {question.question_id}")
            except Exception as inner_e:
                logger.error(f"Individual explanation failed for question {question.question_id}: {str(inner_e)}")
                explanations[question.question_id] = "Could not generate explanation due to an error."
    
    return explanations

# -----------------------------
# Legacy LLM feedback function (for backward compatibility)
# -----------------------------
def generate_feedback_with_llm(answers, correct_answers, questions_text):
    explanations = {}
    wrong_questions = []
    
    # Collect all wrong answers for batch processing
    for q_id, student_ans in answers.items():
        correct_ans = correct_answers.get(q_id)
        if student_ans != correct_ans:
            question_text = questions_text.get(q_id, "")
            wrong_questions.append({
                'q_id': q_id,
                'question': question_text,
                'student_ans': student_ans,
                'correct_ans': correct_ans
            })
    
    # If there are wrong answers, generate explanations individually (for now)
    # TODO: Implement batch processing to reduce API calls
    for item in wrong_questions:
        explanations[item['q_id']] = llm_client.generate_explanation(
            item['question'], item['student_ans'], item['correct_ans']
        )
    
    return explanations

# -----------------------------
# Helper Functions for Planner Integration
# -----------------------------
def extract_topic_from_question(question_text: str) -> str:
    """
    Extract meaningful topic/area from question text
    Enhanced version with better keyword matching and prioritized specific topics
    """
    question_lower = question_text.lower()
    
    # Define topic keywords with priority (more specific first)
    topic_keywords = {
        # Specific Science topics (higher priority)
        'electrochemistry': ['electrochemistry', 'battery', 'electrode', 'electrolyte', 'ion', 'electrochemical', 'galvanic', 'voltaic'],
        'photosynthesis': ['photosynthesis', 'chlorophyll', 'glucose', 'sunlight', 'carbon dioxide', 'plant', 'leaf'],
        'molecular_structure': ['molecular', 'structure', 'formula', 'h2o', 'water', 'molecule', 'bond'],
        
        # General Science topics
        'chemistry': ['chemical', 'reaction', 'atom', 'element', 'compound', 'acid', 'base', 'solution'],
        'physics': ['force', 'energy', 'motion', 'wave', 'electricity', 'magnetic', 'gravity', 'mass'],
        'biology': ['cell', 'organism', 'dna', 'gene', 'evolution', 'ecosystem', 'animal', 'living'],
        
        # Math topics  
        'algebra': ['variable', 'equation', 'solve', 'x', 'y', 'polynomial', 'linear'],
        'geometry': ['angle', 'triangle', 'circle', 'area', 'volume', 'perimeter', 'shape'],
        'calculus': ['derivative', 'integral', 'limit', 'function', 'graph', 'slope'],
        'statistics': ['probability', 'mean', 'median', 'data', 'distribution', 'average'],
        
        # General topics
        'problem_solving': ['explain', 'principle', 'process', 'how', 'why', 'describe'],
        'fundamentals': ['basic', 'definition', 'concept', 'theory', 'fundamental']
    }
    
    # Find matching topics (prioritize more specific ones first)
    matched_topics = []
    for topic, keywords in topic_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in question_lower)
        if matches > 0:
            matched_topics.append((topic, matches))
    
    # Return the topic with most matches, or first match if tied
    if matched_topics:
        # Sort by number of matches (descending) and return the best match
        matched_topics.sort(key=lambda x: x[1], reverse=True)
        best_topic = matched_topics[0][0]
        # Convert to proper case (e.g., "molecular_structure" -> "Molecular Structure")
        return best_topic.replace('_', ' ').title()
    
    # Enhanced fallback: extract meaningful subject-specific terms
    words = question_text.split()
    meaningful_words = []
    for word in words[:10]:  # Check first 10 words
        word_clean = word.lower().strip('.,?!:;')
        if len(word_clean) > 4 and word_clean not in ['what', 'explain', 'describe', 'which', 'basic']:
            meaningful_words.append(word_clean.capitalize())
    
    if meaningful_words:
        return " ".join(meaningful_words[:2])
    
    return "General Concepts"

async def get_historical_weak_areas(user_id: str, subject: str = None) -> list:
    """
    Get historical weak areas for a user across all topics
    Uses the same logic as Performance UI (topics with average < 60%)
    """
    try:
        # Query user's historical performance - get ALL results like PerformanceUI does
        results_col = db[COLLECTIONS["quiz_results"]]
        
        # Get all results for this user (not filtered by subject)
        cursor = results_col.find({
            "user_id": user_id
        }).sort("_id", -1).limit(50)  # Last 50 quizzes for better data
        
        results = list(cursor)
        
        if not results:
            return []
        
        # Calculate topic performance (EXACT same logic as PerformanceUI)
        topic_performance = {}
        for result in results:
            # Handle both new format (questions_details) and old format (topic field)
            questions_details = result.get("questions_details", [])
            
            if questions_details:
                # New format: extract topics from questions_details
                # Count questions and correct answers per topic (SAME as PerformanceUI)
                topic_stats = {}
                
                for question in questions_details:
                    topic = question.get("topic", "Unknown")
                    is_correct = question.get("is_correct", False)
                    
                    if topic not in topic_stats:
                        topic_stats[topic] = {"questions": 0, "correct": 0}
                    
                    topic_stats[topic]["questions"] += 1
                    if is_correct:
                        topic_stats[topic]["correct"] += 1
                
                # Add topic performance data (SAME as PerformanceUI)
                for topic, stats in topic_stats.items():
                    if topic not in topic_performance:
                        topic_performance[topic] = {"scores": [], "total_questions": 0, "correct_answers": 0}
                    
                    # Calculate accuracy for this topic in this quiz
                    topic_accuracy = (stats["correct"] / stats["questions"]) * 100 if stats["questions"] > 0 else 0
                    
                    topic_performance[topic]["scores"].append(topic_accuracy)
                    topic_performance[topic]["total_questions"] += stats["questions"]
                    topic_performance[topic]["correct_answers"] += stats["correct"]
            else:
                # Fallback to old format for backward compatibility
                topic = result.get("topic", "Unknown")
                if topic not in topic_performance:
                    topic_performance[topic] = {"scores": [], "total_questions": 0, "correct_answers": 0}
                
                score = result.get("result", {}).get("score", 0)
                total = result.get("result", {}).get("total", 1)
                topic_performance[topic]["scores"].append((score / total) * 100)
                topic_performance[topic]["total_questions"] += total
                topic_performance[topic]["correct_answers"] += score
        
        # Calculate averages and find weak areas (< 60% average) - SAME as PerformanceUI
        weak_areas = []
        for topic, data in topic_performance.items():
            scores = data["scores"]
            average = sum(scores) / len(scores) if scores else 0
            data["average"] = average  # Store for consistency
            
            if average < 60:  # Same threshold as PerformanceUI
                weak_areas.append(topic)
        
        return weak_areas
        
    except Exception as e:
        logger.error(f"Error fetching historical weak areas: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

def get_default_weak_areas_for_subject(subject: str) -> list:
    """
    Get default weak areas when no specific areas are identified
    """
    default_areas = {
        'science': ['Scientific Method', 'Problem Solving'],
        'math': ['Mathematical Reasoning', 'Problem Solving'],
        'physics': ['Physics Concepts', 'Problem Solving'],
        'chemistry': ['Chemistry Concepts', 'Chemical Reactions'],
        'biology': ['Biology Concepts', 'Life Processes'],
        'english': ['Grammar', 'Reading Comprehension'],
        'history': ['Historical Analysis', 'Critical Thinking']
    }
    
    subject_lower = subject.lower()
    return default_areas.get(subject_lower, [f'{subject} Fundamentals'])

# -----------------------------
# Planner Integration Function
# -----------------------------
async def send_to_planner(subject: str, wrong_questions: list, questions_text: dict, user_id: str = None, debug_mode: bool = True):
    """
    Send performance data to planner API in the required format
    Uses both current quiz wrong answers and historical weak areas from Performance UI logic
    
    Args:
        subject: Subject name (e.g., "Science", "Math")
        wrong_questions: List of question IDs that were answered incorrectly
        questions_text: Dictionary mapping question IDs to question text
        user_id: User ID to get historical performance data
        debug_mode: Whether to log detailed debug information
    
    Returns:
        dict: Response from planner API or error information
    """
    try:
        # Get weak areas ONLY from "Areas for Improvement" (historical performance < 60%)
        weak_areas = []
        
        if user_id:
            try:
                weak_areas = await get_historical_weak_areas(user_id, subject)
            except Exception as e:
                weak_areas = []
        
        # If no Areas for Improvement found, create meaningful defaults based on subject
        if not weak_areas:
            weak_areas = get_default_weak_areas_for_subject(subject)
        
        # Format data for planner API
        planner_data = {
            "subjects": [
                {
                    "subject": subject,
                    "weak_areas": weak_areas  # Send ALL weak areas to planner
                }
            ]
        }
        
        # Always include user_id if provided
        if user_id is not None:
            planner_data["user_id"] = user_id
        
        # Make POST request to planner API
        response = requests.post(
            PLANNER_AGENT_ENDPOINT,
            json=planner_data,
            timeout=DEFAULT_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "planner_response": response.json(),
                "sent_data": planner_data
            }
        else:
            return {
                "success": False,
                "error": f"Planner API returned status {response.status_code}: {response.text}",
                "sent_data": planner_data
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to connect to planner API: {str(e)}",
            "sent_data": planner_data if 'planner_data' in locals() else {}
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error in planner integration: {str(e)}",
            "sent_data": planner_data if 'planner_data' in locals() else None
        }

# -----------------------------
# FastAPI POST endpoint
# -----------------------------
@app.post("/track")
async def track_performance(data: QuizResult, request: Request):
    try:
        # Validate the data
        if not data.questions_details:
            raise HTTPException(status_code=400, detail="Missing required quiz questions data")
        
        # Evaluate MCQs using new detailed structure
        score, total, accuracy, feedback, wrong_questions, topic_performance = evaluate_mcq_detailed(
            data.questions_details
        )
        
        # Generate explanations for wrong answers using LLM
        try:
            explanations = generate_feedback_with_llm_detailed(data.questions_details)
        except Exception as e:
            explanations = {"error": f"Failed to generate explanations: {str(e)}"}

        # Send to planner if there are wrong questions or always send for tracking
        planner_result = None
        if hasattr(data, 'subject') and data.subject:
            subject_name = data.subject
        else:
            # Fallback to topic if subject is not available
            subject_name = data.topic
            
        try:
            planner_result = await send_to_planner(
                subject=subject_name,
                wrong_questions=wrong_questions,
                questions_text=data.questions_text,
                user_id=data.user_id,
                debug_mode=False
            )
        except Exception as e:
            planner_result = {"success": False, "error": str(e)}

        # Prepare result
        result = {
            "score": score,
            "total": total,
            "accuracy": accuracy,
            "feedback": feedback,
            "wrong_questions": wrong_questions,
            "explanations": explanations,
            "planner_integration": planner_result  # Include planner result for debugging
        }

        # Save to MongoDB
        try:
            document = {
                "user_id": data.user_id,
                "quiz_id": data.quiz_id,
                "subject": data.subject,        # Main subject (Science, Math, English, etc.)
                "questions_details": [q.dict() for q in data.questions_details],  # Detailed question-level data
                "topic_performance": topic_performance,  # Performance breakdown by topic
                "result": result,
                "timestamp": logging.Formatter().converter()
            }
            
            insert_result = results_col.insert_one(document)
            
            if insert_result.acknowledged:
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
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# -----------------------------
# Test endpoint to verify service is running
# -----------------------------
@app.get("/ping")
def ping():
    """Simple endpoint to verify the service is running"""
    return {"status": "ok", "message": "Performance Tracker Agent is running"}

# -----------------------------
# Debug endpoint to test planner integration
# -----------------------------
@app.post("/debug/test_planner")
async def test_planner_integration(request: Request = None):
    """
    Debug endpoint to test planner integration with sample data
    Can accept user_id in request body to test with actual user
    """
    try:
        # Check if user_id is provided in request body
        test_user_id = "test_user_123"  # Default
        
        if request:
            try:
                body = await request.json()
                if body and "user_id" in body:
                    test_user_id = body["user_id"]
            except:
                pass  # Use default if no body or parsing fails
        
        # Get actual weak areas for the user instead of sample data
        if test_user_id != "test_user_123":
            # Use real user data - get their actual weak areas
            try:
                test_subject = "Science"
                actual_weak_topics = await get_historical_weak_areas(test_user_id, test_subject)
                
                if actual_weak_topics:
                    # Generate sample questions for actual weak areas
                    test_wrong_questions = [f"q_{i}" for i in range(min(3, len(actual_weak_topics)))]
                    test_questions_text = {}
                    for i, topic in enumerate(actual_weak_topics[:3]):
                        test_questions_text[f"q_{i}"] = f"Sample question about {topic} for testing planner integration"
                else:
                    # No historical data, use minimal sample
                    test_wrong_questions = ["q1"]
                    test_questions_text = {"q1": "No historical data available - sample question for testing"}
                
            except Exception as e:
                # Fallback to sample data
                test_subject = "Science"
                test_wrong_questions = ["q1"]
                test_questions_text = {"q1": "Error getting real data - sample question for testing"}
        else:
            # Use sample test data for test user
            test_subject = "Science"
            test_wrong_questions = ["q1", "q2", "q3"]
            test_questions_text = {
                "q1": "What is the chemical formula for water and its molecular structure?",
                "q2": "Explain the process of photosynthesis in plants and its importance?", 
                "q3": "What are the basic principles of electrochemistry and battery function?"
            }
        
        # Call planner integration with actual or sample data
        result = await send_to_planner(
            subject=test_subject,
            wrong_questions=test_wrong_questions,
            questions_text=test_questions_text,
            user_id=test_user_id,
            debug_mode=False
        )
        
        return {
            "status": "test_completed",
            "test_data": {
                "subject": test_subject,
                "wrong_questions": test_wrong_questions,
                "questions_sample": list(test_questions_text.values())
            },
            "planner_result": result
        }
        
    except Exception as e:
        return {
            "status": "test_failed",
            "error": str(e)
        }
    
# -----------------------------
# Test endpoint to verify database connection
# -----------------------------
# Test endpoints have been removed for production
