"""Point d'entrée de l'interface graphique : python3 -m unprompted.gui

Si la fenêtre ne peut pas s'ouvrir (Tkinter absent, aucun écran), la version terminal
est lancée à la place, pour que la même commande fonctionne sur tout appareil.
"""

import sys

from ..__main__ import main as run_terminal

MISSING_TKINTER_MESSAGE = (
    "Tkinter est introuvable ({error}). Lancement de la version terminal.\n"
    "Pour obtenir la fenêtre, installez Tkinter pour votre version de Python "
    "(sur Debian et Ubuntu : sudo apt install python3-tk).\n"
)
CANNOT_OPEN_MESSAGE = (
    "Impossible d'ouvrir la fenêtre ({error}). Lancement de la version terminal.\n"
)


def main() -> int:
    try:
        import tkinter

        from .app import UnpromptedApp
    except ImportError as error:
        sys.stderr.write(MISSING_TKINTER_MESSAGE.format(error=error))
        return run_terminal()

    try:
        app = UnpromptedApp()
    except tkinter.TclError as error:
        sys.stderr.write(CANNOT_OPEN_MESSAGE.format(error=error))
        return run_terminal()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
