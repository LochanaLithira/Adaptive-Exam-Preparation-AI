#PlannerUI.py
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

def run_planner_ui():
    # --- Load environment variables from root directory ---
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    dotenv_path = PROJECT_ROOT / ".env"  # <-- Changed: .env in root
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
    from logic_planner.plan_manager import save_plan_to_file, load_all_plans
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
    
    # Get plan data from Planner Agent
    try:
        response = requests.get(
            f"{PLANNER_AGENT_URL}/get_plan/{user_id}",
            timeout=DEFAULT_TIMEOUT
        )
        if response.status_code != 200:
            st.error("❌ No study plan found. Please complete some quizzes first.")
            st.stop()
        plan_data = response.json()
        st.session_state.fetched_plan = plan_data.get("plan", [])
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to connect to Performance Tracker: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.stop()

    # --- Helper function to fetch YouTube videos ---
    def fetch_youtube_videos(query, max_results=3):
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            return [{"title": v["snippet"]["title"],
                     "url": f"https://www.youtube.com/watch?v={v['id']['videoId']}",
                     "type": "video"} for v in items]
        else:
            st.warning(f"Error fetching YouTube videos for {query}")
            return []

    # --- Header ---
    st.markdown("<h1 style='text-align: center; margin-top:25px'>🗓️ Personalized Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Plan your week based on your weak areas and available time.</h6>", unsafe_allow_html=True)

    # --- Planner Page ---
    if st.session_state.page == "planner":
        if st.button("📋 View All Saved Plans"):
            st.session_state.page = "all_plans"

        # --- Select study dates ---
        st.session_state.free_days = select_study_dates()
        all_filled = all(d['date'] is not None and d['available_time'] is not None
                         for d in st.session_state.free_days)

        generate_clicked = st.button("📥 Generate your Personalized Plan", use_container_width=True)

        if generate_clicked:
            if not all_filled:
                st.warning("⚠️ Please select a date and available time for all days before generating the plan.")
            else:
                # --- Serialize free days ---
                free_days_serialized = [
                    {
                        "date": day["date"].strftime("%Y-%m-%d") if isinstance(day["date"], (datetime, date)) else day["date"],
                        "available_time": day["available_time"]
                    }
                    for day in st.session_state.free_days
                ]

                # Get user ID from session
                user_data = st.session_state.get('user_data', {})
                user_id = user_data.get('_id')

                if not user_id:
                    st.error("❌ Please log in first.")
                    st.stop()

                # --- Call Planner API to generate plan using stored performance data ---
                try:
                    # Get the stored plan data from Planner service
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
                    
                    # Generate plan using the stored data
                    response = requests.post(
                        PLANNER_AGENT_ENDPOINT,
                        json={
                            "user_id": user_id,
                            "subjects": subjects,
                            "free_days": free_days_serialized
                        },
                        timeout=DEFAULT_TIMEOUT)
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

                if not api_plan:
                    st.warning("⚠️ Planner API returned an empty plan.")
                    st.stop()

                # --- Flatten topics ---
                all_topics = []
                for item in api_plan:
                    all_topics.append({
                        "subject": item.get("subject", "General"),
                        "topic": item.get("topic", item.get("activity"))
                    })

                # --- Distribute topics per day based on available time ---
                days_count = len(st.session_state.free_days)
                total_topics = len(all_topics)
                distributed_plan = []
                
                # If we have more or equal days than topics, distribute one topic per day
                if days_count >= total_topics:
                    for day_num, topic in enumerate(all_topics, 1):
                        distributed_plan.append({
                            "day_num": day_num,
                            "topics": [topic]
                        })
                else:
                    # If we have fewer days than topics, distribute topics evenly
                    topics_per_day = max(1, -(-total_topics // days_count))  # Ceiling division
                    idx = 0
                    for day_num in range(1, days_count + 1):
                        day_topics = []
                        remaining_topics = total_topics - idx
                        remaining_days = days_count - day_num + 1
                        # Calculate how many topics to assign to this day
                        topics_for_this_day = min(
                            topics_per_day,
                            -(-remaining_topics // remaining_days)  # Ceiling division to ensure all topics are covered
                        )
                        
                        for _ in range(topics_for_this_day):
                            if idx < total_topics:
                                day_topics.append(all_topics[idx])
                                idx += 1
                                
                        distributed_plan.append({
                            "day_num": day_num,
                            "topics": day_topics
                        })

                # --- Convert to internal plan format ---
                internal_plan = []
                study_schedule = {"Learn": 60, "Practice": 30, "Review": 15}
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

                # --- Assign dates and sequential times ---
                for i, day_info in enumerate(st.session_state.free_days):
                    day_topics = [d for d in internal_plan if d["Day"] == i+1]
                    slot = day_info['available_time']
                    start_hour = int(slot.split("(")[1].split(":")[0])
                    start_minute = int(slot.split("(")[1].split(":")[1].split("-")[0])
                    available_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M").time()
                    current_time = datetime.combine(day_info['date'], available_time)

                    for topic_data in day_topics:
                        schedule_list = []
                        for key, mins in topic_data['ScheduleMinutes'].items():
                            end_time = current_time + timedelta(minutes=mins)
                            schedule_list.append(f"{key} {topic_data['Topic']} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')})")
                            current_time = end_time
                            if key != "Review":
                                schedule_list.append("Break - 15 min")
                                current_time += timedelta(minutes=15)
                        topic_data['Schedule'] = schedule_list
                        topic_data['Date'] = day_info['date'].strftime("%Y-%m-%d")
                        topic_data['AvailableTime'] = day_info['available_time']

                st.session_state.fetched_plan = internal_plan
                st.session_state.plan_saved_flag = False
                st.success("✅ Plan generated for your selected dates & times!")

        # --- Display Plan ---
        if st.session_state.fetched_plan:
            plan = st.session_state.fetched_plan
            st.markdown("<h2 style='text-align: center;'>📝Personalized Study Plan</h2>", unsafe_allow_html=True)
            existing_plans = load_all_plans(BASE_DIR)

            # --- Check if plan already saved ---
            def is_exact_same(p1, p2):
                return all(d1["Topic"] == d2.get("Topic") and d1.get("Date") == d2.get("Date")
                           for d1, d2 in zip(p1, p2))
            already_saved = any(is_exact_same(plan, p.get("plan", [])) for p in existing_plans)
            st.session_state.plan_saved_flag = already_saved

            if st.session_state.plan_saved_flag:
                st.button("💾 Plan Already Saved", disabled=True, use_container_width=True)
                st.warning("⚠️ This generated plan has already been saved!")
            else:
                if st.button("💾 Save your Plan", type="primary", use_container_width=True):
                    # First create the complete plan data for each day
                    complete_plan = []
                    for entry in plan:
                        plan_entry = {
                            "Day": entry["Day"],
                            "Topic": entry["Topic"],
                            "Date": entry["Date"],
                            "AvailableTime": entry["AvailableTime"],
                            "Schedule": entry["Schedule"],
                            "Resources": entry["Resources"],
                            "Guidance": entry.get("Guidance", f"Focus on {entry['Topic']}")
                        }
                        complete_plan.append(plan_entry)
                    
                    weights = [{"topic": d["Topic"], "weight": 50, "resources": d["Resources"]} for d in complete_plan]
                    try:
                        # Save the plan
                        save_plan_to_file(complete_plan, weights, BASE_DIR)
                        # Store the saved plan in session state
                        st.session_state.last_saved_plan = complete_plan
                        st.session_state.plan_saved_flag = True
                        # Show success message
                        st.success("✅ Plan saved successfully!")
                        
                        # Only switch to all plans after confirming save
                        st.session_state.page = "all_plans"
                        st.experimental_run()
                    except Exception as e:
                        st.error(f"Error saving plan: {str(e)}")
                        st.session_state.plan_saved_flag = False

            # --- Group topics by Day and display ---
            grouped_plan = {}
            for entry in plan:
                day_num = entry["Day"]
                if day_num not in grouped_plan:
                    grouped_plan[day_num] = {
                        "Day": day_num,
                        "Date": entry["Date"],
                        "Topics": [],
                        "Resources": [],
                        "Schedule": []
                    }
                grouped_plan[day_num]["Topics"].append(entry["Topic"])
                grouped_plan[day_num]["Resources"].extend(entry["Resources"])
                grouped_plan[day_num]["Schedule"].extend(entry["Schedule"])

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

                card_html = f"""
                <div style='padding: 10px; border-radius: 10px; background-color: #000000;
                            border: 2px solid #333; margin-bottom: 10px; color: #ffffff;' >
                    <h3 style='text-align: center; color: #ffffff;'>📅 Day {day['Day']}<br>({day['Date']})</h3>
                    <h4 style='text-align: center;'>{topics_html}</h4>
                    <b style='color: #ffffff;'>Schedule:</b>
                    <ul style='color: #ffffff;'>
                        {schedule_html}
                    </ul>
                    <b style='color: #ffffff;'>Resources:</b>
                    <ul style='color: #ffffff;'>
                        {resources_html}
                    </ul>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    # --- All Saved Plans Page ---
    elif st.session_state.page == "all_plans":
        if st.button("⬅️ Back to Planner"):
            st.session_state.page = "planner"
        display_all_plans(BASE_DIR)
