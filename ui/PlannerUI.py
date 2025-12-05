# PlannerUI.py (Updated with improvements)
import streamlit as st
import os
import sys
import requests
import time
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
from utils.subscription import is_current_user_premium

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_inputs(free_days, user_id):
    """
    Validate all inputs before plan generation.
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    if not user_id:
        errors.append("❌ User not logged in. Please log in first.")
    
    if not free_days or len(free_days) == 0:
        errors.append("❌ No study days selected. Please select your exam date and study time.")
    
    if len(free_days) < 2:
        errors.append("⚠️ For an effective study plan, we recommend at least 2 days. Consider selecting a later exam date.")
    
    # Check if all days have required data
    for i, day in enumerate(free_days):
        if not day.get('date'):
            errors.append(f"❌ Day {i+1}: Date is missing")
        if not day.get('available_time'):
            errors.append(f"❌ Day {i+1}: Available time is missing")
    
    return errors


def call_api_with_retry(url, data, max_retries=3, timeout=DEFAULT_TIMEOUT):
    """
    Call API with exponential backoff retry logic.
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise Exception(f"Request timed out after {max_retries} attempts")
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"API request failed: {str(e)}")
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    
    raise Exception("Failed to connect to API")


def show_plan_generation_progress():
    """
    Show progress indicators during plan generation.
    Returns progress bar and status text elements.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    return progress_bar, status_text


def update_progress(progress_bar, status_text, progress, message):
    """Update progress bar and status message."""
    progress_bar.progress(progress)
    status_text.info(f"📊 {message}")


# ============================================================================
# PREMIUM GATE
# ============================================================================

def show_premium_gate():
    """Show premium feature gate for Study Planner"""
    st.markdown(
        """
        <style>
        .premium-container {
            background: linear-gradient(135deg, rgba(16, 24, 39, 0.8) 0%, rgba(17, 24, 39, 0.9) 100%);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            margin: 1rem 0;
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
            height: 90%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""<div class="premium-container">
        <div class="premium-badge">⭐ PREMIUM FEATURE</div>
        <h1 style="color: white; margin-bottom: 1rem;">Study Planner</h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-bottom: 2rem;">
            Unlock the Study Planner to create personalized learning schedules, track your progress, 
            and optimize your study time with AI-powered recommendations.
        </p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #e2e8f0;">📅 Smart Scheduling</h3>
            <p style="color: rgba(255,255,255,0.7);">AI-powered study plans tailored to your weak areas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #e2e8f0;">🎯 Progress Tracking</h3>
            <p style="color: rgba(255,255,255,0.7);">Track completion and time spent on each topic</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #e2e8f0;">📊 Analytics</h3>
            <p style="color: rgba(255,255,255,0.7);">Visualize your learning journey and improvements</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #e2e8f0;">📚 Smart Resources</h3>
            <p style="color: rgba(255,255,255,0.7);">Curated learning materials for each topic</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⭐ Upgrade to Premium", type="primary", use_container_width=True):
            st.session_state.current_page = "subscription"
            st.rerun()


# ============================================================================
# MAIN PLANNER UI
# ============================================================================

def run_planner_ui():
    """Main function to run the Planner UI"""
    
    # Check premium status
    is_premium = is_current_user_premium()
    
    if not is_premium:
        st.markdown("## 📚 Study Planner")
        show_premium_gate()
        return
    
    # --- Load environment variables ---
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    dotenv_path = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path)
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    if not YOUTUBE_API_KEY:
        st.warning("⚠️ YouTube API key not found. Resource fetching may be limited.")
    
    # --- Path setup ---
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    
    # --- Import logic modules ---
    from logic_planner.plan_manager import (
        save_plan_to_storage, 
        load_saved_plans,
        get_user_plans,
        update_plan_progress
    )
    from logic_planner.plan_viewer import display_all_plans
    from logic_planner.resources import resources, fetch_resources_with_fallback
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
    if "show_saved_plans" not in st.session_state:
        st.session_state.show_saved_plans = False
    
    # Get user data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id', None)
    
    if not user_id:
        st.error("❌ User not logged in. Please log in first.")
        st.stop()
    
    # --- Header ---
    st.markdown("<h1 style='text-align: center; margin-top:25px'>📚 Personalized Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Plan your studies efficiently, quicker and smarter!</h6>", unsafe_allow_html=True)
    
    # --- Show saved plans view ---
    if st.session_state.show_saved_plans:
        display_all_plans()
        st.stop()
    
    # --- View Saved Plans Button ---
    if st.button("📂 View All Saved Plans"):
        st.session_state.show_saved_plans = True
        st.rerun()
    
    st.divider()
    
    # --- Select study dates ---
    st.session_state.free_days = select_study_dates()
    
    # --- Generate Plan Button ---
    generate_clicked = st.button(
        "🚀 Generate Your Personalized Plan",
        type="primary",
        use_container_width=True
    )
    
    if generate_clicked:
        # Validate inputs
        validation_errors = validate_inputs(st.session_state.free_days, user_id)
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
            st.stop()
        
        # Show progress indicators
        progress_bar, status_text = show_plan_generation_progress()
        
        try:
            # Step 1: Serialize free days
            update_progress(progress_bar, status_text, 10, "Preparing your study schedule...")
            
            free_days_serialized = [
                {
                    "date": day["date"].strftime("%Y-%m-%d") if isinstance(day["date"], (datetime, date)) else str(day["date"]),
                    "available_time": day["available_time"]
                }
                for day in st.session_state.free_days
            ]
            
                        # Step 2: Fetch performance data (with retry + diagnostics)
            update_progress(progress_bar, status_text, 25, "Fetching your performance data...")
            time.sleep(0.3)  # brief UX pause

            perf_url = f"{PLANNER_AGENT_URL}/get_plan/{user_id}"
            perf_response = None
            perf_attempts = 3
            perf_backoff = 1

            last_exception = None
            for attempt in range(1, perf_attempts + 1):
                try:
                    perf_response = requests.get(perf_url, timeout=DEFAULT_TIMEOUT)
                    break
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt == perf_attempts:
                        # final failure -> show rich error and stop
                        progress_bar.empty()
                        status_text.empty()
                        st.error("❌ Failed to fetch performance data after multiple attempts.")
                        st.exception(e)
                        st.info("💡 Check that your Planner Agent is running and PLANNER_AGENT_URL is correct.")
                        st.stop()
                    else:
                        time.sleep(perf_backoff)
                        perf_backoff *= 2

            # If we have a response, show diagnostics for developers
            if perf_response is not None:
                # Developer diagnostics (hidden by default)
                with st.expander("Developer: performance endpoint diagnostics (click to view)"):
                    st.write(f"URL: {perf_url}")
                    st.write(f"Status code: {perf_response.status_code}")
                    try:
                        st.json(perf_response.json())
                    except Exception:
                        st.text(perf_response.text)

            # Handle non-200 gracefully and provide actionable guidance
            if perf_response is None:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ No response from Planner Agent. Please check service status.")
                st.stop()

            # Accept 200 (OK) and 204 (No Content). For other codes show error details.
            if perf_response.status_code == 204:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ No performance data found (204). Please complete some quizzes first.")
                st.info("💡 Take a few quizzes to help us identify weak areas.")
                st.stop()
            elif perf_response.status_code != 200:
                # Show full response body for debugging
                progress_bar.empty()
                status_text.empty()
                try:
                    body = perf_response.json()
                except Exception:
                    body = perf_response.text
                st.error(f"❌ Unexpected response from Planner Agent: {perf_response.status_code}")
                st.write(body)
                st.info("🔍 Check planner agent logs and ensure `/get_plan/{user_id}` returns JSON.")
                st.stop()

            # Now parse JSON safely
            try:
                stored_data = perf_response.json()
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ Failed to parse Planner Agent response as JSON.")
                st.exception(e)
                st.stop()

            # Extract subjects (weak areas)
            subjects = stored_data.get("subjects") if isinstance(stored_data, dict) else None

            # If backend returns empty subjects or None -> show helpful message
            if not subjects:
                progress_bar.empty()
                status_text.empty()
                st.warning("❌ No weak areas identified yet. Please complete some quizzes.")
                st.info("💡 Try doing 2-3 short quizzes so we can create a personalized plan for you.")
                st.stop()

            
            # Step 3: Generate plan
            update_progress(progress_bar, status_text, 50, "Generating your personalized study plan...")
            time.sleep(0.5)
            
            try:
                plan_data = call_api_with_retry(
                    PLANNER_AGENT_ENDPOINT,
                    {
                        "user_id": user_id,
                        "subjects": subjects,
                        "free_days": free_days_serialized
                    }
                )
                
                if "error" in plan_data:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ {plan_data['error']}")
                    st.stop()
                
                if not plan_data.get("plan"):
                    progress_bar.empty()
                    status_text.empty()
                    st.warning("⚠️ No plan was generated. Please try again.")
                    st.stop()
                
                api_plan = plan_data["plan"]
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Failed to generate plan: {str(e)}")
                st.info("💡 Please check your internet connection and try again.")
                st.stop()
            
            # Step 4: Process and enhance plan
            update_progress(progress_bar, status_text, 75, "Adding learning resources...")
            
            # Continue in Part 2...
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            st.stop()

