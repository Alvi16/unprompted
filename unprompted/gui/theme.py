"""Polices et styles ttk de l'interface : le thème « clam » personnalisé avec la palette."""

import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from tkinter import ttk

from .palette import Palette

SANS_FAMILIES = ("Inter", "Noto Sans", "DejaVu Sans")
MONO_FAMILIES = ("JetBrains Mono", "DejaVu Sans Mono", "Liberation Mono")

Font = tuple[str, int, str]


@dataclass(frozen=True)
class Fonts:
    title: Font
    subtitle: Font
    body: Font
    button: Font
    chip: Font
    topic: Font
    caption: Font
    timer: Font


def pick_family(available: Iterable[str], candidates: Sequence[str], fallback: str) -> str:
    """Première police candidate réellement installée, sinon la police de secours."""
    installed = set(available)
    return next((name for name in candidates if name in installed), fallback)


def build_fonts(root: tk.Misc) -> Fonts:
    installed = tkfont.families(root)
    default_sans = tkfont.nametofont("TkDefaultFont", root=root).actual("family")
    default_mono = tkfont.nametofont("TkFixedFont", root=root).actual("family")
    sans = pick_family(installed, SANS_FAMILIES, default_sans)
    mono = pick_family(installed, MONO_FAMILIES, default_mono)
    return Fonts(
        title=(sans, 22, "bold"),
        subtitle=(sans, 12, "normal"),
        body=(sans, 11, "normal"),
        button=(sans, 14, "bold"),
        chip=(sans, 11, "bold"),
        topic=(sans, 22, "bold"),
        caption=(sans, 10, "bold"),
        timer=(mono, 64, "bold"),
    )


def apply_style(root: tk.Tk, palette: Palette, fonts: Fonts) -> None:
    """Configure le thème « clam » : aucun élément gris par défaut ne doit subsister."""
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(background=palette.background)

    style.configure(
        ".",
        background=palette.background,
        foreground=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.background,
        darkcolor=palette.background,
        troughcolor=palette.background,
        focuscolor=palette.text,
        font=fonts.body,
    )

    _style_containers(style, palette)
    _style_labels(style, palette, fonts)
    _style_buttons(style, palette, fonts)
    _style_combobox(root, style, palette, fonts)
    _style_progressbar(style, palette)


def _style_containers(style: ttk.Style, palette: Palette) -> None:
    style.configure("TFrame", background=palette.background)
    style.configure("Card.TFrame", background=palette.card)
    style.configure("Border.TFrame", background=palette.border)


def _style_labels(style: ttk.Style, palette: Palette, fonts: Fonts) -> None:
    style.configure("TLabel", background=palette.background, foreground=palette.text)
    style.configure("Title.TLabel", font=fonts.title)
    style.configure("Subtitle.TLabel", foreground=palette.text_muted, font=fonts.subtitle)
    style.configure("Caption.TLabel", foreground=palette.text_muted, font=fonts.caption)
    style.configure("Card.TLabel", background=palette.card)
    style.configure("Muted.Card.TLabel", foreground=palette.text_muted, font=fonts.caption)
    style.configure("Topic.Card.TLabel", font=fonts.topic)
    style.configure("Status.Card.TLabel", font=fonts.subtitle)
    style.configure("Alert.Status.Card.TLabel", foreground=palette.timer_alert)
    style.configure("Timer.Card.TLabel", foreground=palette.timer_ok, font=fonts.timer)
    style.configure("Alert.Timer.Card.TLabel", foreground=palette.timer_alert)


def _button(
    style: ttk.Style,
    name: str,
    *,
    fill: str,
    hover: str,
    text: str,
    border: str,
    disabled_fill: str,
    palette: Palette,
) -> None:
    style.configure(
        name,
        background=fill,
        foreground=text,
        bordercolor=border,
        lightcolor=fill,
        darkcolor=fill,
        relief="flat",
    )
    style.map(
        name,
        background=[("disabled", disabled_fill), ("pressed", hover), ("active", hover)],
        foreground=[("disabled", palette.text_muted)],
        bordercolor=[("disabled", palette.border)],
        lightcolor=[("disabled", disabled_fill), ("pressed", hover), ("active", hover)],
        darkcolor=[("disabled", disabled_fill), ("pressed", hover), ("active", hover)],
        relief=[("pressed", "flat"), ("!pressed", "flat")],
    )


