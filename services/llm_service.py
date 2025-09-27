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

# Prioritized list of models to try if one fails
GEMINI_MODELS = [
    'models/gemini-flash-latest',  # This model works successfully
    'models/gemini-pro-latest',
    'models/gemini-1.5-flash',
    'models/gemini-1.5-pro'
]

def get_gemini_model():
    """
    Try to get a working Gemini model from the available options.
    Returns the first available model or the first one in the list if can't verify.
    """
    # Based on testing, models/gemini-flash-latest is confirmed working
    # Return this model directly for reliability
    return 'models/gemini-flash-latest'
    
    # The following code is kept as a fallback but not used by default
    try:
        available_models = [model.name for model in genai.list_models()]
        # Find the first model from our list that's available
        for model_name in GEMINI_MODELS:
            if model_name in available_models:
                return model_name
        # If none found, return the first one and hope it works
        return GEMINI_MODELS[0]
    except:
        # If we can't list models, just return the first one and hope it works
        return GEMINI_MODELS[0]

def extract_text_from_response(response):
    """
    Safely extract text content from a Gemini API response.
    Handles different response structures that might be returned.
    
    Args:
        response: The response object from the Gemini API
        
    Returns:
        str: Extracted text content or error message
    """
    try:
        # Try the standard .text accessor first
        if hasattr(response, 'text'):
            return response.text
            
        # If that fails, try to extract content from parts
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts:
                        combined_text = ""
                        for part in parts:
                            if hasattr(part, 'text'):
                                combined_text += part.text
                        return combined_text
                        
        # If we get here, we couldn't extract text
        return ""
    except Exception as e:
        print(f"Error extracting text from response: {e}")
        return ""

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
        # Initialize the Gemini model with a model that should be available
        model_name = get_gemini_model()
        model = genai.GenerativeModel(model_name)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=150,
            )
        )
        
        # Safely extract text from response
        text_content = extract_text_from_response(response)
        if text_content:
            return text_content.strip()
        else:
            return "Could not extract explanation from the API response."

    except Exception as e:
        error_message = str(e)
        print(f"Error generating explanation: {error_message}")
        
        # Provide a more user-friendly error message for common API issues
        if "404" in error_message or "not found" in error_message.lower():
            print(f"Model access error: {error_message}")
            # Don't return error, let it try the next model in the catch block
            return "Error: Could not access the AI model. Please try again."
        elif "quota exceeded" in error_message.lower() or "429" in error_message:
            print(f"Quota exceeded: {error_message}")
            return "Error: API quota exceeded. Please try again in a few minutes."
        elif "API key" in error_message.lower():
            print(f"API key error: {error_message}")
            return "Error: Invalid API key. Please check your configuration."
        else:
            print(f"Unknown error: {error_message}")
            return f"Error generating explanation: {error_message}"

# Test function
# Test functions removed from production code


# Quiz generator
def generate_quiz(num_questions=5, difficulty='easy'):
    """
    Generate quiz questions using the dataset and Gemini API
    
    Args:
        num_questions (int): Number of questions to generate
        difficulty (str): Difficulty level - 'easy', 'medium', or 'difficult'
        
    Returns:
        str: Generated quiz text
    """
    if df.empty:
        return "No data available to generate quiz."
    
    if "difficulty_level" in df.columns:
        filtered_df = df[df["difficulty_level"].str.lower() == difficulty.lower()]
    else:
        filtered_df = df.sample(min(num_questions * 2, len(df)))
    
    if filtered_df.empty:
        return f"No data available for {difficulty} level quiz."

    # Limit the number of sample rows to avoid token limits
    sample_size = min(num_questions * 2, len(filtered_df))
    if sample_size > 10:  # If we have too many samples, limit them
        sample_size = 10
    
    sample_data = filtered_df.sample(sample_size)
    
    # Extract just the needed columns to reduce prompt size
    if len(sample_data.columns) > 5:
        sample_data = sample_data[['concept_name', 'description', 'category', 'subcategory', 'difficulty_level']]

    # Make a more focused, explicit prompt
    prompt = f"""
    Generate {num_questions} multiple-choice quiz questions at {difficulty} difficulty level.
    
    Here is some data to use for inspiration:
    {sample_data.to_string(index=False)}
    
    IMPORTANT INSTRUCTIONS:
    1. Each question MUST follow this EXACT format:
    Q1: [Question text]
    Category: [category_name]
    A) option 1
    B) option 2
    C) option 3
    D) option 4
    Answer: [Letter] (explanation)
    
    2. Ensure all answer options are plausible but only one is correct.
    3. Make the questions challenging but fair for {difficulty} difficulty.
    4. Provide a brief explanation for the correct answer.
    5. Number the questions sequentially (Q1, Q2, etc.)
    
    Begin the quiz now:
    """
    
    try:
        # Maximum number of retries
        max_retries = 2
        attempt = 0
        
        while attempt <= max_retries:
            try:
                # Initialize the Gemini model with a model that should be available
                model_name = get_gemini_model()
                print(f"Attempt {attempt+1}/{max_retries+1}: Using model {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Generate response with adjusted parameters
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7 if attempt == 0 else 0.8,  # Increase temperature on retry
                        max_output_tokens=2048,  # Increase token limit
                        top_k=40,
                        top_p=0.95,
                    )
                )
                
                # Safely extract text from response
                text_content = extract_text_from_response(response)
                
                # Check if response contains expected format
                if text_content and len(text_content) > 100:
                    # Verify if the format matches our expectations (at least one question)
                    if "Q1:" in text_content and "Category:" in text_content and "Answer:" in text_content:
                        print(f"Quiz generation successful on attempt {attempt+1}")
                        return text_content
                    else:
                        print(f"Response format incorrect on attempt {attempt+1}. Retrying...")
                else:
                    print(f"Response too short or empty on attempt {attempt+1}. Retrying...")
                
                # Increment attempt counter
                attempt += 1
                
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {str(e)}")
                attempt += 1
                if attempt <= max_retries:
                    print("Retrying with different parameters...")
                
        # If we get here, all attempts failed
        return "Error: Quiz generation returned empty or invalid response after multiple attempts. Please try again."
            
    except Exception as e:
        error_message = str(e)
        print(f"Error generating quiz: {error_message}")
        
        # Provide a more user-friendly error message for common API issues
        if "404" in error_message or "not found" in error_message.lower():
            print(f"Model access error: {error_message}")
            # Don't return error, let it try the next model in the catch block
            return "Error: Could not access the AI model. Please try again."
        elif "quota exceeded" in error_message.lower() or "429" in error_message:
            print(f"Quota exceeded: {error_message}")
            return "Error: API quota exceeded. Please try again in a few minutes."
        elif "API key" in error_message.lower():
            print(f"API key error: {error_message}")
            return "Error: Invalid API key. Please check your configuration."
        else:
            print(f"Unknown error: {error_message}")
            return f"Error generating quiz: {error_message}"

