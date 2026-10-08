"""Ouverture réelle de la fenêtre. Ignoré lorsqu'aucun écran n'est disponible."""

import random
import tkinter

import pytest

from unprompted.flow import SessionFlow, Stage
from unprompted.gui.app import UnpromptedApp
from unprompted.modes import Mode
from unprompted.topics import CATALOGUE, THEMES


def _display_available() -> bool:
    try:
        tkinter.Tk().destroy()
    except tkinter.TclError:
        return False
    return True


pytestmark = pytest.mark.skipif(not _display_available(), reason="aucun écran disponible")


@pytest.fixture
def rings():
    return []


@pytest.fixture
def app(clock, rings, monkeypatch):
    flow = SessionFlow(rng=random.Random(0), clock=clock.monotonic)
    window = UnpromptedApp(flow=flow, spin_frames=0)
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
