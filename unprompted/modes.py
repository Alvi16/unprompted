"""Définition des deux modes d'entraînement et des contraintes propres à chacun."""

from dataclasses import dataclass
from enum import Enum

SPEECH_LABEL = "Prise de parole"


class Mode(Enum):
    IMPROVISED = "improvised"
    RESEARCH = "research"


@dataclass(frozen=True)
class DurationBounds:
    """Intervalle de durées autorisées, en secondes (bornes incluses)."""

    minimum: int
    maximum: int

    def contains(self, seconds: int) -> bool:
        return self.minimum <= seconds <= self.maximum


@dataclass(frozen=True)
class ModeSpec:
    """Tout ce qui distingue un mode d'un autre : textes affichés et durées permises.

    prep_choices et speech_choices sont les durées proposées par une interface à
    liste déroulante ; elles restent comprises dans les bornes du mode.
    """

    label: str
    description: str
    topic_intro: str
    prep_label: str
    prep_bounds: DurationBounds
    speech_bounds: DurationBounds
    prep_choices: tuple[int, ...]
    speech_choices: tuple[int, ...]
    default_prep: int
    default_speech: int


MODE_SPECS: dict[Mode, ModeSpec] = {
    Mode.IMPROVISED: ModeSpec(
        label="Improvisé",
        description="sujets simples, courte préparation, vous parlez sur le vif.",
        topic_intro="Sujet",
        prep_label="Préparation",
        prep_bounds=DurationBounds(minimum=15, maximum=5 * 60),
        speech_bounds=DurationBounds(minimum=60, maximum=5 * 60),
        prep_choices=(15, 30, 60, 120, 180, 300),
        speech_choices=(60, 120, 180, 300),
        default_prep=30,
        default_speech=120,
    ),
    Mode.RESEARCH: ModeSpec(
        label="Recherche",
        description="notions approfondies, vous les étudiez puis vous les expliquez.",
        topic_intro="Sujet à étudier puis à expliquer",
        prep_label="Recherche",
        prep_bounds=DurationBounds(minimum=60, maximum=60 * 60),
        speech_bounds=DurationBounds(minimum=60, maximum=10 * 60),
        prep_choices=(60, 300, 600, 900, 1200, 1800, 2700, 3600),
        speech_choices=(60, 120, 180, 300, 600),
        default_prep=600,
        default_speech=180,
    ),
}
