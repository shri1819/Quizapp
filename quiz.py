"""
Quiz Gameplay Screen for QuizMaster.
Features live countdown timer, 4 large responsive answer cards, keyboard shortcuts,
streak bonuses, instant feedback with explanations, and error-proof timer lifecycles.
"""

from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, ModernButton, PillBadge, ConfirmationModal
from core.quiz_engine import QuizSession
from core.audio_manager import audio


class QuizScreen(ctk.CTkFrame):
    """Main interactive trivia quiz screen."""

    def __init__(
        self,
        master,
        session: QuizSession,
        on_quiz_complete: Callable,
        on_quit_to_home: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.session = session
        self.on_quiz_complete = on_quiz_complete
        self.on_quit_to_home = on_quit_to_home

        # Timer state
        self.time_left = self.session.timer_seconds
        self.timer_running = False
        self._timer_after_id: Optional[str] = None

        # Question interaction state
        self.answered = False
        self.option_buttons: List[ctk.CTkButton] = []

        self._build_ui()
        self._load_current_question()

    def _build_ui(self):
        # 1. Top Header Bar
        self.top_header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        self.top_header.pack(fill="x", padx=24, pady=(16, 8))

        # Row 1: Badges, Score, Streak, Timer, and Quit
        h_row1 = ctk.CTkFrame(self.top_header, fg_color="transparent")
        h_row1.pack(fill="x", pady=(0, 8))

        # Left Badges: Category & Difficulty
        self.left_badges = ctk.CTkFrame(h_row1, fg_color="transparent")
        self.left_badges.pack(side="left")

        self.cat_pill = PillBadge(self.left_badges, text="General Knowledge", icon="📚", font_size=11)
        self.cat_pill.pack(side="left", padx=(0, 6))

        self.diff_pill = PillBadge(self.left_badges, text="Easy", icon="🎯", font_size=11)
        self.diff_pill.pack(side="left")

        # Right: Streak, Score, Timer, and Quit
        self.right_info = ctk.CTkFrame(h_row1, fg_color="transparent")
        self.right_info.pack(side="right")

        self.streak_pill = PillBadge(self.right_info, text="0 Streak", icon="🔥", font_size=11)
        self.streak_pill.pack(side="left", padx=(0, 8))

        self.score_pill = PillBadge(
            self.right_info,
            text="Score: 0",
            icon="⭐",
            font_size=11,
            fg_color=Theme.PRIMARY,
            text_color=Theme.TEXT_ON_PRIMARY
        )
        self.score_pill.pack(side="left", padx=(0, 8))

        if self.session.timer_seconds > 0:
            self.timer_pill = PillBadge(
                self.right_info,
                text=f"00:{self.session.timer_seconds:02d}",
                icon="⏱",
                font_size=11,
                fg_color=Theme.BG_SURFACE
            )
            self.timer_pill.pack(side="left", padx=(0, 8))

        self.quit_btn = ModernButton(
            self.right_info,
            text="Exit",
            command=self._confirm_quit,
            variant="surface",
            width=65,
            height=32,
            shortcut="Esc"
        )
        self.quit_btn.pack(side="left")

        # Row 2: Progress Tracker Bar & Question Counter
        h_row2 = ctk.CTkFrame(self.top_header, fg_color="transparent")
        h_row2.pack(fill="x")

        self.progress_lbl = ctk.CTkLabel(
            h_row2,
            text="Question 1 of 10",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.progress_lbl.pack(side="left", padx=(0, 12))

        self.progress_bar = ctk.CTkProgressBar(
            h_row2,
            height=8,
            corner_radius=4,
            progress_color=Theme.PRIMARY,
            fg_color=Theme.BG_SURFACE
        )
        self.progress_bar.pack(side="left", fill="x", expand=True)

        # 2. Main Question Scrollable Container (responsive for all screens)
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        # Question Card
        self.q_card = CardFrame(self.scroll_area, corner_radius=18)
        self.q_card.pack(fill="x", pady=(0, 16))

        self.q_inner = ctk.CTkFrame(self.q_card, fg_color="transparent")
        self.q_inner.pack(fill="x", padx=24, pady=24)

        self.q_number_tag = ctk.CTkLabel(
            self.q_inner,
            text="QUESTION #1",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.PRIMARY
        )
        self.q_number_tag.pack(anchor="w", pady=(0, 8))

        self.q_text_lbl = ctk.CTkLabel(
            self.q_inner,
            text="",
            font=(Theme.FONT_FAMILY, 18, "bold"),
            text_color=Theme.TEXT_MAIN,
            wraplength=850,
            justify="left"
        )
        self.q_text_lbl.pack(anchor="w")

        # 3. Answer Options Grid (2x2)
        self.options_frame = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 16))
        self.options_frame.columnconfigure(0, weight=1, uniform="opts")
        self.options_frame.columnconfigure(1, weight=1, uniform="opts")

        self.option_buttons = []
        prefixes = ["A", "B", "C", "D"]
        for i in range(4):
            r = i // 2
            c = i % 2
            btn = ctk.CTkButton(
                self.options_frame,
                text="",
                font=(Theme.FONT_FAMILY, 14, "bold"),
                height=68,
                corner_radius=14,
                fg_color=Theme.BG_CARD,
                hover_color=Theme.BG_SURFACE_HOVER,
                text_color=Theme.TEXT_MAIN,
                border_width=1.5,
                border_color=Theme.BORDER_COLOR,
                anchor="w",
                command=lambda idx=i: self._on_select_answer(idx)
            )
            padx_tuple = (0, 8) if c == 0 else (8, 0)
            btn.grid(row=r, column=c, padx=padx_tuple, pady=6, sticky="nsew")
            self.option_buttons.append(btn)

        # 4. Explanation & Feedback Card (Initially Hidden)
        self.feedback_card = CardFrame(
            self.scroll_area,
            corner_radius=16,
            fg_color=Theme.BG_SURFACE,
            border_color=Theme.BORDER_COLOR
        )
        self.f_inner = ctk.CTkFrame(self.feedback_card, fg_color="transparent")
        self.f_inner.pack(fill="x", padx=20, pady=16)

        self.f_header_lbl = ctk.CTkLabel(
            self.f_inner,
            text="✓ Correct Answer! +10 Points",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.SUCCESS
        )
        self.f_header_lbl.pack(anchor="w", pady=(0, 4))

        self.f_expl_lbl = ctk.CTkLabel(
            self.f_inner,
            text="",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_MAIN,
            wraplength=850,
            justify="left"
        )
        self.f_expl_lbl.pack(anchor="w", pady=(0, 6))

        self.f_bonus_lbl = ctk.CTkLabel(
            self.f_inner,
            text="",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.WARNING
        )
        self.f_bonus_lbl.pack(anchor="w")

        # 5. Bottom Navigation / Next Question Action Bar
        self.action_bar = CardFrame(self, corner_radius=16)
        self.action_bar.pack(fill="x", padx=24, pady=(0, 16))

        ab_inner = ctk.CTkFrame(self.action_bar, fg_color="transparent")
        ab_inner.pack(fill="x", padx=20, pady=12)

        self.hint_lbl = ctk.CTkLabel(
            ab_inner,
            text="Press [1, 2, 3, 4] or [A, B, C, D] to answer",
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_MUTED
        )
        self.hint_lbl.pack(side="left")

        self.next_btn = ModernButton(
            ab_inner,
            text="Next Question →",
            command=self._handle_next_question,
            variant="primary",
            height=44,
            width=180,
            shortcut="Enter"
        )
        self.next_btn.pack(side="right")
        self.next_btn.configure(state="disabled")

    def _load_current_question(self):
        """Populate UI with the current question data and reset timers."""
        self._cancel_timer()
        self.answered = False
        self.feedback_card.pack_forget()
        self.next_btn.configure(state="disabled")
        self.hint_lbl.configure(text="Press [1, 2, 3, 4] or [A, B, C, D] on your keyboard")

        q = self.session.current_question
        if not q:
            self._finish_quiz()
            return

        # Update Progress
        curr = self.session.current_index + 1
        total = self.session.total_questions
        self.progress_lbl.configure(text=f"Question {curr} of {total}")
        self.progress_bar.set(curr / total)

        # Update Top Badges
        self.cat_pill.set_text(q.get("category", "General"), icon="📚")
        diff = q.get("difficulty", "Easy")
        self.diff_pill.set_text(diff, icon="🎯")
        diff_color = Theme.get_difficulty_color(diff)
        self.diff_pill.configure(border_color=diff_color)

        self.score_pill.set_text(f"Score: {self.session.score}", icon="⭐")
        self.streak_pill.set_text(f"{self.session.streak} Streak", icon="🔥")

        # Question details
        self.q_number_tag.configure(text=f"QUESTION #{curr} • {q.get('category', '').upper()}")
        self.q_text_lbl.configure(text=q["question"])

        # Options
        options = q["options"]
        prefixes = ["A", "B", "C", "D"]
        for i, opt in enumerate(options):
            btn = self.option_buttons[i]
            btn.configure(
                text=f"   {prefixes[i]}.   {opt}",
                state="normal",
                fg_color=Theme.BG_CARD,
                border_color=Theme.BORDER_COLOR,
                text_color=Theme.TEXT_MAIN
            )

        # Start timer if enabled
        if self.session.timer_seconds > 0:
            self.time_left = self.session.timer_seconds
            self._update_timer_display()
            self.timer_running = True
            self.session.start_question_timer()
            self._tick_timer()

    def _tick_timer(self):
        if not self.timer_running:
            return

        if self.time_left > 0:
            self._update_timer_display()
            if self.time_left <= 3:
                audio.play_timer_warning()
            self.time_left -= 1
            self._timer_after_id = self.after(1000, self._tick_timer)
        else:
            self._update_timer_display()
            self._handle_timeout()

    def _update_timer_display(self):
        if self.session.timer_seconds <= 0:
            return

        time_str = f"00:{max(0, self.time_left):02d}"
        if self.time_left <= 5:
            self.timer_pill.set_text(time_str, icon="⚠️")
            self.timer_pill.configure(fg_color=Theme.ERROR, border_color=Theme.ERROR)
            self.timer_pill.label.configure(text_color=Theme.TEXT_ON_PRIMARY)
        elif self.time_left <= 10:
            self.timer_pill.set_text(time_str, icon="⏱")
            self.timer_pill.configure(fg_color=Theme.WARNING, border_color=Theme.WARNING)
            self.timer_pill.label.configure(text_color=Theme.TEXT_ON_PRIMARY)
        else:
            self.timer_pill.set_text(time_str, icon="⏱")
            self.timer_pill.configure(fg_color=Theme.BG_SURFACE, border_color=Theme.BORDER_COLOR)
            self.timer_pill.label.configure(text_color=Theme.TEXT_MAIN)

    def _handle_timeout(self):
        """Auto-submit unanswered when timer expires."""
        if self.answered:
            return
        audio.play_timeout()
        self._process_answer(chosen_index=None)

    def _on_select_answer(self, index: int):
        if self.answered:
            return
        self._process_answer(chosen_index=index)

    def _process_answer(self, chosen_index: Optional[int]):
        """Evaluate chosen option, highlight choices, play sound, and reveal explanation."""
        self.answered = True
        self._cancel_timer()

        q = self.session.current_question
        if not q:
            return

        correct_ans = q["answer"]
        options = q["options"]
        chosen_ans = options[chosen_index] if chosen_index is not None else None

        # Submit to engine
        record = self.session.submit_answer(chosen_ans)
        is_correct = record.get("is_correct", False)
        is_timeout = record.get("is_timeout", False)
        pts = record.get("points_earned", 0)
        streak_b = record.get("streak_bonus", 0)

        # Disable buttons and apply color highlights
        for i, opt in enumerate(options):
            btn = self.option_buttons[i]
            btn.configure(state="disabled")
            if opt == correct_ans:
                btn.configure(
                    fg_color=Theme.SUCCESS,
                    border_color=Theme.SUCCESS,
                    text_color=Theme.TEXT_ON_PRIMARY
                )
            elif chosen_index is not None and i == chosen_index and not is_correct:
                btn.configure(
                    fg_color=Theme.ERROR,
                    border_color=Theme.ERROR,
                    text_color=Theme.TEXT_ON_PRIMARY
                )

        # Audio feedback
        if is_correct:
            if streak_b > 0:
                audio.play_streak_bonus()
            else:
                audio.play_correct()
        elif not is_timeout:
            audio.play_incorrect()

        # Update Top Badges
        self.score_pill.set_text(f"Score: {self.session.score}", icon="⭐")
        self.streak_pill.set_text(f"{self.session.streak} Streak", icon="🔥")

        # Feedback Card Setup
        if is_correct:
            self.feedback_card.configure(border_color=Theme.SUCCESS)
            self.f_header_lbl.configure(
                text=f"✓ Correct!  +{pts} Points",
                text_color=Theme.SUCCESS
            )
        elif is_timeout:
            self.feedback_card.configure(border_color=Theme.ERROR)
            self.f_header_lbl.configure(
                text=f"⏱ Time's Up! Correct Answer: {correct_ans}",
                text_color=Theme.ERROR
            )
        else:
            self.feedback_card.configure(border_color=Theme.ERROR)
            self.f_header_lbl.configure(
                text=f"✕ Incorrect! Correct Answer: {correct_ans}",
                text_color=Theme.ERROR
            )

        self.f_expl_lbl.configure(text=f"Explanation: {q.get('explanation', '')}")

        bonus_txt = []
        if streak_b > 0:
            bonus_txt.append(f"🔥 Streak Bonus: +{streak_b} pts!")
        if record.get("difficulty") != "Easy":
            bonus_txt.append(f"🎯 {record.get('difficulty')} Multiplier applied")
        self.f_bonus_lbl.configure(text=" • ".join(bonus_txt))

        # Show feedback card
        self.feedback_card.pack(fill="x", pady=(0, 16))

        # Enable next button
        is_last = (self.session.current_index + 1 >= self.session.total_questions)
        next_text = "Finish & See Results 🏆" if is_last else "Next Question →"
        self.next_btn.configure(text=next_text, state="normal")
        self.hint_lbl.configure(text="Press [Enter] to continue")

    def _handle_next_question(self):
        if not self.answered:
            return

        has_more = self.session.advance()
        if has_more:
            self._load_current_question()
        else:
            self._finish_quiz()

    def _finish_quiz(self):
        self._cancel_timer()
        audio.play_complete()
        summary = self.session.get_summary()
        self.on_quiz_complete(summary)

    def handle_key_press(self, key: str):
        """Handle keyboard shortcuts for answering and advancing."""
        key = key.upper()
        if not self.answered:
            if key in ("1", "A") and len(self.option_buttons) > 0:
                self._on_select_answer(0)
            elif key in ("2", "B") and len(self.option_buttons) > 1:
                self._on_select_answer(1)
            elif key in ("3", "C") and len(self.option_buttons) > 2:
                self._on_select_answer(2)
            elif key in ("4", "D") and len(self.option_buttons) > 3:
                self._on_select_answer(3)
        else:
            if key in ("RETURN", "SPACE", "ENTER"):
                self._handle_next_question()

    def _confirm_quit(self):
        """Pause timer and ask for confirmation to leave."""
        was_running = self.timer_running
        self.timer_running = False

        def _do_quit():
            self._cancel_timer()
            self.on_quit_to_home()

        def _resume():
            if was_running and not self.answered:
                self.timer_running = True
                self._tick_timer()

        # Confirmation modal
        modal = ConfirmationModal(
            self.winfo_toplevel(),
            title="Exit Quiz Session?",
            message="Your current progress in this quiz challenge will not be saved. Are you sure you want to return to Home?",
            on_confirm=_do_quit,
            confirm_text="Exit Quiz",
            is_danger=True
        )
        modal.protocol("WM_DELETE_WINDOW", lambda: (modal.destroy(), _resume()))

    def _cancel_timer(self):
        """Safely destroy any pending after callbacks."""
        self.timer_running = False
        if self._timer_after_id is not None:
            try:
                self.after_cancel(self._timer_after_id)
            except Exception:
                pass
            self._timer_after_id = None

    def destroy(self):
        """Cleanup timer on widget destruction."""
        self._cancel_timer()
        super().destroy()
