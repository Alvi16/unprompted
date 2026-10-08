import pytest

from unprompted.gui.palette import PALETTE, contrast_ratio

# Seuils WCAG 2 : 4,5 pour du texte courant, 3 pour du texte en gros caractères
# (14 pt gras ou plus, ce qui est le cas des boutons et du chrono).
NORMAL_TEXT = 4.5
LARGE_TEXT = 3.0


def test_contrast_ratio_known_values():
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)
    assert contrast_ratio("#123456", "#FEDCBA") == contrast_ratio("#FEDCBA", "#123456")


@pytest.mark.parametrize("surface", [PALETTE.background, PALETTE.card])
def test_body_text_is_readable_on_every_surface(surface):
    assert contrast_ratio(PALETTE.text, surface) >= NORMAL_TEXT
    assert contrast_ratio(PALETTE.text_muted, surface) >= NORMAL_TEXT


def test_timer_colours_are_readable_on_the_card():
    assert contrast_ratio(PALETTE.timer_ok, PALETTE.card) >= NORMAL_TEXT
    assert contrast_ratio(PALETTE.timer_alert, PALETTE.card) >= NORMAL_TEXT


def test_button_labels_are_readable_on_the_accent_colours():
    assert contrast_ratio(PALETTE.text, PALETTE.accent) >= LARGE_TEXT
    assert contrast_ratio(PALETTE.text, PALETTE.accent_hover) >= NORMAL_TEXT
