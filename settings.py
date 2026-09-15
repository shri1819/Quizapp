"""
Settings Screen for QuizMaster.
Enables managing visual themes, sound effects, gameplay defaults, UI scaling, and persistent data resets.
"""

from typing import Callable
import customtkinter as ctk
from ui.theme import Theme
from ui.components import CardFrame, ModernButton, PillBadge, HeaderBar, ConfirmationModal
from core.settings_manager import SettingsManager
from core.score_manager import ScoreManager
from core.audio_manager import audio


class SettingsScreen(ctk.CTkFrame):
    """Modern settings and preferences management screen."""

    def __init__(
        self,
        master,
        settings_manager: SettingsManager,
        score_manager: ScoreManager,
        on_back: Callable,
        on_theme_changed: Callable,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)

        self.sm = settings_manager
        self.score_mgr = score_manager
        self.on_back = on_back
        self.on_theme_changed = on_theme_changed

        # Bind state variables
        self.var_theme = ctk.StringVar(value=self.sm.get("theme", "Dark"))
        self.var_sound = ctk.BooleanVar(value=self.sm.get("sound_effects", True))
        self.var_timer = ctk.IntVar(value=self.sm.get("default_timer", 30))
        self.var_shuffle_q = ctk.BooleanVar(value=self.sm.get("shuffle_questions", True))
        self.var_shuffle_a = ctk.BooleanVar(value=self.sm.get("shuffle_answers", True))
        self.var_scale = ctk.StringVar(value=self.sm.get("ui_scale", "Normal"))
        self.var_player = ctk.StringVar(value=self.sm.get("player_name", "Player"))

        self._build_ui()

    def _build_ui(self):
        # Header
        header = HeaderBar(
            self,
            title="⚙ Application Settings",
            subtitle="Configure theme, audio, gameplay preferences, and local data",
            on_back=self.on_back
        )
        header.pack(fill="x", padx=24, pady=(16, 10))

        # Scrollable settings list
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 1. Appearance Section
        self._build_section_header(scroll, "🎨 APPEARANCE & DISPLAY")
        app_card = CardFrame(scroll)
        app_card.pack(fill="x", pady=(0, 16))

        app_inner = ctk.CTkFrame(app_card, fg_color="transparent")
        app_inner.pack(fill="x", padx=20, pady=16)

        # Theme Option
        t_row = ctk.CTkFrame(app_inner, fg_color="transparent")
        t_row.pack(fill="x", pady=(0, 12))

        t_lbl = ctk.CTkFrame(t_row, fg_color="transparent")
        t_lbl.pack(side="left")
        ctk.CTkLabel(t_lbl, text="Interface Theme", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(t_lbl, text="Choose between modern dark, light, or system default themes", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        theme_seg = ctk.CTkSegmentedButton(
            t_row,
            values=["Dark", "Light", "System"],
            variable=self.var_theme,
            command=self._on_change_theme,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=34
        )
        theme_seg.pack(side="right")

        # UI Scale Option
        s_row = ctk.CTkFrame(app_inner, fg_color="transparent")
        s_row.pack(fill="x")

        s_lbl = ctk.CTkFrame(s_row, fg_color="transparent")
        s_lbl.pack(side="left")
        ctk.CTkLabel(s_lbl, text="Display Scaling", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(s_lbl, text="Adjust overall typography and widget sizing", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        scale_seg = ctk.CTkSegmentedButton(
            s_row,
            values=["Normal", "Large"],
            variable=self.var_scale,
            command=self._on_change_scale,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=34
        )
        scale_seg.pack(side="right")

        # 2. Gameplay & Audio Section
        self._build_section_header(scroll, "🎮 GAMEPLAY & AUDIO")
        game_card = CardFrame(scroll)
        game_card.pack(fill="x", pady=(0, 16))

        game_inner = ctk.CTkFrame(game_card, fg_color="transparent")
        game_inner.pack(fill="x", padx=20, pady=16)

        # Sound Effects
        snd_row = ctk.CTkFrame(game_inner, fg_color="transparent")
        snd_row.pack(fill="x", pady=(0, 14))

        snd_lbl = ctk.CTkFrame(snd_row, fg_color="transparent")
        snd_lbl.pack(side="left")
        ctk.CTkLabel(snd_lbl, text="Sound Effects", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(snd_lbl, text="Enable audio cues for correct answers, streaks, and timers", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        snd_sw = ctk.CTkSwitch(
            snd_row,
            text="",
            variable=self.var_sound,
            command=self._on_toggle_sound,
            progress_color=Theme.PRIMARY
        )
        snd_sw.pack(side="right")

        # Default Timer
        tmr_row = ctk.CTkFrame(game_inner, fg_color="transparent")
        tmr_row.pack(fill="x", pady=(0, 14))

        tmr_lbl = ctk.CTkFrame(tmr_row, fg_color="transparent")
        tmr_lbl.pack(side="left")
        ctk.CTkLabel(tmr_lbl, text="Default Question Timer", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(tmr_lbl, text="Initial timer preset selected in quiz setup", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        tmr_seg = ctk.CTkSegmentedButton(
            tmr_row,
            values=["No Timer", "15s", "30s", "60s"],
            command=self._on_change_timer,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=34
        )
        cur_t = "No Timer" if self.var_timer.get() == 0 else f"{self.var_timer.get()}s"
        tmr_seg.set(cur_t)
        tmr_seg.pack(side="right")

        # Default Player Name
        pl_row = ctk.CTkFrame(game_inner, fg_color="transparent")
        pl_row.pack(fill="x")

        pl_lbl = ctk.CTkFrame(pl_row, fg_color="transparent")
        pl_lbl.pack(side="left")
        ctk.CTkLabel(pl_lbl, text="Default Player Name", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(pl_lbl, text="Profile name used on leaderboards and results", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        pl_entry = ctk.CTkEntry(
            pl_row,
            textvariable=self.var_player,
            width=150,
            height=34,
            corner_radius=8,
            font=(Theme.FONT_FAMILY, 12)
        )
        pl_entry.pack(side="right")
        self.var_player.trace_add("write", lambda *_: self.sm.set("player_name", self.var_player.get().strip() or "Player"))

        # 3. Data & Storage Section
        self._build_section_header(scroll, "💾 DATA MANAGEMENT & RESETS")
        data_card = CardFrame(scroll)
        data_card.pack(fill="x", pady=(0, 16))

        data_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        data_inner.pack(fill="x", padx=20, pady=16)

        # Clear Scores
        c1_row = ctk.CTkFrame(data_inner, fg_color="transparent")
        c1_row.pack(fill="x", pady=(0, 12))

        c1_lbl = ctk.CTkFrame(c1_row, fg_color="transparent")
        c1_lbl.pack(side="left")
        ctk.CTkLabel(c1_lbl, text="Clear High Scores", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(c1_lbl, text="Permanently wipe all leaderboard records", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        ModernButton(c1_row, text="Clear Scores", command=self._confirm_clear_scores, variant="surface", width=120, height=34).pack(side="right")

        # Reset Lifetime Statistics
        c2_row = ctk.CTkFrame(data_inner, fg_color="transparent")
        c2_row.pack(fill="x", pady=(0, 12))

        c2_lbl = ctk.CTkFrame(c2_row, fg_color="transparent")
        c2_lbl.pack(side="left")
        ctk.CTkLabel(c2_lbl, text="Reset Statistics", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(c2_lbl, text="Reset total quizzes, accuracy, and streaks to zero", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        ModernButton(c2_row, text="Reset Stats", command=self._confirm_reset_stats, variant="surface", width=120, height=34).pack(side="right")

        # Reset Defaults
        c3_row = ctk.CTkFrame(data_inner, fg_color="transparent")
        c3_row.pack(fill="x")

        c3_lbl = ctk.CTkFrame(c3_row, fg_color="transparent")
        c3_lbl.pack(side="left")
        ctk.CTkLabel(c3_lbl, text="Reset All Settings", font=(Theme.FONT_FAMILY, 13, "bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(c3_lbl, text="Restore settings to factory defaults", font=(Theme.FONT_FAMILY, 11), text_color=Theme.TEXT_MUTED).pack(anchor="w")

        ModernButton(c3_row, text="Restore Defaults", command=self._confirm_restore_defaults, variant="danger", width=130, height=34).pack(side="right")

    def _build_section_header(self, parent, title: str):
        ctk.CTkLabel(
            parent,
            text=title,
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(4, 6))

    def _on_change_theme(self, mode: str):
        self.sm.set("theme", mode)
        self.on_theme_changed(mode)

    def _on_change_scale(self, scale_str: str):
        self.sm.set("ui_scale", scale_str)
        scaling_factor = 1.1 if scale_str == "Large" else 1.0
        ctk.set_widget_scaling(scaling_factor)
        ctk.set_window_scaling(scaling_factor)

    def _on_toggle_sound(self):
        enabled = self.var_sound.get()
        self.sm.set("sound_effects", enabled)
        audio.set_enabled(enabled)

    def _on_change_timer(self, val: str):
        t_int = 0 if val == "No Timer" else int(val.replace("s", ""))
        self.var_timer.set(t_int)
        self.sm.set("default_timer", t_int)

    def _confirm_clear_scores(self):
        ConfirmationModal(
            self.winfo_toplevel(),
            title="Clear High Scores?",
            message="This will delete all saved high score records from your computer. This cannot be undone.",
            on_confirm=lambda: self.score_mgr.clear_high_scores(),
            confirm_text="Clear Scores",
            is_danger=True
        )

    def _confirm_reset_stats(self):
        ConfirmationModal(
            self.winfo_toplevel(),
            title="Reset Lifetime Statistics?",
            message="This will reset your questions answered, accuracy rate, best streak, and quiz counts back to zero.",
            on_confirm=lambda: self.score_mgr.reset_statistics(),
            confirm_text="Reset Stats",
            is_danger=True
        )

    def _confirm_restore_defaults(self):
        ConfirmationModal(
            self.winfo_toplevel(),
            title="Restore Default Settings?",
            message="Are you sure you want to reset all preferences to defaults?",
            on_confirm=self._do_restore_defaults,
            confirm_text="Restore Defaults",
            is_danger=True
        )

    def _do_restore_defaults(self):
        self.sm.reset_to_defaults()
        self.var_theme.set(self.sm.get("theme"))
        self.var_sound.set(self.sm.get("sound_effects"))
        self.var_timer.set(self.sm.get("default_timer"))
        self.var_scale.set(self.sm.get("ui_scale"))
        self.var_player.set(self.sm.get("player_name"))
        self.on_theme_changed(self.var_theme.get())
        audio.set_enabled(self.var_sound.get())
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
