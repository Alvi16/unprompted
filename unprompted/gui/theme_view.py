"""Bloc de choix du thème : une grille de boutons, un seul actif à la fois."""

from collections.abc import Callable, Sequence
from tkinter import ttk

COLUMNS = 4


class ThemeSelector(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        themes: Sequence[str],
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        ttk.Label(self, text="THÈME", style="Caption.TLabel").grid(
            row=0, column=0, columnspan=COLUMNS, sticky="w", pady=(0, 4)
        )
        self._buttons: dict[str, ttk.Button] = {}
        for index, theme in enumerate(themes):
            row, column = divmod(index, COLUMNS)
            button = ttk.Button(
                self,
                text=theme,
                style="Chip.TButton",
                command=lambda selected=theme: on_select(selected),
            )
            button.grid(row=row + 1, column=column, sticky="ew", padx=3, pady=3)
            self._buttons[theme] = button
        for column in range(COLUMNS):
            self.columnconfigure(column, weight=1, uniform="themes")

    def show(self, selected: str | None, enabled: bool) -> None:
        for theme, button in self._buttons.items():
            button.configure(style="ChipOn.TButton" if theme == selected else "Chip.TButton")
            button.state(["!disabled"] if enabled else ["disabled"])
