"""
Reusable modern UI components for QuizMaster.
Includes CardFrame, StatCard, PillBadge, ModernButton, ModalDialog, and TimerBadge.
"""

from typing import Callable, Optional, Tuple, Union
import customtkinter as ctk
from ui.theme import Theme
from core.audio_manager import audio


class CardFrame(ctk.CTkFrame):
    """Elevated container frame with rounded corners and border styling."""

    def __init__(
        self,
        master,
        corner_radius: int = 16,
        border_width: int = 1,
        fg_color: Optional[Tuple[str, str]] = None,
        border_color: Optional[Tuple[str, str]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=corner_radius,
            border_width=border_width,
            fg_color=fg_color or Theme.BG_CARD,
            border_color=border_color or Theme.BORDER_COLOR,
            **kwargs
        )


class PillBadge(ctk.CTkFrame):
    """Compact rounded pill badge for categories, difficulties, and tags."""

    def __init__(
        self,
        master,
        text: str,
        icon: str = "",
        fg_color: Optional[Tuple[str, str]] = None,
        text_color: Optional[Tuple[str, str]] = None,
        font_size: int = 12,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=20,
            fg_color=fg_color or Theme.BG_SURFACE,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            **kwargs
        )
        display_text = f"{icon} {text}".strip() if icon else text
        self.label = ctk.CTkLabel(
            self,
            text=display_text,
            font=(Theme.FONT_FAMILY, font_size, "bold"),
            text_color=text_color or Theme.TEXT_MAIN
        )
        self.label.pack(padx=12, pady=4)

    def set_text(self, text: str, icon: str = ""):
        display_text = f"{icon} {text}".strip() if icon else text
        self.label.configure(text=display_text)


class StatCard(CardFrame):
    """Statistics tile with an icon, large metric value, and description."""

    def __init__(
        self,
        master,
        title: str,
        value: str,
        icon: str = "📊",
        accent_color: Optional[Tuple[str, str]] = None,
        width: int = 170,
        height: int = 100,
        **kwargs
    ):
        super().__init__(master, width=width, height=height, **kwargs)
        self.pack_propagate(False)

        # Content container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=14, pady=10)

        # Header row with title & icon
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            top_row,
            text=title.upper(),
            font=(Theme.FONT_FAMILY, 10, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.title_label.pack(side="left")

        self.icon_label = ctk.CTkLabel(
            top_row,
            text=icon,
            font=(Theme.FONT_FAMILY, 14)
        )
        self.icon_label.pack(side="right")

        # Big Value Display
        self.value_label = ctk.CTkLabel(
            content,
            text=value,
            font=(Theme.FONT_FAMILY, 22, "bold"),
            text_color=accent_color or Theme.PRIMARY
        )
        self.value_label.pack(anchor="w", pady=(4, 0))

    def update_value(self, new_value: str):
        self.value_label.configure(text=new_value)


class ModernButton(ctk.CTkButton):
    """Custom styled button with optional keyboard hint badge and sound integration."""

    def __init__(
        self,
        master,
        text: str,
        command: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        variant: str = "primary",  # 'primary', 'secondary', 'success', 'danger', 'surface'
        corner_radius: int = 12,
        height: int = 44,
        play_sound: bool = True,
        **kwargs
    ):
        # Color mapping by variant
        if variant == "primary":
            fg_color = Theme.PRIMARY
            hover_color = Theme.PRIMARY_HOVER
            text_color = Theme.TEXT_ON_PRIMARY
            border_width = 0
            border_color = None
        elif variant == "secondary":
            fg_color = Theme.SECONDARY
            hover_color = Theme.SECONDARY_HOVER
            text_color = Theme.TEXT_ON_PRIMARY
            border_width = 0
            border_color = None
        elif variant == "success":
            fg_color = Theme.SUCCESS
            hover_color = ("#15803D", "#16A34A")
            text_color = Theme.TEXT_ON_PRIMARY
            border_width = 0
            border_color = None
        elif variant == "danger":
            fg_color = Theme.ERROR
            hover_color = ("#B91C1C", "#DC2626")
            text_color = Theme.TEXT_ON_PRIMARY
            border_width = 0
            border_color = None
        else:  # surface / subtle
            fg_color = Theme.BG_SURFACE
            hover_color = Theme.BG_SURFACE_HOVER
            text_color = Theme.TEXT_MAIN
            border_width = 1
            border_color = Theme.BORDER_COLOR

        self._user_command = command
        self._play_sound = play_sound

        display_text = f"{text}  [{shortcut}]" if shortcut else text

        button_kwargs = {
            "text": display_text,
            "command": self._handle_click,
            "corner_radius": corner_radius,
            "height": height,
            "fg_color": fg_color,
            "hover_color": hover_color,
            "text_color": text_color,
            "font": (Theme.FONT_FAMILY, 13, "bold"),
            "border_width": border_width,
            **kwargs
        }
        if border_color is not None:
            button_kwargs["border_color"] = border_color

        super().__init__(master, **button_kwargs)

    def _handle_click(self):
        if self._play_sound:
            audio.play_click()
        if self._user_command:
            self._user_command()


class HeaderBar(ctk.CTkFrame):
    """Standardized navigation header bar with Back button and Title."""

    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        on_back: Optional[Callable] = None,
        back_text: str = "← Back",
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", height=60, **kwargs)
        self.pack_propagate(False)

        if on_back:
            self.back_btn = ModernButton(
                self,
                text=back_text,
                command=on_back,
                variant="surface",
                width=90,
                height=36,
                shortcut="Esc"
            )
            self.back_btn.pack(side="left", padx=(0, 16))

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="y")

        self.title_lbl = ctk.CTkLabel(
            text_frame,
            text=title,
            font=(Theme.FONT_FAMILY, 20, "bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.title_lbl.pack(anchor="w")

        if subtitle:
            self.sub_lbl = ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=(Theme.FONT_FAMILY, 12),
                text_color=Theme.TEXT_MUTED
            )
            self.sub_lbl.pack(anchor="w")


class ConfirmationModal(ctk.CTkToplevel):
    """Clean confirmation dialog modal."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
        on_confirm: Callable,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        is_danger: bool = False
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - 210
        y = master.winfo_rooty() + (master.winfo_height() // 2) - 110
        self.geometry(f"+{x}+{y}")

        card = CardFrame(self, corner_radius=12)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        title_lbl = ctk.CTkLabel(
            card,
            text=title,
            font=(Theme.FONT_FAMILY, 18, "bold"),
            text_color=Theme.ERROR if is_danger else Theme.TEXT_MAIN
        )
        title_lbl.pack(anchor="w", padx=20, pady=(16, 8))

        msg_lbl = ctk.CTkLabel(
            card,
            text=message,
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_MUTED,
            wraplength=360,
            justify="left"
        )
        msg_lbl.pack(anchor="w", padx=20, pady=(0, 20))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        cancel_btn = ModernButton(
            btn_row,
            text=cancel_text,
            command=self.destroy,
            variant="surface",
            width=100
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        def _do_confirm():
            self.destroy()
            on_confirm()

        confirm_btn = ModernButton(
            btn_row,
            text=confirm_text,
            command=_do_confirm,
            variant="danger" if is_danger else "primary",
            width=110
        )
        confirm_btn.pack(side="right")
