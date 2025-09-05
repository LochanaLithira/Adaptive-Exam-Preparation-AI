"""
LLM Service for generating explanations using Google Gemini API
"""

import os
import google.generativeai as genai

# Configure Gemini API
GEN_API_KEY = os.getenv("GEN_API_KEY", "AIzaSyB_BCM8i2fnDwJmIze07aQhcWgUQ1Pw8EQ")
genai.configure(api_key=GEN_API_KEY)

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
    print(f"Explanation: {explanation}")
    return explanation

if __name__ == "__main__":
    test_generate_explanation()
