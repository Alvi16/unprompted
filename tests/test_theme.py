from unprompted.gui.theme import MONO_FAMILIES, SANS_FAMILIES, pick_family


def test_pick_family_returns_the_first_installed_candidate():
    available = ["DejaVu Sans", "Noto Sans"]
    assert pick_family(available, SANS_FAMILIES, "Fallback") == "Noto Sans"


def test_pick_family_prefers_the_earliest_candidate():
    available = ["JetBrains Mono", "Liberation Mono"]
    assert pick_family(available, MONO_FAMILIES, "Fallback") == "JetBrains Mono"


def test_pick_family_uses_the_fallback_when_nothing_matches():
    assert pick_family(["Comic Sans"], SANS_FAMILIES, "Fallback") == "Fallback"
