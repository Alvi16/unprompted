"""Point d'entrée de la fenêtre : messages d'erreur lorsque la fenêtre ne peut pas s'ouvrir."""

import sys

from unprompted.gui import __main__ as entry


def _forget_gui_modules(monkeypatch):
    for name in [name for name in sys.modules if name.startswith("unprompted.gui.app")]:
        monkeypatch.delitem(sys.modules, name)


def test_missing_tkinter_gives_a_clear_message_and_a_failure_code(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    _forget_gui_modules(monkeypatch)

    assert entry.main() == entry.EXIT_CANNOT_OPEN

    message = capsys.readouterr().err
    assert "Tkinter est introuvable" in message
    assert "python3-tk" in message
    assert "python3 -m unprompted" in message


def test_no_display_gives_a_clear_message_and_a_failure_code(monkeypatch, capsys):
    import tkinter

    from unprompted.gui import app

    def fail(*args, **kwargs):
        raise tkinter.TclError("no display name and no $DISPLAY environment variable")

    monkeypatch.setattr(app, "UnpromptedApp", fail)

    assert entry.main() == entry.EXIT_CANNOT_OPEN

    assert "Impossible d'ouvrir la fenêtre" in capsys.readouterr().err
