# logic_planner/generate_plan.py
import random
from logic_planner.resources import resources, fetch_resources_with_fallback
from datetime import datetime, timedelta

def calculate_advanced_weights(records):
    """
    Enhanced weight calculation considering multiple factors:
    - Accuracy (primary factor)
    - Number of attempts (more attempts = needs more focus)
    - Time spent (longer time might indicate struggle)
    - Recency (recent poor performance weighted higher)
    """
    weights = []
    current_date = datetime.now()
    
    for record in records:
        topic = record.get("topic")
        accuracy = record.get("result", {}).get("accuracy", 0)
        attempts = record.get("result", {}).get("attempts", 1)
        time_spent = record.get("result", {}).get("time_spent", 0)
        timestamp = record.get("timestamp")
        
        # Base weight: inverse of accuracy
        base_weight = max(100 - accuracy, 0)
        
        # Attempt penalty: more attempts = needs more practice
        attempt_penalty = min(attempts * 5, 20)  # Cap at 20
        
        # Time factor: longer time = struggle (but normalize it)
        time_factor = min(time_spent / 60, 10) if time_spent > 0 else 0
        
        # Recency bonus: recent poor performance gets priority
        recency_bonus = 0
        if timestamp:
            try:
                record_date = datetime.fromisoformat(timestamp)
                days_ago = (current_date - record_date).days
                if days_ago <= 7:
                    recency_bonus = 10
                elif days_ago <= 30:
                    recency_bonus = 5
            except:
                pass
        
        # Calculate final weight
        final_weight = base_weight + attempt_penalty + time_factor + recency_bonus
        
        # Determine complexity level
        if final_weight > 70:
            complexity = "high"
        elif final_weight > 40:
            complexity = "medium"
        else:
            complexity = "low"
        
        weights.append({
            "topic": topic,
            "weight": max(final_weight, 0),
            "accuracy": accuracy,
            "complexity": complexity,
            "attempts": attempts
        })
    
    return weights


def create_adaptive_schedule(topic_info, available_time_minutes):
    """
    Create schedule based on topic complexity and available time.
    High complexity topics get more learning time.
    Low complexity topics get more practice time.
    """
    complexity = topic_info.get("complexity", "medium")
    
    # Adjust ratios based on complexity
    if complexity == "high":
        ratios = {"Learn": 0.50, "Practice": 0.35, "Review": 0.15}
    elif complexity == "medium":
        ratios = {"Learn": 0.40, "Practice": 0.40, "Review": 0.20}
    else:  # low complexity
        ratios = {"Learn": 0.30, "Practice": 0.45, "Review": 0.25}
    
    # Calculate actual minutes
    schedule = {
        "Learn": int(available_time_minutes * ratios["Learn"]),
        "Practice": int(available_time_minutes * ratios["Practice"]),
        "Review": int(available_time_minutes * ratios["Review"])
    }
    
    # Ensure minimum time for each activity
    for activity in schedule:
        if schedule[activity] < 10:
            schedule[activity] = 10
    
    return schedule


