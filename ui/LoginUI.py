import streamlit as st
import sys
import os
import re

# Add the parent directory to the path so we can import from security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import AuthManager, init_session_state, check_authentication

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

import streamlit as st
import sys
import os
import re

# Add the parent directory to the path so we can import from security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import AuthManager, init_session_state, check_authentication

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def show_professional_header():
    """Display professional header for authentication pages"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 20px 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <h1 style="color: white; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 300; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            🎓 Adaptive Exam Prep AI
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0;">
            Intelligent Learning. Personalized Growth. Academic Excellence.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_login_form():
    """Display the professional login form"""
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">🔐 Welcome Back</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #a0aec0; margin-bottom: 1.5rem;">Sign in to continue your learning journey</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            # Professional input styling
            st.markdown('<p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem;">**Account Credentials**</p>', unsafe_allow_html=True)
            username = st.text_input(
                "Username or Email", 
                placeholder="Enter your username or email address",
                help="You can use either your username or email to log in"
            )
            
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                help="Enter the password you created during registration"
            )
            
            # Advanced options in expander
            with st.expander("⚙️ Advanced Options"):
                remember_me = st.checkbox(
                    "Keep me signed in for 7 days", 
                    help="Your session will remain active for 7 days instead of 24 hours"
                )
            
            st.markdown("</br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button(
                "🚀 Sign In", 
                type="primary", 
                use_container_width=True
            )
            
            if submit_button:
                if username and password:
                    with st.spinner("🔄 Authenticating..."):
                        auth_manager = AuthManager()
                        user_data = auth_manager.authenticate_user(username, password)
                        
                        if user_data:
                            # Create session (longer if remember me is checked)
                            expiry_hours = 168 if remember_me else 24  # 7 days vs 1 day
                            session_token = auth_manager.create_session(user_data['id'], expiry_hours)
                            
                            if session_token:
                                st.session_state.authenticated = True
                                st.session_state.user_data = user_data
                                st.session_state.session_token = session_token
                                st.success(f"🎉 Welcome back, {user_data['full_name']}!")
                                st.rerun()
                            else:
                                st.error("⚠️ Failed to create session. Please try again.")
                        else:
                            st.error("❌ Invalid credentials. Please check your username/email and password.")
                else:
                    st.error("⚠️ Please fill in all required fields.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Professional footer with helpful links
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">🔒 **Secure Login**</p>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">📧 [Forgot Password?](mailto:support@adaptiveexam.ai)</p>', unsafe_allow_html=True)
        with col_c:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">❓ [Need Help?](mailto:support@adaptiveexam.ai)</p>', unsafe_allow_html=True)

def show_registration_form():
    """Display the professional registration form"""
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">📝 Join Our Learning Community</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #a0aec0; margin-bottom: 1.5rem;">Create your account to access personalized exam preparation</p>', unsafe_allow_html=True)
        
        with st.form("registration_form"):
            # Personal Information Section
            st.markdown('<p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem;">**👤 Personal Information**</p>', unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            
            with col_left:
                full_name = st.text_input(
                    "Full Name *", 
                    placeholder="John Doe",
                    help="Enter your full name as it should appear on certificates"
                )
                username = st.text_input(
                    "Username *", 
                    placeholder="johndoe123",
                    help="Choose a unique username (3-20 characters, letters, numbers, and underscores only)"
                )
            
            with col_right:
                email = st.text_input(
                    "Email Address *", 
                    placeholder="john.doe@email.com",
                    help="We'll use this email for important account notifications"
                )
                
                # Show real-time email validation
                if email and not validate_email(email):
                    st.error("⚠️ Please enter a valid email format")
                elif email and validate_email(email):
                    st.success("✅ Valid email format")
            
            # Security Section
            st.markdown('</br><p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem;">**🔐 Account Security**</p>', unsafe_allow_html=True)
            
            password = st.text_input(
                "Password *", 
                type="password", 
                placeholder="Create a strong password",
                help="Minimum 8 characters with uppercase, lowercase, and numbers"
            )
            
            confirm_password = st.text_input(
                "Confirm Password *", 
                type="password", 
                placeholder="Re-enter your password"
            )
            
            # Real-time password strength indicator
            if password:
                is_valid, message = validate_password(password)
                if is_valid:
                    st.success("✅ Strong password")
                else:
                    st.warning(f"⚠️ {message}")
                    
                # Password match indicator
                if confirm_password:
                    if password == confirm_password:
                        st.success("✅ Passwords match")
                    else:
                        st.error("❌ Passwords do not match")
            
            # Agreement Section
            st.markdown('</br><p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem;">**📋 Terms & Privacy**</p>', unsafe_allow_html=True)
            terms_accepted = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy *",
                help="Please read and accept our terms to create your account"
            )
            
            st.markdown("</br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button(
                "🎯 Create My Account", 
                type="primary", 
                use_container_width=True
            )
            
            if submit_button:
                if all([full_name, username, email, password, confirm_password]):
                    if not validate_email(email):
                        st.error("❌ Please enter a valid email address.")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match.")
                    elif not validate_password(password)[0]:
                        st.error(f"❌ {validate_password(password)[1]}")
                    elif not terms_accepted:
                        st.error("❌ Please accept the Terms of Service and Privacy Policy.")
                    else:
                        with st.spinner("🔄 Creating your account..."):
                            auth_manager = AuthManager()
                            success, message = auth_manager.create_user(username, email, password, full_name)
                            if success:
                                st.success(f"🎉 {message}")
                                st.info("🔄 Redirecting to login page...")
                                st.session_state.show_login = True
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                else:
                    st.error("⚠️ Please fill in all required fields (marked with *).")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Professional footer
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">🔒 **256-bit Encryption**</p>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">🛡️ **Privacy Protected**</p>', unsafe_allow_html=True)
        with col_c:
            st.markdown('<p style="color: #a0aec0; font-size: 14px;">📱 **Mobile Optimized**</p>', unsafe_allow_html=True)

def show_user_profile():
    """Display professional user profile information"""
    if not st.session_state.get('authenticated'):
        return
    
    user_data = st.session_state.user_data
    
    # Professional header
    show_professional_header()
    
    # Main profile container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255,255,255,0.1); text-align: center;">
        """, unsafe_allow_html=True)
        
        st.markdown(f'<h3 style="color: #e2e8f0; margin-bottom: 0.5rem;">👋 Welcome back, {user_data["full_name"]}!</h3>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #a0aec0; margin-bottom: 1.5rem;">**@{user_data["username"]}** | {user_data["email"]}</p>', unsafe_allow_html=True)
        
        st.markdown("</br>", unsafe_allow_html=True)
        
        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("� Go to Dashboard", type="primary", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with col_b:
            if st.button("🚪 Sign Out", type="secondary", use_container_width=True):
                logout_user()
        
        st.markdown("</br>", unsafe_allow_html=True)
        
        # User stats (placeholder)
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("📚 Quizzes Taken", "0", help="Total quizzes completed")
        with col_y:
            st.metric("🎯 Average Score", "N/A", help="Your average quiz score")
        with col_z:
            st.metric("🕒 Study Time", "0 hrs", help="Total study time logged")
        
        st.markdown("</div>", unsafe_allow_html=True)

def logout_user():
    """Log out the current user"""
    if st.session_state.get('session_token'):
        auth_manager = AuthManager()
        auth_manager.logout_user(st.session_state.session_token)
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.session_token = None
    st.session_state.current_page = "login"
    st.success("✅ Logged out successfully!")
    st.rerun()

def main():
    """Main login/registration interface with professional design"""
    st.set_page_config(
        page_title="Adaptive Exam Prep AI - Authentication",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling for forms */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #4a5568;
        background-color: #1a202c;
        color: #e2e8f0;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        background-color: #2d3748;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #e2e8f0;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(49, 130, 206, 0.4);
        background: linear-gradient(135deg, #2c5282 0%, #2a4365 100%);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {
        border-radius: 10px;
        background-color: #1a202c;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
        font-size: 16px;
        background-color: #2d3748;
        color: #a0aec0;
        border: 1px solid #4a5568;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #4a5568;
        color: #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3182ce;
        color: white;
        border-color: #3182ce;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: transparent;
    }
    
    /* Dark background */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d3748;
        color: #e2e8f0;
        border-radius: 10px;
    }
    
    .streamlit-expanderContent {
        background-color: #1a202c;
        border-radius: 0 0 10px 10px;
    }
    
    /* Form submit button specific styling */
    .stForm > div > div > button[type="submit"] {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        border: none;
        color: white;
        font-weight: 600;
    }
    
    .stForm > div > div > button[type="submit"]:hover {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
    }
    
    /* Success/Error message styling */
    .stAlert > div {
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Metric styling for user stats */
    [data-testid="metric-container"] {
        background-color: rgba(45, 55, 72, 0.6);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Check if user is already authenticated
    if check_authentication():
        show_user_profile()
        return
    
    # Professional Header
    show_professional_header()
    
    # Initialize page state
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    
    # Main content container
    st.markdown("""
    <div style="max-width: 800px; margin: 0 auto; padding: 0 1rem;">
    """, unsafe_allow_html=True)
    
    # Navigation tabs with professional styling
    st.markdown("</br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 **Sign In**", "📝 **Create Account**"])
    
    with tab1:
        st.markdown("</br>", unsafe_allow_html=True)
        show_login_form()
    
    with tab2:
        st.markdown("</br>", unsafe_allow_html=True)
        show_registration_form()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Features showcase with professional cards
    st.markdown("""
    <div style="max-width: 1200px; margin: 3rem auto 0; padding: 0 1rem;">
        <h3 style="text-align: center; margin-bottom: 2rem; color: #e2e8f0;">
            🌟 Why Choose Adaptive Exam Prep AI?
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem;">🎯 Adaptive Learning</h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.6;">
                <li>Personalized quiz difficulty</li>
                <li>Smart content recommendations</li>
                <li>Real-time progress tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem;">📊 Analytics Dashboard</h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.6;">
                <li>Detailed performance reports</li>
                <li>Weakness identification</li>
                <li>Study time optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem;">📅 Smart Planning</h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.6;">
                <li>Customized study schedules</li>
                <li>Goal setting and tracking</li>
                <li>Intelligent reminders</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional footer
    st.markdown("</br></br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="max-width: 800px; margin: 2rem auto 0; padding: 1rem; text-align: center; background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        <p style="color: #a0aec0; margin-bottom: 0.5rem;">
            🔒 <strong>Enterprise-grade security</strong> • 
            🌐 <strong>24/7 availability</strong> • 
            📱 <strong>Mobile optimized</strong>
        </p>
        <p style="color: #718096; font-size: 14px; margin: 0;">
            Your privacy is protected with 256-bit encryption. We never share your personal information.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
