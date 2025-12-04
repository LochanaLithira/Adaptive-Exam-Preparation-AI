# logic_planner/plan_viewer.py (Updated with Progress Tracking)

import streamlit as st
import os
import json
from datetime import datetime
from fpdf import FPDF
import tempfile
import re

def load_all_plans(BASE_DIR):
    """Load all generated plans from directory"""
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
    
    # Sort by filename (which contains timestamp) - newest first
    plans.sort(key=lambda x: x["filename"], reverse=True)
    return plans


def calculate_plan_completion(plan):
    """Calculate completion percentage for a plan"""
    if not plan:
        return 0.0
    
    # Count topics with completion markers (if available)
    # For now, return 0 as we'll implement tracking separately
    return 0.0


def generate_plan_pdf(plan):
    """Generate PDF for a plan"""
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
                "Schedule": [],
                "Complexity": []
            }
        grouped_plan[day_num]["Topics"].append(entry.get("Topic", ""))
        grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
        grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))
        if "Complexity" in entry:
            grouped_plan[day_num]["Complexity"].append(f"{entry['Topic']}: {entry['Complexity']}")

    def clean_text(t):
        return re.sub(r"[^\x00-\x7F]+", " ", str(t))

    for day in grouped_plan.values():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, clean_text(f"Day {day['Day']} ({day['Date']})"), ln=True)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 8, "Topics:", ln=True)
        pdf.multi_cell(0, 8, clean_text(", ".join(day["Topics"])))
        
        if day["Complexity"]:
            pdf.cell(0, 8, "Complexity Levels:", ln=True)
            pdf.multi_cell(0, 6, clean_text(", ".join(day["Complexity"])))

        pdf.cell(0, 8, "Schedule:", ln=True)
        if day["Schedule"]:
            for s in day["Schedule"]:
                pdf.multi_cell(0, 8, clean_text(f"- {s}"))
        else:
            pdf.multi_cell(0, 8, "- No schedule available")

        pdf.cell(0, 8, "Resources:", ln=True)
        if day["Resources"]:
            seen_urls = set()
            for res in day["Resources"]:
                url = res.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    title = clean_text(res.get("title", ""))
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


