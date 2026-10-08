"""Tirage aléatoire d'un sujet parmi ceux d'un mode."""

import random
from collections.abc import Sequence

from .topics import Topic


def pick_topic(topics: Sequence[Topic], rng: random.Random | None = None) -> Topic:
    """Retourne un sujet au hasard. Le générateur est injectable pour les tests."""
    if not topics:
        raise ValueError("Aucun sujet disponible pour ce mode.")
    chooser = rng if rng is not None else random.Random()
    return chooser.choice(topics)
