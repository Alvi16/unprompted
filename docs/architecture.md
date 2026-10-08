# Architecture

Ce document décrit comment le code est organisé et pourquoi chaque module existe. Les décisions et leurs alternatives sont dans [choix-techniques.md](choix-techniques.md).

## Principe d'organisation

Les modules se répartissent en trois familles.

- **Cœur** : les règles, les données et la machine à états de la session. Un module du cœur ne lit jamais le clavier, n'écrit jamais à l'écran et n'importe jamais Tkinter.
- **Terminal** : le dialogue en ligne de commande.
- **Interface graphique** : la fenêtre Tkinter, dans le paquet `gui/`.

Règles de dépendance :
- le cœur n'importe ni le terminal ni l'interface graphique ;
- le terminal et l'interface graphique importent le cœur, mais jamais l'un l'autre.

| Module | Famille | Rôle | Importe |
|---|---|---|---|
| `modes.py` | Cœur | Définit les modes, leurs textes, leurs bornes et les durées proposées | aucun module du projet |
| `topics.py` | Cœur | Contient le catalogue (par mode, puis par thème) et `topics_for` ; aucune autre logique | `modes` |
| `picker.py` | Cœur | Tire un sujet au hasard | `topics` |
| `durations.py` | Cœur | Lit une durée saisie, formate une durée | aucun module du projet |
| `timer.py` | Cœur | Comptes à rebours : bloquant (`run_countdown`) et non bloquant (`Countdown`) | aucun module du projet |
| `flow.py` | Cœur | Machine à états d'une session : mode, thème, sujet, durées, deux phases chronométrées | `modes`, `picker`, `timer`, `topics` |
| `console.py` | Terminal | Lit le clavier, écrit à l'écran, émet le bip | `durations` |
| `prompts.py` | Terminal | Pose les questions (mode, thème, durées) et redemande jusqu'à une réponse valide | `console`, `durations`, `modes`, `topics` |
| `session.py` | Terminal | Enchaîne toutes les étapes d'une session | `console`, `durations`, `modes`, `picker`, `prompts`, `timer`, `topics` |
| `__main__.py` | Terminal | Point d'entrée, gère l'interruption | `console`, `session` |
| `gui/palette.py` | Interface | Couleurs et calcul de contraste, sans Tkinter | aucun module du projet |
| `gui/theme.py` | Interface | Choix des polices et styles `ttk` du thème « clam » | `palette` |
| `gui/widgets.py` | Interface | Carte à fond sombre et bordure fine, partagée par les blocs | aucun module du projet |
| `gui/mode_view.py` | Interface | Bloc de choix du mode | `modes`, `widgets` |
| `gui/theme_view.py` | Interface | Grille de boutons de thème, un seul actif à la fois | aucun module du projet |
| `gui/topic_view.py` | Interface | Carte du sujet ou du message de tirage | `topics`, `widgets` |
| `gui/duration_view.py` | Interface | Bloc des deux listes de durées | `durations`, `modes`, `widgets` |
| `gui/timer_view.py` | Interface | Bloc du chrono, de la barre et des boutons | `widgets` |
| `gui/app.py` | Interface | Fenêtre : relie `SessionFlow` aux blocs | `durations`, `flow`, `modes`, `topics`, les blocs, `palette`, `theme` |
| `gui/__main__.py` | Interface | Point d'entrée de la fenêtre | `app` |

Les fichiers `__init__.py` ne contiennent qu'une ligne de description : ils signalent à Python que le dossier est un paquet.

## Machine à états de la session

`flow.SessionFlow` porte toute la logique de la fenêtre. Elle ne sait ni dessiner ni lire un clic : l'interface lit son état, lui transmet les actions et appelle `tick()` régulièrement.

| Étape | Signification | Actions permises |
|---|---|---|
| `IDLE` | Aucun sujet tiré | changer de mode, choisir un thème, tirer un sujet (si un thème est choisi), régler les durées |
| `READY` | Sujet tiré, prêt à démarrer | changer de mode, choisir un thème, tirer un autre sujet, régler les durées, démarrer |
| `PREPARING` | Première phase en cours | pause et reprise, réinitialiser |
| `SPEAKING` | Prise de parole en cours | pause et reprise, réinitialiser |
| `DONE` | Session terminée | changer de mode, choisir un thème, tirer un sujet, régler les durées, réinitialiser |

