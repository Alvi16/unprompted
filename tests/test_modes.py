from unprompted.modes import MODE_SPECS, SPEECH_LABEL, Mode


def test_choices_are_sorted_unique_and_inside_the_bounds():
    for spec in MODE_SPECS.values():
        for choices, bounds in (
            (spec.prep_choices, spec.prep_bounds),
            (spec.speech_choices, spec.speech_bounds),
        ):
            assert list(choices) == sorted(set(choices))
            assert all(bounds.contains(seconds) for seconds in choices)


def test_defaults_are_among_the_choices():
    for spec in MODE_SPECS.values():
        assert spec.default_prep in spec.prep_choices
        assert spec.default_speech in spec.speech_choices


def test_the_extreme_bounds_are_offered_as_choices():
    for spec in MODE_SPECS.values():
        assert spec.prep_choices[0] == spec.prep_bounds.minimum
        assert spec.prep_choices[-1] == spec.prep_bounds.maximum
        assert spec.speech_choices[0] == spec.speech_bounds.minimum
        assert spec.speech_choices[-1] == spec.speech_bounds.maximum


def test_labels_are_distinct_between_modes():
    labels = {spec.label for spec in MODE_SPECS.values()}
    assert len(labels) == len(Mode)
    assert all(spec.prep_label != SPEECH_LABEL for spec in MODE_SPECS.values())
