"""Carte centrale : affiche le sujet tiré, ou un message pendant le tirage."""

from tkinter import ttk

from ..topics import Topic
from .widgets import Card

PLACEHOLDER = "Choisissez un thème, puis tirez un sujet."
SIDE_MARGIN = 40
MIN_WRAP = 200


class TopicCard(Card):
    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, padding=16)
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(1, weight=1, minsize=80)
        self._caption = ttk.Label(self.body, style="Muted.Card.TLabel", anchor="center")
        self._caption.grid(row=0, column=0, sticky="ew")
        self._topic = ttk.Label(
            self.body, style="Topic.Card.TLabel", anchor="center", justify="center"
        )
        self._topic.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.body.bind("<Configure>", self._fit_text)
        self.show(None, "")

    def _fit_text(self, event) -> None:
        self._topic.configure(wraplength=max(MIN_WRAP, event.width - SIDE_MARGIN))

    def show(self, topic: Topic | None, intro: str) -> None:
        if topic is None:
            self.show_message(PLACEHOLDER, "")
        else:
            self.show_message(topic.text, f"{intro} · {topic.theme}")

    def show_message(self, text: str, caption: str) -> None:
        self._caption.configure(text=caption.upper())
        self._topic.configure(text=text)
