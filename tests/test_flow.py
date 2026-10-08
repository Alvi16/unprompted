import random

import pytest

from unprompted.flow import ALERT_SECONDS, Event, InvalidAction, SessionFlow, Stage
from unprompted.modes import MODE_SPECS, SPEECH_LABEL, Mode
from unprompted.topics import CATALOGUE, THEMES


@pytest.fixture
def flow(clock):
    return SessionFlow(rng=random.Random(0), clock=clock.monotonic)


def _ready(flow, prep=15, speech=60):
    flow.set_theme(THEMES[0])
    flow.set_durations(prep, speech)
    flow.draw_topic()


def test_initial_state_has_no_theme_and_improvised_defaults(flow):
    spec = MODE_SPECS[Mode.IMPROVISED]
    assert flow.stage is Stage.IDLE
    assert flow.mode is Mode.IMPROVISED
    assert flow.theme is None
    assert flow.topic is None
    assert flow.prep_seconds == spec.default_prep
    assert flow.speech_seconds == spec.default_speech
    assert flow.remaining_seconds == spec.default_prep
    assert flow.progress == 1.0
    assert not flow.is_running


def test_draw_topic_requires_a_theme(flow):
    with pytest.raises(InvalidAction):
        flow.draw_topic()


def test_draw_topic_picks_from_the_chosen_theme(flow):
    for theme in THEMES:
        flow.set_theme(theme)
        topic = flow.draw_topic()
        assert topic.theme == theme
        assert topic.text in CATALOGUE[Mode.IMPROVISED][theme]
        assert flow.topic is topic
        assert flow.stage is Stage.READY


def test_draw_topic_picks_from_the_catalogue_of_the_current_mode(flow):
    other = {Mode.IMPROVISED: Mode.RESEARCH, Mode.RESEARCH: Mode.IMPROVISED}
    for mode in Mode:
        flow.set_mode(mode)
        for theme in THEMES:
            flow.set_theme(theme)
            for _ in range(20):
                text = flow.draw_topic().text
                assert text in CATALOGUE[mode][theme]
                assert text not in CATALOGUE[other[mode]][theme]


def test_set_theme_rejects_an_unknown_theme(flow):
    with pytest.raises(ValueError):
        flow.set_theme("Inconnu")


def test_choosing_another_theme_forgets_the_topic(flow):
    flow.set_theme(THEMES[0])
    flow.draw_topic()
    flow.set_theme(THEMES[1])
    assert flow.theme == THEMES[1]
    assert flow.topic is None
    assert flow.stage is Stage.IDLE


def test_choosing_the_same_theme_keeps_the_topic(flow):
    flow.set_theme(THEMES[0])
    topic = flow.draw_topic()
    flow.set_theme(THEMES[0])
    assert flow.topic is topic
    assert flow.stage is Stage.READY


def test_start_requires_a_drawn_topic(flow):
    with pytest.raises(InvalidAction):
        flow.start()
    flow.set_theme(THEMES[0])
    with pytest.raises(InvalidAction):
        flow.start()


def test_full_session_goes_through_both_phases(flow, clock):
    _ready(flow)
    flow.start()
    assert flow.stage is Stage.PREPARING
    assert flow.phase_label == MODE_SPECS[Mode.IMPROVISED].prep_label
    assert flow.remaining_seconds == 15

    clock.now += 14.5
    assert flow.tick() is None
    assert flow.remaining_seconds == 1

    clock.now += 0.5
    assert flow.tick() is Event.PREPARATION_ENDED
    assert flow.stage is Stage.SPEAKING
    assert flow.phase_label == SPEECH_LABEL
    assert flow.remaining_seconds == 60

    clock.now += 60
    assert flow.tick() is Event.SPEECH_ENDED
    assert flow.stage is Stage.DONE
    assert flow.remaining_seconds == 0
    assert flow.progress == 0.0
    assert not flow.is_running


def test_tick_does_nothing_outside_a_running_phase(flow, clock):
    assert flow.tick() is None
    _ready(flow)
    clock.now += 1000
    assert flow.tick() is None


def test_pause_freezes_the_time_and_resume_continues(flow, clock):
    _ready(flow)
    flow.start()
    clock.now += 5
    flow.toggle_pause()
    assert flow.is_paused
    clock.now += 100
    assert flow.tick() is None
    assert flow.remaining_seconds == 10

    flow.toggle_pause()
    assert not flow.is_paused
    clock.now += 10
    assert flow.tick() is Event.PREPARATION_ENDED


def test_toggle_pause_requires_a_running_phase(flow):
    with pytest.raises(InvalidAction):
        flow.toggle_pause()


def test_progress_decreases_over_the_phase(flow, clock):
    _ready(flow, prep=20)
    flow.start()
    assert flow.progress == 1.0
    clock.now += 10
    assert flow.progress == pytest.approx(0.5)


def test_alert_starts_in_the_last_seconds(flow, clock):
    _ready(flow, prep=30)
    assert not flow.in_alert
    flow.start()
    clock.now += 30 - ALERT_SECONDS - 1
    assert not flow.in_alert
    clock.now += 1
    assert flow.remaining_seconds == ALERT_SECONDS
    assert flow.in_alert


def test_set_mode_keeps_the_theme_but_forgets_the_topic(flow):
    _ready(flow, prep=60, speech=180)
    flow.set_mode(Mode.RESEARCH)
    spec = MODE_SPECS[Mode.RESEARCH]
    assert flow.theme == THEMES[0]
    assert flow.stage is Stage.IDLE
    assert flow.topic is None
    assert flow.prep_seconds == spec.default_prep
    assert flow.speech_seconds == spec.default_speech


def test_selecting_the_current_mode_keeps_the_session(flow):
    flow.set_theme(THEMES[0])
    topic = flow.draw_topic()
    flow.set_mode(Mode.IMPROVISED)
    assert flow.topic is topic
    assert flow.stage is Stage.READY


def test_edits_are_refused_while_running(flow):
    _ready(flow)
    flow.start()
    with pytest.raises(InvalidAction):
        flow.set_mode(Mode.RESEARCH)
    with pytest.raises(InvalidAction):
        flow.set_theme(THEMES[1])
    with pytest.raises(InvalidAction):
        flow.draw_topic()
    with pytest.raises(InvalidAction):
        flow.set_durations(30, 60)


def test_set_durations_rejects_values_outside_the_mode_bounds(flow):
    with pytest.raises(ValueError):
        flow.set_durations(10, 60)
    with pytest.raises(ValueError):
        flow.set_durations(30, 600)
    flow.set_mode(Mode.RESEARCH)
    flow.set_durations(3600, 600)
    assert (flow.prep_seconds, flow.speech_seconds) == (3600, 600)


def test_reset_returns_to_the_drawn_topic(flow, clock):
    _ready(flow)
    topic = flow.topic
    flow.start()
    clock.now += 3
    flow.reset()
    assert flow.stage is Stage.READY
    assert flow.topic is topic
    assert not flow.is_paused
    assert flow.remaining_seconds == 15


def test_reset_without_topic_returns_to_idle(flow):
    flow.reset()
    assert flow.stage is Stage.IDLE


def test_reset_after_the_end_allows_a_new_run(flow, clock):
    _ready(flow)
    flow.start()
    clock.now += 15
    flow.tick()
    clock.now += 60
    flow.tick()
    flow.reset()
    flow.start()
    assert flow.stage is Stage.PREPARING
    assert flow.remaining_seconds == 15
