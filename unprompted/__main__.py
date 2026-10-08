"""Point d'entrée : python3 -m unprompted"""

import sys

from .console import Console
from .session import run_session

EXIT_INTERRUPTED = 130


def main() -> int:
    console = Console()
    try:
        run_session(console)
    except (KeyboardInterrupt, EOFError):
        console.say()
        console.say("Session interrompue.")
        return EXIT_INTERRUPTED
    return 0


if __name__ == "__main__":
    sys.exit(main())
