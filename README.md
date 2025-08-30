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

## 2️⃣ System Architecture

High-Level Flow:

```mermaid
flowchart TD
    A["User Input (exam subject, topics)"] --> B["Planner Agent"]
    B --> C["Quiz Generator Agent"]
    C --> D["Performance Tracker Agent"]
    D --> E["Streamlit Frontend (Dashboard, quizzes, analytics)"]
    D --> B
