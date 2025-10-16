#plan_manager.py
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
    """Sum total minutes based on schedule (Learn=60, Practice=30, Review=15)."""
    total = 0
    for day in plan:
        for s in day.get("Schedule", []):
            if "Learn" in s:
                total += 60
            elif "Practice" in s:
                total += 30
            elif "Review" in s:
                total += 15
    return total


def save_plan_to_storage(plan, weights, base_dir):
    """Save a new plan with completion status and total time."""
    all_plans = load_saved_plans(base_dir)

    # --- Prevent duplicates ---
    if any(existing["plan"] == plan for existing in all_plans):
        return False  # Already exists

    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    total_time = calculate_total_study_time(plan)

    new_entry = {
        "timestamp": timestamp,
        "weights": weights,
        "plan": plan,
        "completed_days": {str(day["Day"]): False for day in plan},
        "total_study_time_minutes": total_time
    }

    all_plans.append(new_entry)
    save_all_plans(base_dir, all_plans)
    return True
