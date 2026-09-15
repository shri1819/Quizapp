"""
Quiz Engine for QuizMaster.
Maintains session state, scoring rules, streak bonuses, time tracking, and performance ratings.
"""

import time
from typing import Any, Dict, List, Optional


class QuizSession:
    """Represents an active quiz session and calculates live metrics."""

    def __init__(
        self,
        questions: List[Dict[str, Any]],
        player_name: str = "Player",
        mode: str = "Classic",
        category: str = "All Categories",
        difficulty: str = "Mixed",
        timer_seconds: int = 30
    ):
        self.questions = questions
        self.player_name = player_name
        self.mode = mode
        self.category = category
        self.difficulty = difficulty
        self.timer_seconds = timer_seconds

        self.current_index = 0
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.unanswered_count = 0

        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.question_start_time = time.time()

        self.answers_history: List[Dict[str, Any]] = []

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)

    def start_question_timer(self):
        """Mark start time for the current question."""
        self.question_start_time = time.time()

    def submit_answer(self, chosen_answer: Optional[str]) -> Dict[str, Any]:
        """
        Process the user's answer (or None for timeout/skip).
        Calculates points, updates streaks, and records history.
        """
        q = self.current_question
        if q is None:
            return {}

        time_spent = round(time.time() - self.question_start_time, 2)
        correct_answer = q["answer"]
        is_timeout = (chosen_answer is None)
        is_correct = (chosen_answer == correct_answer) if not is_timeout else False

        points_earned = 0
        streak_bonus = 0

        if is_correct:
            self.correct_count += 1
            self.streak += 1
            if self.streak > self.max_streak:
                self.max_streak = self.streak

            # Difficulty multiplier
            diff = q.get("difficulty", "Easy")
            if diff == "Hard":
                multiplier = 2.0
            elif diff == "Medium":
                multiplier = 1.5
            else:
                multiplier = 1.0

            base_points = 10 * multiplier

            # Streak bonus
            if self.streak == 10:
                streak_bonus = 25
            elif self.streak == 5:
                streak_bonus = 10
            elif self.streak == 3:
                streak_bonus = 5

            # Speed bonus for Speed Challenge mode
            speed_bonus = 0
            if self.mode == "Speed Challenge" and self.timer_seconds > 0:
                remaining_fraction = max(0.0, (self.timer_seconds - time_spent) / self.timer_seconds)
                speed_bonus = int(5 * remaining_fraction)

            points_earned = int(base_points + streak_bonus + speed_bonus)
            self.score += points_earned
        else:
            self.streak = 0
            if is_timeout:
                self.unanswered_count += 1
            else:
                self.incorrect_count += 1

        record = {
            "question_id": q["id"],
            "question": q["question"],
            "category": q.get("category", "General"),
            "difficulty": q.get("difficulty", "Easy"),
            "options": list(q["options"]),
            "user_answer": chosen_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "is_timeout": is_timeout,
            "explanation": q.get("explanation", ""),
            "points_earned": points_earned,
            "streak_bonus": streak_bonus,
            "time_spent": time_spent
        }
        self.answers_history.append(record)

        return record

    def advance(self) -> bool:
        """Move to the next question. Returns True if more questions exist."""
        self.current_index += 1
        if self.is_finished:
            self.end_time = time.time()
            return False
        self.start_question_timer()
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Generate final performance metrics and rating summary."""
        total_time = int((self.end_time or time.time()) - self.start_time)
        accuracy = round((self.correct_count / self.total_questions * 100), 1) if self.total_questions > 0 else 0.0

        # Knowledge Level Rating & Message
        if accuracy >= 90:
            rating = "Master 🏆"
            message = "Outstanding! Exceptional mastery of trivia."
        elif accuracy >= 80:
            rating = "Expert 🎉"
            message = "Excellent Work! Superb general knowledge."
        elif accuracy >= 70:
            rating = "Advanced 👏"
            message = "Great Job! Strong understanding across topics."
        elif accuracy >= 60:
            rating = "Intermediate 👍"
            message = "Good Effort! Solid foundation, keep learning."
        else:
            rating = "Beginner 💪"
            message = "Keep Practicing! Every quiz sharpens the mind."

        avg_time = round(total_time / self.total_questions, 1) if self.total_questions > 0 else 0.0

        return {
            "player_name": self.player_name,
            "mode": self.mode,
            "category": self.category,
            "difficulty": self.difficulty,
            "score": self.score,
            "percentage": accuracy,
            "correct": self.correct_count,
            "incorrect": self.incorrect_count,
            "unanswered": self.unanswered_count,
            "total_questions": self.total_questions,
            "max_streak": self.max_streak,
            "time_taken_seconds": total_time,
            "avg_time_per_question": avg_time,
            "rating": rating,
            "message": message,
            "history": self.answers_history
        }
