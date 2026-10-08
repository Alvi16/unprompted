import pytest

from unprompted.modes import MODE_SPECS, Mode
from unprompted.topics import CATALOGUE, THEMES, Topic, topics_for

MIN_THEMES = 6
TOPICS_PER_THEME = 10
MAX_WORDS = 3


def test_every_mode_has_a_catalogue():
    assert set(CATALOGUE) == set(Mode)


def test_there_are_at_least_six_distinct_themes():
    assert len(THEMES) >= MIN_THEMES
    assert len(set(THEMES)) == len(THEMES)
    assert all(theme.strip() for theme in THEMES)


@pytest.mark.parametrize("mode", list(Mode))
def test_each_mode_covers_exactly_the_shared_themes(mode):
    assert set(CATALOGUE[mode]) == set(THEMES)


@pytest.mark.parametrize("mode", list(Mode))
def test_each_theme_has_ten_topics_in_each_mode(mode):
    for theme in THEMES:
        assert len(CATALOGUE[mode][theme]) == TOPICS_PER_THEME


@pytest.mark.parametrize("mode", list(Mode))
def test_topics_are_unique_within_a_mode(mode):
    texts = [text for theme in THEMES for text in CATALOGUE[mode][theme]]
    assert len(set(texts)) == len(texts)


def test_no_topic_is_shared_between_the_two_modes():
    improvised = {text for theme in THEMES for text in CATALOGUE[Mode.IMPROVISED][theme]}
    research = {text for theme in THEMES for text in CATALOGUE[Mode.RESEARCH][theme]}
    assert improvised.isdisjoint(research)


@pytest.mark.parametrize("mode", list(Mode))
def test_topics_are_short_expressions_not_sentences(mode):
    for theme in THEMES:
        for text in CATALOGUE[mode][theme]:
            assert text.strip() == text
            assert text
            assert not text.endswith(("?", ".", "!"))
            assert len(text.split()) <= MAX_WORDS


@pytest.mark.parametrize("mode", list(Mode))
def test_topics_for_returns_the_topics_of_the_theme_and_mode(mode):
    for theme in THEMES:
        topics = topics_for(mode, theme)
        assert [topic.text for topic in topics] == list(CATALOGUE[mode][theme])
        assert all(isinstance(topic, Topic) and topic.theme == theme for topic in topics)


def test_topics_for_rejects_an_unknown_theme():
    with pytest.raises(ValueError):
        topics_for(Mode.IMPROVISED, "Inconnu")


def test_bounds_are_coherent():
    for spec in MODE_SPECS.values():
        for bounds in (spec.prep_bounds, spec.speech_bounds):
            assert 0 < bounds.minimum < bounds.maximum


def test_research_allows_longer_preparation_than_improvised():
    improvised = MODE_SPECS[Mode.IMPROVISED].prep_bounds
    research = MODE_SPECS[Mode.RESEARCH].prep_bounds
    assert research.maximum > improvised.maximum
    assert research.minimum > improvised.minimum
