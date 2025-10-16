# logic_planner/plan_viewer.py

import streamlit as st
import os
import json
from datetime import datetime
from fpdf import FPDF
import tempfile
import re

# -------------------------------------------------
# Load all generated plans
# -------------------------------------------------
def load_all_plans(BASE_DIR):
    GENERATED_PLANS_DIR = os.path.join(BASE_DIR, "generated_plans")
    os.makedirs(GENERATED_PLANS_DIR, exist_ok=True)
    plans = []

    for filename in os.listdir(GENERATED_PLANS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(GENERATED_PLANS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    plan_data = json.load(f)
                    plans.append({
                        "file": filepath,
                        "plan": plan_data,
                        "filename": filename
                    })
                except Exception as e:
                    st.warning(f"⚠️ Failed to load plan {filename}: {str(e)}")
    return plans


# -------------------------------------------------
# Generate PDF safely (UTF-8 clean)
# -------------------------------------------------
def generate_plan_pdf(plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Your Saved Study Plan", ln=True, align="C")
    pdf.ln(5)

    grouped_plan = {}
    for entry in plan:
        day_num = entry.get("Day", 0)
        if day_num not in grouped_plan:
            grouped_plan[day_num] = {
                "Day": day_num,
                "Date": entry.get("Date", "Unknown"),
                "Topics": [],
                "Resources": [],
                "Schedule": []
            }
        grouped_plan[day_num]["Topics"].append(entry.get("Topic", ""))
        grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
        grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))

    def clean_text(t):
        return re.sub(r"[^\x00-\x7F]+", " ", str(t))  # strip emojis, etc.

    for day in grouped_plan.values():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, clean_text(f"Day {day['Day']} ({day['Date']})"), ln=True)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 8, "Topics:", ln=True)
        pdf.multi_cell(0, 8, clean_text(", ".join(day["Topics"])))

        pdf.cell(0, 8, "Schedule:", ln=True)
        if day["Schedule"]:
            for s in day["Schedule"]:
                pdf.multi_cell(0, 8, clean_text(f"- {s}"))
        else:
            pdf.multi_cell(0, 8, "- No schedule available")

        pdf.cell(0, 8, "Resources:", ln=True)
        if day["Resources"]:
            for res in day["Resources"]:
                title = clean_text(res.get("title", ""))
                url = clean_text(res.get("url", ""))
                typ = clean_text(res.get("type", ""))
                pdf.multi_cell(0, 6, f"- {title} ({typ}): {url}")
        else:
            pdf.multi_cell(0, 6, "- No resources available")

        pdf.ln(5)

    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, "plan.pdf")
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    return pdf_bytes


# -------------------------------------------------
# Display all saved plans (with Close button)
# -------------------------------------------------
def display_all_plans():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_plans = load_all_plans(BASE_DIR)

    if "show_saved_plans" not in st.session_state:
        st.session_state["show_saved_plans"] = True

    if not all_plans:
        st.info("No saved plans found.")
        if st.button("🔙 Back to Planner"):
            st.session_state["show_saved_plans"] = False
            st.rerun()
        return

    if st.session_state["show_saved_plans"]:
        st.markdown("<h1 style='text-align: center;'>📂 Saved Study Plans</h1>", unsafe_allow_html=True)

        # Close button at the top
        if st.button("❌ Close"):
            st.session_state["show_saved_plans"] = False
            st.rerun()

        for plan_obj in all_plans:
            plan = plan_obj["plan"]
            filename = plan_obj["filename"]
            clean_filename = os.path.splitext(filename)[0]

            with st.expander(f"🗓️ Plan Created On: {clean_filename}"):
                grouped_plan = {}
                for entry in plan:
                    day_num = entry.get("Day", 0)
                    if day_num not in grouped_plan:
                        grouped_plan[day_num] = {
                            "Day": day_num,
                            "Date": entry.get("Date", "Unknown"),
                            "Topics": [],
                            "Resources": [],
                            "Schedule": []
                        }
                    grouped_plan[day_num]["Topics"].append(entry.get("Topic", ""))
                    grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
                    grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))

                for day in grouped_plan.values():
                    st.markdown(f"### 📅 Day {day['Day']} ({day['Date']})")
                    st.markdown(f"**Topics:** {', '.join(day['Topics'])}")

                    st.markdown("**Schedule:**")
                    if day["Schedule"]:
                        for s in day["Schedule"]:
                            st.markdown(f"- {s}")
                    else:
                        st.markdown("- No schedule available")

                    st.markdown("**Resources:**")
                    if day["Resources"]:
                        for res in day["Resources"]:
                            st.markdown(f"- [{res.get('title','')}]({res.get('url','')}) ({res.get('type','')})")
                    else:
                        st.markdown("- No resources available")

                    st.markdown("---")

                total_minutes = sum(len(day["Schedule"]) * 15 for day in grouped_plan.values())
                st.markdown(f"**Total Study Time (approx.):** {total_minutes} minutes")

                # PDF download button
                pdf_bytes = generate_plan_pdf(plan)
                st.download_button(
                    label="💾 Download this plan as PDF",
                    data=pdf_bytes,
                    file_name=f"{clean_filename}.pdf",
                    mime="application/pdf",
                )
