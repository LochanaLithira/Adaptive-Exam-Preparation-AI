"""
Comprehensive Quiz History Dashboard - FIXED VERSION
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import get_svg_icon
from utils.config import get_database, COLLECTIONS

# CSS Constants for styling
GLASS_CARD_STYLE = "background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); transition: all 0.3s ease; margin-bottom: 1rem;"

class QuizHistoryManager:
    """Manage and display comprehensive quiz history"""
    
    def __init__(self, user_id):
        self.user_id = str(user_id) if user_id else None
        self.db = get_database()
        self.results_collection = self.db[COLLECTIONS["quiz_results"]] if self.db is not None else None
    
    def get_all_quiz_results(self) -> List[Dict]:
        """Fetch all quiz results for the current user"""
        if self.results_collection is None:
            return []
        
        try:
            results = list(self.results_collection.find(
                {"user_id": self.user_id}
            ).sort("_id", 1))  # Sort by oldest first
            
            return results
        except Exception as e:
            st.error(f"Error fetching quiz results: {str(e)}")
            return []
    
    def _get_performance_category(self, result: Dict) -> str:
        """Get performance category for a quiz result"""
        accuracy = self._get_accuracy(result)
        if accuracy >= 80:
            return "Excellent"
        elif accuracy >= 60:
            return "Good"
        else:
            return "Needs Work"
    
    def _get_accuracy(self, result: Dict) -> float:
        """Calculate accuracy percentage for a quiz result"""
        score = result.get("result", {}).get("score", 0)
        total = result.get("result", {}).get("total", 1)
        return (score / total) * 100 if total > 0 else 0

def render_quiz_history_header():
    """Render the page header with title and description"""
    st.markdown(f"""
    <div style="{GLASS_CARD_STYLE} text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #e2e8f0; margin: 0 0 1rem 0; font-size: 2.5rem;">
            {get_svg_icon('history', 40, '#667eea')} Quiz History
        </h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin: 0;">
            Complete overview of your learning journey with detailed analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_filters_panel(results: List[Dict]) -> Dict[str, str]:
    """Render filters and sorting controls, return selected options"""
    if not results:
        return {"topic": "All", "performance": "All", "sort": "Newest First", "date_range": "All Time"}
    
    st.markdown("### Filters & Sorting")
    
    # Extract unique subjects from results
    topics = sorted(list(set([r.get("subject", "Unknown") for r in results])))
    topics.insert(0, "All")
    
    # Create filter columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Initialize session state if needed
        if 'topic_filter' not in st.session_state:
            st.session_state.topic_filter = "All"
            
        # Use widget with session state value
        topic_filter = st.selectbox(
            "Filter by Subject",
            options=topics,
            key="topic_filter_selector",
            index=topics.index(st.session_state.topic_filter) if st.session_state.topic_filter in topics else 0
        )
        
        # Update session state based on widget value
        if topic_filter != st.session_state.topic_filter:
            st.session_state.topic_filter = topic_filter
    
    with col2:
        performance_options = ["All", "Excellent", "Good", "Needs Work"]
        
        # Initialize session state if needed
        if 'performance_filter' not in st.session_state:
            st.session_state.performance_filter = "All"
            
        # Use widget with session state value
        performance_filter = st.selectbox(
            "Filter by Performance",
            options=performance_options,
            key="performance_filter_selector",
            index=performance_options.index(st.session_state.performance_filter) if st.session_state.performance_filter in performance_options else 0
        )
        
        # Update session state based on widget value
        if performance_filter != st.session_state.performance_filter:
            st.session_state.performance_filter = performance_filter
    
    with col3:
        sort_options = ["Newest First", "Oldest First", "Best Score", "Worst Score", "Topic A-Z"]
        
        # Initialize session state if needed
        if 'sort_option' not in st.session_state:
            st.session_state.sort_option = "Oldest First"
            
        # Use widget with session state value
        sort_option = st.selectbox(
            "Sort by",
            options=sort_options,
            key="sort_option_selector",
            index=sort_options.index(st.session_state.sort_option) if st.session_state.sort_option in sort_options else 0
        )
        
        # Update session state based on widget value
        if sort_option != st.session_state.sort_option:
            st.session_state.sort_option = sort_option
    
    with col4:
        date_options = ["All Time", "Last 7 Days", "Last 30 Days", "Last 3 Months"]
        
        # Initialize session state if needed
        if 'date_range' not in st.session_state:
            st.session_state.date_range = "All Time"
            
        # Use widget with session state value
        date_range = st.selectbox(
            "Date Range",
            options=date_options,
            key="date_range_selector",
            index=date_options.index(st.session_state.date_range)
        )
        
        # Update session state based on widget value
        if date_range != st.session_state.date_range:
            st.session_state.date_range = date_range
    
    # Search functionality
    # Initialize session state if needed
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
        
    # Use widget with session state value
    search_query = st.text_input(
        "Search in quiz subjects or questions",
        placeholder="Type to search...",
        key="search_query_input",
        value=st.session_state.search_query
    )
    
    # Update session state based on widget value
    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
    
    return {
        "topic": topic_filter,
        "performance": performance_filter,
        "sort": sort_option,
        "date_range": date_range,
        "search": search_query
    }

