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
            
            # Get user data for submission
            user_data = st.session_state.get('user_data', {})
            user_id = user_data.get('_id', 'anonymous')
            
            # Prepare data for FastAPI performance tracker
            answers = {}
            correct_answers = {}
            questions_text = {}
            
            for q in st.session_state.quiz:
                q_key = f"Q{q['id']}"
                answers[q_key] = st.session_state.responses.get(q["id"], "")
                correct_answers[q_key] = q["correct_answer"]
                questions_text[q_key] = q["question"]
            
            # Determine topic from questions (use first question's category)
            topic = st.session_state.quiz[0]["category"] if st.session_state.quiz else "General"
            
            # Prepare payload for FastAPI /track endpoint
            payload = {
                "user_id": str(user_id),
                "quiz_id": hash(str(st.session_state.quiz)) % 10000,  # Generate quiz ID
                "topic": topic,
                "answers": answers,
                "correct_answers": correct_answers,
                "questions_text": questions_text
            }
            
            try:
                # Call FastAPI performance tracker
                response = requests.post(
                    "http://localhost:8000/track",  # FastAPI endpoint
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    st.success("✅ Quiz submitted successfully!")
                    
                    
                else:
                    st.error(f"⚠️ Failed to submit. Status code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to performance tracker API. Please ensure the FastAPI server is running on port 8000.")
                st.info("💡 To start the server, run: `uvicorn agents.performance_tracker_agent:app --reload --port 8000`")
            except Exception as e:
                st.error(f"❌ Error submitting quiz: {e}")

# ---------------- Main ----------------
if __name__ == "__main__":
    st.set_page_config(page_title="University Quiz", page_icon="🎓", layout="centered")
    init_session_state()
    quiz_dashboard()
