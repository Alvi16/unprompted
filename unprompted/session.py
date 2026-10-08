"""Déroulement d'une session complète : mode, thème, tirage, durées, puis les deux chronos."""

import random
import time
from collections.abc import Callable

from .console import Console
from .durations import describe_duration
from .modes import MODE_SPECS, SPEECH_LABEL
from .picker import pick_topic
from .prompts import ask_duration, choose_mode, choose_theme
from .timer import run_countdown
from .topics import topics_for

SIGNAL_REPEATS = 3
SIGNAL_INTERVAL_S = 0.4


def run_session(
    console: Console,
    rng: random.Random | None = None,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    mode = choose_mode(console)
    spec = MODE_SPECS[mode]
    console.say()
    theme = choose_theme(console)

    console.say()
    console.say("Le choix aléatoire est en cours…")
    topic = pick_topic(topics_for(mode, theme), rng)
    console.say(f"{spec.topic_intro} : {topic.text}")
    console.say(f"(Thème : {topic.theme})")
    console.say()

    prep_seconds = ask_duration(console, f"Temps de {spec.prep_label.lower()}", spec.prep_bounds)
    speech_seconds = ask_duration(console, "Temps de prise de parole", spec.speech_bounds)

    _run_phase(console, spec.prep_label, prep_seconds, clock, sleep)
    _run_phase(console, SPEECH_LABEL, speech_seconds, clock, sleep)
    console.say("Session terminée.")


def _run_phase(
    console: Console,
    label: str,
    seconds: int,
    clock: Callable[[], float],
    sleep: Callable[[float], None],
) -> None:
    console.say()
    console.say(f"{label} : {describe_duration(seconds)}, c'est parti.")
    run_countdown(seconds, lambda remaining: console.show_countdown(label, remaining), clock, sleep)
    console.end_countdown()
    console.say(f"Temps de {label.lower()} écoulé !")
    for _ in range(SIGNAL_REPEATS):
        console.ring()
        sleep(SIGNAL_INTERVAL_S)
