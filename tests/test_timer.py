import pytest

from unprompted.timer import Countdown, run_countdown


def test_countdown_ticks_each_second_down_to_zero(clock):
    ticks = []
    run_countdown(3, ticks.append, clock.monotonic, clock.sleep)
    assert ticks == [3, 2, 1, 0]


def test_countdown_lasts_the_requested_duration(clock):
    start = clock.now
    run_countdown(15, lambda _: None, clock.monotonic, clock.sleep)
    assert 15 <= clock.now - start < 15.2


def test_countdown_of_zero_ticks_once_and_returns(clock):
    ticks = []
    run_countdown(0, ticks.append, clock.monotonic, clock.sleep)
    assert ticks == [0]


def test_countdown_rejects_negative_duration(clock):
    with pytest.raises(ValueError):
        run_countdown(-1, lambda _: None, clock.monotonic, clock.sleep)


def test_non_blocking_countdown_waits_for_start(clock):
    countdown = Countdown(10, clock.monotonic)
    clock.now += 50
    assert not countdown.running
    assert countdown.remaining() == 10
    assert not countdown.finished


def test_non_blocking_countdown_reaches_zero(clock):
    countdown = Countdown(10, clock.monotonic)
    countdown.start()
    assert countdown.running
    clock.now += 3.2
    assert countdown.remaining() == 7
    clock.now += 6.8
    assert countdown.remaining() == 0
    assert countdown.finished
    clock.now += 100
    assert countdown.remaining() == 0


def test_non_blocking_countdown_pause_and_resume(clock):
    countdown = Countdown(10, clock.monotonic)
    countdown.start()
    clock.now += 4
    countdown.pause()
    assert not countdown.running
    clock.now += 500
    assert countdown.remaining() == 6
    countdown.start()
    clock.now += 6
    assert countdown.finished


def test_non_blocking_countdown_start_and_pause_are_idempotent(clock):
    countdown = Countdown(10, clock.monotonic)
    countdown.pause()
    countdown.start()
    clock.now += 2
    countdown.start()
    clock.now += 2
    assert countdown.remaining() == 6
    countdown.pause()
    countdown.pause()
    assert countdown.remaining() == 6


def test_non_blocking_countdown_of_zero_is_finished_at_once(clock):
    assert Countdown(0, clock.monotonic).finished


def test_non_blocking_countdown_rejects_negative_duration(clock):
    with pytest.raises(ValueError):
        Countdown(-1, clock.monotonic)
