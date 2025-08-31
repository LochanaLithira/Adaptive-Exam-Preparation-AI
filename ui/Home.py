import streamlit as st
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import init_session_state, check_authentication, login_required
from ui.LoginUI import main as login_main

def show_dashboard():
    """Main dashboard for authenticated users"""
    st.title("📚 Adaptive Exam Preparation Dashboard")
    
    # User welcome message
    user_data = st.session_state.user_data
    st.write(f"Welcome back, **{user_data['full_name']}**! 👋")
    
    # Navigation menu
    st.markdown("---")
    st.subheader("🎯 What would you like to do today?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Take Quiz", use_container_width=True, type="primary"):
            st.session_state.current_page = "quiz"
            st.rerun()
        st.markdown("*Test your knowledge with adaptive quizzes*")
    
    with col2:
        if st.button("📊 View Performance", use_container_width=True, type="primary"):
            st.session_state.current_page = "performance"
            st.rerun()
        st.markdown("*Track your progress and analytics*")
    
    with col3:
        if st.button("📋 Study Planner", use_container_width=True, type="primary"):
            st.session_state.current_page = "planner"
            st.rerun()
        st.markdown("*Plan your study schedule*")
    
    # Recent activity section
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    
    # User-specific activity (placeholder for now)
    user_data = st.session_state.get('user_data', {})
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("🎯 Welcome to your personalized learning dashboard!")
            st.info("📚 Start by taking your first quiz to begin tracking progress")
            st.info("📈 Your performance analytics will appear here after completing quizzes")
        
        with col2:
            st.metric("Quizzes Completed", "0", "0")
            st.metric("Average Score", "N/A", "0%")
            st.metric("Study Hours", "0", "0")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Start First Quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()
    
    with col2:
        if st.button("📈 View Progress"):
            st.session_state.current_page = "performance"
            st.rerun()
    
    with col3:
        if st.button("💡 Study Plan"):
            st.session_state.current_page = "planner"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Settings"):
            st.session_state.current_page = "settings"
            st.rerun()

def show_navigation():
    """Show navigation sidebar"""
    with st.sidebar:
        st.title("📚 Navigation")
        
        user_data = st.session_state.user_data
        st.write(f"👤 {user_data['username']}")
        
        # Navigation menu
        pages = {
            "🏠 Dashboard": "dashboard",
            "📝 Quiz": "quiz", 
            "📊 Performance": "performance",
            "📋 Planner": "planner",
            "⚙️ Settings": "settings"
        }
        
        current_page = st.session_state.get('current_page', 'dashboard')
        
        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True, 
                        type="primary" if current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            from ui.LoginUI import logout_user
            logout_user()

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Adaptive Exam Preparation AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not check_authentication():
        # Show login page
        login_main()
        return
    
    # Show authenticated interface
    show_navigation()
    
    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'dashboard':
        show_dashboard()
    elif current_page == 'quiz':
        st.title("📝 Quiz Module")
        st.info("Quiz module will be integrated here")
        # Quiz functionality will be added when QuizUI is implemented
    elif current_page == 'performance':
        st.title("📊 Performance Analytics")
        st.info("Performance module will be integrated here")
        # Performance tracking will be added when PerformanceUI is implemented
    elif current_page == 'planner':
        st.title("📋 Study Planner")
        st.info("Planner module will be integrated here")
        # Study planning will be added when PlannerUI is implemented
    elif current_page == 'settings':
        st.title("⚙️ Settings")
        st.info("Settings page - coming soon!")
    
if __name__ == "__main__":
    main()