import streamlit as st
import sys
import os
import re
import time

# Add the parent directory to the path so we can import from security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Constants
MIN_PASSWORD_LENGTH = 8
SUCCESS_DISPLAY_DURATION = 5  # seconds
DEFAULT_SESSION_HOURS = 24
EXTENDED_SESSION_HOURS = 168  # 7 days

# Optimize imports with caching
@st.cache_resource
def get_auth_manager():
    """Cache the AuthManager instance to avoid repeated imports"""
    from security.auth import AuthManager
    return AuthManager()

# Import other functions normally
from security.auth import init_session_state, check_authentication
from ui.icons import (
    get_svg_icon, icon_text,
    success_message, error_message, warning_message, info_message
)

def create_svg_button(icon_name: str, text: str, button_id: str, button_type: str = "primary", full_width: bool = True) -> str:
    """
    Create a clickable HTML button with SVG icon.
    
    Args:
        icon_name: Name of the SVG icon
        text: Button text
        button_id: Unique ID for the button
        button_type: "primary" or "secondary"
        full_width: Whether button should be full width
    
    Returns:
        HTML string for the button
    """
    # Get the SVG icon
    svg = get_svg_icon(icon_name, 18, "white")
    
    # Define button colors based on type
    if button_type == "primary":
        bg_color = "linear-gradient(135deg, #3182ce 0%, #2c5282 100%)"
        hover_bg = "linear-gradient(135deg, #2c5282 0%, #2a4365 100%)"
        hover_shadow = "0 8px 25px rgba(49, 130, 206, 0.4)"
    else:
        bg_color = "linear-gradient(135deg, #4a5568 0%, #2d3748 100%)"
        hover_bg = "linear-gradient(135deg, #2d3748 0%, #1a202c 100%)"
        hover_shadow = "0 8px 25px rgba(74, 85, 104, 0.4)"
    
    width_style = "width: 100%;" if full_width else ""
    
    return f"""
    <button id="{button_id}" onclick="window.parent.postMessage({{type: 'streamlit:buttonClick', buttonId: '{button_id}'}}, '*')" 
    style="
        background: {bg_color};
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: all 0.3s ease;
        {width_style}
    "
    onmouseover="this.style.background='{hover_bg}'; this.style.transform='translateY(-2px)'; this.style.boxShadow='{hover_shadow}'"
    onmouseout="this.style.background='{bg_color}'; this.style.transform='translateY(0px)'; this.style.boxShadow='none'"
    >
        {svg} {text}
    </button>
    """

