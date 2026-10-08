import random

import pytest

from unprompted.modes import Mode
from unprompted.picker import pick_topic
from unprompted.topics import THEMES, topics_for


def test_pick_topic_returns_a_topic_of_the_given_list():
    for mode in Mode:
        for theme in THEMES:
            topics = topics_for(mode, theme)
            assert pick_topic(topics) in topics


def test_pick_topic_is_reproducible_with_a_seeded_generator():
    topics = topics_for(Mode.IMPROVISED, THEMES[0])
    assert pick_topic(topics, random.Random(42)) == pick_topic(topics, random.Random(42))


def test_pick_topic_can_reach_every_topic_of_a_theme():
    topics = topics_for(Mode.RESEARCH, THEMES[0])
    rng = random.Random(0)
    seen = {pick_topic(topics, rng) for _ in range(500)}
    assert seen == set(topics)


def test_pick_topic_rejects_empty_list():
    with pytest.raises(ValueError):
        pick_topic(())
