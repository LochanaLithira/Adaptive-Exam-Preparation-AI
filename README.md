<<<<<<< HEAD
# Adaptive Exam Preparation AI

## 1️⃣ Overview

The goal of this system is to assist students in exam preparation by:

- Planning personalized study schedules  
- Generating quizzes based on knowledge gaps  
- Tracking performance and adapting difficulty  

The system is composed of three AI agents:

| Agent | Role | Core Functions |
|-------|------|----------------|
| **Planner Agent** | Generates personalized study plans | Suggests topics, sets schedules, and adapts plans based on progress |
| **Quiz Generator Agent** | Creates quizzes based on topics & difficulty | Generates questions, answers, and explanations using NLP & LLM |
| **Performance Tracker Agent** | Tracks user performance and adapts difficulty | Monitors quiz results, recommends revisions, and provides insights |

# Adaptive Exam Preparation AI

An AI-powered system designed to help students prepare efficiently for exams by planning study schedules, generating quizzes, and tracking performance.

---

## 1️⃣ Overview

The goal of this system is to assist students in exam preparation by:

- Planning personalized study schedules  
- Generating quizzes based on knowledge gaps  
- Tracking performance and adapting difficulty  

The system is composed of three AI agents:

| Agent | Role | Core Functions |
|-------|------|----------------|
| **Planner Agent** | Generates personalized study plans | Suggests topics, sets schedules, and adapts plans based on progress |
| **Quiz Generator Agent** | Creates quizzes based on topics & difficulty | Generates questions, answers, and explanations using NLP & LLM |
| **Performance Tracker Agent** | Tracks user performance and adapts difficulty | Monitors quiz results, recommends revisions, and provides insights |

---

## 2️⃣ System Architecture

The system follows a high-level flow where user inputs guide the AI agents, which work collaboratively to optimize learning:

User Input (exam subject, topics)
│
▼
Planner Agent ──────────────┐
│ │
▼ │
Quiz Generator Agent │
│ │
▼ │
Performance Tracker Agent ◀─┘
│
▼
Streamlit Frontend (Dashboard, quizzes, analytics)

yaml
Copy code

### Data Flow Between Agents

- **Planner Agent → Quiz Generator Agent**  
  Decides which topics and questions need to be generated based on the study plan and knowledge gaps.

- **Quiz Generator Agent → Performance Tracker Agent**  
  Sends quiz results, including answers and completion data, for evaluation and analysis.

- **Performance Tracker Agent → Planner Agent**  
  Provides insights and recommendations to adjust the study plan dynamically according to user performance.

This architecture ensures **continuous feedback** and adaptive learning tailored to each student’s needs.
