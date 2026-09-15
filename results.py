"""
Results Screen for QuizMaster.
Displays comprehensive post-quiz performance analytics, rating badges, metric breakdown, and navigation.
"""

from typing import Callable, Dict, Any
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, StatCard, ModernButton, PillBadge


class ResultsScreen(ctk.CTkFrame):
    """Modern results summary dashboard with score visualizations and action links."""

    def __init__(
        self,
        master,
        summary: Dict[str, Any],
        on_play_again: Callable,
        on_review_answers: Callable,
        on_view_leaderboard: Callable,
        on_return_home: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.summary = summary
        self.on_play_again = on_play_again
        self.on_review_answers = on_review_answers
        self.on_view_leaderboard = on_view_leaderboard
        self.on_return_home = on_return_home

        self._build_ui()

    def _build_ui(self):
        # Scrollable container for responsive layout
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        # 1. Main Hero Score Banner Card
        hero_card = CardFrame(
            scroll,
            corner_radius=20,
            fg_color=Theme.PRIMARY,
            border_color=Theme.SECONDARY
        )
        hero_card.pack(fill="x", pady=(0, 20))

        hero_inner = ctk.CTkFrame(hero_card, fg_color="transparent")
        hero_inner.pack(fill="x", padx=28, pady=28)

        # Title
        ctk.CTkLabel(
            hero_inner,
            text="🎉 QUIZ COMPLETE!",
            font=(Theme.FONT_FAMILY, 14, "bold"),
            text_color=Theme.TEXT_ON_PRIMARY
        ).pack(pady=(0, 8))

        # Percentage Display
        pct = self.summary.get("percentage", 0.0)
        score_lbl = ctk.CTkLabel(
            hero_inner,
            text=f"{pct:.0f}%",
            font=(Theme.FONT_FAMILY, 54, "bold"),
            text_color=Theme.TEXT_ON_PRIMARY
        )
        score_lbl.pack(pady=(0, 4))

        # Rating Tier Badge
        rating = self.summary.get("rating", "Master 🏆")
        rating_pill = PillBadge(
            hero_inner,
            text=f"Rating: {rating}",
            font_size=13,
            fg_color=Theme.BG_SURFACE,
            text_color=Theme.TEXT_MAIN
        )
        rating_pill.pack(pady=(0, 8))

        # Message
        msg = self.summary.get("message", "Great performance!")
        msg_lbl = ctk.CTkLabel(
            hero_inner,
            text=msg,
            font=(Theme.FONT_FAMILY, 14),
            text_color=Theme.TEXT_ON_PRIMARY
        )
        msg_lbl.pack(pady=(0, 12))

        # Summary Sub-pill (Player, Mode, Points)
        score_pts = self.summary.get("score", 0)
        player = self.summary.get("player_name", "Player")
        mode = self.summary.get("mode", "Classic")
        info_pill = PillBadge(
            hero_inner,
            text=f"{player}  •  {score_pts} Total Points  •  {mode} Mode",
            font_size=11,
            fg_color=("#3730A3", "#312E81"),
            text_color=Theme.TEXT_ON_PRIMARY
        )
        info_pill.pack()

        # 2. Detailed Performance Metrics Grid
        metrics_label = ctk.CTkLabel(
            scroll,
            text="PERFORMANCE BREAKDOWN",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        metrics_label.pack(anchor="w", pady=(0, 10))

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for col in range(4):
            grid.columnconfigure(col, weight=1, uniform="metrics")

        # Metric 1: Correct
        correct_count = self.summary.get("correct", 0)
        total_q = self.summary.get("total_questions", 0)
        c_card = StatCard(grid, title="Correct", value=f"{correct_count} / {total_q}", icon="✓", accent_color=Theme.SUCCESS)
        c_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Metric 2: Incorrect
        inc_count = self.summary.get("incorrect", 0)
        i_card = StatCard(grid, title="Incorrect", value=str(inc_count), icon="✕", accent_color=Theme.ERROR)
        i_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Metric 3: Unanswered
        unans = self.summary.get("unanswered", 0)
        u_card = StatCard(grid, title="Unanswered", value=str(unans), icon="⏱", accent_color=Theme.WARNING)
        u_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Metric 4: Max Streak
        streak = self.summary.get("max_streak", 0)
        s_card = StatCard(grid, title="Best Streak", value=f"🔥 {streak}", icon="🔥", accent_color=Theme.WARNING)
        s_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Row 2 Metrics: Time, Accuracy, Avg Time, Category
        t_sec = self.summary.get("time_taken_seconds", 0)
        mins = t_sec // 60
        secs = t_sec % 60
        time_card = StatCard(grid, title="Total Time", value=f"{mins:02d}:{secs:02d}", icon="⌛")
        time_card.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        avg_t = self.summary.get("avg_time_per_question", 0.0)
        avg_card = StatCard(grid, title="Avg Pace", value=f"{avg_t}s / Q", icon="⚡")
        avg_card.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        cat_val = self.summary.get("category", "General")
        cat_card = StatCard(grid, title="Category", value=str(cat_val), icon="📚")
        cat_card.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        diff_val = self.summary.get("difficulty", "Mixed")
        diff_card = StatCard(grid, title="Difficulty", value=str(diff_val), icon="🎯")
        diff_card.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # 3. Action Buttons Card
        action_card = CardFrame(self, corner_radius=16)
        action_card.pack(fill="x", padx=24, pady=(0, 16))

        action_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        action_inner.pack(fill="x", padx=20, pady=14)

        play_again_btn = ModernButton(
            action_inner,
            text="🔄  Play Again",
            command=self.on_play_again,
            variant="primary",
            height=44
        )
        play_again_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        review_btn = ModernButton(
            action_inner,
            text="📊  Review Answers",
            command=self.on_review_answers,
            variant="surface",
            height=44
        )
        review_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        lead_btn = ModernButton(
            action_inner,
            text="🏆  Leaderboard",
            command=self.on_view_leaderboard,
            variant="surface",
            height=44
        )
        lead_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        home_btn = ModernButton(
            action_inner,
            text="🏠  Home",
            command=self.on_return_home,
            variant="surface",
            height=44
        )
        home_btn.pack(side="left", fill="x", expand=True)