# PlannerUI.py - Part 2: Plan Processing and Display
# This continues from Part 1 after Step 4

            # Process topics from API response
            all_topics = []
            for item in api_plan:
                all_topics.append({
                    "subject": item.get("subject", "General"),
                    "topic": item.get("topic", item.get("activity", "Unknown")),
                    "accuracy": item.get("accuracy", 0)
                })
            
            # Distribute topics intelligently across days
            from logic_planner.generate_plan import (
                distribute_topics_intelligently,
                create_adaptive_schedule,
                generate_guidance
            )
            
            # Create topic info with weights
            topics_with_weights = []
            for topic in all_topics:
                accuracy = topic.get("accuracy", 0)
                weight = max(100 - accuracy, 0)
                
                if weight > 70:
                    complexity = "high"
                elif weight > 40:
                    complexity = "medium"
                else:
                    complexity = "low"
                
                topics_with_weights.append({
                    "topic": topic["topic"],
                    "subject": topic["subject"],
                    "accuracy": accuracy,
                    "weight": weight,
                    "complexity": complexity
                })
            
            # Distribute topics across available days
            distributed_plan = distribute_topics_intelligently(
                topics_with_weights,
                st.session_state.free_days,
                None
            )
            
            update_progress(progress_bar, status_text, 85, "Fetching educational resources...")
            
            # Enhance plan with resources and schedules
            # Add timeout protection using ThreadPoolExecutor
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
            
            def safe_fetch_resources(topic_info, youtube_key):
                """Wrapper function to safely fetch resources with timeout"""
                try:
                    return fetch_resources_with_fallback(
                        topic_info["topic"],
                        topic_info.get("subject", "General"),
                        youtube_key,
                        max_youtube_timeout=2  # Strict 2 second timeout for YouTube
                    )
                except Exception as e:
                    print(f"Resource fetch error for {topic_info['topic']}: {e}")
                    # Return basic fallback
                    return [{
                        "type": "read",
                        "title": f"Search for {topic_info['topic']}",
                        "url": f"https://www.google.com/search?q={topic_info['topic'].replace(' ', '+')}"
                    }]
            
            internal_plan = []
            total_topics = sum(len(day_plan["topics"]) for day_plan in distributed_plan)
            processed_topics = 0
            
            for day_plan in distributed_plan:
                day_num = day_plan["day_num"]
                day_date = day_plan.get("date")
                available_time_slot = day_plan.get("available_time")
                
                for topic_info in day_plan["topics"]:
                    # Update progress for each topic
                    processed_topics += 1
                    progress_percent = 85 + int((processed_topics / total_topics) * 10)
                    update_progress(
                        progress_bar, 
                        status_text, 
                        min(progress_percent, 94),
                        f"Processing topic {processed_topics}/{total_topics}: {topic_info['topic'][:30]}..."
                    )
                    
                    # Fetch resources with strict timeout using ThreadPoolExecutor
                    topic_resources = []
                    try:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(
                                safe_fetch_resources,
                                topic_info,
                                YOUTUBE_API_KEY
                            )
                            # Wait maximum 4 seconds total (includes 2s YouTube + processing)
                            topic_resources = future.result(timeout=4)
                    except FuturesTimeoutError:
                        print(f"⏱️ Timeout fetching resources for {topic_info['topic']}, using fallback")
                        # Provide instant fallback
                        topic_resources = [{
                            "type": "concept",
                            "title": f"Learn {topic_info['topic']} on Khan Academy",
                            "url": f"https://www.khanacademy.org/search?page_search_query={topic_info['topic'].replace(' ', '+')}"
                        }]
                    except Exception as e:
                        print(f"❌ Error fetching resources for {topic_info['topic']}: {e}")
                        topic_resources = [{
                            "type": "read",
                            "title": f"Search for {topic_info['topic']}",
                            "url": f"https://www.google.com/search?q={topic_info['topic'].replace(' ', '+')}"
                        }]
                    
                    # Create adaptive schedule based on complexity
                    # Estimate available time from slot
                    if "Morning" in available_time_slot or "Afternoon" in available_time_slot:
                        available_minutes = 180  # 3 hours
                    else:
                        available_minutes = 120  # 2 hours
                    
                    schedule = create_adaptive_schedule(topic_info, available_minutes)
                    
                    # Generate personalized guidance
                    guidance = generate_guidance(topic_info)
                    
                    # Create plan entry
                    plan_entry = {
                        "Day": day_num,
                        "Date": day_date.strftime("%Y-%m-%d") if hasattr(day_date, 'strftime') else str(day_date),
                        "Topic": topic_info["topic"],
                        "Subject": topic_info.get("subject", "General"),
                        "Complexity": topic_info["complexity"],
                        "Accuracy": topic_info["accuracy"],
                        "Weight": topic_info["weight"],
                        "Guidance": guidance,
                        "ScheduleMinutes": schedule,
                        "Resources": topic_resources,
                        "AvailableTime": available_time_slot
                    }
                    
                    internal_plan.append(plan_entry)
            
            # Continue with the rest of the plan processing...
            for entry in internal_plan:
                day_info = next((d for d in st.session_state.free_days if str(d.get('date')) == entry['Date']), None)
                
                if not day_info:
                    continue
                
                # Parse available time
                slot = day_info.get('available_time', 'Morning (08:00AM)')
                try:
                    time_part = slot.split("(")[1].split(")")[0].strip()
                    if 'AM' in time_part.upper() or 'PM' in time_part.upper():
                        time_part = time_part.replace('.', ':').upper()
                        available_time = datetime.strptime(time_part, "%I:%M%p").time()
                    else:
                        parts = time_part.split(":")
                        start_hour = int(parts[0])
                        start_minute = int(parts[1]) if len(parts) > 1 else 0
                        available_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M").time()
                except:
                    available_time = datetime.strptime("09:00AM", "%I:%M%p").time()
                
                # Create schedule with time slots
                current_time = datetime.combine(day_info.get('date', date.today()), available_time)
                schedule_list = []
                
                schedule_mins = entry.get('ScheduleMinutes', {})
                for activity, minutes in schedule_mins.items():
                    end_time = current_time + timedelta(minutes=minutes)
                    schedule_list.append(
                        f"{activity} {entry['Topic']} ({current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')})"
                    )
                    current_time = end_time
                    
                    # Add break after Learn and Practice (not after Review)
                    if activity != "Review":
                        schedule_list.append("Break - 15 min")
                        current_time += timedelta(minutes=15)
                
                entry['Schedule'] = schedule_list
            
            # Save plan
            st.session_state.fetched_plan = internal_plan
            
            update_progress(progress_bar, status_text, 95, "Saving your plan...")
            
            # Save to file
            plan_file_name = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            GENERATED_PLANS_DIR = os.path.join(BASE_DIR, "generated_plans")
            os.makedirs(GENERATED_PLANS_DIR, exist_ok=True)
            plan_file_path = os.path.join(GENERATED_PLANS_DIR, plan_file_name)
            
            with open(plan_file_path, "w") as f:
                json.dump(internal_plan, f, default=str, indent=4)
            
            update_progress(progress_bar, status_text, 100, "Complete!")
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Show success message
            st.success("✅ Your personalized study plan has been generated successfully!")
            
            # Display the plan
            st.markdown("---")
            st.markdown("<h2 style='text-align: center;'>📝 Your Personalized Study Plan</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Follow this schedule to improve your weak areas efficiently</p>", unsafe_allow_html=True)
            
            # Group plan by day
            grouped_plan = {}
            for entry in internal_plan:
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
                # Format date nicely
                try:
                    date_obj = datetime.strptime(day['Date'], "%Y-%m-%d")
                    day_val = date_obj.day
                    if 10 <= day_val % 100 <= 20:
                        suffix = 'th'
                    else:
                        suffix = {1:'st', 2:'nd', 3:'rd'}.get(day_val % 10, 'th')
                    date_display = f"{day_val}{suffix} {date_obj.strftime('%B %Y')}"
                except:
                    date_display = day['Date']
                
                # Create complexity badges
                complexity_badges = []
                for info in day["ComplexityInfo"]:
                    if info["complexity"] == "high":
                        badge_color = "#ff4444"
                        emoji = "🔴"
                    elif info["complexity"] == "medium":
                        badge_color = "#ffaa00"
                        emoji = "🟡"
                    else:
                        badge_color = "#44ff44"
                        emoji = "🟢"
                    
                    complexity_badges.append(
                        f"{emoji} <span style='color: {badge_color}; font-weight: bold;'>{info['topic']}</span> "
                        f"<span style='color: gray; font-size: 0.9em;'>({info['accuracy']}% accuracy)</span>"
                    )
                
                topics_html = "<br>".join(complexity_badges)
                
                # Create schedule HTML
                schedule_html = "".join([f"<li style='margin: 8px 0;'>{s}</li>" for s in day["Schedule"]])
                
                # Create resources HTML
                resources_html = ""
                if day["Resources"]:
                    seen_urls = set()
                    for res in day["Resources"]:
                        if res["url"] not in seen_urls:
                            seen_urls.add(res["url"])
                            type_emoji = {"video": "🎥", "practice": "📝", "read": "📖", "concept": "💡"}.get(res["type"], "📚")
                            resources_html += f"<li style='margin: 5px 0;'>{type_emoji} <a href='{res['url']}' target='_blank'>{res['title']}</a> <span style='color: gray;'>({res['type'].capitalize()})</span></li>"
                else:
                    resources_html = "<li>No resources available</li>"
                
                # Create guidance HTML
                guidance_html = "<br>".join([f"• {g}" for g in day["Guidance"] if g])
                
                # Display day card
                card_html = f"""
                <div style='padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                          border: 2px solid #444; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                    <h2 style='text-align: center; color: #4CAF50; margin-bottom: 5px;'>📅 Day {day['Day']}</h2>
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
            
            # Summary statistics
            total_time = sum(sum(entry.get("ScheduleMinutes", {}).values()) for entry in internal_plan)
            total_topics = len(internal_plan)
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