# gemini_client.py
import os
import re
import json  # ✅ Added for caching
import hashlib  # ✅ Added to create unique keys for caching
from typing import List, Dict
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

try:
    from google import genai
except Exception:
    raise ImportError("google-genai package is required. Run: pip install google-genai")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CACHE_FILE = os.path.join("quiz_cache", "quiz_cache.json")  # ✅ File to store cached quizzes
os.makedirs("quiz_cache", exist_ok=True)  # ✅ Ensure cache directory exists

class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "No GEMINI_API_KEY found in environment. Set GEMINI_API_KEY or use ADC/service account."
            )
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def _load_cache(self) -> Dict:
        """✅ Load cache from file if exists"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self, cache: Dict):
        """✅ Save cache back to file"""
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    def _make_cache_key(self, passages: List[str], topic: str | None, max_q: int) -> str:
        """✅ Create a unique key based on passages + topic + number of questions"""
        raw_data = "\n".join(passages) + (topic or "") + str(max_q)
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def filter_passages(self, passages: List[str]) -> List[str]:
        """
        Filter out trivial or off-topic content before generating quiz questions.
        """
        filtered = []
        for p in passages:
            if any(kw in p.lower() for kw in ['message from', 'published', 'isbn', 'www', 'director', 'copyright']):
                continue
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
        # ✅ Check cache first
        cache = self._load_cache()
        cache_key = self._make_cache_key(passages, topic, max_questions)
        if cache_key in cache:
            cached_quiz = cache[cache_key]
            random.shuffle(cached_quiz)  # Shuffle to provide some variation
            return cached_quiz[:max_questions]

        # Filter passages to remove irrelevant content
        passages = self.filter_passages(passages)

        prompt = self._build_prompt(passages, topic, max_questions)
        resp = self.client.models.generate_content(model=self.model, contents=prompt)

        text = getattr(resp, "text", None) or str(resp)
        quiz = self.parse_quiz(text)

        # ✅ Save generated quiz to cache
        cache[cache_key] = quiz
        self._save_cache(cache)
        print("💾 Quiz saved to cache")

        return quiz

    def _build_prompt(self, passages: List[str], topic: str | None, max_q: int) -> str:
        joined_passages = "\n\n---\n\n".join(passages[:10])
        topic_line = f"Subject/Module Context: {topic}\n" if topic else ""

        structured_prompt = f"""
Generate {max_q} challenging, scenario-based multiple-choice questions strictly based on the following study material.
Focus only on conceptual understanding, application, and reasoning. Include observations, experiments, or real-life examples wherever possible.
Do NOT include trivial or factual recall questions such as names, dates, publishers, or textbook information.

RULES:
1. Base each question strictly on the content provided; do not invent external facts.
2. Provide exactly 4 options (A, B, C, D) per question.
3. Only produce HARD questions.
4. Questions should be scenario-based, application-oriented, or experimental.
5. Mark the correct answer with the corresponding letter.
6. Include a concise explanation (1-2 sentences) for the correct answer.
7. Number questions sequentially (Q1, Q2, ...).
8. *IMPORTANT*: For the "Category" field, provide a SPECIFIC TOPIC related to the question content.
9. Do NOT add any introductory notes, commentary, or questions outside this material.

Format strictly as:
Q1: [Scenario/Observation-based question text]
Category: [Specific educational topic - e.g., "Photosynthesis", "Newton's Second Law", "Atomic Structure"]
A) option 1
B) option 2
C) option 3
D) option 4
Answer: [Letter] (short explanation)

{topic_line}
Content for question generation:
{joined_passages}

Begin generating the quiz now:
"""
        return structured_prompt

    def generate_explanation(self, question_text: str, student_ans: str, correct_ans: str) -> str:
        prompt = (
            f"Question: {question_text}\n"
            f"Student answered: {student_ans}\n"
            f"Correct answer: {correct_ans}\n\n"
            "Please explain in simple, clear language why the student's answer is incorrect "
            "and help them understand the correct solution. Keep the explanation concise and educational."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            text_content = getattr(response, "text", None) or str(response)
            if text_content:
                return text_content.strip()
            else:
                return "Could not extract explanation from the API response."
        except Exception as e:
            error_message = str(e)
            print(f"Error generating explanation: {error_message}")
            if "404" in error_message or "not found" in error_message.lower():
                return "Error: Could not access the AI model. Please try again."
            elif "quota exceeded" in error_message.lower() or "429" in error_message:
                return "Error: API quota exceeded. Please try again in a few minutes."
            elif "API key" in error_message.lower():
                return "Error: Invalid API key. Please check your configuration."
            else:
                return f"Error generating explanation: {error_message}"

    def parse_quiz(self, text: str) -> List[Dict]:
        if not text:
            print("Empty text provided to parse_quiz")
            return []

        quiz = []
        patterns = [
            r"Q\d+: (.*?)\nCategory: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])\s*\((.*?)\)",
            r"Q\d+: (.*?)\nCategory: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])",
            r"Q\d+: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])\s\(?([^\)]*)\)?",
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
                break

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

                    option_matches = re.findall(r"([A-D]\) )(.*?)(?=\n[A-D]\)|Answer:|$)", options_part, re.DOTALL)
                    options = {opt[0]: opt[1].strip() for opt in option_matches}

                    answer_match = re.search(r"Answer: ([A-D])", options_part)
                    answer = answer_match.group(1) if answer_match else None

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
