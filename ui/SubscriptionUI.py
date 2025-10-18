"""
Dedicated Subscription Upgrade Page
Allows users to view and purchase premium subscriptions
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from utils.subscription import get_current_user_subscription, update_current_user_subscription, SubscriptionManager
from ui.icons import icon_text, get_svg_icon

# CSS Constants for styling
GLASS_CARD_STYLE = "background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); transition: all 0.3s ease; margin-bottom: 1rem;"

# Premium Features List
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
        "Custom quiz lengths (up to 50 questions)",
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
    ]
}

# Free tier limitations
FREE_TIER_LIMITS = {
    "quiz_questions": 10,
    "quiz_history": 10,
    "analytics": "Basic",
    "exports": "None"
}

# Premium tier benefits
PREMIUM_TIER_BENEFITS = {
    "quiz_questions": 20,
    "quiz_history": "Unlimited",
    "analytics": "Advanced",
    "exports": "PDF, Excel, CSV"
}

# Pricing options
PRICING_OPTIONS = {
    "monthly": {
        "name": "Monthly Premium",
        "price": "500LKR",
        "period": "per month",
        "savings": "",
        "popular": False
    },
    "yearly": {
        "name": "Yearly Premium",
        "price": "$99.99",
        "period": "per year",
        "savings": "Save 17%",
        "popular": True
    }
}

@login_required
def subscription_page():
    
    # Get user data and subscription info
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id') or user_data.get('id')
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Get current subscription status
    subscription = get_current_user_subscription()
    is_premium = subscription.get('is_premium', False)
    subscription_date = subscription.get('subscription_changed_date')
    
    # If already premium, show current status
    # Current Subscription Status
    if is_premium:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
        ">
            <h2 style="color: white; margin-bottom: 0.5rem;"> Premium Subscription</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-bottom: 0.5rem;">
                You're currently enjoying all premium features!
            </p>
            <p style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">
                Subscription activated: {subscription_date.strftime('%B %d, %Y') if subscription_date else 'Unknown date'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} text-align: center;">
            <h2 style="color: #e2e8f0; margin-bottom: 0.5rem;"> Free Subscription</h2>
            <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-bottom: 0.5rem;">
                You're currently using the free version
            </p>
            <p style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">
                Upgrade to premium to unlock all features!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature comparison
    st.markdown("##  Premium vs Free Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} height: 460px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #e2e8f0;"> Free Plan</h3>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                        Current Plan
                    </p>
                </div>
                <ul style="color: rgba(255,255,255,0.8);">
                    <li>Up to {FREE_TIER_LIMITS['quiz_questions']} questions per quiz</li>
                    <li>{FREE_TIER_LIMITS['analytics']} performance analytics</li>
                </ul>
            </div>
            <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1rem; text-align: center; margin-top: 1rem;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #e2e8f0;">0 LKR</div>
                <div style="color: rgba(255,255,255,0.6);">Free Forever</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="{GLASS_CARD_STYLE} border: 1px solid #667eea; height: 460px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="text-align: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #e2e8f0;"> Premium Plan</h3>
                    <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
                        Unlock All Features
                    </p>
                </div>
                <ul style="color: rgba(255,255,255,0.8);">
                    <li>Up to {PREMIUM_TIER_BENEFITS['quiz_questions']} questions per quiz</li>
                    <li>Access to the planner feature</li>
                    <li>AI-generated explanations for all quiz questions and answers</li>
                    <li>Complete quiz history with questions, correct answers, and your responses</li>
                </ul>
            </div>
            <div style="background: rgba(102, 126, 234, 0.2); border-radius: 8px; padding: 1rem; text-align: center; margin-top: 1rem;">
                <div style="font-size: 1.2rem; font-weight: bold; color: #e2e8f0;">Starting at</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #e2e8f0;">500 LKR<span style="font-size: 1rem; font-weight: normal;"> / month</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Subscription management buttons
    
    # Subscription management buttons
    st.markdown("---")
    st.markdown("##  Change Subscription")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not is_premium:
            # Button to upgrade to premium
            if st.button(" Activate Premium", type="primary", use_container_width=True):
                manager = SubscriptionManager()
                success, message = manager.update_subscription(user_id, "premium")
                if success:
                    st.success(" Upgraded to Premium subscription successfully!")
                    st.session_state.user_data["subscription_type"] = "premium"
                    # Force refresh
                    st.rerun()
                else:
                    st.error(f"❌ Failed to upgrade: {message}")
        else:
            st.info("You're already on the Premium plan!")
    
    with col2:
        if is_premium:
            # Button to downgrade to free
            if st.button(" Switch to Free", use_container_width=True):
                manager = SubscriptionManager()
                success, message = manager.update_subscription(user_id, "free")
                if success:
                    st.success(" Switched to Free subscription.")
                    st.session_state.user_data["subscription_type"] = "free"
                    # Force refresh
                    st.rerun()
                else:
                    st.error(f"❌ Failed to downgrade: {message}")
        else:
            st.info("You're currently on the Free plan.")

    # Support section
    st.markdown("---")
    st.markdown("##  Need Help?")
    st.markdown(f"""
    <div style="{GLASS_CARD_STYLE}">
        <p style="color: rgba(255,255,255,0.8);">
            If you have any questions about your subscription or need assistance, please don't hesitate to contact our support team.
        </p>
        <p style="color: rgba(255,255,255,0.8);">
            Email: <a href="mailto:support@adaptiveexamprep.ai" style="color: #667eea;">support@adaptiveexamprep.ai</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: rgba(255,255,255,0.6);">
        Adaptive Exam Preparation AI - Premium Features
    </div>
    """, unsafe_allow_html=True)

# Main function for direct run
if __name__ == "__main__":
    st.set_page_config(
        page_title="Subscription Management - Adaptive Exam Prep AI",
        page_icon="💎",
        layout="wide"
    )
    init_session_state()
    subscription_page()