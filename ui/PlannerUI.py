# PlannerUI.py
import streamlit as st
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from utils.api_config import (
    PLANNER_AGENT_URL,
    PERFORMANCE_TRACKER_URL,
    DEFAULT_TIMEOUT,
    PLANNER_AGENT_ENDPOINT
)
import json

def run_planner_ui():
    # --- Load environment variables from root directory ---
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    dotenv_path = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path)
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not YOUTUBE_API_KEY:
        st.error("YouTube API key not found! Set it in your .env file.")
        st.stop()

    # --- Path setup ---
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    # --- Import logic modules ---
    from logic_planner.plan_manager import save_plan_to_storage, load_saved_plans
    from logic_planner.plan_viewer import display_all_plans
    from logic_planner.resources import resources
    from logic_planner.date_selector import select_study_dates

    # --- Session state initialization ---
    if "page" not in st.session_state:
        st.session_state.page = "planner"
    if "fetched_plan" not in st.session_state:
        st.session_state.fetched_plan = []
    if "free_days" not in st.session_state:
        st.session_state.free_days = []
    if "plan_saved_flag" not in st.session_state:
        st.session_state.plan_saved_flag = False

    # Get user data from session
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id', None)
    if not user_id:
        st.error("❌ User not logged in. Please log in first.")
        st.stop()

    # --- Header ---
    st.markdown("<h1 style='text-align: center; margin-top:25px'>🗓️ Personalized Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Plan your studies efficiently, quicker and smarter!</h6>", unsafe_allow_html=True)

        # --- Planner Page ---
    if st.session_state.page == "planner":
        # Add flag to toggle between planner and saved plans
        if "show_saved_plans" not in st.session_state:
            st.session_state["show_saved_plans"] = False

        # If showing saved plans, hide all inputs
        if st.session_state["show_saved_plans"]:
            display_all_plans()
            st.stop()

        # Normal planner inputs and generator
        if st.button("📋 View All Saved Plans"):
            st.session_state["show_saved_plans"] = True
            st.rerun()

        # --- Select study dates ---
        st.session_state.free_days = select_study_dates()
        all_filled = all(d['date'] is not None and d['available_time'] is not None for d in st.session_state.free_days)
        generate_clicked = st.button("📥 Generate your Personalized Plan", width="stretch")

        if generate_clicked:
            if not all_filled:
                st.warning("⚠️ Please select a date and available time for all days before generating the plan.")
            else:
                # Show loading message
                loading_msg = st.empty()
                loading_msg.info("🔄 Generating your personalized study plan...")

                with st.spinner('Please wait...'):
                    # --- Serialize free days ---
                    free_days_serialized = [
                        {
                            "date": day["date"].strftime("%Y-%m-%d") if isinstance(day["date"], (datetime, date)) else day["date"],
                            "available_time": day["available_time"]
                        }
                        for day in st.session_state.free_days
                    ]

                    # --- Call Planner API to generate plan using stored performance data ---
                    try:
                        plan_response = requests.get(
                            f"{PLANNER_AGENT_URL}/get_plan/{user_id}",
                            timeout=DEFAULT_TIMEOUT
                        )
                        if plan_response.status_code != 200:
                            st.error("❌ No performance data found. Please complete some quizzes first.")
                            st.stop()

                        stored_data = plan_response.json()
                        subjects = stored_data.get("subjects", [])
                        if not subjects:
                            st.error("❌ No weak areas identified. Please complete some quizzes.")
                            st.stop()

                        response = requests.post(
                            PLANNER_AGENT_ENDPOINT,
                            json={
                                "user_id": user_id,
                                "subjects": subjects,
                                "free_days": free_days_serialized
                            },
                            timeout=DEFAULT_TIMEOUT
                        )
                        response.raise_for_status()
                        plan_data = response.json()
                        if "error" in plan_data:
                            st.error(f"❌ {plan_data['error']}")
                            st.stop()
                        if not plan_data.get("plan"):
                            st.warning("⚠️ No plan was generated. Please try again.")
                            st.stop()

                        api_plan = plan_data["plan"]
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ API request failed: {e}")
                        st.stop()

                    # --- Flatten topics ---
                    all_topics = []
                    for item in api_plan:
                        all_topics.append({
                            "subject": item.get("subject", "General"),
                            "topic": item.get("topic", item.get("activity"))
                        })

                    # --- Distribute topics per day ---
                    days_count = len(st.session_state.free_days)
                    total_topics = len(all_topics)
                    distributed_plan = []

                    if days_count >= total_topics:
                        for day_num, topic in enumerate(all_topics, 1):
                            distributed_plan.append({"day_num": day_num, "topics": [topic]})
                    else:
                        topics_per_day = max(1, -(-total_topics // days_count))
                        idx = 0
                        for day_num in range(1, days_count + 1):
                            day_topics = []
                            remaining_topics = total_topics - idx
                            remaining_days = days_count - day_num + 1
                            topics_for_this_day = min(topics_per_day, -(-remaining_topics // remaining_days))
                            for _ in range(topics_for_this_day):
                                if idx < total_topics:
                                    day_topics.append(all_topics[idx])
                                    idx += 1
                            distributed_plan.append({"day_num": day_num, "topics": day_topics})

                    # --- Convert to internal plan format ---
                    internal_plan = []
                    study_schedule = {"Learn": 60, "Practice": 30, "Review": 15}

                    def fetch_youtube_videos(query, max_results=3):
                        url = "https://www.googleapis.com/youtube/v3/search"
                        params = {
                            "part": "snippet",
                            "q": query,
                            "type": "video",
                            "maxResults": max_results,
                            "key": YOUTUBE_API_KEY
                        }
                        r = requests.get(url, params=params)
                        if r.status_code == 200:
                            items = r.json().get("items", [])
                            return [{"title": v["snippet"]["title"],
                                     "url": f"https://www.youtube.com/watch?v={v['id']['videoId']}",
                                     "type": "video"} for v in items]
                        return []

                    for day in distributed_plan:
                        for topic_info in day["topics"]:
                            youtube_links = fetch_youtube_videos(topic_info["topic"])
                            internal_plan.append({
                                "Day": day["day_num"],
                                "Topic": topic_info["topic"],
                                "Guidance": f"Focus on {topic_info['topic']}",
                                "ScheduleMinutes": study_schedule,
                                "Resources": resources.get(topic_info["topic"], []) + youtube_links
                            })

                    # --- Assign dates and times safely ---
                    for i, day_info in enumerate(st.session_state.free_days):
                        day_topics = [d for d in internal_plan if d["Day"] == i+1]
                        slot = day_info.get('available_time', '')
                        try:
                            time_part = slot.split("(")[1].split("-")[0].strip().rstrip(")")
                            if 'AM' in time_part.upper() or 'PM' in time_part.upper():
                                time_part = time_part.replace('.', ':').upper()
                                available_time = datetime.strptime(time_part, "%I:%M%p").time()
                            else:
                                if ':' in time_part:
                                    start_hour = int(time_part.split(":")[0])
                                    start_minute = int(time_part.split(":")[1])
                                else:
                                    start_hour = int(time_part)
                                    start_minute = 0
                                available_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M").time()
                        except Exception as e:
                            st.warning(f"Could not parse time '{slot}': {e}")
                            available_time = datetime.strptime("09:00AM", "%I:%M%p").time()

                        current_time = datetime.combine(day_info.get('date', date.today()), available_time)
                        for topic_data in day_topics:
                            schedule_list = []
                            if 'ScheduleMinutes' in topic_data and topic_data['ScheduleMinutes']:
                                for key, mins in topic_data['ScheduleMinutes'].items():
                                    try:
                                        end_time = current_time + timedelta(minutes=mins)
                                        schedule_list.append(f"{key} {topic_data['Topic']} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')})")
                                        current_time = end_time
                                        if key != "Review":
                                            schedule_list.append("Break - 15 min")
                                            current_time += timedelta(minutes=15)
                                    except Exception as e:
                                        schedule_list.append(f"{key} {topic_data['Topic']} (Time parsing error)")
                            else:
                                schedule_list.append("No schedule available")
                            topic_data['Schedule'] = schedule_list
                            topic_data['Date'] = day_info.get('date').strftime("%Y-%m-%d") if day_info.get('date') else "Unknown"
                            topic_data['AvailableTime'] = day_info.get('available_time', 'Unknown')

                    # --- Save generated plan ---
                    st.session_state.fetched_plan = internal_plan
                    st.session_state.plan_saved_flag = False

                    plan_file_name = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    GENERATED_PLANS_DIR = os.path.join(BASE_DIR, "generated_plans")
                    os.makedirs(GENERATED_PLANS_DIR, exist_ok=True)
                    plan_file_path = os.path.join(GENERATED_PLANS_DIR, plan_file_name)
                    with open(plan_file_path, "w") as f:
                        json.dump(internal_plan, f, default=str, indent=4)

                    # --- Clear loading message and show ONE success ---
                    loading_msg.empty()
                    st.success("✅ Plan Generated and Saved Successfully!")  # ✅ Only ONE message

                    # --- Display plan ---
                    st.markdown("<h2 style='text-align: center;'>📝 Personalized Study Plan</h2>", unsafe_allow_html=True)

                    grouped_plan = {}
                    for entry in internal_plan:
                        day_num = entry["Day"]
                        if day_num not in grouped_plan:
                            grouped_plan[day_num] = {
                                "Day": day_num,
                                "Date": entry.get("Date", "Unknown"),
                                "Topics": [],
                                "Resources": [],
                                "Schedule": []
                            }
                        # --- Append entry data to actually display them ---
                        grouped_plan[day_num]["Topics"].append(entry.get("Topic", "Unknown"))
                        grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
                        grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))

                    for day in grouped_plan.values():
                        topics_line = " | ".join([f"<b style='color:#1a73e8;'>{t}</b>" for t in day["Topics"]])
                        topics_html = f"Topics for today: {topics_line}"
                        schedule_html = "".join([f"<li>{s}</li>" for s in day["Schedule"]])
                        
                        resources_html = ""
                        if day["Resources"]:
                            for res in day["Resources"]:
                                resources_html += f"<li>- <a href='{res['url']}' target='_blank'>{res['title']}</a> ({res['type'].capitalize()})</li>"
                        else:
                            resources_html = "<li>- No resources available</li>"

                        # Format date
                        date_obj = datetime.strptime(day['Date'], "%Y-%m-%d")
                        day_val = date_obj.day
                        if 10 <= day_val % 100 <= 20:
                            suffix = 'th'
                        else:
                            suffix = {1:'st',2:'nd',3:'rd'}.get(day_val,'th')
                        date_display = f"{day_val}{suffix} {date_obj.strftime('%B %Y')}"

                        card_html = f"""
                        <div style='padding: 10px; border-radius: 10px; background-color: #000000; border: 2px solid #333; margin-bottom: 10px; color: #ffffff;'>
                            <h3 style='text-align: center; color: #ffffff;'>📅 Day {day['Day']}<br>({date_display})</h3>
                            <h4 style='text-align: center;'>{topics_html}</h4>
                            <b style='color: #ffffff;'>Schedule:</b>
                            <ul style='color: #ffffff;'>{schedule_html}</ul>
                            <b style='color: #ffffff;'>Resources:</b>
                            <ul style='color: #ffffff;'>{resources_html}</ul>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
