import random
import re

from unprompted.modes import MODE_SPECS, Mode
from unprompted.session import SIGNAL_REPEATS, run_session
from unprompted.topics import CATALOGUE, THEMES


def _run(make_console, clock, answers):
    console, transcript = make_console(answers)
    start = clock.now
    run_session(console, random.Random(1), clock.monotonic, clock.sleep)
    return "".join(transcript), clock.now - start


def _drawn_topic(output, mode):
    intro = MODE_SPECS[mode].topic_intro
    return re.search(rf"^{re.escape(intro)} : (.+)$", output, re.MULTILINE).group(1)


def test_improvised_session_follows_the_expected_order(make_console, clock):
    output, _ = _run(make_console, clock, ["1", "1", "15s", "1m"])

    steps = [
        "Quel mode choisissez-vous ?",
        "Quel thème choisissez-vous ?",
        "Le choix aléatoire est en cours",
        "Sujet :",
        "(Thème : ",
        "Temps de préparation",
        "Temps de prise de parole",
        "Préparation : 15 s, c'est parti.",
        "Temps de préparation écoulé !",
        "Prise de parole : 1 min, c'est parti.",
        "Temps de prise de parole écoulé !",
        "Session terminée.",
    ]
    positions = [output.index(step) for step in steps]
    assert positions == sorted(positions)


def test_displayed_topic_belongs_to_the_chosen_theme(make_console, clock):
    for position, theme in enumerate(THEMES, start=1):
        output, _ = _run(make_console, clock, ["1", str(position), "15s", "1m"])
        assert _drawn_topic(output, Mode.IMPROVISED) in CATALOGUE[Mode.IMPROVISED][theme]
        assert f"(Thème : {theme})" in output


def test_research_session_uses_research_wording(make_console, clock):
    output, _ = _run(make_console, clock, ["2", "3", "1m", "2m"])
    assert "Sujet à étudier puis à expliquer :" in output
    assert _drawn_topic(output, Mode.RESEARCH) in CATALOGUE[Mode.RESEARCH][THEMES[2]]
    assert "Temps de recherche écoulé !" in output


def test_a_signal_rings_at_the_end_of_each_phase(make_console, clock):
    output, _ = _run(make_console, clock, ["1", "1", "15s", "1m"])
    assert output.count("\a") == 2 * SIGNAL_REPEATS


def test_total_duration_is_preparation_plus_speech(make_console, clock):
    _, elapsed = _run(make_console, clock, ["1", "1", "15s", "1m"])
    expected = 15 + 60 + 2 * SIGNAL_REPEATS * 0.4
    assert expected <= elapsed < expected + 0.5
