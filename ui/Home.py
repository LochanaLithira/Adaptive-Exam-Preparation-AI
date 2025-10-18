import streamlit as st
import sys
import os
import html

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import init_session_state, check_authentication, login_required
from ui.LoginUI import main as login_main
from ui.icons import get_svg_icon, icon_text, info_message
from ui.PerformanceUI import performance_dashboard, PerformanceAnalytics
from ui.QuizUI import quiz_dashboard
from ui.QuizHistoryUI import quiz_history_dashboard
from ui.PlannerUI import run_planner_ui
from ui.SubscriptionUI import subscription_page
from utils.subscription import is_current_user_premium
from ui.home_styles import HOME_CUSTOM_CSS, GLASS_CARD_STYLE

# ✅ set_page_config must be the very first Streamlit command in this file
st.set_page_config(
    page_title="StudyAura",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force sidebar visibility
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

def create_section_header(title, icon_name):
    """Creates a styled section header with an icon"""
    icon_svg = get_svg_icon(icon_name, size=20)
    header_html = f'''
    <div class="section-header">
        {icon_svg} <span style="margin-left: 10px;">{html.escape(title)}</span>
    </div>
    '''
    return st.markdown(header_html, unsafe_allow_html=True)

def create_action_card(title, description, icon_name):
    """Creates a styled action card with hover effects"""
    icon_svg = get_svg_icon(icon_name, size=32)
    return f'''
    <div class="action-card">
        {icon_svg}
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(description)}</p>
    </div>
    '''

def create_blue_info_message(message):
    """Creates a QuizUI-style blue info message"""
    return st.markdown(f'''
    <div class="info-message-blue">
        <p style="margin: 0; font-size: 16px;">{html.escape(message)}</p>
    </div>
    ''', unsafe_allow_html=True)

def create_blue_progress_message(message):
    """Creates a QuizUI-style blue progress message"""
    return st.markdown(f'''
    <div class="progress-message">
        <p style="margin: 0; font-size: 16px;">{html.escape(message)}</p>
    </div>
    ''', unsafe_allow_html=True)

def show_dashboard():
    """Main dashboard for authenticated users"""
    # Create a main container for better layout control
    with st.container():
        # Header with styled title
        book_icon = get_svg_icon("book", size=28)
        st.markdown(f'''
        <div class="title-text">
            {book_icon} 
            <span style="margin-left: 10px;">StudyAura</span>
        </div>
        ''', unsafe_allow_html=True)
    
    # User welcome message
    user_data = st.session_state.user_data
    subscription_type = user_data.get('subscription_type', 'free')
    
    # Show different welcome message based on subscription
    wave_icon = get_svg_icon("wave", size=24)
    if subscription_type == 'premium':
        st.markdown(f'''
        <div class="subtitle-text"> 
            <span style="font-size: 22px;">Welcome back, {html.escape(user_data['full_name'])}</span> <br>
            💎 <b>Premium Member</b>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="subtitle-text">
            <span style="font-size: 22px;">Welcome back, {html.escape(user_data['full_name'])}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    # Custom divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Main action section
    create_section_header("What would you like to do today?", "target")
    
    # Use columns with gaps for better spacing
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")
    
    with col1:
        action_html = create_action_card(
            "Take Quiz", 
            "Test your knowledge with adaptive quizzes", 
            "clipboard"
        )
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("Start Quiz", use_container_width=True, type="primary"):
            st.session_state.current_page = "quiz"
            st.rerun()
    
    with col2:
        action_html = create_action_card(
            "View Performance", 
            "Track your progress and analytics", 
            "chart"
        )
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("Performance", use_container_width=True, type="primary"):
            st.session_state.current_page = "performance"
            st.rerun()
    
    with col3:
        action_html = create_action_card(
            "Study Planner", 
            "Create and manage your study schedule", 
            "calendar"
        )
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("Planner", use_container_width=True, type="primary"):
            st.session_state.current_page = "planner"
            st.rerun()
    


def show_navigation():
    """Show navigation sidebar"""
    # Force sidebar to be visible
    st.markdown("""
    <style>
    section[data-testid="stSidebar"][aria-expanded="false"] > div {
        width: 300px !important;
        margin-left: 0px !important;
    }
    section[data-testid="stSidebar"] {
        width: 300px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Simple navigation menu
        current_page = st.session_state.get('current_page', 'dashboard')
        
        # Dashboard
        if st.button("Dashboard", 
                   use_container_width=True, 
                   type="primary" if current_page == "dashboard" else "secondary",
                   key="nav_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
            
        # Quiz
        if st.button("Quiz", 
                   use_container_width=True, 
                   type="primary" if current_page == "quiz" else "secondary",
                   key="nav_quiz"):
            st.session_state.current_page = "quiz"
            st.rerun()
            
        # Performance
        if st.button("Performance", 
                   use_container_width=True, 
                   type="primary" if current_page == "performance" else "secondary",
                   key="nav_performance"):
            st.session_state.current_page = "performance"
            st.rerun()
            
        # Planner
        is_premium = is_current_user_premium()
        planner_label = "Planner" if is_premium else "Planner"
        if st.button(planner_label, 
                   use_container_width=True, 
                   type="primary" if current_page == "planner" else "secondary",
                   key="nav_planner"):
            st.session_state.current_page = "planner"
            st.rerun()
            
        # Subscription
        if st.button("Subscription", 
                   use_container_width=True, 
                   type="primary" if current_page == "subscription" else "secondary",
                   key="nav_subscription"):
            st.session_state.current_page = "subscription"
            st.rerun()
        
        st.write("---")
        
        # Logout
        if st.button("Logout", 
                   use_container_width=True, 
                   type="secondary",
                   key="nav_logout"):
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
    
    # Apply custom CSS after authentication with force reload
    st.markdown(HOME_CUSTOM_CSS, unsafe_allow_html=True)
    
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
    elif current_page == 'quiz_history':
        try:
            # Let the quiz history UI handle subscription check and content display
            quiz_history_dashboard()
        except Exception as e:
            st.error(f"❌ Quiz history error: {str(e)}")
            st.info("💡 There was an error loading the quiz history. Please check the database connection.")
    
    elif current_page == 'planner':
        # Let the planner UI handle subscription check and content display
        run_planner_ui()
                    
    elif current_page == 'subscription':
        try:
            subscription_page()
        except Exception as e:
            st.error(f"❌ Subscription page error: {str(e)}")
            st.info("💡 There was an error loading the subscription page.")

# Make main function available for import
__all__ = ['main']

if __name__ == "__main__":
    main()