Une action hors de ces cas lève `InvalidAction`, y compris tirer un sujet sans avoir choisi de thème : aucun thème n'est présélectionné. Changer de mode oublie le sujet, garde le thème et rétablit les durées par défaut du mode. Choisir un autre thème oublie le sujet. `reset()` ramène au sujet tiré (`READY`) ou à l'accueil (`IDLE`) s'il n'y en a pas.

`tick()` renvoie l'événement de fin de phase quand il vient de se produire : `PREPARATION_ENDED` (la prise de parole démarre alors aussitôt) ou `SPEECH_ENDED`. Une phase en pause ne se termine jamais.

## Déroulé dans le terminal

`session.run_session` exécute les étapes dans cet ordre.

1. `prompts.choose_mode` affiche les modes et lit le choix. Une réponse invalide est refusée et la question est reposée.
2. `prompts.choose_theme` affiche les thèmes numérotés et lit le choix, avec la même règle.
3. `session` affiche « Le choix aléatoire est en cours… ».
4. `picker.pick_topic` tire un sujet parmi ceux du mode et du thème (`topics.topics_for`). Il est affiché avec son thème.
5. `prompts.ask_duration` lit la durée de la première phase, puis celle de la prise de parole, avec les bornes du mode.
6. Pour chaque phase, `session._run_phase` annonce la phase, lance `timer.run_countdown`, annonce la fin et émet trois bips espacés de 0,4 s.
7. `session` affiche « Session terminée. »

`__main__.main` entoure ce déroulé. `Ctrl+C` ou une entrée coupée produisent le message « Session interrompue. » et le code de sortie 130.

Le point d'entrée de la fenêtre (`gui/__main__.py`) se comporte autrement. Il importe Tkinter lui-même, pour pouvoir expliquer l'échec au lieu d'afficher une trace d'erreur :
- si Tkinter n'est pas installé, il écrit « Tkinter est introuvable » avec la marche à suivre (paquet `python3-tk` sur Debian et Ubuntu, ou version terminal) ;
- si Tkinter ne peut pas ouvrir de fenêtre (aucun écran, par exemple), il écrit « Impossible d'ouvrir la fenêtre : » suivi de la cause ;
- dans les deux cas, le message va sur la sortie d'erreur et le code de sortie est 1.

## Déroulé dans la fenêtre

`gui.app.UnpromptedApp` crée un `SessionFlow`, applique le thème, construit les blocs et planifie `poll()` toutes les 100 ms.

- **Actions :** les boutons appellent les méthodes publiques de la fenêtre (`choose_mode`, `choose_theme`, `draw_topic`, `set_durations`, `press_primary`, `press_reset`), qui appellent `SessionFlow` puis rafraîchissent l'affichage.
- **Verrouillage :** pendant le tirage animé et pendant qu'une phase tourne, le choix du mode, du thème, le tirage et les durées sont désactivés. Tant qu'aucun thème n'est choisi, le tirage l'est aussi.
- **Tirage animé :** le bouton « Tirer un sujet » affiche dix sujets tirés au hasard dans le thème et le mode courants, un toutes les 60 ms, avec le message « Le choix aléatoire est en cours… ». Le sujet final est celui que `SessionFlow` a tiré. L'animation passe par `after`, donc la fenêtre ne se fige pas.
- **Fin de phase :** `poll()` reçoit l'événement de `tick()`, affiche « Temps de … écoulé ! » pendant 4 secondes et émet trois bips du système.
- **Alerte :** pendant les 10 dernières secondes d'une phase, le chrono et la barre passent au rouge.
- **Fermeture :** `close()` annule toutes les tâches planifiées avant de détruire la fenêtre.
- **Taille :** la taille minimale est celle que demandent les blocs ; la largeur initiale est d'au moins 680 pixels.

