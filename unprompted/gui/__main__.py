"""Point d'entrée de l'interface graphique : python3 -m unprompted.gui"""

import sys

EXIT_CANNOT_OPEN = 1

MISSING_TKINTER_MESSAGE = (
    "Tkinter est introuvable : {error}\n"
    "L'interface graphique en a besoin. Installez la prise en charge de Tkinter "
    "pour votre version de Python (sur Debian et Ubuntu : sudo apt install python3-tk), "
    "ou utilisez la version terminal : python3 -m unprompted\n"
)


def main() -> int:
    try:
        import tkinter

        from .app import UnpromptedApp
    except ImportError as error:
        sys.stderr.write(MISSING_TKINTER_MESSAGE.format(error=error))
        return EXIT_CANNOT_OPEN

    try:
        app = UnpromptedApp()
    except tkinter.TclError as error:
        sys.stderr.write(f"Impossible d'ouvrir la fenêtre : {error}\n")
        return EXIT_CANNOT_OPEN
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
