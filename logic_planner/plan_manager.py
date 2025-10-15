#plan_manager.py
import os
import json
from datetime import datetime

def save_plan_to_file(plan, weights, base_dir): 
    """
    Save the plan exactly as it appears in the Planner UI.
    Plan should be a list of entries with complete data.
    """
    plans_dir = os.path.join(base_dir, "saved_plans")
    os.makedirs(plans_dir, exist_ok=True)

    # Save the plan exactly as provided (already has Schedule, Resources, Date, etc.)
    saved_plan = []
    for entry in plan:
        saved_day = {
            "Day": entry["Day"],
            "Topic": entry["Topic"],
            "Date": entry.get("Date", None),
            "AvailableTime": entry.get("AvailableTime", None),
            "Schedule": entry.get("Schedule", []),
            "Resources": entry.get("Resources", []),
            "Guidance": entry.get("Guidance", f"Focus on {entry['Topic']}")
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
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=4, ensure_ascii=False)


def load_all_plans(base_dir):
    """Load all saved plans in saved_plans folder."""
    plans_dir = os.path.join(base_dir, "saved_plans")
    if not os.path.exists(plans_dir):
        return []

    files = [f for f in os.listdir(plans_dir) if f.endswith(".json")]
    all_plans = []
    for f in sorted(files, reverse=True):
        with open(os.path.join(plans_dir, f), "r", encoding="utf-8") as file:
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