"""Éléments d'interface partagés par plusieurs blocs."""

from tkinter import ttk


class Card(ttk.Frame):
    """Cadre à fond de carte entouré d'une bordure fine d'un pixel.

    Les éléments se placent dans card.body, pas dans la carte elle-même.
    """

    def __init__(self, parent: ttk.Frame, padding: int = 20) -> None:
        super().__init__(parent, style="Border.TFrame", padding=1)
        self.body = ttk.Frame(self, style="Card.TFrame", padding=padding)
        self.body.pack(fill="both", expand=True)
