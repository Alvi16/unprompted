"""Ouverture réelle de la fenêtre.

Si l'environnement ne permet pas de démarrer Tk (aucun écran, fichiers d'initialisation
illisibles), les tests sont ignorés avec la cause. Toute autre erreur reste un échec.
"""

import random
import time
import tkinter

import pytest

from unprompted.flow import SessionFlow, Stage
from unprompted.gui.app import UnpromptedApp
from unprompted.modes import Mode
from unprompted.topics import CATALOGUE, THEMES

TK_START_ATTEMPTS = 3
TK_RETRY_DELAY_S = 0.5
ENVIRONMENT_FAILURE_MARKERS = ("init.tcl", "tcl_findLibrary", "display")


def _is_environment_failure(error: tkinter.TclError) -> bool:
    return any(marker in str(error) for marker in ENVIRONMENT_FAILURE_MARKERS)


def _open_window(flow: SessionFlow) -> UnpromptedApp:
    for attempt in range(1, TK_START_ATTEMPTS + 1):
        try:
            return UnpromptedApp(flow=flow, spin_frames=0)
        except tkinter.TclError as error:
            if not _is_environment_failure(error):
                raise
            if attempt == TK_START_ATTEMPTS:
                pytest.skip(f"Tk ne démarre pas dans cet environnement : {error}")
            time.sleep(TK_RETRY_DELAY_S)
    raise AssertionError("inaccessible")


@pytest.fixture
def rings():
    return []


@pytest.fixture
def app(clock, rings, monkeypatch):
    flow = SessionFlow(rng=random.Random(0), clock=clock.monotonic)
    window = _open_window(flow)
    window.withdraw()
    monkeypatch.setattr(window, "bell", lambda *args, **kwargs: rings.append(1))
    yield window
    window.close()


def test_window_opens_with_nothing_to_draw_or_start(app):
    assert app.title() == "Unprompted — prise de parole"
    assert app.draw_button.instate(["disabled"])
    assert app.timer_panel.primary_button.instate(["disabled"])
    assert app.timer_panel.reset_button.instate(["disabled"])


def test_the_window_offers_every_theme(app):
    assert list(app.theme_selector._buttons) == list(THEMES)


def test_choosing_a_theme_enables_the_draw_button(app):
    app.choose_theme(THEMES[2])
    assert app._flow.theme == THEMES[2]
    assert app.draw_button.instate(["!disabled"])
    assert app.timer_panel.primary_button.instate(["disabled"])


def test_drawing_a_topic_comes_from_the_chosen_theme(app):
    app.choose_theme(THEMES[1])
    app.draw_topic()
    assert app._flow.stage is Stage.READY
    assert app._flow.topic.text in CATALOGUE[Mode.IMPROVISED][THEMES[1]]
    assert app.timer_panel.primary_button.instate(["!disabled"])


def test_the_research_mode_draws_from_its_own_catalogue(app):
    app.choose_mode(Mode.RESEARCH)
    app.choose_theme(THEMES[0])
    app.draw_topic()
    assert app._flow.topic.text in CATALOGUE[Mode.RESEARCH][THEMES[0]]
    assert app._flow.topic.text not in CATALOGUE[Mode.IMPROVISED][THEMES[0]]


def test_drawing_without_a_theme_does_nothing(app):
    app.draw_topic()
    assert app._flow.stage is Stage.IDLE
    assert app._flow.topic is None


def test_full_session_rings_at_the_end_of_each_phase(app, clock, rings):
    app.choose_theme(THEMES[0])
    app.set_durations(15, 60)
    app.draw_topic()
    app.press_primary()
    assert app._flow.stage is Stage.PREPARING

    clock.now += 15
    app.poll()
    assert app._flow.stage is Stage.SPEAKING
    assert len(rings) == 1

    clock.now += 60
    app.poll()
    assert app._flow.stage is Stage.DONE
    assert len(rings) == 2
    assert app.timer_panel.primary_button.cget("text") == "Recommencer"


def test_controls_are_locked_while_the_clock_runs(app):
    app.choose_theme(THEMES[0])
    app.draw_topic()
    app.press_primary()
    app.choose_mode(Mode.RESEARCH)
    app.choose_theme(THEMES[1])
    assert app._flow.mode is Mode.IMPROVISED
    assert app._flow.theme == THEMES[0]
    assert app.draw_button.instate(["disabled"])
    assert app.mode_selector._buttons[Mode.RESEARCH].instate(["disabled"])
    assert app.theme_selector._buttons[THEMES[1]].instate(["disabled"])


def test_pause_and_reset_buttons(app):
    app.choose_theme(THEMES[0])
    app.draw_topic()
    app.press_primary()
    assert app.timer_panel.primary_button.cget("text") == "Pause"
    app.press_primary()
    assert app._flow.is_paused
    assert app.timer_panel.primary_button.cget("text") == "Reprendre"
    app.press_reset()
    assert app._flow.stage is Stage.READY
    assert app.draw_button.instate(["!disabled"])
