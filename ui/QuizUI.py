"""
Integrated Quiz Module - Dashboard + Gemini Quiz Generator
"""
import streamlit as st
import sys
import os
import pandas as pd
import requests

# Add parent directory to path for auth modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import icon_text, info_message
from services.llm_service import generate_quiz, parse_quiz


# ---------------- Dashboard & Quiz ----------------
@login_required
def quiz_dashboard():
    """Main quiz interface for authenticated users"""
    st.markdown(icon_text("quiz", "🎓 Interactive Quiz Module", 28), unsafe_allow_html=True)
    
    # Check if user has session data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id')
    
    if not user_id:
        st.error("⚠️ User session not found. Please log in again.")
        return
    
    # Welcome info
    info_message("Welcome to the Adaptive Quiz System! Choose difficulty & start learning!")

    # Session state for quiz
    if "quiz" not in st.session_state:
        st.session_state.quiz = []
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "submission_preview" not in st.session_state:
        st.session_state.submission_preview = []

    # ---------------- Quiz Settings ----------------
    with st.container():
        st.markdown("### ⚙️ Quiz Settings")
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            num_questions = st.slider("Number of questions:", min_value=1, max_value=20, value=5)
        with col2:
            difficulty = st.selectbox("Difficulty level:", ["Easy", "Medium", "Difficult"])

    # ---------------- Generate Quiz ----------------
    if st.button("📝 Generate Quiz", use_container_width=True):
        with st.spinner(f"Generating a {difficulty} quiz..."):
            quiz_text = generate_quiz(num_questions, difficulty.lower())  # ✅ pass difficulty
            st.session_state.quiz = parse_quiz(quiz_text)
            st.session_state.responses = {}
            st.session_state.submission_preview = []
            if not st.session_state.quiz:
                st.warning("⚠️ Could not generate quiz. Please try again.")

    # ---------------- Display Quiz ----------------
    if st.session_state.quiz:
        st.markdown("---")
        st.markdown(f"## 🧩 {difficulty} Quiz")

        for q in st.session_state.quiz:
            st.markdown(f"### Q{q['id']}: {q['question']}")
            st.session_state.responses[q["id"]] = st.radio(
                f"Select your answer for Q{q['id']}:",
                list(q["options"].keys()),
                format_func=lambda x: f"{x}) {q['options'][x]}",
                index=None,
                key=f"q{q['id']}"
            )
            st.divider()

        # Step 1: Finish Quiz → Review answers
        if st.button("✅ Finish Quiz", use_container_width=True):
            # Prepare preview list
            st.session_state.submission_preview = []
            for q in st.session_state.quiz:
                st.session_state.submission_preview.append({
                    "id": q["id"],
                    "question": q["question"],
                    "category": q["category"],
                    "correct_answer": q["correct_answer"],
                    "user_answer": st.session_state.responses.get(q["id"]),
                    "options": q["options"]
                })

    # ---------------- Review Screen ----------------
    if st.session_state.submission_preview:
        st.markdown("## 📋 Review Your Answers")
        df = pd.DataFrame([
            {
                "QID": item["id"],
                "Question": item["question"],
                "Your Answer": (
                    f"{item['user_answer']}) {item['options'][item['user_answer']]}"
                    if item["user_answer"] else "❌ Not Answered"
                ),
                "Saved": "✅ Yes" if item["user_answer"] else "❌ No"
            }
            for item in st.session_state.submission_preview
        ])
        st.dataframe(df)

        # Final Submit button
        if st.button("🚀 Submit Your Answers", use_container_width=True):
            try:
                response = requests.post(
                    "http://localhost:5000/track_performance",
                    json={"results": st.session_state.submission_preview},
                    timeout=5
                )
                if response.status_code == 200:
                    st.success("✅ Submission sent successfully!")
                    st.dataframe(pd.DataFrame(st.session_state.submission_preview))
                    # Clear preview after submission
                    st.session_state.submission_preview = []
                else:
                    st.error(f"⚠️ Failed to submit. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Could not reach tracker API: {e}")


# ---------------- Main ----------------
if __name__ == "__main__":
    st.set_page_config(page_title="University Quiz", page_icon="🎓", layout="centered")
    init_session_state()
    quiz_dashboard()
