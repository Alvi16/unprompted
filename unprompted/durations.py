"""Lecture des durées saisies par l'utilisateur et formatage pour l'affichage."""

import re

SECONDS_PER_MINUTE = 60
_DURATION_PATTERN = re.compile(r"^\s*(\d+)\s*(s|sec|m|min)?\s*$", re.IGNORECASE)
_SECOND_UNITS = {"s", "sec"}


def parse_duration(text: str) -> int:
    """Convertit « 30s », « 5m » ou « 5 » (minutes par défaut) en secondes.

    Lève ValueError si le texte n'est pas une durée entière valide.
    """
    match = _DURATION_PATTERN.match(text)
    if match is None:
        raise ValueError(f"Durée illisible : « {text} ».")
    value = int(match.group(1))
    unit = (match.group(2) or "m").lower()
    return value if unit in _SECOND_UNITS else value * SECONDS_PER_MINUTE


def describe_duration(seconds: int) -> str:
    """Forme lisible pour les messages : « 5 min » ou « 90 s »."""
    minutes, rest = divmod(seconds, SECONDS_PER_MINUTE)
    return f"{minutes} min" if rest == 0 else f"{seconds} s"


def format_clock(seconds: int) -> str:
    """Forme chronomètre « mm:ss » ; jamais négative."""
    minutes, rest = divmod(max(0, seconds), SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{rest:02d}"
