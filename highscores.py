"""
High Scores Leaderboard Screen for QuizMaster.
Displays top ranking quiz runs, medals, score filters, and score database management.
"""

from typing import Callable, Dict, List, Any
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, ModernButton, PillBadge, HeaderBar, ConfirmationModal
from core.score_manager import ScoreManager


class HighScoresScreen(ctk.CTkFrame):
    """Modern leaderboard screen with podiums and customizable filters."""

    def __init__(
        self,
        master,
        score_manager: ScoreManager,
        on_back: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.sm = score_manager
        self.on_back = on_back
        self.filter_mode = "All Modes"

        self._build_ui()
        self._refresh_leaderboard()

    def _build_ui(self):
        # Header
        header = HeaderBar(
            self,
            title="🏆 Hall of Fame & High Scores",
            subtitle="Top trivia performances and leaderboard rankings",
            on_back=self.on_back
        )
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Filter & Action Toolbar
        toolbar = CardFrame(self, corner_radius=14)
        toolbar.pack(fill="x", padx=24, pady=(0, 14))

        t_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        t_inner.pack(fill="x", padx=16, pady=10)

        # Mode Filter Segment
        self.mode_seg = ctk.CTkSegmentedButton(
            t_inner,
            values=["All Modes", "Classic", "Speed Challenge", "Random Challenge"],
            command=self._on_mode_filter,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=36
        )
        self.mode_seg.set("All Modes")
        self.mode_seg.pack(side="left")

        # Clear Scores Button
        clear_btn = ModernButton(
            t_inner,
            text="Clear High Scores",
            command=self._confirm_clear,
            variant="surface",
            height=36
        )
        clear_btn.pack(side="right")

        # Scrollable Leaderboard List
        self.scroll_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def _on_mode_filter(self, value: str):
        self.filter_mode = value
        self._refresh_leaderboard()

    def _refresh_leaderboard(self):
        # Clear list
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        scores = self.sm.get_high_scores(mode=self.filter_mode)

        if not scores:
            empty_card = CardFrame(self.scroll_list, corner_radius=16)
            empty_card.pack(fill="x", pady=20)
            ctk.CTkLabel(
                empty_card,
                text="🏆 No high scores recorded yet for this category.\nComplete a quiz challenge to claim the top spot!",
                font=(Theme.FONT_FAMILY, 14),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            ).pack(padx=20, pady=40)
            return

        # Podium Row for Top 3 (if at least 1 exists)
        if len(scores) >= 1:
            podium_frame = ctk.CTkFrame(self.scroll_list, fg_color="transparent")
            podium_frame.pack(fill="x", pady=(0, 16))

            num_top = min(3, len(scores))
            for i in range(num_top):
                podium_frame.columnconfigure(i, weight=1, uniform="podium")
                self._create_podium_card(podium_frame, i, scores[i])

        # Table Header
        tbl_header = ctk.CTkFrame(self.scroll_list, fg_color="transparent", height=30)
        tbl_header.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(tbl_header, text="RANK", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, width=60, anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_header, text="PLAYER", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, width=160, anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_header, text="SCORE", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_header, text="ACCURACY", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_header, text="CATEGORY / DIFFICULTY", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, width=200, anchor="w").pack(side="left")
        ctk.CTkLabel(tbl_header, text="DATE", font=(Theme.FONT_FAMILY, 10, "bold"), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right")

        # Table Rows for all scores
        for idx, entry in enumerate(scores, start=1):
            self._create_table_row(idx, entry)

    def _create_podium_card(self, parent, rank_idx: int, entry: Dict[str, Any]):
        medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]
        border_colors = [
            ("#EAB308", "#FACC15"),  # Gold
            ("#94A3B8", "#CBD5E1"),  # Silver
            ("#B45309", "#D97706")   # Bronze
        ]

        card = CardFrame(
            parent,
            corner_radius=16,
            border_width=2,
            border_color=border_colors[rank_idx]
        )
        card.grid(row=0, column=rank_idx, padx=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner,
            text=medals[rank_idx],
            font=(Theme.FONT_FAMILY, 13, "bold"),
            text_color=border_colors[rank_idx]
        ).pack(anchor="w")

        player = entry.get("player_name", "Player")
        ctk.CTkLabel(
            inner,
            text=player,
            font=(Theme.FONT_FAMILY, 18, "bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", pady=(4, 2))

        score = entry.get("score", 0)
        pct = entry.get("percentage", 0.0)
        ctk.CTkLabel(
            inner,
            text=f"{score} pts  ({pct:.0f}%)",
            font=(Theme.FONT_FAMILY, 13, "bold"),
            text_color=Theme.PRIMARY
        ).pack(anchor="w")

        cat = entry.get("category", "General")
        ctk.CTkLabel(
            inner,
            text=f"{cat} • {entry.get('mode', 'Classic')}",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(4, 0))

    def _create_table_row(self, rank: int, entry: Dict[str, Any]):
        row_card = CardFrame(self.scroll_list, corner_radius=12)
        row_card.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(row_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        # Rank
        rank_str = f"#{rank}"
        if rank == 1:
            rank_str = "🥇 1"
        elif rank == 2:
            rank_str = "🥈 2"
        elif rank == 3:
            rank_str = "🥉 3"

        ctk.CTkLabel(inner, text=rank_str, font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.PRIMARY, width=60, anchor="w").pack(side="left")

        # Player
        player = entry.get("player_name", "Player")
        ctk.CTkLabel(inner, text=player, font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN, width=160, anchor="w").pack(side="left")

        # Score
        score = str(entry.get("score", 0))
        ctk.CTkLabel(inner, text=f"{score} pts", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.SUCCESS, width=100, anchor="w").pack(side="left")

        # Accuracy
        pct = entry.get("percentage", 0.0)
        ctk.CTkLabel(inner, text=f"{pct:.0f}%", font=(Theme.FONT_FAMILY, 13), text_color=Theme.TEXT_MAIN, width=100, anchor="w").pack(side="left")

        # Category & Diff
        cat = entry.get("category", "General")
        diff = entry.get("difficulty", "Mixed")
        ctk.CTkLabel(inner, text=f"{cat} ({diff})", font=(Theme.FONT_FAMILY, 12), text_color=Theme.TEXT_MUTED, width=200, anchor="w").pack(side="left")

        # Date
        date_str = entry.get("date", "")
        ctk.CTkLabel(inner, text=date_str, font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(side="right")

    def _confirm_clear(self):
        ConfirmationModal(
            self.winfo_toplevel(),
            title="Clear All High Scores?",
            message="This action will permanently remove all leaderboard high scores. Are you sure you want to proceed?",
            on_confirm=self._do_clear_scores,
            confirm_text="Clear All",
            is_danger=True
        )

    def _do_clear_scores(self):
        self.sm.clear_high_scores()
        self._refresh_leaderboard()