Chaque bloc ne fait que deux choses : afficher ce que la fenêtre lui donne (`show`) et rappeler la fenêtre quand l'utilisateur agit. Le bloc du chrono reçoit un objet `TimerViewState` qui contient tout ce qu'il doit afficher.

## Fonctionnement des chronomètres

Les deux chronomètres de `timer.py` reposent sur le même principe : une échéance calculée une seule fois sur l'horloge monotone (heure de départ plus durée), puis un temps restant toujours recalculé depuis cette échéance. La durée totale ne dérive donc pas, même si l'affichage prend du temps.

- **`Countdown`** ne bloque pas. L'appelant l'interroge quand il veut (`remaining`, `finished`) et peut le mettre en pause (`pause`) puis le reprendre (`start`). Le temps restant est arrondi à la seconde supérieure et n'est jamais négatif.
- **`run_countdown`** bloque jusqu'à zéro, en s'appuyant sur `Countdown`. Il appelle l'affichage quand le nombre de secondes entières restantes change, de la durée demandée jusqu'à 0 inclus, et se met en pause 0,1 s entre deux tours.

## Éléments injectables

Chaque dépendance au monde extérieur est un paramètre. Le programme réel utilise les valeurs par défaut ; les tests fournissent des substituts.

| Paramètre | Où | Valeur réelle | Valeur en test |
|---|---|---|---|
| `clock` | `Countdown`, `run_countdown`, `SessionFlow`, `run_session` | `time.monotonic` | horloge simulée |
| `sleep` | `run_countdown`, `run_session` | `time.sleep` | pause qui avance l'horloge simulée sans attendre |
| `rng` | `pick_topic`, `SessionFlow`, `run_session` | générateur aléatoire de Python | générateur à graine fixe |
| `read`, `write` | `console.Console` | `input` et écriture sur la sortie standard | réponses scriptées et enregistrement du texte affiché |
| `flow` | `UnpromptedApp` | un `SessionFlow` neuf | un `SessionFlow` à horloge simulée |
| `spin_frames` | `UnpromptedApp` | 10 images d'animation | 0, pour supprimer l'animation |

Conséquence : une session de 75 secondes se teste en quelques millisecondes, y compris dans la fenêtre.

## Thème de l'interface

- **Palette** (`gui/palette.py`) : neuf couleurs nommées, définies à un seul endroit. Les contrastes sont calculés par `contrast_ratio` et vérifiés par les tests.
- **Polices** (`gui/theme.py`) : pour chaque famille (sans empattement, à chasse fixe), le thème prend la première police installée d'une liste de candidates, puis la police par défaut de Tk à défaut. Le chrono utilise une police à chasse fixe.
- **Styles** : le thème `clam` de `ttk` est personnalisé pour les cadres, les étiquettes, les quatre styles de boutons (principal, secondaire, segment actif et inactif), les listes déroulantes et les deux barres de progression (normale et alerte). Les cartes sont deux cadres imbriqués : l'un couleur de bordure, l'autre couleur de carte, séparés d'un pixel.

## Modifier le catalogue

Les sujets sont dans `unprompted/topics.py`, dans le dictionnaire `CATALOGUE` : une entrée par mode, qui associe à chaque thème un tuple de sujets. Les deux modes ont les mêmes thèmes. Au moment de la rédaction, le catalogue compte 8 thèmes et 10 sujets par thème et par mode, soit 160 sujets.

Le terminal et la fenêtre lisent `THEMES`, déduit des thèmes du mode improvisé. Ajouter un thème ou un sujet ne demande donc aucune autre modification de code, à condition d'ajouter le thème dans les deux modes. La grille de la fenêtre compte 4 boutons par rangée (`COLUMNS` dans `gui/theme_view.py`) et gagne une rangée par tranche de quatre thèmes, ce qui augmente la hauteur de la fenêtre.

Règles imposées par `tests/test_topics.py` :

| Règle | Détail |
|---|---|
| Nombre de thèmes | Au moins 6, aux noms distincts et non vides |
| Cohérence des modes | Les deux modes couvrent exactement les mêmes thèmes |
| Taille d'un thème | Exactement 10 sujets par mode (constante `TOPICS_PER_THEME` du test) |
| Unicité | Aucun sujet en double dans un mode, et aucun sujet commun aux deux modes |
| Forme d'un sujet | 3 mots au plus, sans espace en début ni en fin, sans « ? », « . » ni « ! » final |

