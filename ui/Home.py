import streamlit as st
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import init_session_state, check_authentication, login_required
from ui.LoginUI import main as login_main
from ui.icons import get_svg_icon, icon_text, info_message
from ui.PerformanceUI import performance_dashboard, PerformanceAnalytics
from ui.QuizUI import quiz_dashboard

# ✅ set_page_config must be the very first Streamlit command in this file
st.set_page_config(
    page_title="Adaptive Exam Preparation AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_dashboard():
    """Main dashboard for authenticated users"""
    st.markdown(icon_text("book", "Adaptive Exam Preparation Dashboard", 24), unsafe_allow_html=True)
    
    # User welcome message
    user_data = st.session_state.user_data
    st.markdown(icon_text("wave", f"Welcome back, *{user_data['full_name']}*!", 20), unsafe_allow_html=True)
    
    # Navigation menu
    st.markdown("---")
    st.markdown(icon_text("target", "What would you like to do today?", 20), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Take Quiz", use_container_width=True, type="primary"):
            st.session_state.current_page = "quiz"
            st.rerun()
        st.markdown("Test your knowledge with adaptive quizzes")
    
    with col2:
        if st.button("View Performance", use_container_width=True, type="primary"):
            st.session_state.current_page = "performance"
            st.rerun()
        st.markdown("Track your progress and analytics")
    
    with col3:
        if st.button("Study Planner", use_container_width=True, type="primary"):
            st.session_state.current_page = "planner"
            st.rerun()
        st.markdown("Plan your study schedule")
    
    # Recent activity section
    st.markdown("---")
    st.markdown(icon_text("analytics", "Recent Activity", 20), unsafe_allow_html=True)
    
    # User-specific activity (placeholder for now)
    user_data = st.session_state.get('user_data', {})
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            info_message("Welcome to your personalized learning dashboard!")
            info_message("Start by taking your first quiz to begin tracking progress")
            info_message("Your performance analytics will appear here after completing quizzes")
        
        with col2:
            st.metric("Quizzes Completed", "0", "0")
            st.metric("Average Score", "N/A", "0%")
            st.metric("Study Hours", "0", "0")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Start First Quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()
    
    with col2:
        if st.button("View Progress"):
            st.session_state.current_page = "performance"
            st.rerun()
    
    with col3:
        if st.button("Study Plan"):
            st.session_state.current_page = "planner"
            st.rerun()
    
    with col4:
        if st.button("Settings"):
            st.session_state.current_page = "settings"
            st.rerun()

def show_navigation():
    """Show navigation sidebar"""
    with st.sidebar:
        st.markdown(icon_text("book", "Navigation", 20), unsafe_allow_html=True)
        
        user_data = st.session_state.user_data
        st.markdown(icon_text("user", user_data['username'], 16), unsafe_allow_html=True)
        
        # Navigation menu
        pages = {
            "Dashboard": "dashboard",
            "Quiz": "quiz", 
            "Performance": "performance",
            "Planner": "planner",
            "Settings": "settings"
        }
        
        current_page = st.session_state.get('current_page', 'dashboard')
        
        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True, 
                        type="primary" if current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", use_container_width=True, type="secondary"):
            from ui.LoginUI import logout_user
            logout_user()

def main():
    """Main application entry point"""
    # Initialize session state
    init_session_state()
    
    # Check authentication with error handling
    try:
        authentication_status = check_authentication()
    except Exception as e:
        st.error(f"❌ Authentication system error: {str(e)}")
        st.info("💡 This might be due to database connection issues. Please check MongoDB connection.")
        return
    
    if not authentication_status:
        # Show login page
        try:
            login_main()
        except Exception as e:
            st.error(f"❌ Login interface error: {str(e)}")
            st.info("💡 There was an error loading the login interface.")
        return
    
    # Show authenticated interface
    show_navigation()
    
    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'dashboard':
        show_dashboard()
    elif current_page == 'quiz':
        quiz_dashboard()
    elif current_page == 'performance':
        try:
            performance_dashboard()
        except Exception as e:
            st.error(f"❌ Performance dashboard error: {str(e)}")
            st.info("💡 There was an error loading the performance dashboard. Please check the database connection.")
    elif current_page == 'planner':
        st.markdown(icon_text("planner", "Study Planner", 24), unsafe_allow_html=True)
        st.info("Planner module will be integrated here")
    elif current_page == 'settings':
        st.markdown(icon_text("settings", "Settings", 24), unsafe_allow_html=True)
        st.info("Settings page - coming soon!")

if __name__ == "__main__":
    main()