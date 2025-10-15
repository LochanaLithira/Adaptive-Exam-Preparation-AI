# gemini_client.py
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from google import genai
except Exception:
    raise ImportError("google-genai package is required. Run: pip install google-genai")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "No GEMINI_API_KEY found in environment. Set GEMINI_API_KEY or use ADC/service account."
            )
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def filter_passages(self, passages: List[str]) -> List[str]:
        """
        Filter out trivial or off-topic content before generating quiz questions.
        """
        filtered = []
        for p in passages:
            # Skip if it contains irrelevant keywords
            if any(kw in p.lower() for kw in ['message from', 'published', 'isbn', 'www', 'director', 'copyright']):
                continue
            # Skip very short or empty passages
            if len(p.strip()) < 50:
                continue
            filtered.append(p)
        return filtered

    def generate_quiz_from_passages(
        self, passages: List[str], topic: str | None = None, max_questions: int = 5
    ) -> List[Dict]:
        """
        Ask Gemini to produce multiple choice questions based on passages.
        Returns a list of dicts: {question, category, options, correct_answer, explanation}
        """
        # Filter passages to remove irrelevant content
        passages = self.filter_passages(passages)

        prompt = self._build_prompt(passages, topic, max_questions)
        resp = self.client.models.generate_content(model=self.model, contents=prompt)

        text = getattr(resp, "text", None) or str(resp)
        return self.parse_quiz(text)

    def _build_prompt(self, passages: List[str], topic: str | None, max_q: int) -> str:
        """
        Build a concise prompt for generating scenario-based, application-focused MCQs.
    """
        joined_passages = "\n\n---\n\n".join(passages[:10])
        topic_line = f"Subject: {topic}\n" if topic else ""

        structured_prompt = f"""
    Generate {max_q} challenging MCQs from the material below. Follow these rules strictly:

REQUIREMENTS:
- Base questions on provided content only
- Create scenario-based, application-oriented questions (NO factual recall like names/dates)
- Provide exactly 4 options (A-D) per question
- Hard difficulty only
- Number questions as Q1, Q2, etc.
- Category must be a specific topic (e.g., "Photosynthesis", "Newton's Laws") - NOT generic terms

FORMAT (use exactly):
Q1: [Scenario-based question]
Category: [Specific educational topic]
A) option 1
B) option 2
C) option 3
D) option 4
Answer: [Letter] (brief explanation)

{topic_line}
Content:
{joined_passages}

    Generate quiz:
        """
        return structured_prompt

    def generate_explanation(self, question_text: str, student_ans: str, correct_ans: str) -> str:
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
            # Generate response using the new genai client
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Safely extract text from response
            text_content = getattr(response, "text", None) or str(response)
            
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

    def parse_quiz(self, text: str) -> List[Dict]:
        """
        Parse Gemini's raw quiz text into structured format.
        """
        if not text:
            print("Empty text provided to parse_quiz")
            return []

        quiz = []

        # Regex patterns for standard and alternative formats
        patterns = [
            # Standard format with Category
            r"Q\d+: (.?)\nCategory: (.?)\nA\) (.?)\nB\) (.?)\nC\) (.?)\nD\) (.?)\nAnswer: ([A-D])\s*\((.*?)\)",
            # Alternative format with optional explanation
            r"Q\d+: (.?)\nCategory: (.?)\nA\) (.?)\nB\) (.?)\nC\) (.?)\nD\) (.?)\nAnswer: ([A-D])",
            # Format without Category
            r"Q\d+: (.?)\nA\) (.?)\nB\) (.?)\nC\) (.?)\nD\) (.?)\nAnswer: ([A-D])\s\(?([^\)]*)\)?",
        ]

        

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                for i, match in enumerate(matches, 1):
                    if "Category:" in pattern:
                        question, category, a, b, c, d, answer, explanation = match if len(match) == 8 else (*match, "")
                    else:
                        question, a, b, c, d, answer, explanation = match if len(match) == 7 else (*match, "")
                        category = "Not specified"

                    quiz.append({
                        "id": i,
                        "question": question.strip(),
                        "category": category.strip() if category else "Not specified",
                        "options": {"A": a.strip(), "B": b.strip(), "C": c.strip(), "D": d.strip()},
                        "correct_answer": answer.strip(),
                        "explanation": explanation.strip()
                    })
                break  # Stop after first successful pattern match

        # Backup parsing if regex fails
        if not quiz and "Q1:" in text:
            sections = text.split("Q")
            for i, section in enumerate(sections[1:], 1):
                try:
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

                    # Extract options
                    option_matches = re.findall(r"([A-D]\) )(.*?)(?=\n[A-D]\)|Answer:|$)", options_part, re.DOTALL)
                    options = {opt[0]: opt[1].strip() for opt in option_matches}

                    # Extract answer
                    answer_match = re.search(r"Answer: ([A-D])", options_part)
                    answer = answer_match.group(1) if answer_match else None

                    # Extract explanation
                    explanation_match = re.search(r"Answer: [A-D]\s*\((.*?)\)", options_part)
                    explanation = explanation_match.group(1).strip() if explanation_match else ""

                    if len(options) == 4 and question and answer:
                        quiz.append({
                            "id": i,
                            "question": question,
                            "category": category,
                            "options": options,
                            "correct_answer": answer,
                            "explanation": explanation
                        })
                except Exception as e:
                    print(f"Error parsing question {i}: {e}")

        print(f"Parsed {len(quiz)} questions")
        return quiz