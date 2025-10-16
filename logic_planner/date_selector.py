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
    current_time = datetime.now().time()

    # Define all time slots with their start times
    all_time_slots = [
        ("Morning (08:00AM)", datetime.strptime("08:00", "%H:%M").time()),
        ("Afternoon (12:00PM)", datetime.strptime("12:00", "%H:%M").time()),
        ("Evening (05:00PM)", datetime.strptime("17:00", "%H:%M").time()),
        ("Night (09:00PM)", datetime.strptime("21:00", "%H:%M").time())
    ]

    # Input container for exam details
    st.markdown("<h3 style='text-align:center; color:#1E90FF;'>Enter your Exam Date and Preferred Study Slot</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        exam_date = st.date_input(
            "Select Your Exam Date",
            value=None,
            min_value=tomorrow,  # Minimum is tomorrow (today disabled)
            help="Pick your exam date (must be a future date)",
            format="DD/MM/YYYY"
        )
    
    # Filter time slots based on selected date and current time
    if exam_date:
        if exam_date == tomorrow:
            # If exam is tomorrow, plan starts today - only show future time slots
            available_time_slots = [slot[0] for slot in all_time_slots if slot[1] > current_time]
            if not available_time_slots:
                st.warning("⚠️ No available time slots remaining for today. Please select a later exam date.")
        else:
            # For dates beyond tomorrow, show all time slots (plan starts from tomorrow)
            available_time_slots = [slot[0] for slot in all_time_slots]
    else:
        # No date selected, show all slots
        available_time_slots = [slot[0] for slot in all_time_slots]
        
    with col2:
        preferred_time = st.selectbox(
            "Select Your Preferred Study Time",
            options=[None] + available_time_slots,
            format_func=lambda x: "Choose your Time Slot..." if x is None else x,
            help="Choose your preferred time slot for studying"
        )

    # Only process if both are selected
    if exam_date and preferred_time:
        # Show loading message immediately
        with st.spinner("📅 Calculating your study Schedule..."):
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

                # Format dates in "16th October 2025" format
                def format_date_with_suffix(d):
                    day = d.day
                    if 10 <= day % 100 <= 20:
                        suffix = 'th'
                    else:
                        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                    return f"{day}{suffix} {d.strftime('%B %Y')}"

                start_formatted = format_date_with_suffix(start_date)
                end_formatted = format_date_with_suffix(exam_date - timedelta(days=1))
        
        # Show result after spinner completes
        if days_until_exam > 0:
            # Show selected study period in a card with black background
            st.markdown(
                f"""
                <div style='text-align:center; padding: 15px; background-color: #000000; 
                          border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                          border: 1px solid #333;'>
                    <p style='color: white; margin: 0; font-size: 16px;'>Your study plan will cover:</p>
                    <p style='color: white; font-weight: bold; margin: 10px 0; font-size: 18px;'>
                        {start_formatted} - {end_formatted}
                    </p>
                    <p style='color: white; margin: 0; font-size: 16px;'>Preferred study time: {preferred_time}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ Please select an exam date with enough time to create a study plan.")

    return free_days