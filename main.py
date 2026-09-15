"""
QuizMaster — General Knowledge Challenge
Main Application Entry Point

A modern, professional desktop quiz application built with Python and CustomTkinter.
Features multiple game modes, a per-question countdown timer, streak bonuses,
170+ validated questions across 12 categories, post-quiz answer reviews,
persistent high score leaderboards, and dark/light theme support.
"""

import sys
import os
from typing import Any, Dict, Optional

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from core.settings_manager import SettingsManager
from core.score_manager import ScoreManager
from core.question_manager import QuestionManager
from core.quiz_engine import QuizSession
from core.audio_manager import audio
from ui.theme import Theme

# UI Screens
from ui.splash import SplashScreen
from ui.home import HomeScreen
from ui.setup import SetupScreen
from ui.quiz import QuizScreen
from ui.results import ResultsScreen
from ui.review import ReviewScreen
from ui.highscores import HighScoresScreen
from ui.settings import SettingsScreen
from ui.about import AboutScreen


class QuizMasterApp(ctk.CTk):
    """Main window controller managing screen transitions, settings, and keybindings."""

    def __init__(self):
        super().__init__()

        # 1. Initialize Core Subsystems & Managers
        self.settings_mgr = SettingsManager()
        self.score_mgr = ScoreManager()
        self.question_mgr = QuestionManager()

        # Apply saved settings
        saved_theme = self.settings_mgr.get("theme", "Dark")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        sound_enabled = self.settings_mgr.get("sound_effects", True)
        audio.set_enabled(sound_enabled)

        scale_mode = self.settings_mgr.get("ui_scale", "Normal")
        if scale_mode == "Large":
            ctk.set_widget_scaling(1.1)
            ctk.set_window_scaling(1.1)

        # 2. Window Configuration
        self.title("QuizMaster — General Knowledge Challenge")
        self.geometry("1060x720")
        self.minsize(960, 650)
        self._center_window()

        # 3. View Management Container
        self.container = ctk.CTkFrame(self, fg_color=Theme.BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.current_screen: Optional[ctk.CTkFrame] = None
        self.last_quiz_summary: Optional[Dict[str, Any]] = None
        self.last_quiz_config: Optional[Dict[str, Any]] = None

        # 4. Global Keyboard Bindings
        self.bind("<Key>", self._on_global_key_press)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # 5. Start with Splash Screen
        self.show_splash()

    def _center_window(self):
        """Center the application window on screen."""
        self.update_idletasks()
        width = 1060
        height = 720
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _switch_screen(self, new_screen_class, *args, **kwargs):
        """Safely destroy current view and mount new screen."""
        if self.current_screen is not None:
            # If leaving an active screen with cancel/destroy cleanup
            if hasattr(self.current_screen, "cancel"):
                self.current_screen.cancel()
            self.current_screen.destroy()
            self.current_screen = None

        self.current_screen = new_screen_class(self.container, *args, **kwargs)
        self.current_screen.pack(fill="both", expand=True)

    # ---------------- Screen Navigations ----------------

    def show_splash(self):
        """Display splash screen with progress loader."""
        self._switch_screen(SplashScreen, on_finish=self.show_home)

    def show_home(self):
        """Display main dashboard."""
        self._switch_screen(
            HomeScreen,
            on_start_quiz=lambda: self.show_setup(),
            on_speed_challenge=lambda: self.show_setup(preset_mode="Speed Challenge"),
            on_practice_mode=lambda: self.show_setup(preset_mode="Practice Mode"),
            on_random_challenge=lambda: self.show_setup(preset_mode="Random Challenge"),
            on_view_highscores=self.show_highscores,
            on_view_settings=self.show_settings,
            on_view_about=self.show_about,
            get_stats_callback=self.score_mgr.get_lifetime_stats,
            get_player_name_callback=lambda: self.settings_mgr.get("player_name", "Player")
        )

    def show_setup(self, preset_mode: Optional[str] = None):
        """Display quiz configuration setup screen."""
        def _on_start_quiz_action(config: Dict[str, Any]):
            if preset_mode:
                config["mode"] = preset_mode
            self.start_quiz(config)

        self._switch_screen(
            SetupScreen,
            question_manager=self.question_mgr,
            on_start=_on_start_quiz_action,
            on_back=self.show_home,
            default_player_name=self.settings_mgr.get("player_name", "Player"),
            default_timer=self.settings_mgr.get("default_timer", 30),
            default_shuffle_q=self.settings_mgr.get("shuffle_questions", True),
            default_shuffle_a=self.settings_mgr.get("shuffle_answers", True)
        )

        if preset_mode and isinstance(self.current_screen, SetupScreen):
            self.current_screen.configure_preset(preset_mode)

    def start_quiz(self, config: Dict[str, Any]):
        """Filter questions and launch the active quiz gameplay screen."""
        self.last_quiz_config = config
        player_name = config.get("player_name", "Player")
        category = config.get("category", "All Categories")
        difficulty = config.get("difficulty", "Mixed")
        count = config.get("count", 10)
        timer = config.get("timer", 30)
        shuffle_q = config.get("shuffle_questions", True)
        shuffle_a = config.get("shuffle_answers", True)
        mode = config.get("mode", "Classic")

        # Save active player name in settings
        self.settings_mgr.set("player_name", player_name)

        # Prepare question batch
        questions, err = self.question_mgr.prepare_quiz_questions(
            category=category,
            difficulty=difficulty,
            count=count,
            shuffle_questions=shuffle_q,
            shuffle_answers=shuffle_a
        )

        if err or not questions:
            # In case of issue, show setup again
            self.show_setup()
            return

        session = QuizSession(
            questions=questions,
            player_name=player_name,
            mode=mode,
            category=category,
            difficulty=difficulty,
            timer_seconds=timer
        )

        self._switch_screen(
            QuizScreen,
            session=session,
            on_quiz_complete=self.show_results,
            on_quit_to_home=self.show_home
        )

    def show_results(self, summary: Dict[str, Any]):
        """Display quiz complete analytics and persist scores."""
        self.last_quiz_summary = summary

        # Record to high scores & stats database
        self.score_mgr.add_score({
            "player_name": summary.get("player_name", "Player"),
            "score": summary.get("score", 0),
            "percentage": summary.get("percentage", 0.0),
            "correct": summary.get("correct", 0),
            "incorrect": summary.get("incorrect", 0),
            "unanswered": summary.get("unanswered", 0),
            "total_questions": summary.get("total_questions", 0),
            "max_streak": summary.get("max_streak", 0),
            "category": summary.get("category", "General Knowledge"),
            "difficulty": summary.get("difficulty", "Mixed"),
            "mode": summary.get("mode", "Classic"),
            "time_taken_seconds": summary.get("time_taken_seconds", 0)
        })

        self._switch_screen(
            ResultsScreen,
            summary=summary,
            on_play_again=self._handle_play_again,
            on_review_answers=self.show_review,
            on_view_leaderboard=self.show_highscores,
            on_return_home=self.show_home
        )

    def _handle_play_again(self):
        if self.last_quiz_config:
            self.start_quiz(self.last_quiz_config)
        else:
            self.show_setup()

    def show_review(self):
        """Display question review screen."""
        history = self.last_quiz_summary.get("history", []) if self.last_quiz_summary else []
        self._switch_screen(
            ReviewScreen,
            history=history,
            on_back=lambda: self.show_results(self.last_quiz_summary) if self.last_quiz_summary else self.show_home()
        )

    def show_highscores(self):
        """Display Hall of Fame leaderboard."""
        self._switch_screen(
            HighScoresScreen,
            score_manager=self.score_mgr,
            on_back=self.show_home
        )

    def show_settings(self):
        """Display settings configuration screen."""
        self._switch_screen(
            SettingsScreen,
            settings_manager=self.settings_mgr,
            score_manager=self.score_mgr,
            on_back=self.show_home,
            on_theme_changed=self._apply_theme_change
        )

    def show_about(self):
        """Display about information screen."""
        self._switch_screen(AboutScreen, on_back=self.show_home)

    def _apply_theme_change(self, mode: str):
        """Change system appearance mode dynamically."""
        ctk.set_appearance_mode(mode)

    def _on_global_key_press(self, event):
        """Handle global keyboard shortcuts across screens."""
        key = event.keysym

        # If on quiz screen, forward all key events to QuizScreen
        if isinstance(self.current_screen, QuizScreen):
            self.current_screen.handle_key_press(key)
        elif key == "Escape":
            # Return to Home from any secondary screen except Splash
            if not isinstance(self.current_screen, (HomeScreen, SplashScreen)):
                self.show_home()

    def _on_window_close(self):
        """Clean shutdown handler."""
        if self.current_screen and hasattr(self.current_screen, "destroy"):
            self.current_screen.destroy()
        self.destroy()


def main():
    """Launch QuizMaster desktop application."""
    app = QuizMasterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
