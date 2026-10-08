"""Palette de couleurs de l'interface et calcul de contraste, sans dépendance à Tkinter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    background: str
    card: str
    accent: str
    accent_hover: str
    text: str
    text_muted: str
    timer_ok: str
    timer_alert: str
    border: str


PALETTE = Palette(
    background="#0F0F12",
    card="#1B1B22",
    accent="#6366F1",
    accent_hover="#4F46E5",
    text="#FFFFFF",
    text_muted="#8E8E93",
    timer_ok="#10B981",
    timer_alert="#EF4444",
    border="#2C2C35",
)


def _linear(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    """Luminance relative d'une couleur « #RRGGBB » (définition WCAG 2)."""
    red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _linear(red) + 0.7152 * _linear(green) + 0.0722 * _linear(blue)


def contrast_ratio(first: str, second: str) -> float:
    """Rapport de contraste entre deux couleurs, de 1 (identiques) à 21 (noir sur blanc)."""
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)
