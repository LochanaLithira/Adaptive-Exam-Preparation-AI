"""
Integrated Quiz Module - Dashboard + Gemini Quiz Generator
"""
import streamlit as st
import sys
import os
import pandas as pd
import requests
from pathlib import Path

# Add parent directory to path for auth modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import icon_text, info_message
from services.llm_service import GeminiClient
from services.ir_retriever import SimpleIR, DATA_DIR
from ui.quiz_styles import QUIZ_CUSTOM_CSS  # Import CSS from separate file
from utils.subscription import is_current_user_premium

# ---------------- Initialize Clients ----------------
gemini = GeminiClient()
ir = SimpleIR()

# ---------------- Main Dashboard ----------------
@login_required
def quiz_dashboard():
    """Main quiz interface for authenticated users"""
    st.set_page_config(page_title="University Quiz", page_icon="🎓", layout="wide")
    
    # Load custom CSS
    st.markdown(QUIZ_CUSTOM_CSS, unsafe_allow_html=True)

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# Interactive Learning Quiz")
    with col2:
        user_data = st.session_state.get('user_data', {})

    user_id = user_data.get('_id', "student_1")

    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Document Check
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    existing_files = [os.path.join(root, f) for root, _, files in os.walk(DATA_DIR) for f in files if f.endswith((".pdf", ".txt"))]
    if not existing_files:
        st.error("⚠️ No learning materials found. Please contact your instructor to add study materials.")
        return

    # ---------------- Quiz Settings ----------------
    if "questions" not in st.session_state or not st.session_state.get("questions"):
        st.markdown("<div class='section-header'> Quiz Setup & Configuration</div>", unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='settings-card'>", unsafe_allow_html=True)

            # Subject and Module selection
            col1, col2 = st.columns(2)
            with col1:
                subject_folders = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
                selected_subject = st.selectbox(" Choose Your Subject", options=subject_folders) if subject_folders else None

            with col2:
                selected_module = None
                if selected_subject:
                    subject_path = os.path.join(DATA_DIR, selected_subject)
                    module_files = [f for f in os.listdir(subject_path) if f.endswith((".pdf", ".txt"))]
                    module_names = [Path(f).stem.split('_', 1)[-1] for f in module_files]
                    if module_names:
                        selected_module = st.selectbox(" Choose Module/Unit", options=module_names)

            # Quiz customization
            # Check if user has premium subscription for question limit
            is_premium = is_current_user_premium()
            
            # Set question options based on subscription
            if is_premium:
                question_options = [5, 10, 15, 20]
                max_questions = 20
                st.success(" Premium subscription: Access up to 20 questions per quiz!")
            else:
                question_options = [5, 10]
                max_questions = 10
                
                # Display upgrade message with proper navigation
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info("ℹ Free tier: Maximum 10 questions per quiz.")
                with col2:
                    if st.button(" Upgrade to Premium", key="upgrade_btn"):
                        st.session_state.current_page = "subscription"
                        st.rerun()
            
            num_questions = st.select_slider("Number of Questions", options=question_options, value=min(10, max(question_options)))
            difficulty_display = st.radio("Difficulty", options=["🟢 Easy", "🟡 Medium", "🔴 Hard"], index=1)
            difficulty = difficulty_display.split(" ")[1]

            query = f"{selected_subject} - {selected_module}" if selected_subject and selected_module else None

            # Generate Button
            if st.button(" Generate My Quiz", use_container_width=True, type="primary"):
                if not query:
                    st.error(" Please select a subject and module to continue.")
                else:
                    with st.spinner(" Generating your personalized quiz..."):
                        search_path = os.path.join(DATA_DIR, selected_subject)
                        retrieved = ir.retrieve(query=query, topk=10, folder=search_path)
                        passages = [p for p, _ in retrieved]

                    if not passages:
                        st.error("❌ No relevant content found.")
                    else:
                        try:
                            client = GeminiClient()
                            with st.spinner(" Creating personalized questions..."):
                                questions = client.generate_quiz_from_passages(passages, topic=query, max_questions=num_questions)

                            if not questions:
                                st.error("❌ Failed to generate questions.")
                            else:
                                st.success(f"✅ Quiz with {len(questions)} questions generated!")
                                st.balloons()
                                st.session_state["questions"] = questions
                                st.session_state["user_answers"] = {}
                                st.session_state["submitted"] = False
                                st.session_state["selected_subject"] = selected_subject
                                st.session_state["selected_module"] = selected_module
                                st.session_state["difficulty"] = difficulty
                                st.session_state["num_questions"] = num_questions
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error generating quiz: {e}")

            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Quiz Display ----------------
    if "questions" in st.session_state and st.session_state["questions"]:
        st.markdown("<div class='section-header'>📝 Your Personalized Quiz</div>", unsafe_allow_html=True)

        answered = len(st.session_state.get("user_answers", {}))
        total = len(st.session_state["questions"])
        progress = answered / total if total > 0 else 0

        st.progress(progress)
        st.markdown(f"<div class='progress-text'>📊 Progress: {answered}/{total} answered ({int(progress*100)}%)</div>", unsafe_allow_html=True)

        # Questions
        for idx, q in enumerate(st.session_state["questions"]):
            st.markdown(f"""
                <div class='quiz-question-card'>
                    <h3> {idx+1}.</h>
                    <p>{q['question']}</p>
                </div>
            """, unsafe_allow_html=True)

            options = q.get("options", {})
            option_values = [options[k] for k in sorted(options.keys())]
            current_answer = st.session_state["user_answers"].get(idx)
            choice = st.radio(
                f"Select answer for Question {idx+1}:",
                options=option_values,
                key=f'q{idx}_radio',
                index=option_values.index(current_answer) if current_answer in option_values else None,
                label_visibility="collapsed"
            )
            if choice:
                st.session_state["user_answers"][idx] = choice

        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

        # Submission buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 Start New Quiz"):
                for key in ["questions", "user_answers", "submitted", "show_confirmation"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        with col3:
            all_answered = all(idx in st.session_state["user_answers"] for idx in range(len(st.session_state["questions"])))
            if st.button("📩 Submit Quiz", type="primary", disabled=not all_answered):
                st.session_state["show_confirmation"] = True
                st.rerun()

        # ---------------- Quiz Confirmation Table ----------------
        if st.session_state.get("show_confirmation", False) and not st.session_state.get("submitted", False):
            st.markdown("<div class='section-header'>📋 Review Your Answers</div>", unsafe_allow_html=True)
            
            # Build quiz summary table
            quiz_data = []
            for idx, q in enumerate(st.session_state["questions"]):
                selected_text = st.session_state["user_answers"].get(idx, "Not answered")
                
                # Determine if question is answered
                if idx in st.session_state["user_answers"] and st.session_state["user_answers"][idx]:
                    status = "✅ Answered"
                else:
                    status = "❌ Not Answered"
                
                quiz_data.append({
                    "Question": f"Q{idx + 1}",
                    "Status": status
                })
            
            # Display answers table
            df = pd.DataFrame(quiz_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            
            # Final submission buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("⬅️ Back to Edit", use_container_width=True):
                    st.session_state["show_confirmation"] = False
                    st.rerun()
            
            with col3:
                if st.button("✅ Confirm & Submit", type="primary", use_container_width=True):
                    st.session_state["submitted"] = True
                    
                    # Create columns for centered progress indicators with increased width
                    _, center_col, _ = st.columns([0.5, 3, 0.5])
                    
                    # Add custom CSS to ensure progress indicators are centered
                    st.markdown("""
                    <style>
                    .stProgress > div {
                        display: flex !important;
                        justify-content: center !important;
                        width: 100% !important;
                    }
                    .stInfo {
                        text-align: center !important;
                        margin: 0 auto !important;
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                        width: 100% !important;
                    }
                    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div[data-testid="stVerticalBlock"] {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    with center_col:
                        # Show progress indicator
                        progress_container = st.empty()
                        # Custom styled info message
                        progress_container.markdown("""
                        <div style="background-color: rgba(40, 120, 200, 0.1); 
                                    border: 1px solid #3182ce; 
                                    border-radius: 10px; 
                                    padding: 15px; 
                                    text-align: center; 
                                    color: #e2e8f0;
                                    width: 100%;
                                    margin: 0 auto;
                                    display: block;">
                            <p style="margin: 0; font-size: 16px;">🔄 Processing your quiz submission...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Progress bar
                        progress_bar = st.progress(0)
                    
                    # ✅ Build quiz payload with option letters
                    quiz_payload = []
                    total_questions = len(st.session_state["questions"])
                    
                    for idx, q in enumerate(st.session_state["questions"]):
                        # Update progress
                        progress_value = (idx + 1) / total_questions / 2  # First half of progress (preparing data)
                        with center_col:
                            progress_bar.progress(progress_value)
                            # Custom styled info message with progress
                            progress_container.markdown(f"""
                            <div style="background-color: rgba(40, 120, 200, 0.1); 
                                        border: 1px solid #3182ce; 
                                        border-radius: 10px; 
                                        padding: 15px; 
                                        text-align: center; 
                                        color: #e2e8f0;
                                        width: 100%;
                                        margin: 0 auto;
                                        display: block;">
                                <p style="margin: 0; font-size: 16px;">🔄 Processing quiz data... ({idx + 1}/{total_questions})</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        selected_text = st.session_state["user_answers"].get(idx)

                        option_letter = None
                        for letter, text in q.get("options", {}).items():
                            if text == selected_text:
                                option_letter = letter
                                break

                        quiz_payload.append({
                            "id": idx + 1,
                            "question": q["question"],
                            "category": q.get("category", "General Topic"),
                            "subject": st.session_state.get("selected_subject", "Unknown"),
                            "correct_answer": q["correct_answer"],
                            "user_answer": option_letter,
                            "options": q.get("options", {})
                        })

                    # CSS is already added above
                    
                    try:
                        with center_col:
                            # Custom styled info message instead of using st.info
                            progress_container.markdown("""
                            <div style="background-color: rgba(40, 120, 200, 0.1); 
                                        border: 1px solid #3182ce; 
                                        border-radius: 10px; 
                                        padding: 15px; 
                                        text-align: center; 
                                        color: #e2e8f0;
                                        width: 100%;
                                        margin: 0 auto;
                                        display: block;">
                                <p style="margin: 0; font-size: 16px;">🔄 Submitting your answers to the server...</p>
                            </div>
                            """, unsafe_allow_html=True)
                            progress_bar.progress(0.6)  # 60% progress
                        
                        from utils.api_config import FLASK_TRACKER_ENDPOINT, DEFAULT_TIMEOUT, verify_services_status
                        response = requests.post(
                            FLASK_TRACKER_ENDPOINT,
                            json={"results": quiz_payload},
                            headers={"X-User-ID": user_id},
                            timeout=DEFAULT_TIMEOUT
                        )
                        
                        with center_col:
                            progress_bar.progress(0.8)  # 80% progress
                            # Custom styled info message
                            progress_container.markdown("""
                            <div style="background-color: rgba(40, 120, 200, 0.1); 
                                        border: 1px solid #3182ce; 
                                        border-radius: 10px; 
                                        padding: 15px; 
                                        text-align: center; 
                                        color: #e2e8f0;
                                        width: 100%;
                                        margin: 0 auto;
                                        display: block;">
                                <p style="margin: 0; font-size: 16px;">🔄 Processing your results...</p>
                            </div>
                            """, unsafe_allow_html=True)

                        if response.status_code == 200:
                            # Complete the progress
                            progress_bar.progress(1.0)
                            progress_container.empty()
                            
                            # Parse response
                            result = response.json()
                            
                            # Show simplified success message with increased width
                            _, center_col, _ = st.columns([0.5, 3, 0.5])
                            with center_col:
                                # Custom styled success message
                                st.markdown("""
                                <div style="background-color: rgba(72, 187, 120, 0.1); 
                                            border: 1px solid #48bb78; 
                                            border-radius: 10px; 
                                            padding: 20px; 
                                            text-align: center; 
                                            color: #e2e8f0;
                                            width: 100%;
                                            margin: 10px auto;
                                            display: block;">
                                    <p style="margin: 0; font-size: 18px; font-weight: bold;">✅ Quiz submitted successfully!</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            progress_container.empty()
                            progress_bar.empty()
                            _, center_col, _ = st.columns([0.5, 3, 0.5])
                            with center_col:
                                # Custom styled error message
                                st.markdown(f"""
                                <div style="background-color: rgba(252, 129, 129, 0.1); 
                                            border: 1px solid #fc8181; 
                                            border-radius: 10px; 
                                            padding: 15px; 
                                            text-align: center; 
                                            color: #e2e8f0;
                                            width: 100%;
                                            margin: 0 auto;
                                            display: block;">
                                    <p style="margin: 0; font-size: 16px;">❌ Submission failed. Code: {response.status_code}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    except Exception as e:
                        # Clear progress indicators
                        progress_container.empty()
                        progress_bar.empty()
                        
                        # Show detailed error message in centered column with increased width
                        _, center_col, _ = st.columns([0.5, 3, 0.5])
                        with center_col:
                            # Custom styled error message
                            st.markdown(f"""
                            <div style="background-color: rgba(252, 129, 129, 0.1); 
                                        border: 1px solid #fc8181; 
                                        border-radius: 10px; 
                                        padding: 15px; 
                                        text-align: center; 
                                        color: #e2e8f0;
                                        width: 100%;
                                        margin: 0 auto;
                                        display: block;">
                                <p style="margin: 0; font-size: 16px; font-weight: bold;">❌ Could not submit quiz: {e}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Additional details message
                            st.markdown("""
                            <div style="background-color: rgba(252, 129, 129, 0.05); 
                                        border: 1px solid #fc8181; 
                                        border-radius: 10px; 
                                        padding: 15px; 
                                        text-align: center; 
                                        color: #e2e8f0;
                                        width: 100%;
                                        margin: 10px auto;
                                        display: block;">
                                <p style="margin: 0; font-weight: bold;">Submission Error</p>
                                <p style="margin: 8px 0 0 0;">There was a problem connecting to the quiz tracking service. Your answers were not saved.</p>
                                <p style="margin: 8px 0 0 0;">Please check your internet connection and try again.</p>
                            </div>
                            """, unsafe_allow_html=True)

# ---------------- Main ----------------
if __name__ == "__main__":
    init_session_state()
    quiz_dashboard()