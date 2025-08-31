# performance_ui.py
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.performance_tracker_agent import track_performance, get_feedback
from security.auth import login_required, init_session_state

@login_required
def performance_dashboard():
    st.title("📊 Performance Tracker")
    
    # Check if user has any quiz data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('id')
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Performance tracking dashboard
    st.info("📈 Performance tracking will show your quiz results and progress here.")
    st.write("Features coming soon:")
    st.write("- Quiz score history")
    st.write("- Topic-wise performance analysis") 
    st.write("- Learning progress visualization")
    st.write("- Personalized improvement recommendations")
    
    # Placeholder metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Quizzes Completed", "0", "0")
    
    with col2:
        st.metric("Average Score", "N/A", "0%")
    
    with col3:
        st.metric("Study Streak", "0 days", "0")

if __name__ == "__main__":
    init_session_state()
    performance_dashboard()
