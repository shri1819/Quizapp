"""
Score and Statistics Manager for QuizMaster.
Handles persistence of high scores, leaderboards, and lifetime gameplay statistics.
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_DATA: Dict[str, Any] = {
    "high_scores": [],
    "statistics": {
        "total_quizzes": 0,
        "total_questions_answered": 0,
        "correct_answers": 0,
        "incorrect_answers": 0,
        "unanswered": 0,
        "best_score": 0,
        "best_percentage": 0.0,
        "best_streak": 0,
        "total_time_seconds": 0,
        "category_counts": {}
    }
}


class ScoreManager:
    """Manages high scores and lifetime player statistics."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "scores.json")
        self.file_path = file_path
        self.data: Dict[str, Any] = dict(DEFAULT_DATA)
        self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON or initialize with defaults."""
        if not os.path.exists(self.file_path):
            self.data = json.loads(json.dumps(DEFAULT_DATA))
            self.save_data()
            return self.data

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "high_scores" in loaded and "statistics" in loaded:
                    self.data = loaded
                else:
                    self.data = json.loads(json.dumps(DEFAULT_DATA))
        except Exception:
            self.data = json.loads(json.dumps(DEFAULT_DATA))
            self.save_data()

        return self.data

    def save_data(self) -> bool:
        """Save high scores and statistics to JSON."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception:
            return False

    def add_score(self, entry: Dict[str, Any]) -> None:
        """Add a new quiz score record and update lifetime statistics."""
        # Ensure timestamp and date if not provided
        if "timestamp" not in entry:
            entry["timestamp"] = time.time()
        if "date" not in entry:
            entry["date"] = datetime.now().strftime("%b %d, %Y")

        self.data["high_scores"].append(entry)
        # Keep high scores sorted by score desc, then percentage desc
        self.data["high_scores"].sort(key=lambda x: (x.get("score", 0), x.get("percentage", 0)), reverse=True)

        # Update lifetime statistics
        stats = self.data.setdefault("statistics", dict(DEFAULT_DATA["statistics"]))
        stats["total_quizzes"] = stats.get("total_quizzes", 0) + 1
        
        answered = entry.get("correct", 0) + entry.get("incorrect", 0)
        stats["total_questions_answered"] = stats.get("total_questions_answered", 0) + answered
        stats["correct_answers"] = stats.get("correct_answers", 0) + entry.get("correct", 0)
        stats["incorrect_answers"] = stats.get("incorrect_answers", 0) + entry.get("incorrect", 0)
        stats["unanswered"] = stats.get("unanswered", 0) + entry.get("unanswered", 0)
        stats["total_time_seconds"] = stats.get("total_time_seconds", 0) + entry.get("time_taken_seconds", 0)

        # High marks
        if entry.get("score", 0) > stats.get("best_score", 0):
            stats["best_score"] = entry.get("score", 0)
        if entry.get("percentage", 0.0) > stats.get("best_percentage", 0.0):
            stats["best_percentage"] = entry.get("percentage", 0.0)
        if entry.get("max_streak", 0) > stats.get("best_streak", 0):
            stats["best_streak"] = entry.get("max_streak", 0)

        # Category breakdown
        cat = entry.get("category", "General Knowledge")
        cat_counts = stats.setdefault("category_counts", {})
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

        self.save_data()

    def get_high_scores(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        mode: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve filtered high scores leaderboard."""
        scores = list(self.data.get("high_scores", []))
        if category and category not in ("All Categories", "Mixed"):
            scores = [s for s in scores if s.get("category") == category]
        if difficulty and difficulty != "Mixed":
            scores = [s for s in scores if s.get("difficulty") == difficulty]
        if mode and mode != "All Modes":
            scores = [s for s in scores if s.get("mode") == mode]

        return scores[:limit]

    def get_lifetime_stats(self) -> Dict[str, Any]:
        """Retrieve aggregated player statistics."""
        stats = self.data.get("statistics", dict(DEFAULT_DATA["statistics"]))
        total_answered = stats.get("total_questions_answered", 0)
        correct = stats.get("correct_answers", 0)
        
        # Calculate overall accuracy
        accuracy = round((correct / total_answered * 100), 1) if total_answered > 0 else 0.0
        
        # Average score
        total_quizzes = stats.get("total_quizzes", 0)
        avg_score = round(correct * 10 / total_quizzes, 1) if total_quizzes > 0 else 0.0

        favorite_category = self.get_favorite_category()

        return {
            "total_quizzes": total_quizzes,
            "total_questions_answered": total_answered,
            "correct_answers": correct,
            "incorrect_answers": stats.get("incorrect_answers", 0),
            "unanswered": stats.get("unanswered", 0),
            "overall_accuracy": accuracy,
            "best_score": stats.get("best_score", 0),
            "best_percentage": stats.get("best_percentage", 0.0),
            "best_streak": stats.get("best_streak", 0),
            "total_time_seconds": stats.get("total_time_seconds", 0),
            "avg_score": avg_score,
            "favorite_category": favorite_category
        }

    def get_favorite_category(self) -> str:
        """Determine most frequently played category with valid data."""
        cat_counts = self.data.get("statistics", {}).get("category_counts", {})
        if not cat_counts:
            return "None yet"
        favorite = max(cat_counts.items(), key=lambda item: item[1])
        return favorite[0] if favorite[1] > 0 else "None yet"

    def clear_high_scores(self) -> bool:
        """Clear all high scores."""
        self.data["high_scores"] = []
        return self.save_data()

    def reset_statistics(self) -> bool:
        """Reset lifetime statistics."""
        self.data["statistics"] = json.loads(json.dumps(DEFAULT_DATA["statistics"]))
        return self.save_data()
