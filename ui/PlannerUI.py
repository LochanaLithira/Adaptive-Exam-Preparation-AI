# PlannerUI.py (Fixed Topic Extraction)
import streamlit as st
import os
import sys
import requests
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from utils.api_config import (
    PLANNER_AGENT_URL,
    PERFORMANCE_TRACKER_URL,
    DEFAULT_TIMEOUT,
    PLANNER_AGENT_ENDPOINT
)
from utils.subscription import is_current_user_premium

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

GENERATED_PLANS_DIR = os.path.join(BASE_DIR, "generated_plans")
os.makedirs(GENERATED_PLANS_DIR, exist_ok=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_inputs(free_days, user_id):
    """Validate inputs before plan generation"""
    errors = []
    if not user_id:
        errors.append("❌ User not logged in. Please log in first.")
    if not free_days or len(free_days) == 0:
        errors.append("❌ No study days selected. Please select your exam date and study time.")
    if len(free_days) < 2:
        errors.append("⚠️ For an effective study plan, we recommend at least 2 days.")
    
    for i, day in enumerate(free_days):
        if not day.get('date'):
            errors.append(f"❌ Day {i+1}: Date is missing")
        if not day.get('available_time'):
            errors.append(f"❌ Day {i+1}: Available time is missing")
    
    return errors


def call_api_with_retry(url, data, max_retries=3, timeout=DEFAULT_TIMEOUT):
    """Call API with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"API request failed: {str(e)}")
            time.sleep(2 ** attempt)
    raise Exception("Failed to connect to API")


def update_progress(progress_bar, status_text, progress, message):
    """Update progress indicators"""
    progress_bar.progress(progress)
    status_text.info(f"📊 {message}")


def safe_fetch_resources(topic_info, youtube_key):
    """Safely fetch resources with timeout protection"""
    from logic_planner.resources import fetch_resources_with_fallback
    try:
        return fetch_resources_with_fallback(
            topic_info["topic"],
            topic_info.get("subject", "General"),
            youtube_key,
            max_youtube_timeout=2
        )
    except Exception as e:
        return [{
            "type": "read",
            "title": f"Search for {topic_info['topic']}",
            "url": f"https://www.google.com/search?q={topic_info['topic'].replace(' ', '+')}"
        }]


# ============================================================================
# UI COMPONENTS
# ============================================================================

def show_premium_gate():
    """Display premium feature gate"""
    st.markdown("""
        <style>
        .premium-container {
            background: linear-gradient(135deg, rgba(16, 24, 39, 0.8) 0%, rgba(17, 24, 39, 0.9) 100%);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        .premium-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .feature-card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div class="premium-container">
        <div class="premium-badge">⭐ PREMIUM FEATURE</div>
        <h1 style="color: white; margin-bottom: 1rem;">Study Planner</h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Unlock AI-powered personalized learning schedules and progress tracking.
        </p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    features = [
        ("📅 Smart Scheduling", "AI-powered study plans tailored to your weak areas"),
        ("🎯 Progress Tracking", "Track completion and time spent on each topic"),
        ("📊 Analytics", "Visualize your learning journey and improvements"),
        ("📚 Smart Resources", "Curated learning materials for each topic")
    ]
    
    for i, (title, desc) in enumerate(features):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="feature-card">
                <h3 style="color: #e2e8f0;">{title}</h3>
                <p style="color: rgba(255,255,255,0.7)">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⭐ Upgrade to Premium", type="primary", use_container_width=True):
            st.session_state.current_page = "subscription"
            st.rerun()


def display_plan_card(day_data):
    """Display a single day's plan as a card"""
    try:
        date_obj = datetime.strptime(day_data['Date'], "%Y-%m-%d")
        day_val = date_obj.day
        suffix = 'th' if 10 <= day_val % 100 <= 20 else {1:'st', 2:'nd', 3:'rd'}.get(day_val % 10, 'th')
        date_display = f"{day_val}{suffix} {date_obj.strftime('%B %Y')}"
    except:
        date_display = day_data['Date']
    
    # Complexity badges
    complexity_badges = []
    for info in day_data["ComplexityInfo"]:
        emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(info["complexity"], "⚪")
        color = {"high": "#ff4444", "medium": "#ffaa00", "low": "#44ff44"}.get(info["complexity"], "#888")
        complexity_badges.append(
            f"{emoji} <span style='color: {color}; font-weight: bold;'>{info['topic']}</span> "
            f"<span style='color: gray; font-size: 0.9em;'>({info['accuracy']:.1f}% accuracy)</span>"
        )
    
    topics_html = "<br>".join(complexity_badges)
    schedule_html = "".join([f"<li style='margin: 8px 0;'>{s}</li>" for s in day_data["Schedule"]])
    
    # Resources
    resources_html = ""
    seen_urls = set()
    for res in day_data.get("Resources", []):
        if res["url"] not in seen_urls:
            seen_urls.add(res["url"])
            emoji = {"video": "🎥", "practice": "📝", "read": "📖", "concept": "💡"}.get(res["type"], "📚")
            resources_html += f"<li style='margin: 5px 0;'>{emoji} <a href='{res['url']}' target='_blank'>{res['title']}</a> <span style='color: gray;'>({res['type'].capitalize()})</span></li>"
    
    if not resources_html:
        resources_html = "<li>No resources available</li>"
    
    guidance_html = "<br>".join([f"• {g}" for g in day_data.get("Guidance", []) if g])
    
    card_html = f"""
    <div style='padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
              border: 2px solid #444; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
        <h2 style='text-align: center; color: #4CAF50; margin-bottom: 5px;'>📅 Day {day_data['Day']}</h2>
        <p style='text-align: center; color: #aaa; margin-bottom: 20px;'>{date_display}</p>
        
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>📚 Topics for Today:</h4>
            <p style='line-height: 1.8;'>{topics_html}</p>
        </div>
        
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>💡 Study Guidance:</h4>
            <p style='color: #ddd; line-height: 1.6;'>{guidance_html}</p>
        </div>
        
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>⏰ Schedule:</h4>
            <ul style='color: #ddd; list-style-type: none; padding-left: 0;'>{schedule_html}</ul>
        </div>
        
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;'>
            <h4 style='color: #fff; margin-bottom: 10px;'>📖 Learning Resources:</h4>
            <ul style='color: #ddd; padding-left: 20px;'>{resources_html}</ul>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


# ============================================================================
# PLAN GENERATION
# ============================================================================

def fetch_performance_data(user_id):
    """Fetch user performance data with retry logic"""
    perf_url = f"{PLANNER_AGENT_URL}/get_plan/{user_id}"
    
    for attempt in range(3):
        try:
            response = requests.get(perf_url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 204:
                st.error("❌ No performance data found. Please complete some quizzes first.")
                st.info("💡 Take a few quizzes to help us identify weak areas.")
                st.stop()
            elif response.status_code != 200:
                st.error(f"❌ Unexpected response: {response.status_code}")
                st.stop()
            
            stored_data = response.json()
            subjects = stored_data.get("subjects") if isinstance(stored_data, dict) else None
            
            if not subjects:
                st.warning("❌ No weak areas identified yet. Please complete some quizzes.")
                st.info("💡 Try doing 2-3 short quizzes so we can create a personalized plan.")
                st.stop()
            
            return subjects
            
        except requests.exceptions.RequestException as e:
            if attempt == 2:
                st.error("❌ Failed to fetch performance data.")
                st.exception(e)
                st.stop()
            time.sleep(2 ** attempt)


def generate_study_plan(user_id, free_days):
    """Main plan generation workflow"""
    from logic_planner.planner import (
        distribute_topics_intelligently,
        create_adaptive_schedule,
        generate_guidance
    )
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Prepare data
        update_progress(progress_bar, status_text, 10, "Preparing your study schedule...")
        free_days_serialized = [
            {
                "date": day["date"].strftime("%Y-%m-%d") if isinstance(day["date"], (datetime, date)) else str(day["date"]),
                "available_time": day["available_time"]
            }
            for day in free_days
        ]
        
        # Step 2: Fetch performance
        update_progress(progress_bar, status_text, 25, "Fetching your performance data...")
        subjects = fetch_performance_data(user_id)
        
        # Step 3: Generate plan
        update_progress(progress_bar, status_text, 50, "Generating your personalized study plan...")
        plan_data = call_api_with_retry(
            PLANNER_AGENT_ENDPOINT,
            {"user_id": user_id, "subjects": subjects, "free_days": free_days_serialized}
        )
        
        if "error" in plan_data or not plan_data.get("plan"):
            st.error("❌ Failed to generate plan. Please try again.")
            st.stop()
        
        # Step 4: Process topics - FIXED SECTION
        update_progress(progress_bar, status_text, 65, "Processing topics...")
        topics_with_weights = []
        
        # Debug: Show what we received
        st.info(f"🔍 Debug: Received {len(plan_data['plan'])} items from API")
        
        for idx, item in enumerate(plan_data["plan"]):
            # Extract topic - try multiple possible keys
            topic = (
                item.get("topic") or 
                item.get("activity") or 
                item.get("name") or 
                item.get("title") or 
                f"Topic {idx + 1}"
            )
            
            # Extract subject
            subject = item.get("subject") or item.get("category") or "General"
            
            # Extract accuracy - handle various formats
            accuracy = item.get("accuracy", 0)
            if isinstance(accuracy, str):
                try:
                    accuracy = float(accuracy.replace("%", ""))
                except:
                    accuracy = 0
            
            # Calculate weight and complexity
            weight = max(100 - float(accuracy), 0)
            complexity = "high" if weight > 70 else "medium" if weight > 40 else "low"
            
            topic_data = {
                "topic": str(topic),
                "subject": str(subject),
                "accuracy": float(accuracy),
                "weight": float(weight),
                "complexity": complexity
            }
            
            topics_with_weights.append(topic_data)
            
            # Debug: Show processed topic
            st.info(f"✓ Processed: {topic} ({subject}) - {accuracy}% accuracy")
        
        # Step 5: Distribute topics
        update_progress(progress_bar, status_text, 75, "Creating schedule...")
        distributed_plan = distribute_topics_intelligently(topics_with_weights, free_days, None)
        
        # Step 6: Enhance with resources
        update_progress(progress_bar, status_text, 85, "Fetching educational resources...")
        internal_plan = []
        
        for day_plan in distributed_plan:
            for topic_info in day_plan["topics"]:
                # Validate topic info
                if not topic_info.get("topic") or topic_info["topic"] == "Unknown":
                    st.warning(f"⚠️ Skipping invalid topic in day {day_plan['day_num']}")
                    continue
                
                # Fetch resources with timeout
                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(safe_fetch_resources, topic_info, YOUTUBE_API_KEY)
                        topic_resources = future.result(timeout=4)
                except:
                    topic_resources = [{
                        "type": "read",
                        "title": f"Search for {topic_info['topic']}",
                        "url": f"https://www.google.com/search?q={topic_info['topic'].replace(' ', '+')}"
                    }]
                
                # Create schedule
                available_minutes = 180 if "Morning" in day_plan.get("available_time", "") else 120
                schedule = create_adaptive_schedule(topic_info, available_minutes)
                guidance = generate_guidance(topic_info)
                
                # Parse time slot
                day_info = next((d for d in free_days if str(d.get('date')) == day_plan.get("date")), None)
                slot = day_info.get('available_time', 'Morning (08:00AM)') if day_info else 'Morning (08:00AM)'
                
                try:
                    time_part = slot.split("(")[1].split(")")[0].strip().replace('.', ':').upper()
                    available_time = datetime.strptime(time_part, "%I:%M%p").time()
                except:
                    available_time = datetime.strptime("09:00AM", "%I:%M%p").time()
                
                # Create schedule with time slots
                current_time = datetime.combine(day_plan.get('date', date.today()), available_time)
                schedule_list = []
                
                for activity, minutes in schedule.items():
                    end_time = current_time + timedelta(minutes=minutes)
                    schedule_list.append(
                        f"{activity} {topic_info['topic']} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')})"
                    )
                    current_time = end_time
                    if activity != "Review":
                        schedule_list.append("Break - 15 min")
                        current_time += timedelta(minutes=15)
                
                internal_plan.append({
                    "Day": day_plan["day_num"],
                    "Date": day_plan.get("date").strftime("%Y-%m-%d") if hasattr(day_plan.get("date"), 'strftime') else str(day_plan.get("date")),
                    "Topic": topic_info["topic"],
                    "Subject": topic_info.get("subject", "General"),
                    "Complexity": topic_info["complexity"],
                    "Accuracy": topic_info["accuracy"],
                    "Weight": topic_info["weight"],
                    "Guidance": guidance,
                    "ScheduleMinutes": schedule,
                    "Resources": topic_resources,
                    "AvailableTime": slot,
                    "Schedule": schedule_list
                })
        
        # Validate we have a plan
        if not internal_plan:
            st.error("❌ No valid topics found to create a plan. Please check your performance data.")
            st.stop()
        
        # Step 7: Save plan
        update_progress(progress_bar, status_text, 95, "Saving your plan...")
        plan_file_name = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        plan_file_path = os.path.join(GENERATED_PLANS_DIR, plan_file_name)
        
        with open(plan_file_path, "w") as f:
            json.dump(internal_plan, f, default=str, indent=4)
        
        update_progress(progress_bar, status_text, 100, "Complete!")
        time.sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
        
        return internal_plan
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)  # Show full traceback for debugging
        st.stop()


def display_generated_plan(plan):
    """Display the generated study plan"""
    st.success("✅ Your personalized study plan has been generated successfully!")
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>📝 Your Personalized Study Plan</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Follow this schedule to improve your weak areas efficiently</p>", unsafe_allow_html=True)
    
    # Group by day
    grouped_plan = {}
    for entry in plan:
        day_num = entry["Day"]
        if day_num not in grouped_plan:
            grouped_plan[day_num] = {
                "Day": day_num,
                "Date": entry.get("Date", "Unknown"),
                "Topics": [],
                "ComplexityInfo": [],
                "Resources": [],
                "Schedule": [],
                "Guidance": []
            }
        
        grouped_plan[day_num]["Topics"].append(entry.get("Topic", "Unknown"))
        grouped_plan[day_num]["ComplexityInfo"].append({
            "topic": entry.get("Topic"),
            "complexity": entry.get("Complexity", "medium"),
            "accuracy": entry.get("Accuracy", 0)
        })
        grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
        grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))
        grouped_plan[day_num]["Guidance"].append(entry.get("Guidance", ""))
    
    # Display each day
    for day in sorted(grouped_plan.values(), key=lambda x: x["Day"]):
        display_plan_card(day)
    
    # Summary stats
    total_time = sum(sum(entry.get("ScheduleMinutes", {}).values()) for entry in plan)
    total_topics = len(plan)
    total_days = len(grouped_plan)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Days", total_days)
    with col2:
        st.metric("📚 Total Topics", total_topics)
    with col3:
        st.metric("⏱️ Total Study Time", f"{total_time // 60}h {total_time % 60}m")
    
    st.info("💾 Your plan has been automatically saved. View it anytime from 'View All Saved Plans'!")


# ============================================================================
# MAIN UI
# ============================================================================

def run_planner_ui():
    """Main function to run the Planner UI"""
    
    # Check premium status
    if not is_current_user_premium():
        st.markdown("## 📚 Study Planner")
        show_premium_gate()
        return
    
    # Import logic modules
    from logic_planner.date_selector import select_study_dates
    from logic_planner.plan_viewer import display_all_plans
    
    # Session state
    if "page" not in st.session_state:
        st.session_state.page = "planner"
    if "fetched_plan" not in st.session_state:
        st.session_state.fetched_plan = []
    if "free_days" not in st.session_state:
        st.session_state.free_days = []
    if "show_saved_plans" not in st.session_state:
        st.session_state.show_saved_plans = False
    
    # Get user
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id', None)
    
    if not user_id:
        st.error("❌ User not logged in. Please log in first.")
        st.stop()
    
    # Header
    st.markdown("<h1 style='text-align: center; margin-top:25px'>📚 Personalized Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Plan your studies efficiently, quicker and smarter!</h6>", unsafe_allow_html=True)
    
    # Show saved plans view
    if st.session_state.show_saved_plans:
        display_all_plans()
        st.stop()
    
    # View saved plans button
    if st.button("📂 View All Saved Plans"):
        st.session_state.show_saved_plans = True
        st.rerun()
    
    st.divider()
    
    # Select dates
    st.session_state.free_days = select_study_dates()
    
    # Generate button
    if st.button("🚀 Generate Your Personalized Plan", type="primary", use_container_width=True):
        # Validate
        validation_errors = validate_inputs(st.session_state.free_days, user_id)
        if validation_errors:
            for error in validation_errors:
                st.error(error)
            st.stop()
        
        # Generate and display
        plan = generate_study_plan(user_id, st.session_state.free_days)
        st.session_state.fetched_plan = plan
        display_generated_plan(plan)