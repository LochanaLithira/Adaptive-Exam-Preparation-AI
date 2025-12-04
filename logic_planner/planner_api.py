from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import IndexModel
from datetime import datetime
from pymongo.errors import PyMongoError
from bson import ObjectId
from utils.config import get_database, COLLECTIONS
from utils.api_config import DEFAULT_TIMEOUT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Planner Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

db = get_database()
if db is None: 
    raise RuntimeError("MongoDB connection failed")

# Define all collections
user_plans_collection = db[COLLECTIONS.get("user_plans", "user_plans")]
plan_progress_collection = db[COLLECTIONS.get("plan_progress", "plan_progress")]
quiz_results_collection = db[COLLECTIONS.get("quiz_results", "quiz_results")]  # ← ADDED THIS

# Ensure indexes
user_plans_collection.create_indexes([IndexModel([("user_id", 1)], name="idx_user_plans_user_id")])
plan_progress_collection.create_indexes([
    IndexModel([("user_id", 1), ("plan_id", 1), ("day", 1), ("topic", 1)], name="idx_progress_unique_key", unique=True),
    IndexModel([("user_id", 1)], name="idx_progress_user_id"),
    IndexModel([("plan_id", 1)], name="idx_progress_plan_id"),
])

@app.get("/ping")
async def ping(): 
    return {"status": "ok", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}

