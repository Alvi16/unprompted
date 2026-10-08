"""Étapes d'une session et chronomètre, indépendants de toute interface (aucun import Tkinter).

Une interface (graphique ou autre) lit l'état exposé par SessionFlow pour s'afficher,
lui transmet les actions de l'utilisateur et appelle tick() régulièrement.
"""

import random
import time
from collections.abc import Callable
from enum import Enum

from .modes import MODE_SPECS, SPEECH_LABEL, Mode, ModeSpec
from .picker import pick_topic
from .timer import Countdown
from .topics import THEMES, Topic, topics_for

ALERT_SECONDS = 10


class Stage(Enum):
    IDLE = "idle"
    READY = "ready"
    PREPARING = "preparing"
    SPEAKING = "speaking"
    DONE = "done"


class Event(Enum):
    PREPARATION_ENDED = "preparation_ended"
    SPEECH_ENDED = "speech_ended"


class InvalidAction(Exception):
    """Action demandée à un moment où elle n'est pas permise."""


_RUNNING = (Stage.PREPARING, Stage.SPEAKING)
_EDITABLE = (Stage.IDLE, Stage.READY, Stage.DONE)


class SessionFlow:
    """Machine à états d'une session : mode, thème, sujet, durées, puis les deux chronos."""

    def __init__(
        self,
        rng: random.Random | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._rng = rng
        self._clock = clock
        self._mode = Mode.IMPROVISED
        self._theme: str | None = None
        self._prep_seconds = self.spec.default_prep
        self._speech_seconds = self.spec.default_speech
        self._topic: Topic | None = None
        self._stage = Stage.IDLE
        self._countdown: Countdown | None = None
        self._paused = False

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def spec(self) -> ModeSpec:
        return MODE_SPECS[self._mode]

    @property
    def theme(self) -> str | None:
        return self._theme

    @property
    def topic(self) -> Topic | None:
        return self._topic

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def prep_seconds(self) -> int:
        return self._prep_seconds

    @property
    def speech_seconds(self) -> int:
        return self._speech_seconds

    @property
    def is_running(self) -> bool:
        return self._stage in _RUNNING

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def phase_label(self) -> str:
        if self._stage is Stage.PREPARING:
            return self.spec.prep_label
        if self._stage is Stage.SPEAKING:
            return SPEECH_LABEL
        return ""

    @property
    def _phase_total(self) -> int:
        return self._prep_seconds if self._stage is Stage.PREPARING else self._speech_seconds

    @property
    def remaining_seconds(self) -> int:
        """Secondes restantes de la phase en cours ; durée de préparation avant le départ."""
        if self._countdown is not None and self.is_running:
            return self._countdown.remaining()
        if self._stage is Stage.DONE:
            return 0
        return self._prep_seconds

    @property
    def progress(self) -> float:
        """Part du temps restant de la phase en cours, de 1.0 (début) à 0.0 (fin)."""
        if self.is_running:
            return self.remaining_seconds / self._phase_total
        return 0.0 if self._stage is Stage.DONE else 1.0

    @property
    def in_alert(self) -> bool:
        """Vrai pendant les dernières secondes d'une phase en cours."""
        return self.is_running and self.remaining_seconds <= ALERT_SECONDS

    def set_mode(self, mode: Mode) -> None:
        """Change de mode : le sujet est oublié, le thème gardé, les durées remises par défaut."""
        self._require(*_EDITABLE)
        if mode is self._mode:
            return
        self._mode = mode
        self._prep_seconds = self.spec.default_prep
        self._speech_seconds = self.spec.default_speech
        self._topic = None
        self._stage = Stage.IDLE

    def set_theme(self, theme: str) -> None:
        """Choisit le thème dans lequel le sujet sera tiré. Un autre thème fait oublier le sujet."""
        self._require(*_EDITABLE)
        if theme not in THEMES:
            raise ValueError(f"Thème inconnu : « {theme} ».")
        if theme == self._theme:
            return
        self._theme = theme
        self._topic = None
        self._stage = Stage.IDLE

    def draw_topic(self) -> Topic:
        """Tire un sujet au hasard dans le thème choisi, parmi ceux du mode courant."""
        self._require(*_EDITABLE)
        if self._theme is None:
            raise InvalidAction("Choisissez un thème avant de tirer un sujet.")
        self._topic = pick_topic(topics_for(self._mode, self._theme), self._rng)
        self._stage = Stage.READY
        return self._topic

    def set_durations(self, prep_seconds: int, speech_seconds: int) -> None:
        self._require(*_EDITABLE)
        spec = self.spec
        if not spec.prep_bounds.contains(prep_seconds):
            raise ValueError(f"Durée de {spec.prep_label.lower()} hors limites : {prep_seconds} s.")
        if not spec.speech_bounds.contains(speech_seconds):
            raise ValueError(f"Durée de prise de parole hors limites : {speech_seconds} s.")
        self._prep_seconds = prep_seconds
        self._speech_seconds = speech_seconds

    def start(self) -> None:
        self._require(Stage.READY)
        self._stage = Stage.PREPARING
        self._begin_countdown(self._prep_seconds)

    def toggle_pause(self) -> None:
        self._require(*_RUNNING)
        assert self._countdown is not None
        if self._paused:
            self._countdown.start()
        else:
            self._countdown.pause()
        self._paused = not self._paused

    def reset(self) -> None:
        """Arrête le chrono et revient au sujet tiré (ou à l'accueil s'il n'y en a pas)."""
        self._countdown = None
        self._paused = False
        self._stage = Stage.READY if self._topic is not None else Stage.IDLE

    def tick(self) -> Event | None:
        """À appeler régulièrement. Renvoie l'événement de fin de phase qui vient de se produire."""
        if not self.is_running or self._paused:
            return None
        assert self._countdown is not None
        if not self._countdown.finished:
            return None
        if self._stage is Stage.PREPARING:
            self._stage = Stage.SPEAKING
            self._begin_countdown(self._speech_seconds)
            return Event.PREPARATION_ENDED
        self._stage = Stage.DONE
        self._countdown = None
        return Event.SPEECH_ENDED

    def _begin_countdown(self, seconds: int) -> None:
        self._countdown = Countdown(seconds, self._clock)
        self._countdown.start()

    def _require(self, *stages: Stage) -> None:
        if self._stage not in stages:
            raise InvalidAction(f"Action impossible à l'étape « {self._stage.value} ».")