def apply_filters(results: List[Dict], filters: Dict[str, str]) -> List[Dict]:
    """Apply all filters to the results"""
    filtered_results = results.copy()
    
    # Create helper functions for performance calculations
    def get_accuracy(result: Dict) -> float:
        score = result.get("result", {}).get("score", 0)
        total = result.get("result", {}).get("total", 1)
        return (score / total) * 100 if total > 0 else 0
    
    def get_performance_category(result: Dict) -> str:
        accuracy = get_accuracy(result)
        if accuracy >= 80:
            return "Excellent"
        elif accuracy >= 60:
            return "Good"
        else:
            return "Needs Work"

    # Filter by subject
    if filters["topic"] != "All":
        filtered_results = [r for r in filtered_results if r.get("subject", "Unknown") == filters["topic"]]
    
    # Filter by performance
    if filters["performance"] != "All":
        filtered_results = [r for r in filtered_results if get_performance_category(r) == filters["performance"]]
    
    # Filter by date range
    if filters["date_range"] != "All Time":
        now = datetime.now(timezone.utc)
        if filters["date_range"] == "Last 7 Days":
            cutoff_date = now - timedelta(days=7)
        elif filters["date_range"] == "Last 30 Days":
            cutoff_date = now - timedelta(days=30)
        elif filters["date_range"] == "Last 3 Months":
            cutoff_date = now - timedelta(days=90)
        
        filtered_results = [r for r in filtered_results 
                          if r.get("_id") and r["_id"].generation_time >= cutoff_date]
    
    # Apply search filter
    if filters["search"]:
        search_term = filters["search"].lower()
        search_filtered = []
        for r in filtered_results:
            # Search in subject
            if search_term in r.get("subject", "Unknown").lower():
                search_filtered.append(r)
                continue
            
            # Search in questions text
            questions_text = r.get("questions_text", {})
            for question in questions_text.values():
                if search_term in question.lower():
                    search_filtered.append(r)
                    break
        
        filtered_results = search_filtered
    
    # Apply sorting
    if filters["sort"] == "Newest First":
        filtered_results.sort(key=lambda x: x.get("_id", datetime.now(timezone.utc)), reverse=True)
    elif filters["sort"] == "Oldest First":
        filtered_results.sort(key=lambda x: x.get("_id", datetime.now(timezone.utc)))
    elif filters["sort"] == "Best Score":
        filtered_results.sort(key=lambda x: get_accuracy(x), reverse=True)
    elif filters["sort"] == "Worst Score":
        filtered_results.sort(key=lambda x: get_accuracy(x))
    elif filters["sort"] == "Topic A-Z":
        filtered_results.sort(key=lambda x: x.get("subject", "Unknown"))
    
    return filtered_results

