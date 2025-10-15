from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
from pymongo.errors import PyMongoError
from utils.api_config import PERFORMANCE_TRACKER_URL, DEFAULT_TIMEOUT
from utils.config import get_database, COLLECTIONS

app = FastAPI()

# Get MongoDB connection
db = get_database()
if db is None:
    raise RuntimeError("Failed to connect to MongoDB")

# Get or create user_plans collection
user_plans_collection = db[COLLECTIONS.get("user_plans", "user_plans")]
# Create index on user_id if it doesn't exist
user_plans_collection.create_index("user_id", unique=True)

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return JSONResponse({"status": "ok", "message": "Planner service is running"})

@app.post("/send_weak_data")
async def receive_weak_data(request: Request):
    data = await request.json()

    user_id = data.get("user_id")
    free_days = data.get("free_days", [])
    
    if not user_id:
        return JSONResponse({"error": "user_id missing"})

    # Get subjects and weak areas from the request data
    subjects = data.get("subjects", [])
    
    # Flatten weak areas into topics
    all_topics = []
    for subject in subjects:
        subject_name = subject.get("subject", "General")
        weak_areas = subject.get("weak_areas", [])
        for topic in weak_areas:
            all_topics.append({
                "subject": subject_name,
                "topic": topic
            })
    
    # If no performance data or weak areas found, return error
    if not all_topics:
        return JSONResponse({
            "error": "No performance data found in the request."
        })
    
    # Store the data in MongoDB
    try:
        plan_data = {
            "user_id": user_id,
            "subjects": subjects,
            "topics": all_topics,
            "last_updated": datetime.utcnow()
        }
        user_plans_collection.update_one(
            {"user_id": user_id},
            {"$set": plan_data},
            upsert=True
        )
    except PyMongoError as e:
        return JSONResponse({"error": f"Database error: {str(e)}"})

    # Generate plan based on free days
    plan = []
    topics_per_day = max(1, len(all_topics) // len(free_days)) if free_days else len(all_topics)
    
    day_index = 0
    topic_index = 0
    
    while topic_index < len(all_topics):
        topic_info = all_topics[topic_index]
        day_data = free_days[day_index] if free_days else {"date": "Today", "available_time": "Full day"}
        
        # Create plan entry
        plan_entry = {
            "subject": topic_info["subject"],
            "topic": topic_info["topic"],
            "activity": ["Learn", "Practice", "Review"][topic_index % 3],
            "resource": ["Video", "Worksheet", "Notes"][topic_index % 3],
            "date": day_data.get("date", "Today"),
            "time": day_data.get("available_time", "Full day")
        }
        plan.append(plan_entry)
        
        # Move to next topic and possibly next day
        topic_index += 1
        if topic_index % topics_per_day == 0:
            day_index = min(day_index + 1, len(free_days) - 1 if free_days else 0)
    
    print(f"Generated plan for user {user_id}: {plan}")
    return JSONResponse({"user_id": user_id, "plan": plan})


@app.get("/get_plan/{user_id}")
async def get_plan(user_id: str):
    try:
        # Fetch from MongoDB
        plan_data = user_plans_collection.find_one({"user_id": user_id})
        if not plan_data:
            return JSONResponse({"error": "No performance data found. Please complete some quizzes first."})
        
        # Return the subjects data directly
        return JSONResponse({
            "user_id": user_id,
            "subjects": plan_data.get("subjects", [])
        })
    except PyMongoError as e:
        return JSONResponse({"error": f"Database error: {str(e)}"})
