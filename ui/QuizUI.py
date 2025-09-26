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
            difficulty = st.selectbox("Difficulty level:", ["Easy", "Medium", "Hard"])

    # ---------------- Generate Quiz ----------------
    if st.button("📝 Generate Quiz", use_container_width=True):
        status_placeholder = st.empty()
        with status_placeholder.status("Generating quiz...") as status:
            try:
                # Display model info before generation
                status.update(label="Connecting to AI model...", state="running")
                
                quiz_text = generate_quiz(num_questions, difficulty)  # ✅ pass difficulty
                
                if not quiz_text:
                    status.update(label="Failed to generate quiz", state="error")
                    st.error("⚠️ Empty response received. Please try again.")
                elif quiz_text.startswith("Error") or quiz_text.startswith("No data"):
                    status.update(label="Failed to generate quiz", state="error")
                    st.error(quiz_text)
                    st.info("💡 If you continue to have issues, try again in a few minutes as there may be temporary API limits.")
                    
                    # Suggest a different approach
                    st.info("💡 Try using fewer questions or a different difficulty level.")
                else:
                    status.update(label="Processing quiz data...", state="running")
                    st.session_state.quiz = parse_quiz(quiz_text)
                    st.session_state.responses = {}
                    st.session_state.submission_preview = []
                    
                    if not st.session_state.quiz:
                        status.update(label="Quiz format error", state="error")
                        st.warning("⚠️ Could not parse quiz format. The AI response format may be incorrect.")
                        with st.expander("Debug: Show raw AI response"):
                            st.code(quiz_text)
                    else:
                        status.update(label=f"✅ Generated {len(st.session_state.quiz)} questions!", state="complete")
                        st.success(f"✅ Successfully generated a {difficulty} quiz with {len(st.session_state.quiz)} questions!")
            except Exception as e:
                status.update(label="Error generating quiz", state="error")
                st.error(f"⚠️ Error generating quiz: {str(e)}")
                st.info("💡 Try refreshing the page or returning later if this issue persists.")

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
                # Import API configuration
                from utils.api_config import FLASK_TRACKER_ENDPOINT, DEFAULT_TIMEOUT, verify_services_status
                
                # Check if services are running
                services_status = verify_services_status()
                if not services_status["flask_tracker"]:
                    st.warning("⚠️ Flask Tracker service may not be running. Will attempt submission anyway.")
                
                # Get user_id from session state
                user_data = st.session_state.get('user_data', {})
                user_id = user_data.get('_id', 'current_user')
                
                response = requests.post(
                    FLASK_TRACKER_ENDPOINT,
                    json={"results": st.session_state.submission_preview},
                    headers={"X-User-ID": user_id},  # Add user ID to headers
                    timeout=DEFAULT_TIMEOUT
                )
                if response.status_code == 200:
                    st.success("✅ Submission sent successfully!")
                    st.dataframe(pd.DataFrame(st.session_state.submission_preview))
                    # Clear preview after submission
                    st.session_state.submission_preview = []
                else:
                    st.error(f"⚠️ Failed to submit. Status code: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection error: Make sure the tracker service (tracker.py) is running on port 5000")
                st.info("To start the tracker service, run: python services/tracker.py")
            except requests.exceptions.Timeout:
                st.error("❌ Connection timeout: The tracker API took too long to respond")
                st.info("This might be due to high processing load or network issues")
            except Exception as e:
                st.error(f"❌ Could not reach tracker API: {e}")


# ---------------- Main ----------------
if __name__ == "__main__":
    st.set_page_config(page_title="University Quiz", page_icon="🎓", layout="centered")
    init_session_state()
    quiz_dashboard()