La nature des sujets n'est pas testable : elle relève de la relecture. Un sujet d'improvisation doit pouvoir être traité sans préparation ; un sujet de recherche doit être une notion qu'il faut étudier avant de l'expliquer.

Procédure :
1. Modifier `CATALOGUE` dans `unprompted/topics.py`.
2. Lancer `python3 -m pytest`.
3. Pour porter un thème à plus ou moins de 10 sujets, modifier aussi `TOPICS_PER_THEME` dans le test, puis les documents qui le mentionnent.

## Tests

Un fichier de tests par module, plus un fichier d'outils partagés.

| Fichier | Ce qu'il vérifie |
|---|---|
| `conftest.py` | Fournit l'horloge simulée et la console scriptée aux autres fichiers |
| `test_durations.py` | Formats acceptés et refusés, affichage des durées |
| `test_modes.py` | Durées proposées triées, comprises dans les bornes, valeurs par défaut incluses, bornes extrêmes proposées |
| `test_topics.py` | Au moins 6 thèmes distincts, mêmes thèmes dans les deux modes, 10 sujets par thème et par mode, aucun doublon ni sujet commun aux deux modes, sujets courts (pas de phrase), `topics_for`, bornes cohérentes entre les modes |
| `test_picker.py` | Le sujet tiré appartient à la liste, reproductibilité avec graine, tous les sujets d'un thème atteignables, liste vide refusée |
| `test_timer.py` | `run_countdown` (séquence 3, 2, 1, 0, durée respectée, durée nulle ou négative) et `Countdown` (attente du départ, pause et reprise, idempotence) |
| `test_flow.py` | Parcours complet, thème obligatoire avant le tirage, sujet tiré dans le thème et le mode choisis, pause, progression, alerte, verrouillage hors étapes permises, bornes de durée, réinitialisation |
| `test_prompts.py` | Choix du mode et du thème, réponses invalides refusées, bornes de durée respectées |
| `test_session.py` | Ordre des étapes, sujet du thème et du mode choisis, vocabulaire du mode recherche, nombre de bips, durée totale |
| `test_palette.py` | Calcul du contraste et lisibilité des couleurs du thème |
| `test_theme.py` | Choix de la police parmi les candidates |
| `test_gui_entry.py` | Messages et code de sortie du point d'entrée de la fenêtre quand Tkinter est absent ou qu'aucun écran n'est disponible. Ne demande pas d'écran |
| `test_gui_smoke.py` | Ouverture réelle de la fenêtre, tous les thèmes proposés, tirage impossible sans thème, parcours complet avec horloge simulée, bips, verrouillage, pause et réinitialisation. Ignoré s'il n'y a pas d'écran |

## Fichiers de configuration

`pyproject.toml` est lu par les outils de vérification. Le programme ne le lit pas : il ne change donc jamais son comportement.

| Ligne | Effet |
|---|---|
| `line-length = 100` | `ruff` refuse les lignes de plus de 100 caractères |
| `target-version = "py312"` | `ruff` vérifie le code pour Python 3.12 |
| `select = ["E", "F", "I", "UP", "B"]` | Familles de contrôles actives : style (E), erreurs de code (F), ordre des imports (I), syntaxe modernisée (UP), pièges courants (B) |
| `testpaths = ["tests"]` | `pytest` cherche les tests dans `tests/` |
| `pythonpath = ["."]` | `pytest` ajoute la racine aux chemins d'import, ce qui lui permet de trouver le paquet `unprompted` |

Deux autres fichiers de la racine concernent l'environnement de développement :

| Fichier | Rôle |
|---|---|
| `requirements-dev.txt` | Liste les outils de vérification avec leurs versions exactes (`pytest`, `ruff`). S'installe avec `pip install -r requirements-dev.txt`. Le programme lui-même n'a aucune dépendance |
| `.gitignore` | Exclut du dépôt les fichiers générés : `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/` et `.venv/` |