def parse_quiz(text):
    """
    Parse the generated quiz text into structured format
    
    Args:
        text (str): Raw quiz text from Gemini API
        
    Returns:
        list: List of quiz questions with structured data
    """
    if not text:
        print("Empty text provided to parse_quiz")
        return []
    
    quiz = []
    
    # Try different regex patterns to handle variations in formatting
    patterns = [
        # Standard format
        r"Q\d+: (.*?)\nCategory: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])",
        # Alternative format with optional explanation
        r"Q\d+: (.*?)\nCategory: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])[\s\(]",
        # Format without category
        r"Q\d+: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])",
    ]
    
    print(f"Parsing quiz text ({len(text)} chars)")
    
    for pattern in patterns:
        if "Category:" in pattern:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                print(f"Found {len(matches)} matches with pattern containing Category")
                for i, match in enumerate(matches, 1):
                    question, category, a, b, c, d, answer = match
                    quiz.append({
                        "id": i,
                        "question": question.strip(),
                        "category": category.strip() if category else "None",
                        "options": {"A": a.strip(), "B": b.strip(), "C": c.strip(), "D": d.strip()},
                        "correct_answer": answer.strip()
                    })
                break
        else:
            # Handle pattern without category
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                print(f"Found {len(matches)} matches with pattern without Category")
                for i, match in enumerate(matches, 1):
                    question, a, b, c, d, answer = match
                    quiz.append({
                        "id": i,
                        "question": question.strip(),
                        "category": "Not specified",
                        "options": {"A": a.strip(), "B": b.strip(), "C": c.strip(), "D": d.strip()},
                        "correct_answer": answer.strip()
                    })
                break
    
    # If we couldn't parse any questions, try to manually extract them
    if not quiz and "Q1:" in text:
        print("Using backup parsing approach")
        sections = text.split("Q")
        for i, section in enumerate(sections[1:], 1):  # Skip the first split which is before Q1
            try:
                # Try to extract question
                question_parts = section.split("\nCategory:", 1)
                if len(question_parts) < 2:
                    question_parts = section.split("\nA)", 1)
                    if len(question_parts) < 2:
                        continue
                    question = question_parts[0].strip()
                    options_part = "A)" + question_parts[1]
                    category = "Not specified"
                else:
                    question = question_parts[0].strip()
                    rest = question_parts[1]
                    category_parts = rest.split("\nA)", 1)
                    if len(category_parts) < 2:
                        continue
                    category = category_parts[0].strip()
                    options_part = "A)" + category_parts[1]
                
                # Try to extract options
                option_matches = re.findall(r"([A-D]\) )(.*?)(?=\n[A-D]\)|Answer:|$)", options_part, re.DOTALL)
                options = {}
                for opt_letter, opt_text in option_matches:
                    letter = opt_letter[0]
                    options[letter] = opt_text.strip()
                
                # Try to extract answer
                answer_match = re.search(r"Answer: ([A-D])", options_part)
                if answer_match:
                    answer = answer_match.group(1)
                    
                    # Only add if we have all required fields
                    if len(options) == 4 and question and answer:
                        quiz.append({
                            "id": i,
                            "question": question,
                            "category": category,
                            "options": options,
                            "correct_answer": answer
                        })
            except Exception as e:
                print(f"Error parsing question {i}: {e}")
    
    print(f"Parsed {len(quiz)} questions")
    return quiz

if __name__ == "__main__":
    # Main execution block for manual testing
    print("LLM Service - Available functions:")
    print("- generate_quiz(): Generate quiz questions")
    print("- generate_explanation(): Generate explanations for incorrect answers")
