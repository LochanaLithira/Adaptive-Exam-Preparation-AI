import streamlit as st
import os
import sys
import datetime
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from logic_planner.performance_loader import load_performance
from logic_planner.planner import generate_plan, calculate_weights
from logic_planner.resources import resources
from logic_planner.plan_manager import save_plan_to_file, load_all_plans
from logic_planner.plan_viewer import display_all_plans


def is_same_plan(p1, p2):
    topics1 = [d['Topic'] for d in p1]
    topics2 = [d['Topic'] for d in p2]
    return topics1 == topics2


def run_planner_ui():
    st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)

    if "show_saved_plans" not in st.session_state:
        st.session_state.show_saved_plans = False

    st.markdown("<h1 style='text-align:center;'>🗓️ Personalized Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'>A Guidance to improve your performance. Attempt quizzes to get new study plans. Mark and see the total time you studied!</h6>", unsafe_allow_html=True)
    st.divider()

    col_main, col_right = st.columns([5, 1])
    with col_right:
        if st.button("📂 View Saved Plans"):
            st.session_state.show_saved_plans = True
            st.rerun()

    if st.session_state.show_saved_plans:
        if st.button("⬅️ Back to Current Plan"):
            st.session_state.show_saved_plans = False
            st.rerun()

        st.markdown("<h3 style='text-align:center;'>📄 Previously Saved Plans</h3>", unsafe_allow_html=True)
        saved_plans = load_all_plans(BASE_DIR)
        if not saved_plans:
            st.info("ℹ️ No saved plans found yet. Save your first plan to view it here!")
        else:
            display_all_plans(BASE_DIR)
        return

    records = load_performance()
    if not records:
        st.warning("⚠️ No performance data available yet. Please attempt a quiz first!")
        return

    weights = calculate_weights(records)
    plan = generate_plan(records)
    topic_weight_map = {w['topic']: w['weight'] for w in weights}

    existing_plans = load_all_plans(BASE_DIR)
    already_saved = any(is_same_plan(p.get("plan", []), plan) for p in existing_plans)

    if already_saved:
        st.button("💾 Plan Already Saved", disabled=True, use_container_width=True)
    else:
        if st.button("💾 Save This Plan", use_container_width=True, type="primary"):
            save_plan_to_file(plan, weights, BASE_DIR)
            st.success("✅ Plan saved successfully!")
            st.rerun()

    study_schedule = {
        "Learn": 30,
        "Practice Morning": 20,
        "Practice Afternoon": 20,
        "Practice Night": 20,
        "Review": 15
    }

    # ---------- FIXED LOOP ----------
    for day in plan[:7]:   # only show first 7 days
        day_num = day["Day"]
        topic = day["Topic"]
        if "Date" in day:
            date = datetime.datetime.strptime(day["Date"], "%Y-%m-%d").strftime("%d %b %Y")
        else:
            today = datetime.date.today()
            date = (today + datetime.timedelta(days=day["Day"])).strftime("%d %b %Y")

        weight = topic_weight_map.get(topic, 0)

        if weight > 50:
            text_color = "red"
            bg_color = "#ffebee"
        elif weight > 25:
            text_color = "orange"
            bg_color = "#fff3e0"
        else:
            text_color = "green"
            bg_color = "#e8f5e8"

        # build one HTML block per day
        html_content = f"""
        <div style='padding: 15px; border-radius: 10px; background-color: {bg_color};
                    border: 2px solid #ddd; min-height: 350px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;'>

            <h3 style='text-align: center; color: #333;'>📅 {date} - Day {day_num}</h3>
            <h4 style='color: {text_color}; text-align: center;'>Topic: {topic}</h4>

            <p style='color: #333'><b>Schedule:</b></p>
            <ul style="color: black;">
                <li>Learn Concept: {study_schedule['Learn']} min</li>
                <li>Practice (Morning): {study_schedule['Practice Morning']} min</li>
                <li>Practice (Afternoon / Evening): {study_schedule['Practice Afternoon']} min</li>
                <li>Practice (Night): {study_schedule['Practice Night']} min</li>
                <li>Review: {study_schedule['Review']} min</li>
            </ul>

            <p style='color: #333'><b>Resources:</b></p>
            <ul>
        """

        # add resources dynamically
        topic_resources = resources.get(topic, [])
        if topic_resources:
            for res in topic_resources:
                html_content += f"<li><a href='{res['url']}' target='_blank'>{res['title']}</a> ({res['type'].capitalize()})</li>"
        else:
            html_content += "<li>No resources available</li>"

        # close the block
        html_content += "</ul></div>"

        # render with components.html (never escapes)
        components.html(html_content, height=400, scrolling=True)
