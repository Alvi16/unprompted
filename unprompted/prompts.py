"""Questions posées à l'utilisateur : chacune boucle jusqu'à obtenir une réponse valide."""

from collections.abc import Sequence

from .console import Console
from .durations import describe_duration, parse_duration
from .modes import MODE_SPECS, DurationBounds, Mode
from .topics import THEMES


def _ask_index(console: Console, count: int) -> int:
    """Demande un numéro de 1 à count et renvoie sa position, de 0 à count - 1."""
    while True:
        answer = console.ask(f"Votre choix (1-{count}) : ")
        if answer.isdecimal() and 1 <= int(answer) <= count:
            return int(answer) - 1
        console.say("Choix invalide, recommencez.")


def choose_mode(console: Console) -> Mode:
    modes = list(Mode)
    console.say("Quel mode choisissez-vous ?")
    for number, mode in enumerate(modes, start=1):
        spec = MODE_SPECS[mode]
        console.say(f"  {number}. {spec.label} : {spec.description}")
    return modes[_ask_index(console, len(modes))]


def choose_theme(console: Console, themes: Sequence[str] = THEMES) -> str:
    console.say("Quel thème choisissez-vous ?")
    for number, theme in enumerate(themes, start=1):
        console.say(f"  {number}. {theme}")
    return themes[_ask_index(console, len(themes))]


def ask_duration(console: Console, label: str, bounds: DurationBounds) -> int:
    low = describe_duration(bounds.minimum)
    high = describe_duration(bounds.maximum)
    prompt = f"{label}, de {low} à {high} (ex. 30s, 5m ; sans unité = minutes) : "
    while True:
        try:
            seconds = parse_duration(console.ask(prompt))
        except ValueError as error:
            console.say(str(error))
            continue
        if bounds.contains(seconds):
            return seconds
        console.say(f"Durée hors limites : choisissez entre {low} et {high}.")
