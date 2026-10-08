"""Bloc de choix du mode : deux boutons côte à côte."""

from collections.abc import Callable
from tkinter import ttk

from ..modes import MODE_SPECS, Mode
from .widgets import Card


class ModeSelector(ttk.Frame):
    def __init__(self, parent: ttk.Frame, on_select: Callable[[Mode], None]) -> None:
        super().__init__(parent)
        card = Card(self, padding=6)
        card.pack(fill="x")
        self._buttons: dict[Mode, ttk.Button] = {}
        for mode in Mode:
            button = ttk.Button(
                card.body,
                text=MODE_SPECS[mode].label,
                command=lambda selected=mode: on_select(selected),
            )
            button.pack(side="left", expand=True, fill="x", padx=2)
            self._buttons[mode] = button

    def show(self, mode: Mode, enabled: bool) -> None:
        for candidate, button in self._buttons.items():
            button.configure(style="SegmentOn.TButton" if candidate is mode else "Segment.TButton")
            button.state(["!disabled"] if enabled else ["disabled"])
