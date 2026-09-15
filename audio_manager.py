"""
Audio Manager for QuizMaster.
Provides safe, asynchronous audio feedback using native OS capabilities (winsound on Windows).
Gracefully falls back to silent operation if sound is disabled or unavailable.
"""

import sys
import threading
import time

try:
    if sys.platform == "win32":
        import winsound
    else:
        winsound = None
except ImportError:
    winsound = None


class AudioManager:
    """Safe, non-blocking sound synthesizer and effect player."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def set_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self.enabled = enabled

    def _play_async(self, sound_func, *args):
        """Execute sound generation function in a daemon thread."""
        if not self.enabled or winsound is None:
            return
        thread = threading.Thread(target=sound_func, args=args, daemon=True)
        thread.start()

    def play_click(self):
        """Play a subtle UI click tone."""
        def _click():
            try:
                winsound.Beep(900, 30)
            except Exception:
                pass
        self._play_async(_click)

    def play_correct(self):
        """Play a pleasant ascending chime for correct answer."""
        def _correct():
            try:
                winsound.Beep(523, 70)  # C5
                time.sleep(0.02)
                winsound.Beep(659, 70)  # E5
                time.sleep(0.02)
                winsound.Beep(784, 120) # G5
            except Exception:
                pass
        self._play_async(_correct)

    def play_incorrect(self):
        """Play a low buzzer tone for incorrect answer."""
        def _incorrect():
            try:
                winsound.Beep(260, 160)
                time.sleep(0.03)
                winsound.Beep(200, 220)
            except Exception:
                pass
        self._play_async(_incorrect)

    def play_timer_warning(self):
        """Play short urgent tick tone when timer is low."""
        def _warning():
            try:
                winsound.Beep(1200, 60)
            except Exception:
                pass
        self._play_async(_warning)

    def play_timeout(self):
        """Play timeout buzzer."""
        def _timeout():
            try:
                winsound.Beep(320, 250)
            except Exception:
                pass
        self._play_async(_timeout)

    def play_streak_bonus(self):
        """Play a high-energy celebratory arpeggio for streaks."""
        def _streak():
            try:
                winsound.Beep(587, 60)  # D5
                time.sleep(0.01)
                winsound.Beep(740, 60)  # F#5
                time.sleep(0.01)
                winsound.Beep(880, 60)  # A5
                time.sleep(0.01)
                winsound.Beep(1175, 140) # D6
            except Exception:
                pass
        self._play_async(_streak)

    def play_complete(self):
        """Play victory completion fanfare."""
        def _complete():
            try:
                notes = [(523, 100), (659, 100), (784, 120), (1046, 250)]
                for freq, dur in notes:
                    winsound.Beep(freq, dur)
                    time.sleep(0.03)
            except Exception:
                pass
        self._play_async(_complete)


# Global audio manager instance
audio = AudioManager(enabled=True)
