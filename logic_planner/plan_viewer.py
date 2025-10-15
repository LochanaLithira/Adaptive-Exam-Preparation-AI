#plan_viewer.py
import streamlit as st
import os
import json 
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

SAVE_FILE = "completed_days.json"

def load_completed_days():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_completed_days(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def calculate_total_minutes(grouped_plan, completed_days):
    """Calculate total study time from grouped plan structure"""
    total = 0
    for day in grouped_plan:
        day_num = str(day['Day'])
        if completed_days.get(day_num, False):
            # Count actual schedule time (excluding breaks)
            for schedule_item in day.get("Schedule", []):
                if "Break" not in schedule_item:
                    # Extract time from schedule format
                    if "Learn" in schedule_item:
                        total += 60
                    elif "Practice" in schedule_item:
                        total += 30
                    elif "Review" in schedule_item:
                        total += 15
    return total

def generate_plan_pdf(plan_json):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("📄 Study Plan", styles["Title"]))
    story.append(Spacer(1, 12))

    plan = plan_json.get("plan", [])
    for day in plan:
        day_num = day.get("Day", "?")
        date_display = day.get("Date", "No Date")
        topics = day.get("Topics", [])

        story.append(Paragraph(f"📅 Day {day_num} - {date_display}", styles["Heading2"]))
        story.append(Paragraph(f"Topics: {', '.join(topics)}", styles["Normal"]))

        # Schedule
        story.append(Paragraph("Schedule:", styles["Heading3"]))
        day_schedule = day.get("Schedule", [])
        schedule_items = []
        if day_schedule:
            for s in day_schedule:
                schedule_items.append(ListItem(Paragraph(s, styles["Normal"])))
        else:
            schedule_items = [
                ListItem(Paragraph("Learn - 60 min", styles["Normal"])),
                ListItem(Paragraph("Break - 15 min", styles["Normal"])),
                ListItem(Paragraph("Practice - 30 min", styles["Normal"])),
                ListItem(Paragraph("Break - 15 min", styles["Normal"])),
                ListItem(Paragraph("Review - 15 min", styles["Normal"]))
            ]
        story.append(ListFlowable(schedule_items, bulletType="bullet"))
        story.append(Spacer(1, 12))

        # Resources
        story.append(Paragraph("Resources:", styles["Heading3"]))
        res_items = []
        for res in day.get("Resources", []):
            res_items.append(ListItem(Paragraph(f"{res['title']} ({res['type'].capitalize()}) - {res['url']}", styles["Normal"])))
        if res_items:
            story.append(ListFlowable(res_items, bulletType="bullet"))
        else:
            story.append(Paragraph("No resources available", styles["Normal"]))
        story.append(Spacer(1, 20))

    doc.build(story)
    buffer.seek(0)
    return buffer

def display_all_plans(base_dir):
    plans_dir = os.path.join(base_dir, "saved_plans")
    if not os.path.exists(plans_dir):
        st.info("No saved plans found.")
        return

    if "completed_days_store" not in st.session_state:
        st.session_state.completed_days_store = load_completed_days()

    files = [f for f in sorted(os.listdir(plans_dir), reverse=True) if f.endswith(".json")]

    for file_name in files:
        file_path = os.path.join(plans_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            plan_json = json.load(f)

        timestamp = plan_json.get("timestamp", "Unknown Time")
        plan = plan_json.get("plan", [])
        plan_key = file_name.replace(".json", "")

        if plan_key not in st.session_state.completed_days_store:
            st.session_state.completed_days_store[plan_key] = {}

        # --- GROUP TOPICS BY DATE (same as Planner UI) ---
        grouped_plan = {}
        for entry in plan:
            date_key = entry.get("Date", "No Date")
            day_num = entry.get("Day")
            
            if date_key not in grouped_plan:
                grouped_plan[date_key] = {
                    "Day": day_num,  # Use the original Day number
                    "Date": date_key,
                    "Topics": [],
                    "Resources": [],
                    "Schedule": []
                }
            grouped_plan[date_key]["Topics"].append(entry.get("Topic"))
            grouped_plan[date_key]["Resources"].extend(entry.get("Resources", []))
            grouped_plan[date_key]["Schedule"].extend(entry.get("Schedule", []))

        # Convert to list and sort by original Day number
        grouped_plan_list = list(grouped_plan.values())
        grouped_plan_list.sort(key=lambda x: x["Day"])

        with st.expander(f"Plan created on {timestamp}"):
            total_time_placeholder = st.empty()

            pdf_file = generate_plan_pdf({"plan": grouped_plan_list})
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_file,
                file_name=f"study_plan_{timestamp}.pdf",
                mime="application/pdf",
            )

            # Display cards per day (exactly like Planner UI)
            for day in grouped_plan_list:
                # Handle date display
                date_str = day.get("Date")
                if date_str and date_str != "No Date":
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    day_formatted = date_obj.strftime("%d").lstrip("0")
                    day_suffix = "th"
                    if day_formatted in ["1", "21", "31"]:
                        day_suffix = "st"
                    elif day_formatted in ["2", "22"]:
                        day_suffix = "nd"
                    elif day_formatted in ["3", "23"]:
                        day_suffix = "rd"
                    date_display = f"{day_formatted}{day_suffix} {date_obj.strftime('%B %Y')}"
                else:
                    date_display = "No Date Set"

                # Topics grouped as "x | y | z" (same as Planner UI)
                topics_line = " | ".join([f"<b style='color:#1a73e8;'>{t}</b>" for t in day["Topics"]])
                topics_html = f"Topics for today: {topics_line}"

                schedule_html = "".join([f"<li>{s}</li>" for s in day.get("Schedule", [])])

                if day["Resources"]:
                    resources_html = "".join([
                        f"<li>- <a href='{res['url']}' target='_blank'>{res['title']}</a> ({res['type'].capitalize()})</li>"
                        for res in day["Resources"]
                    ])
                else:
                    resources_html = "<li>- No resources available</li>"

                checkbox_key = f"{plan_key}_day_{day['Day']}"
                saved_value = st.session_state.completed_days_store[plan_key].get(str(day['Day']), False)
                completed = st.checkbox("Mark Done", key=checkbox_key, value=saved_value)
                if completed != saved_value:
                    st.session_state.completed_days_store[plan_key][str(day['Day'])] = completed
                    save_completed_days(st.session_state.completed_days_store)

                bg_color = "#000000" if not completed else "#1a4d1a"
                border_color = "#333" if not completed else "#4caf50"

                card_html = f"""
                <div style='padding: 10px; border-radius: 10px; background-color: {bg_color};
                            border: 2px solid {border_color}; margin-bottom: 10px; color: #ffffff;' >
                    <h3 style='text-align: center; color: #ffffff;'>📅 Day {day['Day']}<br>({date_display})</h3>
                    <h4 style='text-align: center;'>{topics_html}</h4>
                    <b style='color: #ffffff;'>Schedule:</b>
                    <ul style='color: #ffffff;'>
                        {schedule_html}
                    </ul>
                    <b style='color: #ffffff;'>Resources:</b>
                    <ul style='color: #ffffff;'>
                        {resources_html}
                    </ul>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            total_minutes = calculate_total_minutes(grouped_plan_list, st.session_state.completed_days_store[plan_key])
            hours, minutes = divmod(total_minutes, 60)
            total_time_placeholder.markdown(
                f"<div style='padding:8px; border-radius:8px; background-color:#000; color:#fff; "
                f"text-align:right; font-weight:bold;'>⏱️ Total Study Time: {hours}h {minutes}m</div>",
                unsafe_allow_html=True
            )