def distribute_topics_intelligently(topics, available_days, daily_time_slots):
    """
    Intelligently distribute topics across available days based on:
    - Topic complexity/weight (harder topics first)
    - Available time per day
    - Cognitive load management (don't overload any single day)
    - Spaced repetition (review earlier topics)
    """
    if not topics or not available_days:
        return []
    
    # Sort topics by weight (weakest/most important first)
    sorted_topics = sorted(topics, key=lambda x: x["weight"], reverse=True)
    
    # Initialize plan structure
    daily_plan = []
    for day_idx, day_info in enumerate(available_days):
        daily_plan.append({
            "day_num": day_idx + 1,
            "date": day_info.get("date"),
            "available_time": day_info.get("available_time"),
            "topics": [],
            "total_time_allocated": 0
        })
    
    # Estimate time needed per topic based on complexity
    def estimate_topic_time(complexity):
        time_map = {
            "high": 120,    # 2 hours for difficult topics
            "medium": 90,   # 1.5 hours for medium topics
            "low": 60       # 1 hour for easier topics
        }
        return time_map.get(complexity, 90)
    
    # Parse available time from slot (rough estimate)
    def parse_time_slot(slot):
        # Morning/Afternoon/Evening/Night ~ 3-4 hours each
        if "Morning" in slot or "Afternoon" in slot:
            return 180  # 3 hours
        elif "Evening" in slot or "Night" in slot:
            return 180  # 3 hours
        return 120  # default 2 hours
    
    # First pass: Distribute high-priority topics
    topic_index = 0
    for day in daily_plan:
        day_capacity = parse_time_slot(day["available_time"])
        
        while topic_index < len(sorted_topics):
            topic = sorted_topics[topic_index]
            topic_time = estimate_topic_time(topic["complexity"])
            
            # Check if topic fits in this day
            if day["total_time_allocated"] + topic_time <= day_capacity:
                day["topics"].append(topic)
                day["total_time_allocated"] += topic_time
                topic_index += 1
            else:
                break  # Move to next day
        
        if topic_index >= len(sorted_topics):
            break
    
    # Second pass: Fill remaining days with review sessions
    if topic_index >= len(sorted_topics):
        # Add review sessions for difficult topics on later days
        review_topics = [t for t in sorted_topics if t["complexity"] == "high"][:3]
        
        for day in daily_plan:
            if not day["topics"] and review_topics:
                # Add review session
                review_topic = review_topics.pop(0)
                day["topics"].append({
                    **review_topic,
                    "is_review": True
                })
    
    # Remove empty days
    daily_plan = [day for day in daily_plan if day["topics"]]
    
    return daily_plan


def generate_plan(records, free_days=None):
    """
    Generate an intelligent study plan based on performance records.
    
    Args:
        records: List of performance records with topics and results
        free_days: List of available study days with dates and time slots
    
    Returns:
        List of daily study plans with topics, schedules, and resources
    """
    if not records:
        return []
    
    # Calculate weights with advanced algorithm
    weights = calculate_advanced_weights(records)
    
    # If no free days provided, create default 7-day plan
    if not free_days:
        from datetime import date, timedelta
        free_days = []
        for i in range(7):
            free_days.append({
                "date": date.today() + timedelta(days=i),
                "available_time": "Morning (08:00AM)"
            })
    
    # Distribute topics intelligently across days
    distributed_plan = distribute_topics_intelligently(weights, free_days, None)
    
    # Generate detailed plan with schedules and resources
    detailed_plan = []
    
    for day_plan in distributed_plan:
        for topic_info in day_plan["topics"]:
            # Determine available time for this topic
            topic_time = estimate_topic_time(topic_info["complexity"])
            
            # Create adaptive schedule
            schedule = create_adaptive_schedule(topic_info, topic_time)
            
            # Fetch resources
            topic_resources = fetch_resources_with_fallback(
                topic_info["topic"],
                topic_info.get("subject", "General")
            )
            
            # Create plan entry
            plan_entry = {
                "Day": day_plan["day_num"],
                "Date": day_plan["date"],
                "Topic": topic_info["topic"],
                "Complexity": topic_info["complexity"],
                "Weight": topic_info["weight"],
                "Accuracy": topic_info["accuracy"],
                "IsReview": topic_info.get("is_review", False),
                "Guidance": generate_guidance(topic_info),
                "ScheduleMinutes": schedule,
                "Resources": topic_resources,
                "EstimatedTime": sum(schedule.values())
            }
            
            detailed_plan.append(plan_entry)
    
    return detailed_plan


def generate_guidance(topic_info):
    """Generate personalized guidance based on topic performance"""
    complexity = topic_info.get("complexity", "medium")
    accuracy = topic_info.get("accuracy", 0)
    topic = topic_info.get("topic", "this topic")
    
    if complexity == "high":
        if accuracy < 40:
            return f"⚠️ {topic} needs significant attention. Start with fundamentals and build up gradually."
        else:
            return f"📚 {topic} is challenging. Focus on understanding core concepts before practicing."
    elif complexity == "medium":
        if accuracy < 60:
            return f"📖 {topic} needs more practice. Review key concepts and work through examples."
        else:
            return f"✅ {topic} is progressing well. Focus on practice problems to solidify understanding."
    else:  # low complexity
        return f"🎯 {topic} is well understood. Quick review and advanced practice recommended."


def estimate_topic_time(complexity):
    """Helper function to estimate time needed per topic"""
    time_map = {
        "high": 120,    # 2 hours
        "medium": 90,   # 1.5 hours
        "low": 60       # 1 hour
    }
    return time_map.get(complexity, 90)