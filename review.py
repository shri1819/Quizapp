"""
Answer Review Screen for QuizMaster.
Allows reviewing each question answered during the quiz, user choices vs correct answers, and explanations.
"""

from typing import Callable, Dict, List, Any
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, ModernButton, PillBadge, HeaderBar


class ReviewScreen(ctk.CTkFrame):
    """Detailed question-by-question review screen with filter options."""

    def __init__(
        self,
        master,
        history: List[Dict[str, Any]],
        on_back: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.history = history
        self.on_back = on_back
        self.filter_mode = "All"  # "All", "Incorrect", "Correct"

        self._build_ui()

    def _build_ui(self):
        # Header
        header = HeaderBar(
            self,
            title="Quiz Answer Review",
            subtitle="Analyze your performance, correct answers, and explanations",
            on_back=self.on_back,
            back_text="← Back to Results"
        )
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Filter row
        filter_card = CardFrame(self, corner_radius=14)
        filter_card.pack(fill="x", padx=24, pady=(0, 14))

        f_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=10)

        correct_count = sum(1 for h in self.history if h.get("is_correct"))
        inc_count = len(self.history) - correct_count

        self.filter_seg = ctk.CTkSegmentedButton(
            f_inner,
            values=[
                f"All ({len(self.history)})",
                f"Incorrect ({inc_count})",
                f"Correct ({correct_count})"
            ],
            command=self._on_filter_changed,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=36
        )
        self.filter_seg.set(f"All ({len(self.history)})")
        self.filter_seg.pack(side="left")

        # Scrollable Question List
        self.scroll_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self._render_question_cards()

    def _on_filter_changed(self, value: str):
        if "Incorrect" in value:
            self.filter_mode = "Incorrect"
        elif "Correct" in value:
            self.filter_mode = "Correct"
        else:
            self.filter_mode = "All"
        self._render_question_cards()

    def _render_question_cards(self):
        # Clear existing cards
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        filtered = []
        for idx, item in enumerate(self.history, start=1):
            is_correct = item.get("is_correct", False)
            if self.filter_mode == "Correct" and not is_correct:
                continue
            if self.filter_mode == "Incorrect" and is_correct:
                continue
            filtered.append((idx, item))

        if not filtered:
            empty_card = CardFrame(self.scroll_list, corner_radius=14)
            empty_card.pack(fill="x", pady=20)
            ctk.CTkLabel(
                empty_card,
                text="No questions matching the selected filter.",
                font=(Theme.FONT_FAMILY, 14),
                text_color=Theme.TEXT_MUTED
            ).pack(padx=20, pady=30)
            return

        for original_idx, item in filtered:
            self._create_review_card(original_idx, item)

    def _create_review_card(self, idx: int, item: Dict[str, Any]):
        is_correct = item.get("is_correct", False)
        is_timeout = item.get("is_timeout", False)

        border_col = Theme.SUCCESS if is_correct else Theme.ERROR

        card = CardFrame(
            self.scroll_list,
            corner_radius=16,
            border_color=border_col,
            border_width=1.5
        )
        card.pack(fill="x", pady=(0, 14))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Header Row: Question number, status pill, category
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))

        if is_correct:
            status_text = f"✓ Question {idx} (Correct)"
            status_col = Theme.SUCCESS
        elif is_timeout:
            status_text = f"⏱ Question {idx} (Timed Out)"
            status_col = Theme.WARNING
        else:
            status_text = f"✕ Question {idx} (Incorrect)"
            status_col = Theme.ERROR

        ctk.CTkLabel(
            top_row,
            text=status_text,
            font=(Theme.FONT_FAMILY, 14, "bold"),
            text_color=status_col
        ).pack(side="left")

        cat = item.get("category", "General")
        diff = item.get("difficulty", "Easy")
        diff_pill = PillBadge(
            top_row,
            text=f"{cat} • {diff}",
            font_size=10,
            fg_color=Theme.BG_SURFACE
        )
        diff_pill.pack(side="right")

        # Question text
        q_text = item.get("question", "")
        ctk.CTkLabel(
            inner,
            text=q_text,
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_MAIN,
            wraplength=850,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Answer Comparison Box
        ans_box = ctk.CTkFrame(
            inner,
            corner_radius=10,
            fg_color=Theme.BG_SURFACE
        )
        ans_box.pack(fill="x", pady=(0, 10))

        ans_inner = ctk.CTkFrame(ans_box, fg_color="transparent")
        ans_inner.pack(fill="x", padx=14, pady=10)

        # Your Answer
        user_ans = item.get("user_answer") or "(Unanswered / Timed out)"
        user_col = Theme.SUCCESS if is_correct else Theme.ERROR

        u_row = ctk.CTkFrame(ans_inner, fg_color="transparent")
        u_row.pack(fill="x", pady=2)
        ctk.CTkLabel(
            u_row,
            text="Your Answer: ",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_MUTED,
            width=110,
            anchor="w"
        ).pack(side="left")
        ctk.CTkLabel(
            u_row,
            text=user_ans,
            font=(Theme.FONT_FAMILY, 13, "bold"),
            text_color=user_col
        ).pack(side="left")

        # Correct Answer (if incorrect or timeout)
        if not is_correct:
            c_row = ctk.CTkFrame(ans_inner, fg_color="transparent")
            c_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                c_row,
                text="Correct Answer: ",
                font=(Theme.FONT_FAMILY, 12, "bold"),
                text_color=Theme.TEXT_MUTED,
                width=110,
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                c_row,
                text=item.get("correct_answer", ""),
                font=(Theme.FONT_FAMILY, 13, "bold"),
                text_color=Theme.SUCCESS
            ).pack(side="left")

        # Explanation
        expl = item.get("explanation", "")
        if expl:
            e_lbl = ctk.CTkLabel(
                inner,
                text=f"💡 {expl}",
                font=(Theme.FONT_FAMILY, 12),
                text_color=Theme.TEXT_MUTED,
                wraplength=850,
                justify="left"
            )
            e_lbl.pack(anchor="w")
