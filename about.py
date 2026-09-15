"""
About Screen for QuizMaster.
Displays application info, version numbers, feature highlights, and system details.
"""

import sys
from typing import Callable
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, PillBadge, HeaderBar


class AboutScreen(ctk.CTkFrame):
    """Informational screen showcasing app features and technical specifications."""

    def __init__(self, master, on_back: Callable, **kwargs):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        # Header
        header = HeaderBar(
            self,
            title="ℹ About QuizMaster",
            subtitle="Application information, specifications, and architecture",
            on_back=self.on_back
        )
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 1. Branding Hero Card
        hero_card = CardFrame(scroll, corner_radius=18, fg_color=Theme.BG_CARD)
        hero_card.pack(fill="x", pady=(0, 16))

        h_inner = ctk.CTkFrame(hero_card, fg_color="transparent")
        h_inner.pack(fill="x", padx=24, pady=20)

        top_row = ctk.CTkFrame(h_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        logo_lbl = ctk.CTkLabel(top_row, text="🧠", font=(Theme.FONT_FAMILY, 36))
        logo_lbl.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(top_row, fg_color="transparent")
        title_col.pack(side="left")

        ctk.CTkLabel(
            title_col,
            text="QuizMaster",
            font=(Theme.FONT_FAMILY, 24, "bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="General Knowledge Challenge • Version 1.0.0",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.PRIMARY
        ).pack(anchor="w")

        v_pill = PillBadge(top_row, text="100% Offline & Private", icon="🛡️", font_size=11, fg_color=Theme.BG_SURFACE)
        v_pill.pack(side="right")

        desc_text = (
            "QuizMaster is a professional, modern desktop trivia application developed in Python. "
            "Engineered with a high-contrast aesthetic, fluid interactions, responsive components, "
            "and an extensive bank of 170+ meticulously curated questions across 12 diverse knowledge disciplines."
        )
        ctk.CTkLabel(
            h_inner,
            text=desc_text,
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_MUTED,
            wraplength=800,
            justify="left"
        ).pack(anchor="w", pady=(0, 4))

        # 2. Key Features Card
        feat_card = CardFrame(scroll, corner_radius=18)
        feat_card.pack(fill="x", pady=(0, 16))

        f_inner = ctk.CTkFrame(feat_card, fg_color="transparent")
        f_inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            f_inner,
            text="⭐ APPLICATION HIGHLIGHTS",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 12))

        features = [
            ("📚", "170+ Verified Trivia Questions", "Extensive database spanning Science, History, Geography, Space, Tech, and more."),
            ("🎮", "Multiple Game Modes", "Classic Custom Quiz, 15-second Speed Challenge, Untimed Practice Mode, and Random Challenge."),
            ("🔥", "Streak Bonuses & Multipliers", "Dynamic scoring with Easy (1x), Medium (1.5x), Hard (2x) and consecutive streak bonuses."),
            ("⏱", "Live Countdown Timer", "Dynamic color transitions (Indigo → Amber → Crimson) with audio cues and auto-submission."),
            ("📊", "Deep Answer Review", "Full post-quiz review showing your selections, correct answers, and thorough explanations."),
            ("🏆", "Persistent Hall of Fame", "Local leaderboards tracking rankings, accuracies, and lifetime statistics."),
            ("⌨️", "Complete Keyboard Support", "Answer instantly with [1-4] or [A-D], advance with [Enter], and exit with [Esc]."),
            ("🎨", "Modern Dual Theme System", "Switch freely between sleek Dark Mode, crisp Light Mode, and System Theme.")
        ]

        f_grid = ctk.CTkFrame(f_inner, fg_color="transparent")
        f_grid.pack(fill="x")
        f_grid.columnconfigure(0, weight=1)
        f_grid.columnconfigure(1, weight=1)

        for i, (icon, title, desc) in enumerate(features):
            r = i // 2
            c = i % 2
            item_frame = ctk.CTkFrame(f_grid, fg_color="transparent")
            item_frame.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            item_top = ctk.CTkFrame(item_frame, fg_color="transparent")
            item_top.pack(anchor="w")

            ctk.CTkLabel(item_top, text=icon, font=(Theme.FONT_FAMILY, 14)).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(item_top, text=title, font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(side="left")

            ctk.CTkLabel(item_frame, text=desc, font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED, wraplength=380, justify="left").pack(anchor="w", padx=(20, 0))

        # 3. Technical Specifications Card
        tech_card = CardFrame(scroll, corner_radius=18)
        tech_card.pack(fill="x")

        t_inner = ctk.CTkFrame(tech_card, fg_color="transparent")
        t_inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            t_inner,
            text="⚙ TECHNICAL ENVIRONMENT",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        py_ver = sys.version.split()[0]
        specs = [
            ("Python Version", f"Python {py_ver}"),
            ("GUI Engine", "CustomTkinter 6.0+"),
            ("Audio Synthesis", "Native Asynchronous Audio Buffer"),
            ("Data Layer", "Pure Local JSON Storage")
        ]

        specs_row = ctk.CTkFrame(t_inner, fg_color="transparent")
        specs_row.pack(fill="x")
        for idx, (lbl, val) in enumerate(specs):
            specs_row.columnconfigure(idx, weight=1)
            cell = ctk.CTkFrame(specs_row, fg_color=Theme.BG_SURFACE, corner_radius=10)
            cell.grid(row=0, column=idx, padx=4, sticky="nsew")
            c_inner = ctk.CTkFrame(cell, fg_color="transparent")
            c_inner.pack(padx=12, pady=10)
            ctk.CTkLabel(c_inner, text=lbl.upper(), font=(Theme.FONT_FAMILY, 9, "bold"), text_color=Theme.TEXT_MUTED).pack()
            ctk.CTkLabel(c_inner, text=val, font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_MAIN).pack(pady=(2, 0))