@app.post("/send_weak_data")
async def receive_weak_data(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        free_days = data.get("free_days", [])
        subjects = data.get("subjects", [])
        
        logger.info(f"📥 Received weak data for user: {user_id}")
        logger.info(f"📅 Free days: {len(free_days)}")
        logger.info(f"📚 Subjects: {subjects}")
        
        if not user_id:
            return JSONResponse({"error": "Missing user_id"}, 400)
        
        if not free_days:
            return JSONResponse({"error": "Missing free_days. Please select available study days."}, 400)
        
        if not subjects:
            return JSONResponse({"error": "No subjects found. Complete some quizzes first."}, 400)
        
        # Extract all weak topics from all subjects
        all_topics = []
        for s in subjects:
            subject_name = s.get("subject", "General")
            weak_areas = s.get("weak_areas", [])
            accuracy = s.get("accuracy", 0)
            
            for topic in weak_areas:
                all_topics.append({
                    "subject": subject_name,
                    "topic": topic,
                    "accuracy": accuracy
                })
        
        if not all_topics:
            # No weak areas identified - use all topics with low scores
            logger.warning("⚠️ No weak areas in subjects, checking all topics...")
            
            # Get topics from the request if available
            all_topics_data = data.get("topics", [])
            for topic_data in all_topics_data:
                if topic_data.get("average_score", 100) < 70:  # Only topics scoring below 70
                    all_topics.append({
                        "subject": topic_data.get("subject", "General"),
                        "topic": topic_data.get("name", "Unknown"),
                        "accuracy": topic_data.get("average_score", 0)
                    })
        
        if not all_topics:
            return JSONResponse({
                "error": "No weak areas found. All topics are performing well!",
                "message": "Complete more quizzes or try challenging topics."
            }, 400)
        
        logger.info(f"✅ Processing {len(all_topics)} weak topics")
        
        # Save to database
        plan_data = {
            "user_id": user_id,
            "subjects": subjects,
            "topics": all_topics,
            "free_days": free_days,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        
        user_plans_collection.update_one(
            {"user_id": user_id},
            {"$set": plan_data},
            upsert=True
        )
        
        # Generate study plan
        plan = generate_study_plan(all_topics, free_days)
        
        logger.info(f"✅ Generated plan with {len(plan)} days")
        
        return {
            "user_id": user_id,
            "plan": plan,
            "total_days": len(free_days),
            "total_topics": len(all_topics),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error in send_weak_data: {str(e)}")
        return JSONResponse({
            "error": f"Internal server error: {str(e)}"
        }, 500)

def generate_study_plan(topics, free_days):
    plan = []
    sorted_topics = sorted(topics, key=lambda x: x.get("accuracy", 0))
    topics_per_day = max(1, len(sorted_topics) // len(free_days))
    day_index = 0
    topic_index = 0
    
    while topic_index < len(sorted_topics) and day_index < len(free_days):
        topic_info = sorted_topics[topic_index]
        day_data = free_days[day_index]
        activities = ["Learn", "Practice", "Review"]
        resources = ["Video", "Worksheet", "Notes"]
        
        plan.append({
            "day": day_index + 1,
            "subject": topic_info["subject"],
            "topic": topic_info["topic"],
            "activity": activities[topic_index % 3],
            "resource": resources[topic_index % 3],
            "date": day_data.get("date", "Unknown"),
            "time": day_data.get("available_time", "Full day"),
            "accuracy": topic_info.get("accuracy", 0)
        })
        
        topic_index += 1
        day_index = day_index + 1 if topic_index % topics_per_day == 0 else day_index
    
    return plan

@app.get("/get_plan/{user_id}")
async def get_plan(user_id: str):
    """
    Get study plan for a user. 
    First checks user_plans collection, then generates from quiz_results if needed.
    """
    logger.info(f"🔍 Looking for user_id: {user_id}")
    
    # First, try to find existing plan
    plan_data = user_plans_collection.find_one({"user_id": user_id})
    
    # If no plan exists, generate from quiz_results
    if not plan_data:
        logger.info(f"📊 No plan found, checking quiz_results...")
        
        # Get quiz results for this user - try both string and ObjectId
        quiz_results = list(quiz_results_collection.find({"user_id": user_id}))
        
        logger.info(f"✅ Found {len(quiz_results)} quiz results with string user_id")
        
        if not quiz_results:
            # Try with ObjectId format
            try:
                quiz_results = list(quiz_results_collection.find({"user_id": ObjectId(user_id)}))
                logger.info(f"✅ Found {len(quiz_results)} quiz results using ObjectId")
            except Exception as e:
                logger.error(f"❌ Error with ObjectId: {e}")
        
        if not quiz_results:
            # Check if there's any data in the collection at all
            total_count = quiz_results_collection.count_documents({})
            sample_quiz = quiz_results_collection.find_one()
            
            logger.warning(f"📋 Total quizzes in DB: {total_count}")
            logger.warning(f"📋 Sample quiz document: {sample_quiz}")
            
            return {
                "user_id": user_id,
                "subjects": [],
                "topics": [],
                "weak_areas": [],  # Added for compatibility
                "last_updated": None,
                "message": "No quiz data found. Complete quizzes to generate a study plan."
            }
        
        # Generate plan from quiz results - GROUP BY SUBJECT
        subjects_dict = {}
        
        for quiz in quiz_results:
            # Extract subject (handle multiple field names)
            subject = (
                quiz.get("subject") or 
                quiz.get("Subject") or 
                quiz.get("Topic", "").split("/")[0].strip() or
                "General"
            )
            
            # Extract topic
            topic_full = quiz.get("topic") or quiz.get("Topic") or "Unknown Topic"
            
            # If topic contains subject prefix, remove it
            if "/" in topic_full:
                topic = topic_full.split("/")[-1].strip()
            else:
                topic = topic_full
            
            # Get score (handle multiple field names)
            score = float(
                quiz.get("score") or 
                quiz.get("Score") or 
                quiz.get("accuracy") or 
                0
            )
            
            # Initialize subject if not exists
            if subject not in subjects_dict:
                subjects_dict[subject] = {
                    "subject": subject,
                    "topics": {},
                    "total_attempts": 0,
                    "total_score": 0
                }
            
            # Add topic data
            if topic not in subjects_dict[subject]["topics"]:
                subjects_dict[subject]["topics"][topic] = {
                    "name": topic,
                    "total_score": 0,
                    "attempts": 0
                }
            
            subjects_dict[subject]["topics"][topic]["total_score"] += score
            subjects_dict[subject]["topics"][topic]["attempts"] += 1
            subjects_dict[subject]["total_attempts"] += 1
            subjects_dict[subject]["total_score"] += score
        
        # Build response with weak areas per subject
        subjects_list = []
        all_topics = []
        
        for subject_name, subject_data in subjects_dict.items():
            weak_areas = []
            
            for topic_name, topic_data in subject_data["topics"].items():
                avg_score = topic_data["total_score"] / topic_data["attempts"]
                
                topic_info = {
                    "name": topic_name,
                    "average_score": round(avg_score, 2),
                    "attempts": topic_data["attempts"],
                    "subject": subject_name,
                    "status": "weak" if avg_score < 60 else "moderate" if avg_score < 80 else "strong"
                }
                
                all_topics.append(topic_info)
                
                # Add to weak areas if score < 70
                if avg_score < 70:
                    weak_areas.append(topic_name)
            
            # Calculate subject accuracy
            subject_accuracy = (
                subject_data["total_score"] / subject_data["total_attempts"]
                if subject_data["total_attempts"] > 0 else 0
            )
            
            subjects_list.append({
                "subject": subject_name,
                "accuracy": round(subject_accuracy, 2),
                "weak_areas": weak_areas,
                "total_topics": len(subject_data["topics"]),
                "attempts": subject_data["total_attempts"]
            })
        
        # Sort topics by score (weakest first)
        all_topics.sort(key=lambda x: x["average_score"])
        
        # Sort subjects by accuracy (weakest first)
        subjects_list.sort(key=lambda x: x["accuracy"])
        
        logger.info(f"✅ Generated plan with {len(all_topics)} topics from {len(quiz_results)} quiz attempts")
        
        return {
            "user_id": user_id,
            "subjects": subjects_list,  # Changed format to include weak_areas
            "topics": all_topics,
            "last_updated": datetime.utcnow().isoformat(),
            "message": f"Generated from {len(quiz_results)} quiz attempts"
        }
    
    # Plan exists in database
    plan_data.pop("_id", None)
    
    # Handle last_updated field safely
    last_updated = plan_data.get("last_updated")
    if isinstance(last_updated, datetime):
        last_updated = last_updated.isoformat()
    
    return {
        "user_id": user_id,
        "subjects": plan_data.get("subjects", []),
        "topics": plan_data.get("topics", []),
        "last_updated": last_updated
    }

@app.post("/update_progress")
async def update_progress(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    plan_id = data.get("plan_id")
    day = data.get("day")
    topic = data.get("topic")
    
    if not all([user_id, plan_id, day, topic]): 
        return JSONResponse({"error": "Missing required fields"}, 400)
    
    try:
        progress_data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "day": day,
            "topic": topic,
            "time_spent_minutes": data.get("time_spent_minutes", 0),
            "completed": data.get("completed", False),
            "last_updated": datetime.utcnow()
        }
        
        plan_progress_collection.update_one(
            {"user_id": user_id, "plan_id": plan_id, "day": day, "topic": topic},
            {"$set": progress_data},
            upsert=True
        )
        
        return {
            "success": True,
            "overall_progress": calculate_plan_progress(user_id, plan_id)
        }
    except PyMongoError as e: 
        return JSONResponse({"error": str(e)}, 500)

@app.get("/get_progress/{user_id}/{plan_id}")
async def get_progress(user_id: str, plan_id: str):
    records = list(plan_progress_collection.find({"user_id": user_id, "plan_id": plan_id}))
    for r in records: 
        r.pop("_id", None)
    
    return {
        "progress_records": records,
        "overall_progress": calculate_plan_progress(user_id, plan_id)
    }

def calculate_plan_progress(user_id: str, plan_id: str) -> float:
    try:
        records = list(plan_progress_collection.find({"user_id": user_id, "plan_id": plan_id}))
        if not records: 
            return 0.0
        
        completed = sum(1 for r in records if r.get("completed"))
        return round((completed / len(records)) * 100, 2)
    except Exception as e:
        logger.error(f"Error calculating progress: {e}")
        return 0.0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)