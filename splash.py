"""
Splash Screen for QuizMaster.
Displays application branding, subtitle, animated progress indicator, and auto-transitions to Home.
"""

from typing import Callable
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame


class SplashScreen(ctk.CTkFrame):
    """Modern branded splash screen with progress animation."""

    def __init__(self, master, on_finish: Callable, **kwargs):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)
        self.on_finish = on_finish
        self.progress_val = 0.0
        self.is_active = True

        self._build_ui()
        self._animate_progress()

    def _build_ui(self):
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Branded Emblem Card
        logo_card = CardFrame(
            center_frame,
            corner_radius=24,
            border_width=2,
            border_color=Theme.PRIMARY,
            width=120,
            height=120
        )
        logo_card.pack(pady=(0, 24))
        logo_card.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(
            logo_card,
            text="🧠",
            font=(Theme.FONT_FAMILY, 56)
        )
        logo_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_lbl = ctk.CTkLabel(
            center_frame,
            text="QuizMaster",
            font=(Theme.FONT_FAMILY, 38, "bold"),
            text_color=Theme.TEXT_MAIN
        )
        title_lbl.pack(pady=(0, 6))

        # Subtitle
        sub_lbl = ctk.CTkLabel(
            center_frame,
            text="General Knowledge Challenge",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.PRIMARY
        )
        sub_lbl.pack(pady=(0, 4))

        tagline_lbl = ctk.CTkLabel(
            center_frame,
            text="Test Your Knowledge. Challenge Yourself.",
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_MUTED
        )
        tagline_lbl.pack(pady=(0, 32))

        # Animated Progress Bar
        self.prog_bar = ctk.CTkProgressBar(
            center_frame,
            width=320,
            height=8,
            corner_radius=4,
            progress_color=Theme.PRIMARY,
            fg_color=Theme.BG_SURFACE
        )
        self.prog_bar.set(0.0)
        self.prog_bar.pack(pady=(0, 16))

        self.status_lbl = ctk.CTkLabel(
            center_frame,
            text="Loading question database...",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED
        )
        self.status_lbl.pack()

    def _animate_progress(self):
        """Simulate loading sequence smoothly."""
        if not self.is_active:
            return

        self.progress_val += 0.04
        if self.progress_val >= 1.0:
            self.prog_bar.set(1.0)
            self.status_lbl.configure(text="Ready!")
            self.after(300, self._finish)
        else:
            self.prog_bar.set(self.progress_val)
            if self.progress_val > 0.6:
                self.status_lbl.configure(text="Preparing challenge engine...")
            elif self.progress_val > 0.3:
                self.status_lbl.configure(text="Validating 160+ trivia questions...")
            self.after(40, self._animate_progress)

    def _finish(self):
        if self.is_active:
            self.is_active = False
            self.on_finish()

    def cancel(self):
        """Cancel ongoing animation safely on manual skip or navigation."""
        self.is_active = False
