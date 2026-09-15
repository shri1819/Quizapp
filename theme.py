"""
Theme and Design System tokens for QuizMaster.
Supports seamless switching between dark and light themes with modern palette tokens.
"""

from typing import Dict, Tuple

class Theme:
    """Color palettes, typography standards, and styling constants."""

    # Modern HSL-tailored Color Palettes (Dark and Light)
    # Format: (Light Value, Dark Value) for CustomTkinter dual-mode compatibility

    # Backgrounds
    BG_MAIN = ("#F1F5F9", "#0F172A")       # Main window canvas
    BG_CARD = ("#FFFFFF", "#1E293B")       # Elevated card background
    BG_SURFACE = ("#F8FAFC", "#243247")    # Subtle inner container surface
    BG_SURFACE_HOVER = ("#E2E8F0", "#334155")
    BORDER_COLOR = ("#CBD5E1", "#334155")  # Subtle card outline

    # Brand Colors
    PRIMARY = ("#4F46E5", "#6366F1")       # Electric Indigo
    PRIMARY_HOVER = ("#4338CA", "#4F46E5")
    SECONDARY = ("#7C3AED", "#8B5CF6")     # Vivid Violet
    SECONDARY_HOVER = ("#6D28D9", "#7C3AED")
    ACCENT = ("#06B6D4", "#22D3EE")        # Cyan

    # Status Colors
    SUCCESS = ("#16A34A", "#22C55E")       # Vibrant Emerald Green
    SUCCESS_BG = ("#DCFCE7", "#14532D")
    ERROR = ("#DC2626", "#EF4444")         # Bright Crimson
    ERROR_BG = ("#FEE2E2", "#7F1D1D")
    WARNING = ("#D97706", "#F59E0B")       # Amber Glow
    WARNING_BG = ("#FEF3C7", "#78350F")
    INFO = ("#2563EB", "#38BDF8")          # Sky Blue

    # Text Colors
    TEXT_MAIN = ("#0F172A", "#F8FAFC")     # High-contrast primary text
    TEXT_MUTED = ("#64748B", "#94A3B8")    # Subtitle / descriptive text
    TEXT_ON_PRIMARY = ("#FFFFFF", "#FFFFFF")

    # Difficulty Color Accents
    DIFF_EASY = ("#16A34A", "#22C55E")
    DIFF_MEDIUM = ("#D97706", "#F59E0B")
    DIFF_HARD = ("#DC2626", "#EF4444")

    # Fonts
    FONT_FAMILY = "Segoe UI"

    @classmethod
    def font_hero(cls, size_scale: float = 1.0) -> Tuple[str, int, str]:
        return (cls.FONT_FAMILY, int(30 * size_scale), "bold")

    @classmethod
    def font_title(cls, size_scale: float = 1.0) -> Tuple[str, int, str]:
        return (cls.FONT_FAMILY, int(22 * size_scale), "bold")

    @classmethod
    def font_subtitle(cls, size_scale: float = 1.0) -> Tuple[str, int, str]:
        return (cls.FONT_FAMILY, int(16 * size_scale), "bold")

    @classmethod
    def font_body(cls, size_scale: float = 1.0) -> Tuple[str, int]:
        return (cls.FONT_FAMILY, int(13 * size_scale))

    @classmethod
    def font_body_bold(cls, size_scale: float = 1.0) -> Tuple[str, int, str]:
        return (cls.FONT_FAMILY, int(13 * size_scale), "bold")

    @classmethod
    def font_small(cls, size_scale: float = 1.0) -> Tuple[str, int]:
        return (cls.FONT_FAMILY, int(11 * size_scale))

    @classmethod
    def font_button(cls, size_scale: float = 1.0) -> Tuple[str, int, str]:
        return (cls.FONT_FAMILY, int(14 * size_scale), "bold")

    @classmethod
    def get_difficulty_color(cls, difficulty: str) -> Tuple[str, str]:
        if difficulty == "Easy":
            return cls.DIFF_EASY
        elif difficulty == "Medium":
            return cls.DIFF_MEDIUM
        elif difficulty == "Hard":
            return cls.DIFF_HARD
        return cls.PRIMARY
