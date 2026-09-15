"""
Quiz Setup Screen for QuizMaster.
Allows configuring player name, category, difficulty, question count, timer, and shuffle settings.
"""

from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, ModernButton, PillBadge, HeaderBar
from core.question_manager import QuestionManager


class SetupScreen(ctk.CTkFrame):
    """Configuration screen for customizing a quiz challenge session."""

    def __init__(
        self,
        master,
        question_manager: QuestionManager,
        on_start: Callable,
        on_back: Callable,
        default_player_name: str = "Player",
        default_timer: int = 30,
        default_shuffle_q: bool = True,
        default_shuffle_a: bool = True,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.qm = question_manager
        self.on_start = on_start
        self.on_back = on_back

        # Configuration variables
        self.var_player = ctk.StringVar(value=default_player_name)
        self.var_category = ctk.StringVar(value="All Categories")
        self.var_difficulty = ctk.StringVar(value="Mixed")
        self.var_count = ctk.IntVar(value=10)
        self.var_timer = ctk.IntVar(value=default_timer)
        self.var_shuffle_q = ctk.BooleanVar(value=default_shuffle_q)
        self.var_shuffle_a = ctk.BooleanVar(value=default_shuffle_a)

        self._build_ui()
        self._update_availability()

    def _build_ui(self):
        # Header
        header = HeaderBar(
            self,
            title="Quiz Setup & Configuration",
            subtitle="Tailor your challenge parameters and question filters",
            on_back=self.on_back
        )
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Scrollable configuration area
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 1. Player Name & Game Mode Row
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 14))
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=1)

        # Player Name Card
        p_card = CardFrame(row1)
        p_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        p_inner = ctk.CTkFrame(p_card, fg_color="transparent")
        p_inner.pack(fill="both", expand=True, padx=16, pady=14)

        ctk.CTkLabel(
            p_inner,
            text="👤 PLAYER NAME",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 6))

        self.player_entry = ctk.CTkEntry(
            p_inner,
            textvariable=self.var_player,
            font=(Theme.FONT_FAMILY, 13),
            height=38,
            corner_radius=10,
            placeholder_text="Enter your name"
        )
        self.player_entry.pack(fill="x")

        # Question Availability Card
        self.avail_card = CardFrame(row1)
        self.avail_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        a_inner = ctk.CTkFrame(self.avail_card, fg_color="transparent")
        a_inner.pack(fill="both", expand=True, padx=16, pady=14)

        ctk.CTkLabel(
            a_inner,
            text="📊 AVAILABLE QUESTIONS",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.avail_lbl = ctk.CTkLabel(
            a_inner,
            text="Loading...",
            font=(Theme.FONT_FAMILY, 18, "bold"),
            text_color=Theme.PRIMARY
        )
        self.avail_lbl.pack(anchor="w")

        # 2. Category Selection Card
        cat_card = CardFrame(scroll)
        cat_card.pack(fill="x", pady=(0, 14))
        cat_inner = ctk.CTkFrame(cat_card, fg_color="transparent")
        cat_inner.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(
            cat_inner,
            text="📚 SELECT CATEGORY",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        categories = ["All Categories"] + self.qm.get_all_categories()
        self.cat_optionmenu = ctk.CTkOptionMenu(
            cat_inner,
            values=categories,
            variable=self.var_category,
            command=lambda _: self._update_availability(),
            font=(Theme.FONT_FAMILY, 13, "bold"),
            height=40,
            corner_radius=10,
            fg_color=Theme.BG_SURFACE,
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_HOVER,
            dropdown_font=(Theme.FONT_FAMILY, 12)
        )
        self.cat_optionmenu.pack(fill="x")

        # 3. Difficulty Selection Card
        diff_card = CardFrame(scroll)
        diff_card.pack(fill="x", pady=(0, 14))
        diff_inner = ctk.CTkFrame(diff_card, fg_color="transparent")
        diff_inner.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(
            diff_inner,
            text="🎯 SELECT DIFFICULTY",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        self.diff_seg = ctk.CTkSegmentedButton(
            diff_inner,
            values=["Mixed", "Easy", "Medium", "Hard"],
            variable=self.var_difficulty,
            command=lambda _: self._update_availability(),
            font=(Theme.FONT_FAMILY, 13, "bold"),
            height=40,
            corner_radius=10,
            selected_color=Theme.PRIMARY[1],
            selected_hover_color=Theme.PRIMARY_HOVER[1]
        )
        self.diff_seg.pack(fill="x")

        # 4. Number of Questions Card
        count_card = CardFrame(scroll)
        count_card.pack(fill="x", pady=(0, 14))
        count_inner = ctk.CTkFrame(count_card, fg_color="transparent")
        count_inner.pack(fill="x", padx=18, pady=16)

        count_top = ctk.CTkFrame(count_inner, fg_color="transparent")
        count_top.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            count_top,
            text="🔢 NUMBER OF QUESTIONS",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        self.count_display_lbl = ctk.CTkLabel(
            count_top,
            text=f"{self.var_count.get()} Questions",
            font=(Theme.FONT_FAMILY, 13, "bold"),
            text_color=Theme.PRIMARY
        )
        self.count_display_lbl.pack(side="right")

        # Preset buttons row
        preset_row = ctk.CTkFrame(count_inner, fg_color="transparent")
        preset_row.pack(fill="x", pady=(0, 10))
        for cnt in [5, 10, 15, 20, 30, 50]:
            btn = ModernButton(
                preset_row,
                text=str(cnt),
                command=lambda c=cnt: self._set_count(c),
                variant="surface",
                height=32,
                corner_radius=8
            )
            btn.pack(side="left", fill="x", expand=True, padx=2)

        # Slider for fine adjustments
        self.count_slider = ctk.CTkSlider(
            count_inner,
            from_=5,
            to=50,
            number_of_steps=45,
            variable=self.var_count,
            command=self._on_slider_change,
            progress_color=Theme.PRIMARY,
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_HOVER
        )
        self.count_slider.pack(fill="x", pady=(6, 0))

        # 5. Timer & Shuffling Row
        row5 = ctk.CTkFrame(scroll, fg_color="transparent")
        row5.pack(fill="x", pady=(0, 16))
        row5.columnconfigure(0, weight=1)
        row5.columnconfigure(1, weight=1)

        # Timer Card
        timer_card = CardFrame(row5)
        timer_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        t_inner = ctk.CTkFrame(timer_card, fg_color="transparent")
        t_inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            t_inner,
            text="⏱ TIMER PER QUESTION",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        timer_seg = ctk.CTkSegmentedButton(
            t_inner,
            values=["No Timer", "15s", "30s", "60s"],
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=36,
            corner_radius=8,
            command=self._on_timer_change
        )
        # Set initial timer segment
        init_t_val = "No Timer" if self.var_timer.get() == 0 else f"{self.var_timer.get()}s"
        timer_seg.set(init_t_val)
        timer_seg.pack(fill="x")

        # Shuffle Options Card
        shuf_card = CardFrame(row5)
        shuf_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        s_inner = ctk.CTkFrame(shuf_card, fg_color="transparent")
        s_inner.pack(fill="both", expand=True, padx=16, pady=14)

        ctk.CTkLabel(
            s_inner,
            text="🔀 RANDOMIZATION",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 8))

        sw1 = ctk.CTkSwitch(
            s_inner,
            text="Shuffle Questions",
            variable=self.var_shuffle_q,
            font=(Theme.FONT_FAMILY, 12),
            progress_color=Theme.PRIMARY
        )
        sw1.pack(anchor="w", pady=2)

        sw2 = ctk.CTkSwitch(
            s_inner,
            text="Shuffle Answer Options",
            variable=self.var_shuffle_a,
            font=(Theme.FONT_FAMILY, 12),
            progress_color=Theme.PRIMARY
        )
        sw2.pack(anchor="w", pady=2)

        # 6. Error / Warning Banner Frame
        self.warning_frame = CardFrame(
            scroll,
            corner_radius=12,
            fg_color=Theme.ERROR_BG,
            border_color=Theme.ERROR
        )
        w_inner = ctk.CTkFrame(self.warning_frame, fg_color="transparent")
        w_inner.pack(fill="x", padx=16, pady=12)

        self.warning_lbl = ctk.CTkLabel(
            w_inner,
            text="",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.ERROR,
            wraplength=700,
            justify="left"
        )
        self.warning_lbl.pack(side="left", fill="x", expand=True)

        # 7. Start Action Button Card
        action_card = CardFrame(self, corner_radius=16)
        action_card.pack(fill="x", padx=24, pady=(0, 16))

        action_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        action_inner.pack(fill="x", padx=20, pady=12)

        self.start_btn = ModernButton(
            action_inner,
            text="🚀  START QUIZ CHALLENGE",
            command=self._handle_start_quiz,
            variant="primary",
            height=48,
            shortcut="Enter"
        )
        self.start_btn.pack(fill="x")

    def _set_count(self, count: int):
        self.var_count.set(count)
        self.count_display_lbl.configure(text=f"{count} Questions")
        self._update_availability()

    def _on_slider_change(self, value):
        val = int(value)
        self.count_display_lbl.configure(text=f"{val} Questions")
        self._update_availability()

    def _on_timer_change(self, value: str):
        if value == "No Timer":
            self.var_timer.set(0)
        elif value == "15s":
            self.var_timer.set(15)
        elif value == "30s":
            self.var_timer.set(30)
        elif value == "60s":
            self.var_timer.set(60)

    def _update_availability(self):
        cat = self.var_category.get()
        diff = self.var_difficulty.get()
        req_count = self.var_count.get()

        available = self.qm.get_available_count(cat, diff)
        self.avail_lbl.configure(text=f"{available} Matching Trivia Items")

        if req_count > available:
            self.warning_lbl.configure(
                text=f"⚠️ Requested {req_count} questions, but only {available} exist for selected filters. "
                     f"Please lower question count or select 'All Categories' / 'Mixed' difficulty."
            )
            self.warning_frame.pack(fill="x", pady=(0, 14))
            self.start_btn.configure(state="disabled")
        else:
            self.warning_frame.pack_forget()
            self.start_btn.configure(state="normal")

    def _handle_start_quiz(self):
        player = self.var_player.get().strip() or "Player"
        config = {
            "player_name": player,
            "mode": "Classic",
            "category": self.var_category.get(),
            "difficulty": self.var_difficulty.get(),
            "count": self.var_count.get(),
            "timer": self.var_timer.get(),
            "shuffle_questions": self.var_shuffle_q.get(),
            "shuffle_answers": self.var_shuffle_a.get()
        }
        self.on_start(config)

    def configure_preset(self, mode: str):
        """Configure setup preset for quick game modes."""
        if mode == "Speed Challenge":
            self.var_category.set("All Categories")
            self.var_difficulty.set("Mixed")
            self.var_count.set(15)
            self.var_timer.set(15)
        elif mode == "Practice Mode":
            self.var_category.set("All Categories")
            self.var_difficulty.set("Mixed")
            self.var_count.set(10)
            self.var_timer.set(0)
        elif mode == "Random Challenge":
            self.var_category.set("All Categories")
            self.var_difficulty.set("Mixed")
            self.var_count.set(15)
            self.var_timer.set(30)

        self.count_display_lbl.configure(text=f"{self.var_count.get()} Questions")
        self._update_availability()
