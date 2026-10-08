"""Fenêtre principale : relie la machine à états (SessionFlow) aux blocs d'affichage."""

import random
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from ..durations import format_clock
from ..flow import Event, SessionFlow, Stage
from ..modes import SPEECH_LABEL, Mode
from ..topics import THEMES, topics_for
from .duration_view import DurationPanel
from .mode_view import ModeSelector
from .palette import PALETTE
from .theme import apply_style, build_fonts
from .theme_view import ThemeSelector
from .timer_view import TimerPanel, TimerViewState
from .topic_view import TopicCard

POLL_INTERVAL_MS = 100
SPIN_FRAMES = 10
SPIN_INTERVAL_MS = 60
BELL_REPEATS = 3
BELL_INTERVAL_MS = 400
NOTICE_DURATION_MS = 4000
MIN_WIDTH = 680
GAP = 12
PICKING_MESSAGE = "Le choix aléatoire est en cours…"

STATUS_PICK_THEME = "Choisissez un thème pour commencer."
STATUS_DRAW = "Tirez un sujet pour commencer."
STATUS_READY = "Prêt à démarrer."
STATUS_DONE = "Terminé."


class UnpromptedApp(tk.Tk):
    """Fenêtre de l'application. Les méthodes publiques sont les actions de l'utilisateur."""

    def __init__(self, flow: SessionFlow | None = None, spin_frames: int = SPIN_FRAMES) -> None:
        super().__init__()
        self._flow = flow if flow is not None else SessionFlow()
        self._spin_frames = spin_frames
        self._rng = random.Random()
        self._spinning = False
        self._notice: str | None = None
        self._pending: set[str] = set()

        self.title("Unprompted — prise de parole")
        apply_style(self, PALETTE, build_fonts(self))
        self._build()
        self.update_idletasks()
        width, height = max(self.winfo_reqwidth(), MIN_WIDTH), self.winfo_reqheight()
        self.minsize(width, height)
        self.geometry(f"{width}x{height}")
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._refresh()
        self._schedule(POLL_INTERVAL_MS, self._poll_loop)

    def _build(self) -> None:
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, GAP))
        ttk.Label(header, text="Unprompted", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Entraînement à la prise de parole", style="Subtitle.TLabel").pack(
            side="right"
        )

        self.mode_selector = ModeSelector(outer, on_select=self.choose_mode)
        self.mode_selector.pack(fill="x", pady=(0, GAP))

        self.theme_selector = ThemeSelector(outer, THEMES, on_select=self.choose_theme)
        self.theme_selector.pack(fill="x", pady=(0, GAP))

        self.topic_card = TopicCard(outer)
        self.topic_card.pack(fill="both", expand=True, pady=(0, GAP))

        self.draw_button = ttk.Button(
            outer, text="Tirer un sujet", style="Primary.TButton", command=self.draw_topic
        )
        self.draw_button.pack(fill="x", pady=(0, GAP))

        self.duration_panel = DurationPanel(outer, on_change=self.set_durations)
        self.duration_panel.pack(fill="x", pady=(0, GAP))

        self.timer_panel = TimerPanel(
            outer, on_primary=self.press_primary, on_reset=self.press_reset
        )
        self.timer_panel.pack(fill="x")

    # --- Actions de l'utilisateur -------------------------------------------------

    def choose_mode(self, mode: Mode) -> None:
        if self._locked:
            return
        self._flow.set_mode(mode)
        self._refresh()

    def choose_theme(self, theme: str) -> None:
        if self._locked:
            return
        self._flow.set_theme(theme)
        self._refresh()

    def draw_topic(self) -> None:
        if self._locked or self._flow.theme is None:
            return
        self._flow.draw_topic()
        self._spin(self._spin_frames)

    def set_durations(self, prep_seconds: int, speech_seconds: int) -> None:
        if self._locked:
            return
        self._flow.set_durations(prep_seconds, speech_seconds)
        self._refresh()

    def press_primary(self) -> None:
        if self._spinning:
            return
        stage = self._flow.stage
        if stage is Stage.READY:
            self._flow.start()
        elif self._flow.is_running:
            self._flow.toggle_pause()
        elif stage is Stage.DONE:
            self._flow.reset()
        self._refresh()

    def press_reset(self) -> None:
        if self._spinning:
            return
        self._notice = None
        self._flow.reset()
        self._refresh()

    def poll(self) -> None:
        """Fait avancer le chronomètre. Appelée toutes les POLL_INTERVAL_MS par la fenêtre."""
        event = self._flow.tick()
        if event is not None:
            self._announce(event)
        if event is not None or self._flow.is_running:
            self._refresh()

    def close(self) -> None:
        for job in self._pending:
            self.after_cancel(job)
        self._pending.clear()
        self.destroy()

    # --- Mécanique interne --------------------------------------------------------

    @property
    def _locked(self) -> bool:
        return self._spinning or self._flow.is_running

    def _schedule(self, delay_ms: int, callback: Callable[[], None]) -> None:
        job = self.after(delay_ms, callback)
        self._pending.add(job)

    def _poll_loop(self) -> None:
        self.poll()
        self._schedule(POLL_INTERVAL_MS, self._poll_loop)

    def _spin(self, frames_left: int) -> None:
        if frames_left <= 0:
            self._spinning = False
            self._refresh()
            return
        self._spinning = True
        theme = self._flow.theme
        assert theme is not None
        sample = self._rng.choice(topics_for(self._flow.mode, theme))
        self.topic_card.show_message(sample.text, PICKING_MESSAGE)
        self._refresh()
        self._schedule(SPIN_INTERVAL_MS, lambda: self._spin(frames_left - 1))

    def _announce(self, event: Event) -> None:
        label = SPEECH_LABEL if event is Event.SPEECH_ENDED else self._flow.spec.prep_label
        self._notice = f"Temps de {label.lower()} écoulé !"
        self._ring(BELL_REPEATS)
        self._schedule(NOTICE_DURATION_MS, self._clear_notice)

    def _ring(self, remaining: int) -> None:
        self.bell()
        if remaining > 1:
            self._schedule(BELL_INTERVAL_MS, lambda: self._ring(remaining - 1))

    def _clear_notice(self) -> None:
        self._notice = None
        self._refresh()

    def _refresh(self) -> None:
        flow = self._flow
        locked = self._locked
        self.mode_selector.show(flow.mode, enabled=not locked)
        self.theme_selector.show(flow.theme, enabled=not locked)
        self.duration_panel.show(
            flow.spec, flow.prep_seconds, flow.speech_seconds, enabled=not locked
        )
        if not self._spinning:
            self.topic_card.show(flow.topic, flow.spec.topic_intro)
        can_draw = not locked and flow.theme is not None
        self.draw_button.state(["!disabled"] if can_draw else ["disabled"])
        self.timer_panel.show(self._timer_state())

    def _timer_state(self) -> TimerViewState:
        flow = self._flow
        stage = flow.stage
        status, status_alert = self._status_text(stage)
        if stage is Stage.DONE:
            primary_text = "Recommencer"
        elif flow.is_running:
            primary_text = "Reprendre" if flow.is_paused else "Pause"
        else:
            primary_text = "Démarrer"
        return TimerViewState(
            status=status,
            status_alert=status_alert,
            clock=format_clock(flow.remaining_seconds),
            progress=flow.progress * 100,
            alert=flow.in_alert or stage is Stage.DONE,
            primary_text=primary_text,
            primary_enabled=stage is not Stage.IDLE and not self._spinning,
            reset_enabled=(flow.is_running or stage is Stage.DONE) and not self._spinning,
        )

    def _status_text(self, stage: Stage) -> tuple[str, bool]:
        if self._notice is not None:
            return self._notice, True
        if stage is Stage.IDLE:
            return (STATUS_PICK_THEME if self._flow.theme is None else STATUS_DRAW), False
        if stage is Stage.READY:
            return STATUS_READY, False
        if stage is Stage.DONE:
            return STATUS_DONE, False
        label = self._flow.phase_label
        return (f"{label} — en pause" if self._flow.is_paused else label), False
