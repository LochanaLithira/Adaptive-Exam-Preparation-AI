import streamlit as st
from datetime import date, timedelta, datetime

def select_study_dates():
    # Inline CSS to reduce vertical gaps
    st.markdown(
        """
        <style>
        div.block-container {padding-top: 1rem;}
        .compact-field p {margin-bottom: 2px; margin-top: 6px;}
        .compact-field div[data-baseweb="select"] {margin-top: -5px;}
        </style>
        """,
        unsafe_allow_html=True
    )

    free_days = []
    today = date.today()
    tomorrow = today + timedelta(days=1)

    time_slots = [
        "Morning (08:00-12:00)",
        "Afternoon (12:00-17:00)",
        "Evening (17:00-21:00)",
        "Night (21:00-00:00)"
    ]

    # Input container for exam details
    st.markdown("<h3 style='text-align:center; color:#1E90FF;'>Exam Details</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        exam_date = st.date_input(
            "Select Your Exam Date",
            value=None,
            min_value=tomorrow,  # Minimum exam date is tomorrow
            help="Pick your exam date (must be a future date)"
        )
        
    with col2:
        preferred_time = st.selectbox(
            "Select Your Preferred Study Time",
            options=time_slots,
            help="Choose your preferred time slot for studying"
        )

    if exam_date and preferred_time:
        # If exam is tomorrow, start plan from today; otherwise start from tomorrow
        if exam_date == tomorrow:
            start_date = today
        else:
            start_date = tomorrow
        
        # Calculate available days from start_date until the day before exam
        days_until_exam = (exam_date - start_date).days

        if days_until_exam > 0:
            # Generate study dates starting from start_date
            current_date = start_date
            while current_date < exam_date:
                free_days.append({
                    "date": current_date,
                    "available_time": preferred_time
                })
                current_date += timedelta(days=1)

            # Show selected study period in a card with black background
            st.markdown(
                f"""
                <div style='text-align:center; padding: 15px; background-color: #000000; 
                          border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                          border: 1px solid #333;'>
                    <p style='color: white; margin: 0; font-size: 16px;'>Your study plan will cover:</p>
                    <p style='color: white; font-weight: bold; margin: 10px 0; font-size: 18px;'>
                        {start_date.strftime('%b %d, %Y')} - {(exam_date - timedelta(days=1)).strftime('%b %d, %Y')}
                    </p>
                    <p style='color: white; margin: 0; font-size: 16px;'>Preferred study time: {preferred_time}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ Please select an exam date with enough time to create a study plan.")

    return free_days