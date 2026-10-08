"""Bloc de choix des deux durées : deux listes déroulantes aux valeurs imposées par le mode."""

from collections.abc import Callable
from tkinter import ttk

from ..durations import describe_duration
from ..modes import SPEECH_LABEL, ModeSpec
from .widgets import Card


class DurationPanel(Card):
    def __init__(self, parent: ttk.Frame, on_change: Callable[[int, int], None]) -> None:
        super().__init__(parent, padding=12)
        self._on_change = on_change
        self._spec: ModeSpec | None = None
        self.body.columnconfigure((0, 1), weight=1, uniform="durations")

        self._prep_label = ttk.Label(self.body, style="Muted.Card.TLabel")
        self._prep_label.grid(row=0, column=0, sticky="w")
        self._speech_label = ttk.Label(
            self.body, text=SPEECH_LABEL.upper(), style="Muted.Card.TLabel"
        )
        self._speech_label.grid(row=0, column=1, sticky="w", padx=(8, 0))

        self._prep_box = ttk.Combobox(self.body, state="readonly", width=12)
        self._prep_box.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self._speech_box = ttk.Combobox(self.body, state="readonly", width=12)
        self._speech_box.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))
        for box in (self._prep_box, self._speech_box):
            box.bind("<<ComboboxSelected>>", self._changed)

    def show(self, spec: ModeSpec, prep: int, speech: int, enabled: bool) -> None:
        if spec is not self._spec:
            self._spec = spec
            self._prep_label.configure(text=spec.prep_label.upper())
            self._prep_box.configure(values=[describe_duration(s) for s in spec.prep_choices])
            self._speech_box.configure(values=[describe_duration(s) for s in spec.speech_choices])
        self._prep_box.current(spec.prep_choices.index(prep))
        self._speech_box.current(spec.speech_choices.index(speech))
        for box in (self._prep_box, self._speech_box):
            box.state(["!disabled"] if enabled else ["disabled"])

    def _changed(self, event) -> None:
        assert self._spec is not None
        event.widget.selection_clear()
        prep = self._spec.prep_choices[self._prep_box.current()]
        speech = self._spec.speech_choices[self._speech_box.current()]
        self._on_change(prep, speech)
