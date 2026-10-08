import pytest

from unprompted.modes import DurationBounds, Mode
from unprompted.prompts import ask_duration, choose_mode, choose_theme
from unprompted.topics import THEMES


@pytest.mark.parametrize(("answer", "expected"), [("1", Mode.IMPROVISED), ("2", Mode.RESEARCH)])
def test_choose_mode_returns_the_selected_mode(make_console, answer, expected):
    console, _ = make_console([answer])
    assert choose_mode(console) is expected


def test_choose_mode_asks_again_after_invalid_answers(make_console):
    console, transcript = make_console(["x", "0", "3", "", "2"])
    assert choose_mode(console) is Mode.RESEARCH
    assert "".join(transcript).count("Choix invalide") == 4


def test_choose_theme_lists_every_theme(make_console):
    console, transcript = make_console(["1"])
    choose_theme(console)
    text = "".join(transcript)
    for number, theme in enumerate(THEMES, start=1):
        assert f"{number}. {theme}" in text


def test_choose_theme_returns_the_selected_theme(make_console):
    for position, theme in enumerate(THEMES, start=1):
        console, _ = make_console([str(position)])
        assert choose_theme(console) == theme


def test_choose_theme_asks_again_after_invalid_answers(make_console):
    too_high = str(len(THEMES) + 1)
    console, transcript = make_console(["x", "0", too_high, "2"])
    assert choose_theme(console) == THEMES[1]
    assert "".join(transcript).count("Choix invalide") == 3


def test_ask_duration_returns_seconds_for_a_valid_answer(make_console):
    console, _ = make_console(["30s"])
    assert ask_duration(console, "Temps", DurationBounds(15, 300)) == 30


def test_ask_duration_rejects_unreadable_answers(make_console):
    console, transcript = make_console(["abc", "2m"])
    assert ask_duration(console, "Temps", DurationBounds(15, 300)) == 120
    assert "Durée illisible" in "".join(transcript)


def test_ask_duration_rejects_out_of_bounds_answers(make_console):
    console, transcript = make_console(["10s", "6m", "5m"])
    assert ask_duration(console, "Temps", DurationBounds(15, 300)) == 300
    assert "".join(transcript).count("hors limites") == 2
