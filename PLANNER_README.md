# Adaptive Exam Preparation Planner

An intelligent study planner application that generates a **7-day personalized study plan** based on your performance in different topics. The system provides guidance, study schedules, and resources for each topic, and tracks your progress.

---

## Features

### 1. Performance Analysis
- Stores sample performance records in a JSON file (`performance.json`).
- Summarizes topic accuracy.
- Calculates weights for topics based on accuracy:
  - Lower accuracy → higher weight → more focus needed.

### 2. Personalized Study Plan
- Generates a **7-day study plan**:
  - Day-wise topic allocation: Weak → Medium → Good pattern.
  - Each day includes:
    - **Topic**
    - **Schedule** (Learn, Practice, Review with allocated times)
    - **Resources** (clickable links)
- Allows saving plans to a timestamped JSON file (`saved_plans` folder).

### 3. Plan Management
- Load all previously saved plans.
- Check if a plan is already saved.
- Persistently track completed days (`completed_days.json`).

### 4. Progress Tracking
- Checkbox to mark completion of each day.
- Automatically calculates **total study time** based on completed days.
- Dynamic display of progress and study time in **Streamlit** interface.

---

## Project Structure

adaptive_exam_preparation-AI/
├── logic_planner/
│ ├── performance_loader.py # Load performance & summarize by topic
│ ├── plan_viewer.py # Display saved plans, track completion, generate new plans
│ ├── planner.py # Calculate topic weights & generate 7-day plan
│ └── resources.py # Topic-wise resources (links, PDFs, videos)
└─└── plan_manager.py # # Save/load plans, manage plan files
├── saved_plans/ # Auto-generated folder storing saved plans
├── completed_days.json # Tracks completed days across all plans
├── data/
│ └── performance.json # sample Performance records (topic + accuracy)
└── PLANNER_README.md

## PlannerUI inside /ui - connects all parts and builds the main planner interface