"""
Upgrade Popup Component for Adaptive Exam Preparation AI
Reusable component for feature gates and premium upgrade messaging
"""

import streamlit as st
from typing import Optional, List, Dict

def show_upgrade_popup(
    feature_name: str,
    description: str,
    premium_features: List[str],
    current_limit: Optional[str] = None,
    premium_limit: Optional[str] = None,
    show_popup: bool = True
) -> None:
    """
    Display upgrade popup for premium features
    
    Args:
        feature_name: Name of the feature being restricted
        description: Description of what the feature does
        premium_features: List of premium benefits
        current_limit: Current limitation for free users
        premium_limit: What premium users get
        show_popup: Whether to show as popup or inline message
    """
    
    if show_popup:
        # Create modal-like container
        with st.container():
            st.markdown("""
                <style>
                .upgrade-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    border-radius: 15px;
                    color: white;
                    text-align: center;
                    margin: 1rem 0;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                }
                .upgrade-title {
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 1rem;
                }
                .upgrade-description {
                    font-size: 1.1rem;
                    margin-bottom: 1.5rem;
                    opacity: 0.9;
                }
                .feature-list {
                    text-align: left;
                    background: rgba(255,255,255,0.1);
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                }
                .premium-badge {
                    background: #FFD700;
                    color: #333;
                    padding: 0.3rem 0.8rem;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="upgrade-container">
                    <div class="upgrade-title">
                        🚀 Unlock {feature_name} with Premium
                    </div>
                    <div class="upgrade-description">
                        {description}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Feature comparison section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🆓 Free Plan")
        if current_limit:
            st.info(f"**Current Limit:** {current_limit}")
        
        st.markdown("**What you get:**")
        free_features = [
            "✅ Basic quiz generation",
            "✅ Performance tracking",
            "✅ Study progress monitoring",
            "✅ Quiz history (last 10)"
        ]
        
        for feature in free_features:
            st.markdown(f"- {feature}")
    
    with col2:
        st.markdown("### ⭐ Premium Plan")
        if premium_limit:
            st.success(f"**Premium Benefit:** {premium_limit}")
        
        st.markdown("**Everything in Free, plus:**")
        for feature in premium_features:
            st.markdown(f"- ✨ {feature}")
    
    # Upgrade button section
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Upgrade to Premium", type="primary", use_container_width=True):
            show_upgrade_flow()

def show_feature_gate(
    feature_name: str,
    icon: str = "🔒",
    message: Optional[str] = None
) -> None:
    """
    Show a simple feature gate message
    
    Args:
        feature_name: Name of the locked feature
        icon: Icon to display
        message: Custom message (optional)
    """
    
    if message is None:
        message = f"This feature requires a Premium subscription."
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
            border-left: 4px solid #ff6b6b;
        '>
            <h3>{icon} {feature_name} - Premium Feature</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Unlock {feature_name}", type="primary"):
        show_upgrade_flow()

def show_usage_limit_warning(
    feature_name: str,
    current_usage: int,
    limit: int,
    reset_info: str = "daily"
) -> None:
    """
    Show usage limit warning when approaching or at limit
    
    Args:
        feature_name: Name of the feature with limits
        current_usage: Current usage count
        limit: Maximum allowed usage
        reset_info: When the limit resets (e.g., "daily", "monthly")
    """
    
    percentage = (current_usage / limit) * 100
    
    if percentage >= 100:
        st.error(f"🚫 **{feature_name} Limit Reached**")
        st.markdown(f"You've used {current_usage}/{limit} {feature_name.lower()} for this {reset_info} period.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"💡 **Tip:** Premium users get unlimited {feature_name.lower()}!")
        with col2:
            if st.button("Upgrade Now"):
                show_upgrade_flow()
                
    elif percentage >= 80:
        st.warning(f"⚠️ **{feature_name} Limit Warning**")
        st.markdown(f"You've used {current_usage}/{limit} {feature_name.lower()} ({percentage:.0f}% of your {reset_info} limit)")
        
        if st.button("Get Unlimited Access"):
            show_upgrade_flow()

def show_upgrade_flow():
    """
    Display the upgrade flow/simulation
    This is a placeholder for actual payment integration
    """
    
    st.balloons()
    
    with st.container():
        st.markdown("### 🎉 Ready to Upgrade?")
        
        st.info("""
        **This is a demo version.** In the full version, this would connect to:
        - Stripe/PayPal for payment processing
        - Email notifications for subscription confirmations
        - Automatic account upgrades
        """)
        
        # Simulate upgrade process
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("**Choose Your Plan:**")
            
            plan_choice = st.radio(
                "Select subscription:",
                ["Monthly Premium ($9.99/month)", "Yearly Premium ($99.99/year - Save 17%!)"],
                key="upgrade_plan_choice"
            )
            
            if st.button("🔄 Simulate Upgrade", type="primary", use_container_width=True):
                # Import here to avoid circular imports
                from utils.subscription import update_current_user_subscription
                
                # Simulate successful payment
                with st.spinner("Processing upgrade..."):
                    import time
                    time.sleep(2)
                
                # Update subscription in database
                success, message = update_current_user_subscription("premium")
                
                if success:
                    st.success("🎉 **Upgrade Successful!**")
                    st.info("Your account has been upgraded to Premium. Please refresh the page to access all features!")
                    st.rerun()
                else:
                    st.error(f"Upgrade failed: {message}")

# ==============================
# Premium Feature Configurations
# ==============================

PREMIUM_FEATURES = {
    "advanced_analytics": [
        "Detailed topic-wise performance insights",
        "Learning pattern analysis",
        "Personalized improvement recommendations",
        "Export analytics to PDF/Excel",
        "Historical performance trends"
    ],
    
    "unlimited_quizzes": [
        "Unlimited quiz generation per day",
        "Custom quiz lengths (up to 100 questions)",
        "Advanced difficulty settings",
        "Specialized exam formats",
        "Save unlimited quiz templates"
    ],
    
    "ai_insights": [
        "AI-powered learning recommendations",
        "Intelligent study scheduling",
        "Weakness identification and remediation",
        "Learning style optimization",
        "Predictive performance modeling"
    ],
    
    "custom_content": [
        "Upload your own study materials",
        "Create custom question banks",
        "Import questions from PDF/Word documents",
        "Organize content by subjects and topics",
        "Share custom content with study groups"
    ]
}

# Usage limits for free users
FREE_USER_LIMITS = {
    "daily_quizzes": 5,
    "quiz_history": 10,
    "analytics_depth": "basic",
    "export_formats": ["basic_text"],
    "custom_templates": 1
}