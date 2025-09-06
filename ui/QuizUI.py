"""
Integrated Quiz Module - Dashboard + Gemini Quiz Generator
"""
import streamlit as st
import sys
import os
import pandas as pd
import random
import re
import requests

# Add parent directory to path for auth modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import get_svg_icon, icon_text, info_message
from services.llm_service import generate_quiz, parse_quiz



# ---------------- Dashboard & Quiz ----------------
@login_required
def quiz_dashboard():
    """Main quiz interface for authenticated users"""
    st.markdown(icon_text("quiz", "Interactive Quiz Module", 28), unsafe_allow_html=True)
    
    # Check if user has session data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id')
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Welcome info
    info_message("Welcome to the Adaptive Quiz System!")

    # Session state for quiz
    if "quiz" not in st.session_state:
        st.session_state.quiz = []
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    num_questions = st.slider("Select number of questions:", min_value=1, max_value=20, value=5)

    if st.button("📝 Generate Quiz"):
        with st.spinner("Generating quiz..."):
            quiz_text = generate_quiz(num_questions)
            st.session_state.quiz = parse_quiz(quiz_text)
            st.session_state.responses = {}
    
    # Display quiz questions
    if st.session_state.quiz:
        for q in st.session_state.quiz:
            st.markdown(f"### Q{q['id']}: {q['question']}")
            st.session_state.responses[q["id"]] = st.radio(
                f"Select your answer:",
                list(q["options"].keys()),
                format_func=lambda x: f"{x}) {q['options'][x]}",
                key=f"q{q['id']}"
            )
        st.markdown("---")
        if st.button("✅ Finish Quiz"):
            st.markdown("## 📤 Submitting Your Responses...")
            submission = []
            for q in st.session_state.quiz:
                submission.append({
                    "id": q["id"],
                    "question": q["question"],
                    "category": q["category"],
                    "correct_answer": q["correct_answer"],
                    "user_answer": st.session_state.responses.get(q["id"]),
                    "options": q["options"]
                })
            #Dummy API call
            try:
                response = requests.post(
                    "http://localhost:5000/track_performance",
                    json={"results": submission},
                    timeout=5
                )
                if response.status_code == 200:
                    st.success("✅ Submission sent successfully!")
                    st.json(response.json())
                else:
                    st.error(f"⚠️ Failed to submit. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Could not reach tracker API: {e}")

# ---------------- Main ----------------
if __name__ == "__main__":
    st.set_page_config(page_title="University Quiz", page_icon="🎓", layout="centered")
    init_session_state()
    quiz_dashboard()
