import streamlit as st
import os
import json
import datetime
import streamlit.components.v1 as components
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
from logic_planner.resources import resources

SAVE_FILE = "completed_days.json"


def load_completed_days():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_completed_days(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def calculate_total_minutes(plan, completed_days):
    study_schedule = {"Learn": 30, "Practice": 30, "Review": 15}
    total = 0
    for day in plan:
        day_num = str(day['Day'])
        if completed_days.get(day_num, False):
            total += sum(study_schedule.values())
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
        topic = day.get("Topic", "No Topic")

        story.append(Paragraph(f"📅 Day {day_num} - {date_display}", styles["Heading2"]))
        story.append(Paragraph(f"Topic: {topic}", styles["Normal"]))

        story.append(Paragraph("Schedule:", styles["Heading3"]))
        schedule_items = [
            ListItem(Paragraph("Learn Concepts: 30 min", styles["Normal"])),
            ListItem(Paragraph("Practice: 1 hour (20 mins × 3)", styles["Normal"])),
            ListItem(Paragraph("Review: 15 min", styles["Normal"]))
        ]
        story.append(ListFlowable(schedule_items, bulletType="bullet"))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Resources:", styles["Heading3"]))
        res_items = []
        for res in resources.get(topic, []):
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
        with open(file_path, "r") as f:
            plan_json = json.load(f)

        timestamp = plan_json.get("timestamp", "Unknown Time")
        plan = plan_json.get("plan", [])
        plan_key = file_name.replace(".json", "")

        if plan_key not in st.session_state.completed_days_store:
            st.session_state.completed_days_store[plan_key] = {}

        with st.expander(f"Plan created on {timestamp}"):
            total_time_placeholder = st.empty()

            # PDF download button
            pdf_file = generate_plan_pdf(plan_json)
            st.download_button(
                label="📥 Download Plan as PDF",
                data=pdf_file,
                file_name=f"study_plan_{timestamp}.pdf",
                mime="application/pdf",
            )

            # Show cards (3 per row)
            for week_start in range(0, len(plan), 3):
                week = plan[week_start:week_start + 3]
                cols = st.columns(len(week), gap="large")

                for i, day in enumerate(week):
                    with cols[i]:
                        day_num = str(day['Day'])
                        topic = day.get("Topic", "No Topic")

                        date_str = day.get("Date")
                        if date_str:
                            date_display = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b %Y")
                        else:
                            date_display = (datetime.date.today() + datetime.timedelta(days=day["Day"])).strftime(
                                "%d %b %Y"
                            )

                        checkbox_key = f"{plan_key}_day_{day_num}"
                        saved_value = st.session_state.completed_days_store[plan_key].get(day_num, False)
                        completed = st.checkbox("Mark Done", key=checkbox_key, value=saved_value)

                        if completed != saved_value:
                            st.session_state.completed_days_store[plan_key][day_num] = completed
                            save_completed_days(st.session_state.completed_days_store)

                        bg_color = "#1e1e1e" if not completed else "#0a3d0a"
                        border_color = "#ccc" if not completed else "#4caf50"

                        html_content = f"""
                        <div style='padding: 15px; border-radius: 12px; background-color:{bg_color};
                                    border: 2px solid {border_color}; min-height: 380px; color:white;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); position:relative;'>

                            <h3 style='text-align:center;'>📅 Day {day_num} - {date_display}</h3>
                            <h4 style='color:#ffd700; text-align:center;'>Topic: {topic}</h4>
                            <b>Schedule:</b>
                            <ul>
                                <li>Learn Concepts: 30 min</li>
                                <li>Practice: 1 hour (20 mins × 3)</li>
                                <li>Review: 15 min</li>
                            </ul>
                            <b>Resources:</b>
                            <ul>
                        """

                        topic_resources = resources.get(topic, [])
                        if topic_resources:
                            for res in topic_resources:
                                html_content += f"<li><a href='{res['url']}' target='_blank' style='color:lightblue;'>{res['title']}</a> ({res['type'].capitalize()})</li>"
                        else:
                            html_content += "<li>No resources available</li>"

                        html_content += "</ul></div>"

                        components.html(html_content, height=420, scrolling=True)

            total_minutes = calculate_total_minutes(plan, st.session_state.completed_days_store[plan_key])
            hours, minutes = divmod(total_minutes, 60)
            total_time_placeholder.markdown(
                f"<div style='padding:8px; border-radius:8px; background-color:#000; color:#fff; "
                f"text-align:right; font-weight:bold;'>⏱️ Total Study Time: {hours}h {minutes}m</div>",
                unsafe_allow_html=True
            )
