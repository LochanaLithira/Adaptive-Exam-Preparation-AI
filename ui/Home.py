import streamlit as st
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import init_session_state, check_authentication, login_required
from ui.LoginUI import main as login_main
from ui.icons import get_svg_icon, icon_text, info_message
from ui.PerformanceUI import performance_dashboard, PerformanceAnalytics

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
    
    # Get user performance metrics
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('id') or user_data.get('_id') if user_data else None
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if user_id:
                # Try to get actual performance data
                try:
                    analytics = PerformanceAnalytics(user_id)
                    metrics = analytics.calculate_performance_metrics()
                    
                    if metrics['total_quizzes'] > 0:
                        info_message(f"Great job! You've completed {metrics['total_quizzes']} quizzes")
                        info_message(f"Your average score is {metrics['average_score']:.1f}%")
                        info_message("Keep up the excellent work! 🌟")
                    else:
                        info_message("Welcome to your personalized learning dashboard!")
                        info_message("Start by taking your first quiz to begin tracking progress")
                        info_message("Your performance analytics will appear here after completing quizzes")
                except Exception as e:
                    info_message("Welcome to your personalized learning dashboard!")
                    info_message("Start by taking your first quiz to begin tracking progress")
                    info_message("Your performance analytics will appear here after completing quizzes")
            else:
                info_message("Welcome to your personalized learning dashboard!")
                info_message("Start by taking your first quiz to begin tracking progress")
                info_message("Your performance analytics will appear here after completing quizzes")
        
        with col2:
            if user_id:
                try:
                    analytics = PerformanceAnalytics(user_id)
                    metrics = analytics.calculate_performance_metrics()
                    
                    st.metric("Quizzes Completed", metrics['total_quizzes'], 
                             f"+{metrics['total_quizzes']}" if metrics['total_quizzes'] > 0 else "0")
                    st.metric("Average Score", f"{metrics['average_score']:.1f}%" if metrics['average_score'] > 0 else "N/A", 
                             f"{metrics['accuracy_percentage']:.1f}%" if metrics['accuracy_percentage'] > 0 else "0%")
                    st.metric("Study Streak", f"{metrics['study_streak']} days", 
                             f"+{metrics['study_streak']}" if metrics['study_streak'] > 0 else "0")
                except Exception:
                    st.metric("Quizzes Completed", "0", "0")
                    st.metric("Average Score", "N/A", "0%")
                    st.metric("Study Streak", "0", "0")
            else:
                st.metric("Quizzes Completed", "0", "0")
                st.metric("Average Score", "N/A", "0%")
                st.metric("Study Streak", "0", "0")
    
    # Quick actions
    st.markdown("---")
    
    # Mini Performance Preview (only show if user has data)
    user_id = user_data.get('id') or user_data.get('_id') if user_data else None
    if user_id:
        try:
            analytics = PerformanceAnalytics(user_id)
            metrics = analytics.calculate_performance_metrics()
            
            if metrics['total_quizzes'] > 0:
                st.markdown(icon_text("trending-up", "Quick Performance Overview", 20), unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #667eea, #764ba2); 
                                border-radius: 10px; padding: 1rem; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 1.5rem;">{metrics['total_quizzes']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Total Quizzes</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #f093fb, #f5576c); 
                                border-radius: 10px; padding: 1rem; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 1.5rem;">{metrics['average_score']:.1f}%</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Avg Score</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); 
                                border-radius: 10px; padding: 1rem; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 1.5rem;">{metrics['total_questions']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Questions Answered</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #43e97b, #38f9d7); 
                                border-radius: 10px; padding: 1rem; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 1.5rem;">{metrics['study_streak']}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Day Streak</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
        except Exception:
            pass  # Don't show error, just skip the preview
    
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
        
        user_data = st.session_state.get('user_data', {})
        if user_data and 'username' in user_data:
            st.markdown(icon_text("user", user_data['username'], 16), unsafe_allow_html=True)
        else:
            st.markdown(icon_text("user", "Guest User", 16), unsafe_allow_html=True)
        
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
        st.markdown(icon_text("quiz", "Quiz Module", 24), unsafe_allow_html=True)
        st.info("Quiz module will be integrated here")
    elif current_page == 'performance':
        # Ensure user session is maintained for performance dashboard
        if 'user_data' not in st.session_state or not st.session_state.user_data:
            st.error("User session expired. Please log in again.")
            st.button("🔄 Go to Dashboard", on_click=lambda: setattr(st.session_state, 'current_page', 'dashboard'))
        else:
            # Show the full performance dashboard
            try:
                performance_dashboard()
            except Exception as e:
                st.error(f"Error loading performance dashboard: {str(e)}")
                st.info("Please try refreshing the page or logging in again.")
    elif current_page == 'planner':
        st.markdown(icon_text("planner", "Study Planner", 24), unsafe_allow_html=True)
        st.info("Planner module will be integrated here")
    elif current_page == 'settings':
        st.markdown(icon_text("settings", "Settings", 24), unsafe_allow_html=True)
        st.info("Settings page - coming soon!")

if __name__ == "__main__":
    main()