"""Entrées/sorties du terminal, isolées pour pouvoir être simulées dans les tests."""

import sys
from collections.abc import Callable

from .durations import format_clock

BELL = "\a"


def _write_now(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


class Console:
    """Seul endroit du programme qui lit le clavier et écrit à l'écran."""

    def __init__(
        self,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = _write_now,
    ) -> None:
        self._read = read
        self._write = write

    def say(self, text: str = "") -> None:
        self._write(text + "\n")

    def ask(self, prompt: str) -> str:
        return self._read(prompt).strip()

    def show_countdown(self, label: str, remaining: int) -> None:
        self._write(f"\r{label} : {format_clock(remaining)}")

    def end_countdown(self) -> None:
        self._write("\n")

    def ring(self) -> None:
        self._write(BELL)
