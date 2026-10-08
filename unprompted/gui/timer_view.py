"""Bloc du chronomètre : phase en cours, grand temps, barre de progression et boutons."""

from collections.abc import Callable
from dataclasses import dataclass
from tkinter import ttk

from .widgets import Card


@dataclass(frozen=True)
class TimerViewState:
    """Tout ce que le bloc doit afficher, calculé par la fenêtre à chaque rafraîchissement."""

    status: str
    status_alert: bool
    clock: str
    progress: float
    alert: bool
    primary_text: str
    primary_enabled: bool
    reset_enabled: bool


class TimerPanel(Card):
    def __init__(
        self,
        parent: ttk.Frame,
        on_primary: Callable[[], None],
        on_reset: Callable[[], None],
    ) -> None:
        super().__init__(parent, padding=16)
        self._status = ttk.Label(self.body, style="Status.Card.TLabel", anchor="center")
        self._status.pack(fill="x")
        self._clock = ttk.Label(self.body, style="Timer.Card.TLabel", anchor="center")
        self._clock.pack(fill="x", pady=(4, 8))
        self._bar = ttk.Progressbar(
            self.body, style="Timer.Horizontal.TProgressbar", maximum=100, mode="determinate"
        )
        self._bar.pack(fill="x", pady=(0, 12))

        buttons = ttk.Frame(self.body, style="Card.TFrame")
        buttons.pack()
        self.primary_button = ttk.Button(buttons, style="Primary.TButton", command=on_primary)
        self.primary_button.pack(side="left", padx=6)
        self.reset_button = ttk.Button(
            buttons, text="Réinitialiser", style="Secondary.TButton", command=on_reset
        )
        self.reset_button.pack(side="left", padx=6)

    def show(self, state: TimerViewState) -> None:
        status_style = "Alert.Status.Card.TLabel" if state.status_alert else "Status.Card.TLabel"
        clock_style = "Alert.Timer.Card.TLabel" if state.alert else "Timer.Card.TLabel"
        bar_style = (
            "Alert.Timer.Horizontal.TProgressbar"
            if state.alert
            else "Timer.Horizontal.TProgressbar"
        )
        self._status.configure(text=state.status, style=status_style)
        self._clock.configure(text=state.clock, style=clock_style)
        self._bar.configure(style=bar_style, value=state.progress)
        self.primary_button.configure(text=state.primary_text)
        self.primary_button.state(["!disabled"] if state.primary_enabled else ["disabled"])
        self.reset_button.state(["!disabled"] if state.reset_enabled else ["disabled"])
