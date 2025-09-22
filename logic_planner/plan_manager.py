#plan_manager.py
import os
import json
from datetime import datetime, timedelta
from logic_planner.resources import resources

def save_plan_to_file(plan, weights, base_dir):
    plans_dir = os.path.join(base_dir, "saved_plans")
    os.makedirs(plans_dir, exist_ok=True)

    study_schedule = {"Learn": 30, "Practice": 30, "Review": 15}
    start_hour = 8  # start at 8:00 AM

    saved_plan = []
    for idx, day in enumerate(plan, start=1):
        topic = day["Topic"]
        guidance = day.get("Guidance", f"Concentrate on weak areas in {topic}.")
        
        # Allocate time slots
        current_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=start_hour)
        schedule_list = []
        for key, minutes in study_schedule.items():
            end_time = current_time + timedelta(minutes=minutes)
            schedule_list.append(f"{key} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}): {minutes} min")
            current_time = end_time
        
        # Resources
        day_resources = resources.get(topic, [])

        saved_day = {
            "Day": idx,
            "Topic": topic,
            "Guidance": guidance,
            "Schedule": schedule_list,
            "Resources": day_resources
        }
        saved_plan.append(saved_day)

    # Save with timestamp and weights
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    plan_data = {
        "timestamp": timestamp,
        "weights": weights,
        "plan": saved_plan
    }

    file_path = os.path.join(plans_dir, f"{timestamp}.json")
    with open(file_path, "w") as f:
        json.dump(plan_data, f, indent=4)

def load_all_plans(base_dir):
    """Load all saved plans in saved_plans folder."""
    plans_dir = os.path.join(base_dir, "saved_plans")
    if not os.path.exists(plans_dir):
        return []

    files = [f for f in os.listdir(plans_dir) if f.endswith(".json")]
    all_plans = []
    for f in sorted(files, reverse=True):
        with open(os.path.join(plans_dir, f), "r") as file:
            try:
                all_plans.append(json.load(file))
            except:
                continue
    return all_plans


def is_plan_already_saved(new_plan, existing_plans):
    """Check if the exact same plan is already saved."""
    for p in existing_plans:
        if p.get("plan") == new_plan:
            return True
    return False