def create_form_svg_button(icon_name: str, text: str, button_type: str = "submit") -> str:
    """
    Create a form submit button with SVG icon.
    
    Args:
        icon_name: Name of the SVG icon
        text: Button text
        button_type: Type of button (default: "submit")
    
    Returns:
        HTML string for the form button
    """
    svg = get_svg_icon(icon_name, 18, "white")
    
    return f"""
    <button type="{button_type}" style="
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: all 0.3s ease;
        width: 100%;
    "
    onmouseover="this.style.background='linear-gradient(135deg, #38a169 0%, #2f855a 100%)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(72, 187, 120, 0.4)'"
    onmouseout="this.style.background='linear-gradient(135deg, #48bb78 0%, #38a169 100%)'; this.style.transform='translateY(0px)'; this.style.boxShadow='none'"
    >
        {svg} {text}
    </button>
    """

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength against security requirements."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def show_professional_header():
    """Display professional header with SVG icon."""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem; background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); padding: 2rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
        <h1 style="color: #e2e8f0; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 15px;">
            {get_svg_icon('graduation', 32, '#3182ce')} Adaptive Exam Prep AI
        </h1>
        <p style="color: #a0aec0; font-size: 18px; margin: 0; font-style: italic;">
            Intelligent Learning. Personalized Growth. Academic Excellence.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_login_form():
    """Display the login form with SVG icons"""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 2rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        """, unsafe_allow_html=True)

        # Section header with SVG icon
        st.markdown(f"""
        <h3 style="color: #e2e8f0; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            {get_svg_icon('lock', 24, '#3182ce')} Welcome Back
        </h3>
        <p style="color: #a0aec0; margin-bottom: 1.5rem;">Sign in to continue your learning journey</p>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            # Credentials section with SVG icon
            st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('user', 18, '#3182ce')} Account Credentials
                </p>
            </div>
            """, unsafe_allow_html=True)
            
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

            # Advanced options with simple text
            with st.expander("Advanced Options"):
                remember_me = st.checkbox(
                    "Keep me signed in for 7 days",
                    help="Your session will remain active for 7 days instead of 24 hours"
                )

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Login button with simple text
            submit_button = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True
            )

        if submit_button:
            if username and password:
                auth_manager = get_auth_manager()
                user_data = auth_manager.authenticate_user(username, password)

                if user_data:
                    # Create session (longer if remember me is checked)
                    expiry_hours = EXTENDED_SESSION_HOURS if remember_me else DEFAULT_SESSION_HOURS
                    session_token = auth_manager.create_session(user_data['_id'], expiry_hours)

                    if session_token:
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_data
                        st.session_state.session_token = session_token
                        success_message("Login successful! Redirecting to dashboard...")
                        st.rerun()
                    else:
                        warning_message("Failed to create session. Please try again.")
                else:
                    error_message("Invalid credentials. Please check your username/email and password.")
            else:
                warning_message("Please fill in all required fields.")

        st.markdown("</div>", unsafe_allow_html=True)

def show_registration_form():
    """Display the registration form with SVG icons"""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 2rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        """, unsafe_allow_html=True)

        # Section header with SVG icon
        st.markdown(f"""
        <h3 style="color: #e2e8f0; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            {get_svg_icon('edit', 24, '#3182ce')} Join Our Learning Community
        </h3>
        <p style="color: #a0aec0; margin-bottom: 1.5rem;">Create your account to access personalized exam preparation</p>
        """, unsafe_allow_html=True)

        with st.form("registration_form"):
            # Personal Information Section with SVG icon
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('user', 18, '#3182ce')} Personal Information
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_left, col_right = st.columns(2)

            with col_left:
                full_name = st.text_input(
                    "Full Name *",
                    placeholder="John Doe"
                )
                username = st.text_input(
                    "Username *",
                    placeholder="johndoe123"
                )

            with col_right:
                email = st.text_input(
                    "Email Address *",
                    placeholder="john.doe@email.com"
                )

                # Show real-time email validation
                if email and not validate_email(email):
                    warning_message("Please enter a valid email format")

            # Security Section with SVG icon
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('shield', 18, '#3182ce')} Account Security
                </p>
            </div>
            """, unsafe_allow_html=True)

            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Create a strong password"
            )

            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter your password"
            )

            # Real-time password strength indicator
            if password:
                is_valid, message = validate_password(password)
                if not is_valid:
                    warning_message(message)

                # Password match indicator
                if confirm_password:
                    if password != confirm_password:
                        error_message("Passwords do not match")

            # Agreement Section with SVG icon
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="color: #e2e8f0; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('clipboard', 18, '#3182ce')} Terms & Privacy
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            terms_accepted = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy *"
            )

            # Registration button with simple text
            submit_button = st.form_submit_button(
                "Create My Account",
                type="primary",
                use_container_width=True
            )

            if submit_button:
                if all([full_name, username, email, password, confirm_password]):
                    if not validate_email(email):
                        error_message("Please enter a valid email address.")
                    elif password != confirm_password:
                        error_message("Passwords do not match.")
                    elif not validate_password(password)[0]:
                        error_message(validate_password(password)[1])
                    elif not terms_accepted:
                        error_message("Please accept the Terms of Service and Privacy Policy.")
                    else:
                        auth_manager = get_auth_manager()
                        success, message = auth_manager.create_user(username, email, password, full_name)
                        if success:
                            # Show balloons celebration and set success state
                            st.balloons()

                            # Set flag to show success state with timestamp
                            st.session_state.account_created = True
                            st.session_state.success_timestamp = time.time()
                            st.rerun()
                        else:
                            error_message(message)
                else:
                    warning_message("Please fill in all required fields (marked with *).")

        st.markdown("</div>", unsafe_allow_html=True)

        # Show success message if account was just created
        if st.session_state.get('account_created', False):
            current_time = time.time()
            success_time = st.session_state.get('success_timestamp', current_time)
            elapsed_time = current_time - success_time

            # Professional success message with SVG icon
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                margin: 1rem 0;
                box-shadow: 0 8px 32px rgba(72, 187, 120, 0.3);
                border: 1px solid rgba(255,255,255,0.2);
                animation: slideIn 0.5s ease-out;
            ">
                <h4 style="color: white; margin: 0; font-size: 1.2rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    {get_svg_icon('check_circle', 24, 'white')} Account Created Successfully!
                </h4>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0; font-size: 1rem;">
                    Welcome to Adaptive Exam Prep AI! Your learning journey begins now.
                </p>
            </div>
            <style>
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            </style>
            """, unsafe_allow_html=True)

            # Show countdown and auto-navigate after defined duration
            remaining_time = max(0, SUCCESS_DISPLAY_DURATION - int(elapsed_time))

            if remaining_time > 0:
                info_message(f"Redirecting to Sign In in {remaining_time} seconds...")
                # Auto-refresh every second to update countdown
                time.sleep(1)
                st.rerun()
            else:
                # Time's up, navigate to login
                st.session_state.account_created = False
                st.session_state.active_form = "login"
                st.session_state.scroll_to_top = True
                st.rerun()

        # Professional footer with SVG icons
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <p style="color: #a0aec0; font-size: 14px; display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('lock', 16, '#a0aec0')} <strong>256-bit Encryption</strong>
            </p>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <p style="color: #a0aec0; font-size: 14px; display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('shield', 16, '#a0aec0')} <strong>Privacy Protected</strong>
            </p>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""
            <p style="color: #a0aec0; font-size: 14px; display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('adaptive', 16, '#a0aec0')} <strong>Mobile Optimized</strong>
            </p>
            """, unsafe_allow_html=True)

def show_user_profile():
    """Display professional user profile information with SVG icons"""
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

        # Welcome message with SVG icon
        st.markdown(f"""
        <h3 style="color: #e2e8f0; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 10px;">
            {get_svg_icon('wave', 24, '#48bb78')} Welcome back, {user_data["full_name"]}!
        </h3>
        <p style="color: #a0aec0; margin-bottom: 1.5rem;">
            <strong>@{user_data["username"]}</strong> | {user_data["email"]}
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Action buttons with simple text
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Go to Dashboard", type="primary", use_container_width=True):
                # Navigate to main app (this should be handled by app.py)
                st.switch_page("app.py")

        with col_b:
            if st.button("Sign Out", type="secondary", use_container_width=True):
                logout_user()

        st.markdown("<br>", unsafe_allow_html=True)

        # User stats with SVG icons
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.markdown(f"""
            <div style="background: rgba(45, 55, 72, 0.6); border-radius: 10px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 0.5rem;">
                    {get_svg_icon('quiz', 20, '#3182ce')} <span style="color: #e2e8f0; font-weight: 600;">Quizzes</span>
                </div>
                <div style="color: #48bb78; font-size: 24px; font-weight: bold;">0</div>
                <div style="color: #a0aec0; font-size: 12px;">Total completed</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_y:
            st.markdown(f"""
            <div style="background: rgba(45, 55, 72, 0.6); border-radius: 10px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 0.5rem;">
                    {get_svg_icon('target', 20, '#3182ce')} <span style="color: #e2e8f0; font-weight: 600;">Score</span>
                </div>
                <div style="color: #48bb78; font-size: 24px; font-weight: bold;">N/A</div>
                <div style="color: #a0aec0; font-size: 12px;">Average score</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_z:
            st.markdown(f"""
            <div style="background: rgba(45, 55, 72, 0.6); border-radius: 10px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 0.5rem;">
                    {get_svg_icon('clock', 20, '#3182ce')} <span style="color: #e2e8f0; font-weight: 600;">Study Time</span>
                </div>
                <div style="color: #48bb78; font-size: 24px; font-weight: bold;">0 hrs</div>
                <div style="color: #a0aec0; font-size: 12px;">Total logged</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

def logout_user():
    """Log out the current user"""
    if st.session_state.get('session_token'):
        auth_manager = get_auth_manager()
        auth_manager.logout_user(st.session_state.session_token)

    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.session_token = None
    st.session_state.active_form = "login"
    success_message("Logged out successfully!")
    st.rerun()

def main():
    """Main login/registration interface with professional design and SVG icons"""
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
        display: flex;
        align-items: center;
        gap: 8px;
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
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(49, 130, 206, 0.4);
        background: linear-gradient(135deg, #2c5282 0%, #2a4365 100%);
    }

    /* Form submit button specific styling */
    .stForm > div > div > button[type="submit"] {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        border: none;
        color: white;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .stForm > div > div > button[type="submit"]:hover {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d3748;
        color: #e2e8f0;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .streamlit-expanderContent {
        background-color: #1a202c;
        border-radius: 0 0 10px 10px;
    }

    /* Dark background */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%);
    }

    /* Success/Error message styling */
    .stAlert > div {
        border-radius: 10px;
        backdrop-filter: blur(10px);
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

    # Add scroll anchor for navigation
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

    # Handle scroll to top if needed
    if st.session_state.get('scroll_to_top', False):
        st.session_state.scroll_to_top = False
        st.markdown("""
        <script>
        setTimeout(function() {
            const methods = [
                () => window.parent.document.querySelector('h1').scrollIntoView({behavior: 'smooth', block: 'start'}),
                () => window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({top: 0, behavior: 'smooth'}),
                () => window.parent.scrollTo({top: 0, behavior: 'smooth'}),
                () => window.parent.document.body.scrollTop = 0
            ];

            for (let method of methods) {
                try {
                    method();
                    break;
                } catch (e) {
                    continue;
                }
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)

    # Initialize page state for form control
    if 'active_form' not in st.session_state:
        st.session_state.active_form = "login"

    # Main content container
    st.markdown("""
    <div style="max-width: 800px; margin: 0 auto; padding: 0 1rem;">
    """, unsafe_allow_html=True)

    # Navigation buttons with simple text
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        login_style = "primary" if st.session_state.active_form == "login" else "secondary"
        if st.button("Sign In", type=login_style, use_container_width=True):
            st.session_state.active_form = "login"
            st.rerun()

    with col2:
        register_style = "primary" if st.session_state.active_form == "register" else "secondary"
        if st.button("Create Account", type=register_style, use_container_width=True):
            st.session_state.active_form = "register"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Show the appropriate form based on session state
    if st.session_state.active_form == "login":
        show_login_form()
    else:
        show_registration_form()

    st.markdown("</div>", unsafe_allow_html=True)

    # Features showcase with professional cards and SVG icons
    st.markdown(f"""
    <div style="max-width: 1200px; margin: 3rem auto 0; padding: 0 1rem;">
        <h3 style="text-align: center; margin-bottom: 2rem; color: #e2e8f0; display: flex; align-items: center; justify-content: center; gap: 10px;">
            {get_svg_icon('star', 24, '#ffd700')} Why Choose Adaptive Exam Prep AI?
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                {get_svg_icon('target', 20, '#3182ce')} Adaptive Learning
            </h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.8; list-style: none; padding: 0;">
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Personalized quiz difficulty
                </li>
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Smart content recommendations
                </li>
                <li style="display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Real-time progress tracking
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                {get_svg_icon('analytics', 20, '#3182ce')} Analytics Dashboard
            </h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.8; list-style: none; padding: 0;">
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Detailed performance reports
                </li>
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Weakness identification
                </li>
                <li style="display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Study time optimization
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: #3182ce; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                {get_svg_icon('planner', 20, '#3182ce')} Smart Planning
            </h4>
            <ul style="text-align: left; color: #a0aec0; line-height: 1.8; list-style: none; padding: 0;">
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Customized study schedules
                </li>
                <li style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Goal setting and tracking
                </li>
                <li style="display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon('arrow_right', 14, '#48bb78')} Intelligent reminders
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Professional footer with SVG icons
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="max-width: 800px; margin: 2rem auto 0; padding: 1rem; text-align: center; background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        <p style="color: #a0aec0; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 15px;">
            <span style="display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('lock', 16, '#48bb78')} <strong>Enterprise-grade security</strong>
            </span>
            <span style="display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('clock', 16, '#48bb78')} <strong>24/7 availability</strong>
            </span>
            <span style="display: flex; align-items: center; gap: 5px;">
                {get_svg_icon('adaptive', 16, '#48bb78')} <strong>Mobile optimized</strong>
            </span>
        </p>
        <p style="color: #718096; font-size: 14px; margin: 0; display: flex; align-items: center; justify-content: center; gap: 5px;">
            {get_svg_icon('shield', 14, '#718096')} Your privacy is protected with 256-bit encryption. We never share your personal information.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
