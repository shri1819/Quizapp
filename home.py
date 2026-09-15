"""
Home Dashboard for QuizMaster.
Displays prominent Start Quiz actions, game modes, lifetime statistics, and navigation.
"""

from typing import Callable, Dict, Any
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, StatCard, ModernButton, PillBadge


class HomeScreen(ctk.CTkFrame):
    """Modern dashboard screen presenting stats, game modes, and main actions."""

    def __init__(
        self,
        master,
        on_start_quiz: Callable,
        on_speed_challenge: Callable,
        on_practice_mode: Callable,
        on_random_challenge: Callable,
        on_view_highscores: Callable,
        on_view_settings: Callable,
        on_view_about: Callable,
        get_stats_callback: Callable,
        get_player_name_callback: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.on_start_quiz = on_start_quiz
        self.on_speed_challenge = on_speed_challenge
        self.on_practice_mode = on_practice_mode
        self.on_random_challenge = on_random_challenge
        self.on_view_highscores = on_view_highscores
        self.on_view_settings = on_view_settings
        self.on_view_about = on_view_about
        self.get_stats = get_stats_callback
        self.get_player_name = get_player_name_callback

        self._build_ui()

    def _build_ui(self):
        # Scrollable container for perfect responsive scaling
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=24, pady=20)

        # 1. Header Section
        header_card = CardFrame(self.scroll_container, corner_radius=16)
        header_card.pack(fill="x", pady=(0, 20))

        header_inner = ctk.CTkFrame(header_card, fg_color="transparent")
        header_inner.pack(fill="x", padx=24, pady=20)

        left_header = ctk.CTkFrame(header_inner, fg_color="transparent")
        left_header.pack(side="left")

        title_row = ctk.CTkFrame(left_header, fg_color="transparent")
        title_row.pack(anchor="w")

        emblem = ctk.CTkLabel(title_row, text="🧠", font=(Theme.FONT_FAMILY, 28))
        emblem.pack(side="left", padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            title_row,
            text="QuizMaster",
            font=(Theme.FONT_FAMILY, 28, "bold"),
            text_color=Theme.TEXT_MAIN
        )
        title_lbl.pack(side="left")

        sub_lbl = ctk.CTkLabel(
            left_header,
            text="General Knowledge Challenge • Test your trivia mastery across 12 categories",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(4, 0))

        # Right Player Badge
        right_header = ctk.CTkFrame(header_inner, fg_color="transparent")
        right_header.pack(side="right")

        player_name = self.get_player_name()
        self.player_badge = PillBadge(
            right_header,
            text=player_name,
            icon="👤",
            fg_color=Theme.PRIMARY,
            text_color=Theme.TEXT_ON_PRIMARY
        )
        self.player_badge.pack()

        # 2. Main Featured Action Card
        featured_card = CardFrame(
            self.scroll_container,
            corner_radius=18,
            fg_color=Theme.PRIMARY,
            border_color=Theme.SECONDARY
        )
        featured_card.pack(fill="x", pady=(0, 20))

        feat_inner = ctk.CTkFrame(featured_card, fg_color="transparent")
        feat_inner.pack(fill="x", padx=28, pady=24)

        feat_text = ctk.CTkFrame(feat_inner, fg_color="transparent")
        feat_text.pack(side="left", fill="both", expand=True)

        feat_title = ctk.CTkLabel(
            feat_text,
            text="Ready for the Challenge?",
            font=(Theme.FONT_FAMILY, 22, "bold"),
            text_color=Theme.TEXT_ON_PRIMARY
        )
        feat_title.pack(anchor="w")

        feat_desc = ctk.CTkLabel(
            feat_text,
            text="Customize categories, question count, difficulty, and timer to start your quiz session.",
            font=(Theme.FONT_FAMILY, 13),
            text_color=("#E0E7FF", "#E0E7FF")
        )
        feat_desc.pack(anchor="w", pady=(4, 0))

        start_btn = ModernButton(
            feat_inner,
            text="🎯  START CUSTOM QUIZ",
            command=self.on_start_quiz,
            variant="surface",
            height=50,
            width=220,
            corner_radius=14
        )
        start_btn.pack(side="right", padx=(20, 0))

        # 3. Quick Game Modes Grid
        modes_label = ctk.CTkLabel(
            self.scroll_container,
            text="GAME MODES",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        modes_label.pack(anchor="w", pady=(0, 10))

        modes_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        modes_grid.pack(fill="x", pady=(0, 20))
        modes_grid.columnconfigure(0, weight=1, uniform="modes")
        modes_grid.columnconfigure(1, weight=1, uniform="modes")
        modes_grid.columnconfigure(2, weight=1, uniform="modes")

        # Mode 1: Speed Challenge
        self._create_mode_tile(
            modes_grid,
            col=0,
            icon="⚡",
            title="Speed Challenge",
            desc="15 seconds per question with speed bonus multipliers.",
            badge="Fast & Intense",
            command=self.on_speed_challenge
        )

        # Mode 2: Practice Mode
        self._create_mode_tile(
            modes_grid,
            col=1,
            icon="📖",
            title="Practice Mode",
            desc="No timer. Learn with instant in-depth explanations.",
            badge="Untimed",
            command=self.on_practice_mode
        )

        # Mode 3: Random Challenge
        self._create_mode_tile(
            modes_grid,
            col=2,
            icon="🎲",
            title="Random Challenge",
            desc="15 randomized questions across all 12 categories.",
            badge="Mixed Trivia",
            command=self.on_random_challenge
        )

        # 4. Lifetime Statistics Dashboard
        stats_label = ctk.CTkLabel(
            self.scroll_container,
            text="YOUR LIFETIME PERFORMANCE",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        stats_label.pack(anchor="w", pady=(0, 10))

        self.stats_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=(0, 24))
        for col in range(5):
            self.stats_grid.columnconfigure(col, weight=1, uniform="stats")

        # Create StatCards
        stats = self.get_stats()
        self.card_quizzes = StatCard(self.stats_grid, title="Quizzes", value=str(stats.get("total_quizzes", 0)), icon="📋")
        self.card_quizzes.grid(row=0, column=0, padx=5, sticky="ew")

        self.card_questions = StatCard(self.stats_grid, title="Answered", value=str(stats.get("total_questions_answered", 0)), icon="❓")
        self.card_questions.grid(row=0, column=1, padx=5, sticky="ew")

        self.card_accuracy = StatCard(self.stats_grid, title="Accuracy", value=f"{stats.get('overall_accuracy', 0.0)}%", icon="🎯", accent_color=Theme.SUCCESS)
        self.card_accuracy.grid(row=0, column=2, padx=5, sticky="ew")

        self.card_streak = StatCard(self.stats_grid, title="Best Streak", value=f"🔥 {stats.get('best_streak', 0)}", icon="🔥", accent_color=Theme.WARNING)
        self.card_streak.grid(row=0, column=3, padx=5, sticky="ew")

        self.card_fav = StatCard(self.stats_grid, title="Favorite Topic", value=str(stats.get("favorite_category", "None")), icon="⭐")
        self.card_fav.grid(row=0, column=4, padx=5, sticky="ew")

        # 5. Bottom Navigation Toolbar
        nav_card = CardFrame(self.scroll_container, corner_radius=14)
        nav_card.pack(fill="x", pady=(0, 10))

        nav_inner = ctk.CTkFrame(nav_card, fg_color="transparent")
        nav_inner.pack(fill="x", padx=16, pady=12)

        high_score_btn = ModernButton(
            nav_inner,
            text="🏆  Leaderboard & High Scores",
            command=self.on_view_highscores,
            variant="surface",
            height=40
        )
        high_score_btn.pack(side="left", padx=(0, 10))

        settings_btn = ModernButton(
            nav_inner,
            text="⚙  Settings",
            command=self.on_view_settings,
            variant="surface",
            height=40
        )
        settings_btn.pack(side="left", padx=(0, 10))

        about_btn = ModernButton(
            nav_inner,
            text="ℹ  About QuizMaster",
            command=self.on_view_about,
            variant="surface",
            height=40
        )
        about_btn.pack(side="right")

    def _create_mode_tile(self, parent, col: int, icon: str, title: str, desc: str, badge: str, command: Callable):
        card = CardFrame(parent, corner_radius=16)
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))

        icon_lbl = ctk.CTkLabel(top, text=icon, font=(Theme.FONT_FAMILY, 24))
        icon_lbl.pack(side="left")

        badge_pill = PillBadge(top, text=badge, font_size=10, fg_color=Theme.BG_SURFACE)
        badge_pill.pack(side="right")

        t_lbl = ctk.CTkLabel(
            inner,
            text=title,
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_MAIN
        )
        t_lbl.pack(anchor="w", pady=(0, 4))

        d_lbl = ctk.CTkLabel(
            inner,
            text=desc,
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_MUTED,
            wraplength=220,
            justify="left"
        )
        d_lbl.pack(anchor="w", pady=(0, 14))

        play_btn = ModernButton(
            inner,
            text="Play Mode →",
            command=command,
            variant="surface",
            height=36
        )
        play_btn.pack(fill="x")

    def refresh_data(self):
        """Update live statistics and player name from manager."""
        stats = self.get_stats()
        self.card_quizzes.update_value(str(stats.get("total_quizzes", 0)))
        self.card_questions.update_value(str(stats.get("total_questions_answered", 0)))
        self.card_accuracy.update_value(f"{stats.get('overall_accuracy', 0.0)}%")
        self.card_streak.update_value(f"🔥 {stats.get('best_streak', 0)}")
        self.card_fav.update_value(str(stats.get("favorite_category", "None")))

        player_name = self.get_player_name()
        self.player_badge.set_text(player_name, icon="👤")
