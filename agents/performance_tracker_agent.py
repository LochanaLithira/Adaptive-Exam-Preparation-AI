from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.config import get_database, COLLECTIONS

# Import LLM service
from services.llm_service import generate_explanation

app = FastAPI(title="Performance Tracker Agent")

# -----------------------------
# MongoDB connection
# -----------------------------
db = get_database()
if db is None:
    raise Exception("MongoDB connection failed")

results_col = db[COLLECTIONS["quiz_results"]]

# -----------------------------
# Pydantic model for input
# -----------------------------
class QuizResult(BaseModel):
    user_id: int
    quiz_id: int
    topic: str
    answers: dict           # {"Q1": "A"}
    correct_answers: dict   # {"Q1": "B"}
    questions_text: dict    # {"Q1": "What is 2+2?"}

# -----------------------------
# Core MCQ evaluation function
# -----------------------------
def evaluate_mcq(answers: dict, correct_answers: dict):
    score = 0
    wrong_questions = {}

    for q_id, student_ans in answers.items():
        correct_ans = correct_answers.get(q_id)
        if student_ans == correct_ans:
            score += 1
        else:
            wrong_questions[q_id] = correct_ans

    total = len(correct_answers)
    accuracy = (score / total) * 100
    feedback = f"You scored {score}/{total} ({accuracy:.2f}%)."
    if wrong_questions:
        feedback += f" Review questions: {', '.join(wrong_questions.keys())}"

    return score, total, accuracy, feedback, wrong_questions

# -----------------------------
# Generate LLM explanations
# -----------------------------
def generate_feedback_with_llm(answers, correct_answers, questions_text):
    explanations = {}
    for q_id, student_ans in answers.items():
        correct_ans = correct_answers.get(q_id)
        if student_ans != correct_ans:
            question_text = questions_text.get(q_id, "")
            explanations[q_id] = generate_explanation(question_text, student_ans, correct_ans)
    return explanations

# -----------------------------
# FastAPI POST endpoint
# -----------------------------
@app.post("/track")
def track_performance(data: QuizResult):
    try:
        # Evaluate MCQs
        score, total, accuracy, feedback, wrong_questions = evaluate_mcq(
            data.answers, data.correct_answers
        )

        # Generate explanations for wrong answers using LLM
        explanations = generate_feedback_with_llm(
            data.answers, data.correct_answers, data.questions_text
        )

        # Prepare result
        result = {
            "score": score,
            "total": total,
            "accuracy": accuracy,
            "feedback": feedback,
            "wrong_questions": wrong_questions,
            "explanations": explanations
        }

        # Save to MongoDB
        results_col.insert_one({
            "user_id": data.user_id,
            "quiz_id": data.quiz_id,
            "topic": data.topic,
            "answers": data.answers,
            "result": result
        })

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
