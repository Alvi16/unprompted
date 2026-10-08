"""Outils de test partagés : horloge simulée et console scriptée."""

import pytest

from unprompted.console import Console


class FakeClock:
    """Horloge dont la pause fait avancer le temps sans attendre réellement."""

    def __init__(self) -> None:
        self.now = 1000.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def make_console():
    """Fabrique une console qui répond avec les réponses données et enregistre tout."""

    def factory(answers: list[str]) -> tuple[Console, list[str]]:
        pending = iter(answers)
        transcript: list[str] = []

        def read(prompt: str) -> str:
            transcript.append(prompt)
            answer = next(pending, None)
            if answer is None:
                raise EOFError
            return answer

        return Console(read=read, write=transcript.append), transcript

    return factory