def display_plan_card(plan_obj, index):
    """Display a single plan card with enhanced UI"""
    plan = plan_obj["plan"]
    filename = plan_obj["filename"]
    clean_filename = os.path.splitext(filename)[0]
    
    # Extract timestamp from filename
    try:
        timestamp_str = clean_filename.split("_")[-2] + "_" + clean_filename.split("_")[-1]
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        formatted_date = timestamp.strftime("%B %d, %Y at %I:%M %p")
    except:
        formatted_date = clean_filename
    
    # Calculate stats
    total_topics = len(plan)
    total_days = len(set(entry.get("Day", 1) for entry in plan))
    total_time = sum(sum(entry.get("ScheduleMinutes", {}).values()) for entry in plan if "ScheduleMinutes" in entry)
    completion = calculate_plan_completion(plan)
    
    # Determine status
    if completion >= 100:
        status = "✅ Completed"
        status_color = "#4CAF50"
    elif completion > 0:
        status = "🔄 In Progress"
        status_color = "#FF9800"
    else:
        status = "📝 Not Started"
        status_color = "#2196F3"
    
    with st.expander(f"📅 **Plan #{index + 1}** - Created on {formatted_date}", expanded=(index == 0)):
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Topics", total_topics)
        with col2:
            st.metric("📅 Days", total_days)
        with col3:
            st.metric("⏱️ Total Time", f"{total_time // 60}h {total_time % 60}m")
        with col4:
            st.markdown(f"<p style='text-align: center; color: {status_color}; font-weight: bold; margin-top: 10px;'>{status}</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Group plan by day
        grouped_plan = {}
        for entry in plan:
            day_num = entry.get("Day", 0)
            if day_num not in grouped_plan:
                grouped_plan[day_num] = {
                    "Day": day_num,
                    "Date": entry.get("Date", "Unknown"),
                    "Topics": [],
                    "Complexities": [],
                    "Accuracies": [],
                    "Resources": [],
                    "Schedule": [],
                    "Guidance": []
                }
            grouped_plan[day_num]["Topics"].append(entry.get("Topic", ""))
            grouped_plan[day_num]["Complexities"].append(entry.get("Complexity", "medium"))
            grouped_plan[day_num]["Accuracies"].append(entry.get("Accuracy", 0))
            grouped_plan[day_num]["Resources"].extend(entry.get("Resources", []))
            grouped_plan[day_num]["Schedule"].extend(entry.get("Schedule", []))
            if "Guidance" in entry:
                grouped_plan[day_num]["Guidance"].append(entry["Guidance"])
        
        # Display each day
        for day in sorted(grouped_plan.values(), key=lambda x: x["Day"]):
            st.markdown(f"### 📅 Day {day['Day']} - {day['Date']}")
            
            # Topics with complexity badges
            st.markdown("**📚 Topics:**")
            for i, topic in enumerate(day['Topics']):
                complexity = day['Complexities'][i] if i < len(day['Complexities']) else "medium"
                accuracy = day['Accuracies'][i] if i < len(day['Accuracies']) else 0
                
                if complexity == "high":
                    badge = "🔴"
                    color = "#ff4444"
                elif complexity == "medium":
                    badge = "🟡"
                    color = "#ffaa00"
                else:
                    badge = "🟢"
                    color = "#44ff44"
                
                st.markdown(f"{badge} <span style='color: {color}; font-weight: bold;'>{topic}</span> <span style='color: gray; font-size: 0.9em;'>({accuracy}% accuracy)</span>", unsafe_allow_html=True)
            
            # Guidance
            if day['Guidance']:
                st.markdown("**💡 Study Guidance:**")
                for guidance in day['Guidance']:
                    if guidance:
                        st.info(guidance)
            
            # Schedule
            st.markdown("**⏰ Schedule:**")
            if day["Schedule"]:
                for s in day["Schedule"]:
                    st.markdown(f"- {s}")
            else:
                st.markdown("- No schedule available")
            
            # Resources
            st.markdown("**📖 Resources:**")
            if day["Resources"]:
                seen_urls = set()
                for res in day["Resources"]:
                    url = res.get("url", "")
                    if url not in seen_urls:
                        seen_urls.add(url)
                        type_emoji = {"video": "🎥", "practice": "📝", "read": "📖", "concept": "💡"}.get(res.get("type", ""), "📚")
                        st.markdown(f"{type_emoji} [{res.get('title','')}]({url}) ({res.get('type','').capitalize()})")
            else:
                st.markdown("- No resources available")
            
            st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            pdf_bytes = generate_plan_pdf(plan)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_bytes,
                file_name=f"{clean_filename}.pdf",
                mime="application/pdf",
                key=f"download_{index}"
            )
        
        with col2:
            if st.button("🗑️ Delete This Plan", key=f"delete_{index}"):
                try:
                    os.remove(plan_obj["file"])
                    st.success("✅ Plan deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to delete plan: {e}")


def display_all_plans():
    """Main function to display all saved plans"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_plans = load_all_plans(BASE_DIR)

    if "show_saved_plans" not in st.session_state:
        st.session_state["show_saved_plans"] = True

    if not all_plans:
        st.info("📭 No saved plans found. Generate your first plan to get started!")
        if st.button("🔙 Back to Planner"):
            st.session_state["show_saved_plans"] = False
            st.rerun()
        return

    if st.session_state["show_saved_plans"]:
        st.markdown("<h1 style='text-align: center;'>📂 Your Saved Study Plans</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>You have {len(all_plans)} saved plan(s)</p>", unsafe_allow_html=True)

        # Close button at the top
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔙 Back to Planner", use_container_width=True):
                st.session_state["show_saved_plans"] = False
                st.rerun()
        
        st.divider()
        
        # Display all plans
        for index, plan_obj in enumerate(all_plans):
            display_plan_card(plan_obj, index)