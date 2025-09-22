# logic/plan_viewer.py
import streamlit as st
import os
import json
import datetime
from logic_planner.resources import resources


SAVE_FILE = "completed_days.json"

def load_completed_days():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_completed_days(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


# Calculate total minutes

def calculate_total_minutes(plan, completed_days):
    study_schedule = {
        "Learn": 30,
        "Practice": 30,
        "Review": 15
    }  # minutes
    total = 0
    for day in plan:
        day_num = str(day['Day'])
        if completed_days.get(day_num, False):
            total += sum(study_schedule.values())
    return total

# Display all saved plans

def display_all_plans(base_dir):
    plans_dir = os.path.join(base_dir, "saved_plans")
    if not os.path.exists(plans_dir):
        st.info("No saved plans found.")
        return

    # Load persistent completed_days once
    if "completed_days_store" not in st.session_state:
        st.session_state.completed_days_store = load_completed_days()

    files = [f for f in sorted(os.listdir(plans_dir), reverse=True) if f.endswith(".json")]

    for file_name in files:
        file_path = os.path.join(plans_dir, file_name)
        with open(file_path, "r") as f:
            plan_data = f.read()
            plan_json = eval(plan_data) if isinstance(plan_data, str) else plan_data

        timestamp = plan_json.get("timestamp", "Unknown Time")
        plan = plan_json.get("plan", [])

        plan_key = file_name.replace(".json", "")

        # Ensure storage exists for this plan
        if plan_key not in st.session_state.completed_days_store:
            st.session_state.completed_days_store[plan_key] = {}

        with st.expander(f"Plan created on {timestamp}"):
            total_time_placeholder = st.empty()

            # 7 columns for 7 days
            cols = st.columns(7)

            for i, day in enumerate(plan):
                day_num = str(day['Day'])
                topic = day["Topic"]
                checkbox_key = f"{plan_key}_day_{day_num}"

                # Get saved state
                saved_value = st.session_state.completed_days_store[plan_key].get(day_num, False)

                # Place each day in its column (checkbox + card)
                with cols[i]:
                    completed = st.checkbox(
                        "Mark Status",
                        key=checkbox_key,
                        value=saved_value
                    )

                    # Update persistent state if changed
                    if completed != saved_value:
                        st.session_state.completed_days_store[plan_key][day_num] = completed
                        save_completed_days(st.session_state.completed_days_store)

                    # Display day info
                    st.markdown(
                        f"""
                        <div style='padding: 10px; border-radius: 8px; background-color:black;
                                    border: 1px solid #ccc; min-height: 300px;'>
                            <h4 style='text-align:center;'>Day {day_num}</h4>
                            <b>Topic:</b> {topic}<br>
                            <b>Schedule:</b>
                            <ul>
                                <li>Learn Concepts: 30 min</li>
                                <li>Practice: 1 hour
                                (Morning/Afternoon
                                /Night:
                                20 mins each)</li>
                                <li>Review: 15 min</li>
                            </ul>
                            <b>Resources:</b>
                            <ul>
                        """,
                        unsafe_allow_html=True
                    )

                    topic_resources = resources.get(topic, [])
                    if topic_resources:
                        for res in topic_resources:
                            st.markdown(
                                f"- <a href='{res['url']}' target='_blank'>{res['title']}</a> ({res['type'].capitalize()})",
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown("- No resources available", unsafe_allow_html=True)

                    st.markdown("</ul></div>", unsafe_allow_html=True)

            # Update total study time dynamically
            total_minutes = calculate_total_minutes(plan, st.session_state.completed_days_store[plan_key])
            hours, minutes = divmod(total_minutes, 60)
            total_time_placeholder.markdown(
                f"<div style='padding:8px; border-radius:8px; background-color:#000; color:#fff; "
                f"text-align:right; font-weight:bold;'>⏱️ Total Study Time: {hours}h {minutes}m</div>",
                unsafe_allow_html=True
            )

#generate plan
def generate_plan(records):
    """
    Generates a 7-day study plan based on performance records.
    Each day includes:
    - Topic
    - Guidance (focus notes)
    - Schedule (Learn/Practice/Review with allocated times)
    - Resources (clickable links)
    """
    from .planner import calculate_weights  # assuming you have this function
    weights = calculate_weights(records)
    sorted_topics = sorted(weights, key=lambda x: x['weight'], reverse=True)
    top_topics = sorted_topics[:7]

    study_schedule_minutes = {"Learn": 30, "Practice": 30, "Review": 15}
    start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0))  # 8 AM

    plan = []

    for i, topic_info in enumerate(top_topics, start=1):
        topic = topic_info['topic']
        guidance = f"Concentrate on weak areas in {topic}."

        # Allocate time slots
        current_time = start_time
        schedule_list = []
        for key, minutes in study_schedule_minutes.items():
            end_time = current_time + datetime.timedelta(minutes=minutes)
            schedule_list.append(f"{key} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')})")
            current_time = end_time

        # Resources for topic
        topic_resources = resources.get(topic, [])

        # Construct day plan
        day_plan = {
            "Day": i,
            "Topic": topic,
            "Guidance": guidance,
            "Schedule": schedule_list,
            "Resources": topic_resources
        }

        plan.append(day_plan)

    return plan
