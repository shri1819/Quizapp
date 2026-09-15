"""
Question Manager for QuizMaster.
Handles loading, validation, filtering, shuffling, and fallback generation of quiz questions.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional, Tuple

VALID_CATEGORIES = [
    "General Knowledge",
    "Science",
    "History",
    "Geography",
    "Technology",
    "Computers",
    "Sports",
    "Entertainment",
    "Literature",
    "Mathematics",
    "Space",
    "Nature"
]

VALID_DIFFICULTIES = ["Easy", "Medium", "Hard"]

# Hardcoded fallback questions in case file is absent or corrupted
FALLBACK_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the capital city of Japan?",
        "category": "Geography",
        "difficulty": "Easy",
        "options": ["Tokyo", "Kyoto", "Osaka", "Hiroshima"],
        "answer": "Tokyo",
        "explanation": "Tokyo has been the capital and largest city of Japan since 1868."
    },
    {
        "id": 2,
        "question": "Which planet is known as the Red Planet?",
        "category": "Space",
        "difficulty": "Easy",
        "options": ["Venus", "Mars", "Jupiter", "Mercury"],
        "answer": "Mars",
        "explanation": "Mars appears reddish because of iron oxide on its surface."
    },
    {
        "id": 3,
        "question": "Which chemical element has the symbol 'Au'?",
        "category": "Science",
        "difficulty": "Easy",
        "options": ["Silver", "Gold", "Copper", "Aluminum"],
        "answer": "Gold",
        "explanation": "The symbol 'Au' comes from the Latin word 'aurum'."
    },
    {
        "id": 4,
        "question": "Who painted the Mona Lisa?",
        "category": "Entertainment",
        "difficulty": "Easy",
        "options": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo"],
        "answer": "Leonardo da Vinci",
        "explanation": "Leonardo da Vinci created the Mona Lisa in Florence during the Italian Renaissance."
    },
    {
        "id": 5,
        "question": "In which year did World War II end?",
        "category": "History",
        "difficulty": "Easy",
        "options": ["1943", "1945", "1948", "1950"],
        "answer": "1945",
        "explanation": "World War II concluded in 1945 following the surrender of Axis forces."
    }
]


class QuestionValidationError(Exception):
    """Raised when question data fails validation checks."""
    pass


class QuestionManager:
    """Manages question loading, verification, and filtering."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "questions.json")
        self.file_path = file_path
        self.questions: List[Dict[str, Any]] = []
        self.load_questions()

    def validate_question(self, q: Dict[str, Any], seen_ids: set) -> None:
        """Thoroughly validate a single question dictionary."""
        if not isinstance(q, dict):
            raise QuestionValidationError("Question record must be a dictionary.")

        qid = q.get("id")
        if qid is None or not isinstance(qid, int):
            raise QuestionValidationError(f"Invalid or missing question ID: {qid}")
        if qid in seen_ids:
            raise QuestionValidationError(f"Duplicate question ID detected: {qid}")
        seen_ids.add(qid)

        question_text = q.get("question")
        if not question_text or not isinstance(question_text, str) or not question_text.strip():
            raise QuestionValidationError(f"Question #{qid} has empty or non-string question text.")

        category = q.get("category")
        if not category or not isinstance(category, str) or not category.strip():
            raise QuestionValidationError(f"Question #{qid} has invalid category: {category}")

        difficulty = q.get("difficulty")
        if difficulty not in VALID_DIFFICULTIES:
            raise QuestionValidationError(f"Question #{qid} has invalid difficulty: {difficulty}")

        options = q.get("options")
        if not isinstance(options, list) or len(options) != 4:
            raise QuestionValidationError(f"Question #{qid} must have exactly 4 options.")
        if len(set(options)) != 4:
            raise QuestionValidationError(f"Question #{qid} contains duplicate options: {options}")
        for opt in options:
            if not isinstance(opt, str) or not opt.strip():
                raise QuestionValidationError(f"Question #{qid} contains empty option.")

        answer = q.get("answer")
        if not answer or not isinstance(answer, str) or answer not in options:
            raise QuestionValidationError(f"Question #{qid} answer '{answer}' is not in options {options}.")

        explanation = q.get("explanation")
        if not explanation or not isinstance(explanation, str) or not explanation.strip():
            raise QuestionValidationError(f"Question #{qid} has missing or empty explanation.")

    def load_questions(self) -> List[Dict[str, Any]]:
        """Load questions from JSON, validate them, or fallback gracefully."""
        self.questions = []
        if not os.path.exists(self.file_path):
            self.questions = list(FALLBACK_QUESTIONS)
            self._save_fallback()
            return self.questions

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list) or not raw_data:
                raise QuestionValidationError("Questions JSON must contain a non-empty list.")

            seen_ids = set()
            valid_questions = []
            for item in raw_data:
                try:
                    self.validate_question(item, seen_ids)
                    valid_questions.append(item)
                except QuestionValidationError as err:
                    print(f"[Warning] Skipping invalid question: {err}")

            if valid_questions:
                self.questions = valid_questions
            else:
                self.questions = list(FALLBACK_QUESTIONS)

        except Exception as e:
            print(f"[Error] Failed to load questions file ({e}). Using fallbacks.")
            self.questions = list(FALLBACK_QUESTIONS)
            self._save_fallback()

        return self.questions

    def _save_fallback(self) -> None:
        """Attempt to write fallback questions to disk."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.questions, f, indent=4)
        except Exception:
            pass

    def get_all_categories(self) -> List[str]:
        """Return distinct categories available in current question bank."""
        cats = sorted(list({q["category"] for q in self.questions if "category" in q}))
        return cats if cats else VALID_CATEGORIES

    def filter_questions(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter questions matching category and difficulty criteria."""
        filtered = self.questions

        if category and category not in ("All Categories", "Mixed", "All"):
            filtered = [q for q in filtered if q.get("category") == category]

        if difficulty and difficulty not in ("Mixed", "All"):
            filtered = [q for q in filtered if q.get("difficulty") == difficulty]

        return filtered

    def get_available_count(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> int:
        """Count how many questions match the specified filters."""
        return len(self.filter_questions(category, difficulty))

    def prepare_quiz_questions(
        self,
        category: str = "All Categories",
        difficulty: str = "Mixed",
        count: int = 10,
        shuffle_questions: bool = True,
        shuffle_answers: bool = True
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Prepares a validated, filtered, and prepared list of questions for a quiz session.
        Returns (prepared_questions, error_message).
        """
        matching = self.filter_questions(category, difficulty)

        if not matching:
            return [], f"No questions found for category '{category}' and difficulty '{difficulty}'."

        if count > len(matching):
            # Inform caller that requested count exceeds available
            return [], (
                f"There are only {len(matching)} questions matching your selected filters. "
                f"Please choose fewer questions or change your filters."
            )

        # Select subset
        if shuffle_questions:
            selected = random.sample(matching, count)
        else:
            selected = matching[:count]

        # Prepare copy and optionally shuffle answer choices while preserving correct answer
        prepared = []
        for q in selected:
            q_copy = {
                "id": q["id"],
                "question": q["question"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "answer": q["answer"],
                "explanation": q["explanation"],
                "options": list(q["options"])
            }
            if shuffle_answers:
                random.shuffle(q_copy["options"])
            prepared.append(q_copy)

        return prepared, None