def _style_buttons(style: ttk.Style, palette: Palette, fonts: Fonts) -> None:
    style.configure("TButton", font=fonts.button, padding=(20, 12), borderwidth=1)
    _button(
        style,
        "Primary.TButton",
        fill=palette.accent,
        hover=palette.accent_hover,
        text=palette.text,
        border=palette.accent,
        disabled_fill=palette.border,
        palette=palette,
    )
    _button(
        style,
        "Secondary.TButton",
        fill=palette.card,
        hover=palette.border,
        text=palette.text,
        border=palette.border,
        disabled_fill=palette.card,
        palette=palette,
    )
    _button(
        style,
        "Segment.TButton",
        fill=palette.card,
        hover=palette.border,
        text=palette.text_muted,
        border=palette.card,
        disabled_fill=palette.card,
        palette=palette,
    )
    _button(
        style,
        "SegmentOn.TButton",
        fill=palette.accent,
        hover=palette.accent_hover,
        text=palette.text,
        border=palette.accent,
        disabled_fill=palette.accent,
        palette=palette,
    )
    style.map("SegmentOn.TButton", foreground=[("disabled", palette.text)])
    _button(
        style,
        "Chip.TButton",
        fill=palette.card,
        hover=palette.border,
        text=palette.text_muted,
        border=palette.border,
        disabled_fill=palette.card,
        palette=palette,
    )
    style.configure("Chip.TButton", font=fonts.chip, padding=(8, 8))
    _button(
        style,
        "ChipOn.TButton",
        fill=palette.accent,
        hover=palette.accent_hover,
        text=palette.text,
        border=palette.accent,
        disabled_fill=palette.accent,
        palette=palette,
    )
    style.configure("ChipOn.TButton", font=fonts.chip, padding=(8, 8))
    style.map("ChipOn.TButton", foreground=[("disabled", palette.text)])


def _style_combobox(root: tk.Tk, style: ttk.Style, palette: Palette, fonts: Fonts) -> None:
    style.configure(
        "TCombobox",
        fieldbackground=palette.card,
        background=palette.card,
        foreground=palette.text,
        arrowcolor=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.card,
        darkcolor=palette.card,
        selectbackground=palette.card,
        selectforeground=palette.text,
        padding=8,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("disabled", palette.background), ("readonly", palette.card)],
        foreground=[("disabled", palette.text_muted), ("readonly", palette.text)],
        arrowcolor=[("disabled", palette.text_muted)],
        background=[("active", palette.border)],
        selectbackground=[("readonly", palette.card)],
        selectforeground=[("readonly", palette.text)],
    )
    family, size, _ = fonts.subtitle
    root.option_add("*TCombobox.font", f"{{{family}}} {size}")
    root.option_add("*TCombobox*Listbox.background", palette.card)
    root.option_add("*TCombobox*Listbox.foreground", palette.text)
    root.option_add("*TCombobox*Listbox.selectBackground", palette.accent)
    root.option_add("*TCombobox*Listbox.selectForeground", palette.text)
    root.option_add("*TCombobox*Listbox.font", f"{{{family}}} {size}")
    style.configure(
        "Vertical.TScrollbar",
        background=palette.border,
        troughcolor=palette.card,
        bordercolor=palette.card,
        arrowcolor=palette.text,
    )


def _style_progressbar(style: ttk.Style, palette: Palette) -> None:
    for name, color in (
        ("Timer.Horizontal.TProgressbar", palette.timer_ok),
        ("Alert.Timer.Horizontal.TProgressbar", palette.timer_alert),
    ):
        style.configure(
            name,
            background=color,
            lightcolor=color,
            darkcolor=color,
            troughcolor=palette.background,
            bordercolor=palette.border,
            thickness=10,
        )