def render_filter_summary(original_count: int, filtered_count: int, filters: Dict[str, str]):
    """Render a summary of applied filters"""
    active_filters = []
    
    if filters["topic"] != "All":
        active_filters.append(f"Subject: {filters['topic']}")
    if filters["performance"] != "All":
        active_filters.append(f"Performance: {filters['performance']}")
    if filters["date_range"] != "All Time":
        active_filters.append(f"Date: {filters['date_range']}")
    if filters["search"]:
        active_filters.append(f"Search: '{filters['search']}'")
    
    if active_filters or filtered_count != original_count:
        filter_text = " | ".join(active_filters) if active_filters else "No filters applied"
        
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} padding: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #e2e8f0; font-weight: 600;">Showing {filtered_count} of {original_count} quizzes</span>
                    {f"<br><span style='color: rgba(255,255,255,0.7); font-size: 0.9rem;'>Filters: {filter_text}</span>" if active_filters else ""}
                </div>
                <div>
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">Sorted by: {filters['sort']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_quiz_statistics(results: List[Dict]):
    """Render overall statistics for all quiz results"""
    if not results:
        return
    
    def get_accuracy(result: Dict) -> float:
        score = result.get("result", {}).get("score", 0)
        total = result.get("result", {}).get("total", 1)
        return (score / total) * 100 if total > 0 else 0
    
    total_quizzes = len(results)
    total_questions = sum(r.get("result", {}).get("total", 0) for r in results)
    total_correct = sum(r.get("result", {}).get("score", 0) for r in results)
    overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    # Performance categories
    excellent = len([r for r in results if get_accuracy(r) >= 80])
    good = len([r for r in results if 60 <= get_accuracy(r) < 80])
    needs_work = len([r for r in results if get_accuracy(r) < 60])
    
    st.markdown("### Overall Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center;">
            <div style="margin-bottom: 0.5rem;">{get_svg_icon('quiz', 32, '#667eea')}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #667eea;">{total_quizzes}</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Total Quizzes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        accuracy_color = '#22c55e' if overall_accuracy >= 70 else '#f59e0b' if overall_accuracy >= 50 else '#ef4444'
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center;">
            <div style="margin-bottom: 0.5rem;">{get_svg_icon('target', 32, accuracy_color)}</div>
            <div style="font-size: 2rem; font-weight: bold; color: {accuracy_color};">{overall_accuracy:.1f}%</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Overall Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center;">
            <div style="margin-bottom: 0.5rem;">{get_svg_icon('chart', 32, '#06b6d4')}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #06b6d4;">{total_questions}</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Total Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center;">
            <div style="margin-bottom: 0.5rem;">{get_svg_icon('check_circle', 32, '#22c55e')}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #22c55e;">{excellent}</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Excellent Results</div>
        </div>
        """, unsafe_allow_html=True)

def get_answer_text_mapping(answer_letter: str, options: dict = None) -> str:
    """
    Convert answer letters to full text using stored options, with fallback
    This shows the actual answer text instead of just the letter
    
    Handles various answer formats:
    - User answer: "A) " (with trailing space)
    - Correct answer: "C" (just letter)
    - Options format: {"A) ": "text...", "B) ": "text...", ...}
    """
    if not answer_letter:
        return "No answer"
    
    # If we have the options dictionary, use the actual text
    if options and isinstance(options, dict):
        # Normalize the answer: remove spaces and parentheses, keep only letter
        answer_normalized = answer_letter.strip().rstrip(' ').rstrip(')').upper()
        
        # Try to find matching option in various formats
        for option_key, option_text in options.items():
            # Normalize the option key the same way
            option_normalized = option_key.strip().rstrip(' ').rstrip(')').upper()
            
            # If the normalized forms match
            if option_normalized == answer_normalized:
                # Return with the original option key format + text (ensure space after key)
                key_clean = option_key.strip()
                if not key_clean.endswith(' '):
                    key_clean += ' '
                return f"{key_clean}{option_text}"
        
        # If no direct match found, try matching just the letter part
        for option_key, option_text in options.items():
            # Extract just the letter from option key: "A) " -> "A"
            option_letter = option_key.strip().rstrip(' ').rstrip(')').upper()
            if option_letter == answer_normalized:
                # Use consistent formatting: "A) text..."
                return f"{option_letter}) {option_text}"
    
    # Fallback: just return the letter with basic formatting
    answer_clean = answer_letter.strip().rstrip(')').rstrip(' ').upper()
    if len(answer_clean) == 1:
        return f"Option {answer_clean}"
    else:
        return answer_letter

def get_question_text_from_ir_service(q_key: str, user_answer: str, correct_answer: str) -> str:
    """
    Try to provide meaningful question context for older quiz results
    This is a fallback for older quiz results that don't have question_text stored
    """
    try:
        # Create a more informative placeholder that gives context about the answer format
        if user_answer and correct_answer:
            if len(user_answer) == 1 and len(correct_answer) == 1:
                # Looks like multiple choice (A, B, C, D)
                return f"Question {q_key} (Multiple Choice Question - Full text not available in older quiz format)"
            else:
                # Might be a different answer format
                return f"Question {q_key} (Question text not available in older quiz format)"
        else:
            return f"Question {q_key}"
    except Exception:
        return f"Question {q_key}"

def render_detailed_quiz_cards(results: List[Dict]):
    """Render detailed cards for each quiz result"""
    if not results:
        return
    
    st.markdown("### Detailed Quiz History")
    
    # Display results in a grid format
    for i, result in enumerate(results):
        accuracy = (result.get("result", {}).get("score", 0) / result.get("result", {}).get("total", 1)) * 100
        
        # Color coding based on performance
        if accuracy >= 80:
            color = "#22c55e"
            icon = "check_circle"
            status = "Excellent"
            border_color = "#22c55e"
        elif accuracy >= 60:
            color = "#f59e0b"
            icon = "target"
            status = "Good"
            border_color = "#f59e0b"
        else:
            color = "#ef4444"
            icon = "refresh"
            status = "Needs Work"
            border_color = "#ef4444"
        
        # Format date
        quiz_date = result.get("_id").generation_time if result.get("_id") else datetime.now(timezone.utc)
        formatted_date = quiz_date.strftime("%B %d, %Y at %I:%M %p")
        
        # Get topic and quiz details
        topic = result.get("subject", "Unknown")
        score = result.get("result", {}).get("score", 0)
        total = result.get("result", {}).get("total", 1)
        quiz_id = result.get("quiz_id", "N/A")
        
        # Create expandable card for each quiz
        with st.expander(f"Quiz #{i+1}: {topic} - {accuracy:.1f}% ({formatted_date})", 
                         expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Quiz details using native Streamlit components instead of HTML table
                st.markdown(f"""
                <div style="{GLASS_CARD_STYLE} border-left: 4px solid {border_color};">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
                        {get_svg_icon(icon, 24, color)}
                        <div>
                            <h4 style="color: #e2e8f0; margin: 0; font-size: 1.2rem;">{topic}</h4>
                            <p style="color: {color}; margin: 0; font-weight: 600;">{status} Performance</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick Performance Summary
                st.markdown("**📊 Quick Summary:**")
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                
                with perf_col1:
                    st.metric("Score", f"{score}/{total}", delta=f"{accuracy:.1f}%")
                
                with perf_col2:
                    if accuracy >= 80:
                        st.metric("Performance", "Excellent", delta="🌟")
                    elif accuracy >= 60:
                        st.metric("Performance", "Good", delta="👍")
                    else:
                        st.metric("Performance", "Needs Work", delta="📚")
                
                with perf_col3:
                    wrong_count = total - score
                    if wrong_count > 0:
                        st.metric("Need Review", f"{wrong_count} questions", delta="❌")
                    else:
                        st.metric("Perfect Score!", "All correct", delta="🎉")
                
                st.markdown("---")
                
                # Enhanced Questions & Answers Section
                st.markdown("**🔍 Questions & Answers:**")
                
                # Get explanations from result field
                explanations = result.get("result", {}).get("explanations", {})
                
                # Handle both new format (questions_details) and old format (answers/correct_answers)
                questions_details = result.get("questions_details", [])
                
                if questions_details:
                    # New format: Use questions_details array
                    for i, question_detail in enumerate(questions_details, 1):
                        question_text = question_detail.get("question_text", f"Question {i}")
                        user_answer = question_detail.get("user_answer", "No answer")
                        correct_answer = question_detail.get("correct_answer", "Unknown")
                        is_correct = question_detail.get("is_correct", False)
                        question_id = question_detail.get("question_id", f"Q{i}")
                        
                        # Display question
                        st.markdown(f"**Question {i}:** {question_text}")
                        
                        # Get options for this question to display full answer text
                        question_options = question_detail.get("options", {})
                        
                        # Display answers with full text using stored options
                        user_answer_text = get_answer_text_mapping(user_answer, question_options)
                        correct_answer_text = get_answer_text_mapping(correct_answer, question_options)
                        
                        answer_col1, answer_col2 = st.columns([1, 1])
                        
                        with answer_col1:
                            if is_correct:
                                st.success(f"✓ Your answer: **{user_answer_text}**")
                            else:
                                st.error(f"✗ Your answer: **{user_answer_text}**")
                        
                        with answer_col2:
                            st.info(f"🎯 Correct answer: **{correct_answer_text}**")
                        
                        # Show explanation for wrong answers
                        if not is_correct and explanations.get(question_id):
                            st.markdown("**💡 Explanation:**")
                            explanation_text = explanations[question_id]
                            st.markdown(f"""
                            <div style="background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)); 
                                        border-left: 4px solid #3b82f6; 
                                        padding: 1rem; 
                                        border-radius: 8px; 
                                        margin: 0.5rem 0;">
                                <span style="color: #e2e8f0;">{explanation_text}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if i < len(questions_details):  # Don't add separator after last question
                            st.markdown("---")
                
                else:
                    # Old format: Use answers and correct_answers dictionaries
                    answers = result.get("answers", {})
                    correct_answers = result.get("correct_answers", {})
                    
                    if answers and correct_answers:
                        # Show info banner for older quiz format
                        st.info("ℹ️ This is an older quiz format. Question texts are not available, but answers and explanations are preserved.")
                        for q_key in sorted(answers.keys()):
                            user_answer = answers.get(q_key, "No answer")
                            correct_answer = correct_answers.get(q_key, "Unknown")
                            is_correct = user_answer == correct_answer
                            
                            # Try to get question text (fallback for older format)
                            question_text = get_question_text_from_ir_service(q_key, user_answer, correct_answer)
                            
                            # Display question
                            st.markdown(f"**{question_text}**")
                            
                            # Display answers with enhanced text (no options available in old format)
                            user_answer_text = get_answer_text_mapping(user_answer, None)
                            correct_answer_text = get_answer_text_mapping(correct_answer, None)
                            
                            answer_col1, answer_col2 = st.columns([1, 1])
                            
                            with answer_col1:
                                if is_correct:
                                    st.success(f"✓ Your answer: **{user_answer_text}**")
                                else:
                                    st.error(f"✗ Your answer: **{user_answer_text}**")
                            
                            with answer_col2:
                                st.info(f"🎯 Correct answer: **{correct_answer_text}**")
                            
                            # Show explanation for wrong answers
                            if not is_correct and explanations.get(q_key):
                                st.markdown("**💡 Explanation:**")
                                explanation_text = explanations[q_key]
                                st.markdown(f"""
                                <div style="background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)); 
                                            border-left: 4px solid #3b82f6; 
                                            padding: 1rem; 
                                            border-radius: 8px; 
                                            margin: 0.5rem 0;">
                                    <span style="color: #e2e8f0;">{explanation_text}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Add separator between questions
                            remaining_keys = [k for k in sorted(answers.keys()) if k > q_key]
                            if remaining_keys:  # Don't add separator after last question
                                st.markdown("---")
                    else:
                        st.info("No question details available for this quiz")
            
            with col2:
                # Performance visualization using Streamlit components
                st.markdown(f"""
                <div style="{GLASS_CARD_STYLE} text-align: center;">
                    <h5 style="color: #e2e8f0; margin: 0 0 1rem 0;">Performance</h5>
                    <div style="font-size: 3rem; font-weight: bold; color: {color}; margin: 1rem 0;">
                        {accuracy:.1f}%
                    </div>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 8px; margin: 1rem 0;">
                        <div style="background: {color}; border-radius: 10px; height: 100%; width: {accuracy}%;"></div>
                    </div>
                    <p style="color: rgba(255,255,255,0.7); margin: 0;">
                        {score} out of {total} correct
                    </p>
                </div>
                """, unsafe_allow_html=True)
                


@login_required
def quiz_history_dashboard():
    """Main quiz history dashboard"""
        
    # Page header
    render_quiz_history_header()
    
    # Get user data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id')
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Initialize quiz history manager
    history_manager = QuizHistoryManager(user_id)
    all_results = history_manager.get_all_quiz_results()
    
    if not all_results:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #e2e8f0; margin-bottom: 1rem;">No Quiz History Yet</h3>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 2rem;">
                Start taking quizzes to build your learning history and track your progress!
            </p>
            <div style="margin-top: 2rem;">
                <a href="#" onclick="window.location.reload()" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                ">Take Your First Quiz</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Show overall statistics
    render_quiz_statistics(all_results)
    
    st.markdown("---")
    
    # Now render filters and get user selections
    filters = render_filters_panel(all_results)
    
    # Apply filters to get filtered results
    try:
        filtered_results = apply_filters(all_results, filters)
        
        # Show filter summary
        render_filter_summary(len(all_results), len(filtered_results), filters)
        
        st.markdown("---")
        
        # Show detailed quiz history (use filtered results)
        if filtered_results:
            render_detailed_quiz_cards(filtered_results)
        else:
            st.markdown(f"""
            <div style="{GLASS_CARD_STYLE} text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                <h3 style="color: #e2e8f0; margin-bottom: 1rem;">No Results Found</h3>
                <p style="color: rgba(255,255,255,0.7);">
                    No quizzes match your current filters. Try adjusting the filters above.
                </p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error processing quiz history: {str(e)}")
        st.info("Try clearing the filters or refreshing the page.")

# ---------------- Main ----------------
if __name__ == "__main__":
    st.set_page_config(
        page_title="Quiz History - Adaptive Exam Preparation AI",
        page_icon="📊",
        layout="wide"
    )
    init_session_state()
    quiz_history_dashboard()