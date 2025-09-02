# ui/plannerui.py
import streamlit as st
from agents.planner_agent import PlannerAgent
from ui.icons import icon_text

def show_planner(student_id: str):
    st.markdown(icon_text("planner", "Personalized Study Planner", 24), unsafe_allow_html=True)

    # Sample performance data for now
    sample_data = {
        "Math": {"score": 60, "weak": True},
        "Science": {"score": 85, "weak": False},
        "History": {"score": 50, "weak": True},
        "English": {"score": 75, "weak": False},
    }

    # Inject the sample data into PlannerAgent
    planner = PlannerAgent(performance_data=sample_data)
    plan = planner.generate_plan()

    st.markdown("---")
    st.subheader("Your Recommended Study Plan 📘")
    
    for item in plan:
        st.markdown(f"**{item['subject']}** - {item['hours_per_week']} hrs/week | Focus: {item['focus']}")
        st.info(item['recommendation'])
