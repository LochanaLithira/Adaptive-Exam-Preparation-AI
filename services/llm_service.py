"""
LLM Service for generating explanations using Google Gemini API
"""

import os
import re
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
GEN_API_KEY = os.getenv("GEN_API_KEY", "AIzaSyB_BCM8i2fnDwJmIze07aQhcWgUQ1Pw8EQ")
genai.configure(api_key=GEN_API_KEY)

# Load dataset for quiz generation
try:
    df = pd.read_csv('services/cleaned_dataset.csv')
except FileNotFoundError:
    # Dataset not found - quiz generation will use fallback methods
    df = pd.DataFrame()

def generate_explanation(question_text: str, student_ans: str, correct_ans: str) -> str:
    """
    Generate a natural language explanation for a wrong answer using Gemini API.
    
    Args:
        question_text (str): The original question
        student_ans (str): Student's incorrect answer
        correct_ans (str): The correct answer
    
    Returns:
        str: Generated explanation or error message
    """
    prompt = (
        f"Question: {question_text}\n"
        f"Student answered: {student_ans}\n"
        f"Correct answer: {correct_ans}\n\n"
        "Please explain in simple, clear language why the student's answer is incorrect "
        "and help them understand the correct solution. Keep the explanation concise and educational."
    )

    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=150,
            )
        )
        
        # Extract text from response
        explanation = response.text.strip()
        return explanation

    except Exception as e:
        return f"Error generating explanation: {str(e)}"

# Test function
def test_generate_explanation():
    """Test the generate_explanation function"""
    question = "What is 2+2?"
    student_answer = "3"
    correct_answer = "4"
    
    explanation = generate_explanation(question, student_answer, correct_answer)
    return explanation


# Quiz generator
def generate_quiz(num_questions=5):
    """
    Generate quiz questions using the dataset and Gemini API
    
    Args:
        num_questions (int): Number of questions to generate
        
    Returns:
        str: Generated quiz text
    """
    if df.empty:
        return "No data available to generate quiz."
    
    sample_data = df.sample(min(num_questions * 2, len(df)))
    prompt = f"""
    Based on this cleaned dataset:
    {sample_data.to_string(index=False)}

    Generate {num_questions} multiple-choice quiz questions.

    Each question must include its related category.

    Format response exactly like this:
    Q1: [Question text]
    Category: [category_name]
    A) option 1
    B) option 2
    C) option 3
    D) option 4
    Answer: B (explanation...)
    """
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )
        
        return response.text
        
    except Exception as e:
        return f"Error generating quiz: {str(e)}"

def parse_quiz(text):
    """
    Parse the generated quiz text into structured format
    
    Args:
        text (str): Raw quiz text from Gemini API
        
    Returns:
        list: List of quiz questions with structured data
    """
    quiz = []
    pattern = r"Q\d+: (.*?)\nCategory: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])"
    matches = re.findall(pattern, text, re.DOTALL)

    for i, match in enumerate(matches, 1):
        question, category, a, b, c, d, answer = match
        quiz.append({
            "id": i,
            "question": question.strip(),
            "category": category.strip() if category else "None",
            "options": {"A": a.strip(), "B": b.strip(), "C": c.strip(), "D": d.strip()},
            "correct_answer": answer.strip()
        })
    return quiz

if __name__ == "__main__":
    test_generate_explanation()
