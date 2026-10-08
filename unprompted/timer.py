"""Comptes à rebours, indépendants de tout affichage : l'horloge et la pause sont injectables."""

import math
import time
from collections.abc import Callable

POLL_INTERVAL_S = 0.1


class Countdown:
    """Compte à rebours non bloquant, avec pause : l'appelant l'interroge quand il veut.

    L'échéance est calculée sur l'horloge monotone au démarrage, donc le temps
    restant ne dérive pas, quelle que soit la fréquence des interrogations.
    """

    def __init__(self, duration_s: int, clock: Callable[[], float] = time.monotonic) -> None:
        if duration_s < 0:
            raise ValueError("La durée ne peut pas être négative.")
        self._clock = clock
        self._left = float(duration_s)
        self._deadline: float | None = None

    @property
    def running(self) -> bool:
        return self._deadline is not None

    def start(self) -> None:
        """Démarre, ou reprend après une pause. Sans effet s'il tourne déjà."""
        if self._deadline is None:
            self._deadline = self._clock() + self._left

    def pause(self) -> None:
        """Fige le temps restant. Sans effet s'il est déjà en pause."""
        if self._deadline is not None:
            self._left = max(0.0, self._deadline - self._clock())
            self._deadline = None

    def remaining(self) -> int:
        """Secondes entières restantes, arrondies au supérieur, jamais négatives."""
        left = self._left if self._deadline is None else self._deadline - self._clock()
        return max(0, math.ceil(left))

    @property
    def finished(self) -> bool:
        return self.remaining() == 0


def run_countdown(
    duration_s: int,
    on_tick: Callable[[int], None],
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Décompte en bloquant jusqu'à zéro et appelle on_tick à chaque seconde entière restante.

    on_tick reçoit les secondes restantes, de duration_s jusqu'à 0 inclus.
    """
    countdown = Countdown(duration_s, clock)
    countdown.start()
    last_shown: int | None = None
    while True:
        remaining = countdown.remaining()
        if remaining != last_shown:
            on_tick(remaining)
            last_shown = remaining
        if remaining == 0:
            return
        sleep(POLL_INTERVAL_S)
