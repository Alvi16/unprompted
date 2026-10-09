"""Point d'entrée de la fenêtre : repli vers le terminal quand la fenêtre ne peut pas s'ouvrir."""

import sys

from unprompted.gui import __main__ as entry

TERMINAL_EXIT_CODE = 42


def _forget_gui_modules(monkeypatch):
    for name in [name for name in sys.modules if name.startswith("unprompted.gui.app")]:
        monkeypatch.delitem(sys.modules, name)


def _record_terminal(monkeypatch):
    launches = []

    def fake_terminal():
        launches.append(True)
        return TERMINAL_EXIT_CODE

    monkeypatch.setattr(entry, "run_terminal", fake_terminal)
    return launches


def test_missing_tkinter_falls_back_to_the_terminal_with_an_explanation(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    _forget_gui_modules(monkeypatch)
    launches = _record_terminal(monkeypatch)

    assert entry.main() == TERMINAL_EXIT_CODE

    assert launches == [True]
    message = capsys.readouterr().err
    assert "Tkinter est introuvable" in message
    assert "Lancement de la version terminal" in message
    assert "python3-tk" in message


def test_no_display_falls_back_to_the_terminal_with_an_explanation(monkeypatch, capsys):
    import tkinter

    from unprompted.gui import app

    def fail(*args, **kwargs):
        raise tkinter.TclError("no display name and no $DISPLAY environment variable")

    monkeypatch.setattr(app, "UnpromptedApp", fail)
    launches = _record_terminal(monkeypatch)

    assert entry.main() == TERMINAL_EXIT_CODE

    assert launches == [True]
    message = capsys.readouterr().err
    assert "Impossible d'ouvrir la fenêtre" in message
    assert "Lancement de la version terminal" in message
