# logic_planner/plan_manager.py
import os
import json
from datetime import datetime

SAVE_FILE = "saved_plans.json"

def load_saved_plans(base_dir):
    """Load all saved plans from a single JSON file."""
    path = os.path.join(base_dir, SAVE_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_all_plans(base_dir, plans):
    """Save all plans back to JSON."""
    path = os.path.join(base_dir, SAVE_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=4, ensure_ascii=False)


def calculate_total_study_time(plan):
    """
    Sum total minutes based on schedule.
    Now uses ScheduleMinutes if available, falls back to activity counting.
    """
    total = 0
    for day in plan:
        # Try to get from ScheduleMinutes first (new format)
        if "ScheduleMinutes" in day:
            schedule_mins = day.get("ScheduleMinutes", {})
            total += sum(schedule_mins.values())
        # Fallback to old format (Learn=60, Practice=30, Review=15)
        elif "Schedule" in day:
            for s in day.get("Schedule", []):
                if "Learn" in s:
                    total += 60
                elif "Practice" in s:
                    total += 30
                elif "Review" in s:
                    total += 15
    return total


def initialize_progress_tracking(plan):
    """
    Initialize progress tracking structure for a plan.
    Returns dict with completion status for each day/topic.
    """
    progress = {
        "overall_completion": 0.0,
        "days": {}
    }
    
    # Group by day
    days_dict = {}
    for entry in plan:
        day_num = entry.get("Day", 1)
        if day_num not in days_dict:
            days_dict[day_num] = []
        days_dict[day_num].append(entry.get("Topic", "Unknown"))
    
    # Initialize tracking for each day
    for day_num, topics in days_dict.items():
        progress["days"][f"day_{day_num}"] = {
            "completed": False,
            "topics": topics,
            "topics_completed": [],
            "time_spent_minutes": 0,
            "completion_percentage": 0.0
        }
    
    return progress


def save_plan_to_storage(plan, weights, base_dir, user_id=None):
    """
    Save a new plan with completion status and total time.
    Enhanced with progress tracking and user_id support.
    """
    all_plans = load_saved_plans(base_dir)

    # --- Prevent duplicates (check by plan content) ---
    if any(existing["plan"] == plan for existing in all_plans):
        return False  # Already exists

    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    total_time = calculate_total_study_time(plan)
    progress = initialize_progress_tracking(plan)

    new_entry = {
        "user_id": user_id,
        "timestamp": timestamp,
        "weights": weights,
        "plan": plan,
        "progress": progress,
        "total_study_time_minutes": total_time,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

    all_plans.append(new_entry)
    save_all_plans(base_dir, all_plans)
    return True


def get_user_plans(base_dir, user_id):
    """
    Get all plans for a specific user.
    """
    all_plans = load_saved_plans(base_dir)
    return [plan for plan in all_plans if plan.get("user_id") == user_id]


def update_plan_progress(base_dir, plan_timestamp, day_num, topic, time_spent=0):
    """
    Update progress for a specific topic in a plan.
    
    Args:
        base_dir: Base directory for plan storage
        plan_timestamp: Timestamp of the plan to update
        day_num: Day number (1, 2, 3, ...)
        topic: Topic that was completed
        time_spent: Minutes spent on the topic
    
    Returns:
        bool: True if update successful, False otherwise
    """
    all_plans = load_saved_plans(base_dir)
    
    # Find the plan
    plan_found = False
    for plan_entry in all_plans:
        if plan_entry.get("timestamp") == plan_timestamp:
            plan_found = True
            
            # Update progress
            day_key = f"day_{day_num}"
            if day_key in plan_entry["progress"]["days"]:
                day_progress = plan_entry["progress"]["days"][day_key]
                
                # Add topic to completed list if not already there
                if topic not in day_progress["topics_completed"]:
                    day_progress["topics_completed"].append(topic)
                
                # Add time spent
                day_progress["time_spent_minutes"] += time_spent
                
                # Calculate day completion percentage
                total_topics = len(day_progress["topics"])
                completed_topics = len(day_progress["topics_completed"])
                day_progress["completion_percentage"] = (completed_topics / total_topics * 100) if total_topics > 0 else 0
                
                # Mark day as completed if all topics done
                if completed_topics >= total_topics:
                    day_progress["completed"] = True
                
                # Update overall completion
                plan_entry["progress"]["overall_completion"] = calculate_overall_completion(plan_entry["progress"])
                
                # Update last_updated timestamp
                plan_entry["last_updated"] = datetime.now().isoformat()
            
            break
    
    if plan_found:
        save_all_plans(base_dir, all_plans)
        return True
    return False


def calculate_overall_completion(progress):
    """
    Calculate overall completion percentage for a plan.
    """
    days = progress.get("days", {})
    if not days:
        return 0.0
    
    total_days = len(days)
    completed_days = sum(1 for day in days.values() if day.get("completed", False))
    
    return (completed_days / total_days * 100) if total_days > 0 else 0.0


def get_plan_analytics(base_dir, user_id):
    """
    Get analytics for all plans of a user.
    
    Returns:
        dict: Analytics including completion rates, time spent, etc.
    """
    user_plans = get_user_plans(base_dir, user_id)
    
    if not user_plans:
        return {
            "total_plans": 0,
            "completed_plans": 0,
            "in_progress_plans": 0,
            "total_study_time_minutes": 0,
            "average_completion": 0.0
        }
    
    total_plans = len(user_plans)
    completed_plans = sum(1 for p in user_plans if p["progress"]["overall_completion"] >= 100)
    in_progress_plans = sum(1 for p in user_plans if 0 < p["progress"]["overall_completion"] < 100)
    total_time = sum(p.get("total_study_time_minutes", 0) for p in user_plans)
    avg_completion = sum(p["progress"]["overall_completion"] for p in user_plans) / total_plans
    
    return {
        "total_plans": total_plans,
        "completed_plans": completed_plans,
        "in_progress_plans": in_progress_plans,
        "not_started_plans": total_plans - completed_plans - in_progress_plans,
        "total_study_time_minutes": total_time,
        "average_completion": round(avg_completion, 2),
        "plans": user_plans
    }


def delete_plan(base_dir, plan_timestamp):
    """
    Delete a plan by its timestamp.
    """
    all_plans = load_saved_plans(base_dir)
    all_plans = [p for p in all_plans if p.get("timestamp") != plan_timestamp]
    save_all_plans(base_dir, all_plans)
    return True


def mark_day_complete(base_dir, plan_timestamp, day_num):
    """
    Mark an entire day as complete.
    """
    all_plans = load_saved_plans(base_dir)
    
    for plan_entry in all_plans:
        if plan_entry.get("timestamp") == plan_timestamp:
            day_key = f"day_{day_num}"
            if day_key in plan_entry["progress"]["days"]:
                day_progress = plan_entry["progress"]["days"][day_key]
                
                # Mark all topics as completed
                day_progress["topics_completed"] = day_progress["topics"].copy()
                day_progress["completed"] = True
                day_progress["completion_percentage"] = 100.0
                
                # Update overall completion
                plan_entry["progress"]["overall_completion"] = calculate_overall_completion(plan_entry["progress"])
                plan_entry["last_updated"] = datetime.now().isoformat()
            
            break
    
    save_all_plans(base_dir, all_plans)
    return True