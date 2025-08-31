"""
Quiz UI Module - Interactive Quiz Interface
"""
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import get_svg_icon, icon_text, info_message
from ui.icons import get_svg_icon, icon_text, info_message

@login_required
def quiz_dashboard():
    """Main quiz interface for authenticated users"""
    st.markdown(icon_text("quiz", "Interactive Quiz Module", 24), unsafe_allow_html=True)
    
    # Check if user has session data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id')
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Quiz dashboard content
    info_message("Welcome to the Adaptive Quiz System!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(icon_text("book", "Available Quiz Topics", 20), unsafe_allow_html=True)
        st.write("• Mathematics")
        st.write("• Science")
        st.write("• History")
        st.write("• Literature")
        st.write("• Programming")
        
    with col2:
        st.markdown(icon_text("target", "Quick Stats", 20), unsafe_allow_html=True)
        st.metric("Quizzes Available", "Coming Soon", "∞")
        st.metric("Your Progress", "0%", "0")
        st.metric("Difficulty Level", "Adaptive", f"{get_svg_icon('adaptive')}")
    
    st.markdown("---")
    
    # Coming soon features
    st.markdown(icon_text("light_bulb", "Features Coming Soon", 20), unsafe_allow_html=True)
    
    features = [
        f"{get_svg_icon('target')} Adaptive difficulty based on performance",
        f"{get_svg_icon('analytics')} Real-time performance tracking", 
        f"{get_svg_icon('brain')} AI-generated questions",
        f"{get_svg_icon('progress')} Progress visualization",
        f"{get_svg_icon('trophy')} Achievement system",
        f"{get_svg_icon('adaptive')} Mobile-optimized interface"
    ]
    
    for feature in features:
        st.write(feature)
    
    # Placeholder for future quiz integration
    if st.button(f"{get_svg_icon('rocket')} Start Demo Quiz (Coming Soon)", type="primary"):
        st.balloons()
        st.markdown(icon_text("party", "Quiz system will be integrated here!", color="#22c55e"), unsafe_allow_html=True)

if __name__ == "__main__":
    init_session_state()
    quiz_dashboard()