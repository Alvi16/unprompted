# Choix techniques

Ce document recense les décisions du projet : le contexte, les options comparées, le choix retenu et ses conséquences. Il se termine par les limites connues. L'organisation du code est décrite dans [architecture.md](architecture.md).

## Langage : Python

**Contexte.** Les langages disponibles et maîtrisés sont C, C++, Python et C#. Vérification faite sur la machine de développement : g++ 13.3.0, Python 3.12.3 et .NET 8.0.131 sont installés.

**Options comparées.**

| Option | Adéquation au besoin | Remarque |
|---|---|---|
| Python | Saisie, chronomètre, interface et tests s'écrivent en peu de code | `pytest` et `ruff` déjà installés |
| C++ | Réalisable, mais plus de code pour la saisie et le chronomètre | Compilation et `Makefile` à prévoir |
| C# | Réalisable avec .NET 8 | Moins d'historique de pratique que le C++ |

**Décision.** Python, choisi par l'auteur.

**Conséquences.** Le programme se lance sans compilation. Les performances ne sont pas un enjeu : le programme attend la plupart du temps.

## Bibliothèque standard uniquement

**Contexte.** Le programme n'a besoin que de lire une saisie, tirer au hasard, mesurer le temps, afficher du texte et ouvrir une fenêtre.

**Options.** Utiliser des bibliothèques tierces (son, interface), ou se limiter à la bibliothèque standard.

**Décision.** Bibliothèque standard uniquement, Tkinter compris. Aucune dépendance d'exécution n'est déclarée.

**Conséquences.** Rien à installer pour lancer le programme. Les seules dépendances sont des outils de vérification (`pytest`, `ruff`). Le signal sonore est limité en conséquence (voir les limites connues).

## Interface graphique : Tkinter et ttk

**Contexte.** Une interface de bureau était demandée, avec une charte sombre. Vérification faite sur la machine de développement : Tkinter 8.6 est installé avec le thème `clam` ; Qt (PyQt5, PyQt6, PySide6), CustomTkinter, pygame, kivy et wx ne le sont pas.

**Options comparées.**

| Option | Dans les compétences de l'auteur | Installation | Réemploi du code existant |
|---|---|---|---|
| Tkinter et `ttk` | Python, oui | aucune | cœur et tests conservés |
| Qt (PySide6) | non | à installer | cœur et tests conservés |
| Interface web (HTML, CSS, JavaScript) | non | polices et styles chargés depuis Internet | logique à réécrire en JavaScript |

**Décision.** Tkinter et `ttk`, avec le thème `clam` personnalisé. L'interface web a été écartée car elle sort des compétences de l'auteur, dépend d'Internet et dupliquerait la logique.

**Conséquences.** Le rendu est cohérent et soigné, mais Tkinter n'offre ni coins arrondis, ni ombres, ni dégradés natifs. Le rendu a été vérifié par des captures de la fenêtre réelle dans plusieurs états.

## Distribution : lancement depuis le dépôt

**Contexte.** Le projet doit pouvoir être cloné depuis GitHub et lancé sur un autre appareil, sans préparation compliquée.

**Options.**

| Option | Avantages | Inconvénients |
|---|---|---|
| Lancer depuis le dépôt (`python3 -m unprompted`) | Aucune installation, aucune dépendance | Le dossier courant doit être la racine du dépôt |
| Paquet installable (`pip install`) | Commandes disponibles partout | Demande un outil de construction (`setuptools`), une déclaration de projet et un accès réseau à l'installation |

**Décision.** Lancer depuis le dépôt. Le programme n'a aucune dépendance d'exécution, donc il n'y a rien à installer pour la version terminal. Les outils de vérification sont listés dans `requirements-dev.txt`, avec leurs versions exactes. La documentation décrit l'installation, le lancement et le dépannage, et la commande de la fenêtre se replie d'elle-même sur le terminal quand elle ne peut pas s'ouvrir (voir « Repli automatique vers le terminal »).

**Conséquences.** Le parcours « cloner, créer un environnement virtuel, installer les outils, lancer les tests, lancer le programme » a été vérifié de bout en bout sur une copie propre. Lancer la commande depuis un autre dossier échoue avec `No module named unprompted`, ce que le dépannage du README explique. Les versions des outils sont fixées à la main et ne se mettent pas à jour seules.

## Repli automatique vers le terminal

**Contexte.** La fenêtre dépend de Tkinter, qui n'est pas toujours installé (paquet distinct sur Debian et Ubuntu), et d'un écran, qui n'existe pas sur une session distante. Sur un appareil inconnu, l'une ou l'autre peut manquer.

**Options.** Afficher une erreur et s'arrêter, ou lancer automatiquement la version terminal.

**Décision.** Lancer la version terminal, après un message qui donne la cause et, pour Tkinter, la marche à suivre pour obtenir la fenêtre. Le message va sur la sortie d'erreur.

**Conséquences.** La même commande, `python3 -m unprompted.gui`, donne toujours un entraînement utilisable. Le code de sortie devient celui de la version terminal (0, ou 130 en cas d'interruption) : un échec d'ouverture de la fenêtre n'est plus signalé par un code d'erreur. Le test `test_gui_entry.py` vérifie les deux cas de repli.

## Vérification automatique

**Contexte.** Le projet doit fonctionner sur d'autres appareils, mais il n'est testé à la main que sous Ubuntu.

**Options.** Ne rien automatiser, ou utiliser GitHub Actions, gratuit pour un dépôt public.

**Décision.** Un workflow GitHub Actions exécute le contrôle de style, les tests et un lancement du terminal sous Linux, Windows et macOS, avec Python 3.10, 3.11, 3.12 et 3.13 (12 combinaisons).

**Conséquences.** Les résultats pour Windows, macOS et les autres versions de Python sont connus sans posséder ces machines, et visibles dans l'onglet Actions. Les versions des outils restent fixées à la main dans `requirements-dev.txt` : aucune mise à jour automatique n'est configurée. La version minimale de Python réellement prise en charge est établie par ces résultats, pas par une supposition. Les tests qui ouvrent la fenêtre sont ignorés sur une machine sans écran ; leur exécution effective sous Windows et macOS dépend de l'environnement de GitHub et se lit dans les résultats.

## Séparation du cœur et de l'interaction

**Contexte.** Deux interfaces existent, le terminal et la fenêtre, et d'autres peuvent suivre.

**Options.** Écrire la logique directement dans le code d'affichage, ou la séparer.

**Décision.** Séparer. Les modules du cœur n'écrivent jamais à l'écran, n'importent jamais Tkinter ni un module d'interaction. La logique de la fenêtre vit dans une machine à états, `SessionFlow`, que la fenêtre se contente de lire et de piloter. L'horloge, la pause, le générateur aléatoire et les entrées-sorties sont des paramètres.

**Conséquences.** Les règles se testent sans écran ni attente. Les deux interfaces partagent les modes, les sujets, les durées et les bornes. Le coût est un peu plus de structure : une vingtaine de modules au lieu d'un fichier unique.

## Deux chronomètres sur une même base

**Contexte.** Le terminal peut bloquer en attendant. Une fenêtre ne le peut pas : elle gèlerait.

**Options.** Un seul chronomètre bloquant, un seul chronomètre non bloquant, ou les deux sur une base commune.

**Décision.** Un chronomètre non bloquant, `Countdown`, interrogé par l'appelant. La version bloquante du terminal, `run_countdown`, s'appuie sur lui. Dans les deux cas, l'échéance est calculée une seule fois sur l'horloge monotone et le temps restant est recalculé depuis cette échéance. Un décompte qui dormirait une seconde par tour dériverait, car l'affichage et les pauses prennent un peu plus d'une seconde chacun. L'horloge monotone n'est pas affectée par un changement de l'heure système.

**Conséquences.** La durée totale correspond à la durée demandée, et le même comportement est testé une seule fois. Le test `test_countdown_lasts_the_requested_duration` le vérifie avec une horloge simulée.

## Durées : saisie, listes et bornes par mode

**Contexte.** Les deux modes n'ont pas le même rythme. Le mode improvisé suppose une préparation courte. Le mode recherche suppose un vrai temps d'étude.

**Décision sur les bornes.**

| Mode | Première phase | Prise de parole |
|---|---|---|
| Improvisé | de 15 s à 5 min | de 1 min à 5 min |
| Recherche | de 1 min à 60 min | de 1 min à 10 min |

Ces valeurs sont des choix de conception, pas une norme. Elles sont regroupées dans `modes.py` et se modifient à cet unique endroit.

**Décision sur la saisie dans le terminal.** Une durée s'écrit avec un nombre entier et une unité facultative : `s`, `sec`, `m` ou `min`. Sans unité, le nombre est en minutes. Les secondes sont nécessaires, car la plus courte préparation du mode improvisé est de 15 s.

**Décision pour la fenêtre.** Des listes déroulantes à valeurs fixes, définies par mode dans `modes.py` (par exemple 15 s, 30 s, 1, 2, 3 et 5 min pour la préparation improvisée). Chaque liste est comprise dans les bornes du mode, contient les bornes extrêmes et la valeur par défaut. Les tests le vérifient.

**Conséquences.** Une saisie de terminal hors bornes est refusée avec les bornes rappelées. La fenêtre ne peut pas produire de durée invalide.

## Thème : palette et polices

**Contexte.** La charte fournit neuf couleurs et demande des polices précises (Inter, JetBrains Mono). Vérification faite : ces deux polices ne sont pas installées sur la machine de développement ; `Noto Sans` et `DejaVu Sans Mono` le sont.

**Décision sur la palette.** Appliquer la charte telle quelle, définie à un seul endroit (`gui/palette.py`). Les contrastes sont calculés et testés : le texte courant atteint au moins 4,5 contre le fond, et le texte blanc sur l'accent atteint 4,47. Ce dernier rapport est inférieur à 4,5 : il est acceptable seulement pour du texte en gros caractères (14 points gras ou plus, seuil de 3), ce qui est le cas des boutons.

**Décision sur les polices.** Une liste de candidates par famille, dans l'ordre de la charte, puis un repli sur les polices installées, puis sur les polices par défaut de Tk. Ainsi la fenêtre s'affiche correctement sur une machine sans Inter ni JetBrains Mono.

**Conséquences.** Le rendu varie légèrement selon les polices installées. Le chrono, en police à chasse fixe, garde une largeur constante.

## Signal de fin : le bip du système

**Contexte.** Il faut un signal à la fin de chaque phase, sans ajouter de dépendance.

**Options.** Le bip du système (le caractère `\a` dans le terminal, la méthode `bell` de Tkinter dans la fenêtre), ou une bibliothèque audio.

**Décision.** Le bip du système, émis trois fois à 0,4 s d'intervalle, accompagné dans la fenêtre du message « Temps de … écoulé ! » et du passage au rouge du chrono pendant les 10 dernières secondes.

**Conséquences.** Aucune dépendance, mais le rendu sonore dépend du système : certains terminaux ou environnements de bureau le rendent muet. Le programme émet bien le signal, mais le son n'a pas été écouté lors des vérifications.

## Thèmes et sujets courts

**Contexte.** Un premier catalogue mélangeait des questions entières (« Peut-on réussir sans diplôme ? ») et des notions, sans thème à choisir. Cela ne correspondait pas à l'usage voulu : choisir un domaine, puis recevoir un sujet précis dans ce domaine.

**Options.** Un catalogue unique pour les deux modes, ou un catalogue par mode ; des sujets en phrases, ou en mots.

**Décision.** Un catalogue par mode, organisé selon les mêmes thèmes, avec dix sujets par thème et par mode. Chaque sujet est un mot ou une expression de trois mots au plus (« Wi-Fi », « Théorème CAP »). Aucun sujet n'est commun aux deux modes.
- **Improvisé :** des sujets simples, dont on peut parler sur le vif.
- **Recherche :** des notions approfondies, qu'il faut étudier avant de les expliquer.

Aucun thème n'est présélectionné : il faut en choisir un avant de tirer.

Une première version partageait un seul catalogue entre les deux modes. Elle a été abandonnée parce que les modes ne différaient alors que par le nom de la première phase et les durées, ce qui ne justifiait pas deux modes. Lors de la séparation, les sujets déjà techniques du catalogue commun ont été déplacés vers le mode recherche ou remplacés par des sujets plus simples en improvisé.

**Conséquences.** Chaque mode a une raison d'être propre, et le choix du mode change réellement ce que l'on doit traiter. Les tests vérifient les thèmes communs, les dix sujets par thème et par mode, l'absence de doublon, l'absence de sujet commun aux deux modes et la brièveté des sujets. Le niveau des sujets (simple ou approfondi) ne se teste pas : il relève de la relecture du catalogue.

## Tirage aléatoire sans mémoire

**Décision.** Un sujet est tiré avec `random.choice` dans le thème choisi, à chaque tirage, sans historique.

**Conséquences.** Deux tirages successifs peuvent donner le même sujet. Une mémoire des sujets déjà vus n'a pas été ajoutée, car elle n'était pas demandée.

## Limites connues

| Limite | Détail |
|---|---|
| Signal sonore | Dépend du système ; non écouté lors des vérifications. |
| Mémoire | Aucune : un sujet peut se répéter. |
| Taille du catalogue | Réduite : dix sujets par thème et par mode. Le nombre actuel de thèmes est donné dans la section « Modifier le catalogue » de `architecture.md`. |
| Niveau des sujets | Jugé à la relecture du catalogue ; aucun test ne le vérifie. |
| Description du mode | Affichée dans le terminal ; la fenêtre ne l'affiche pas, par manque de place. |
| Contrôle du chrono | Pause et réinitialisation dans la fenêtre seulement ; pas de passage anticipé à la phase suivante. |
| Session | Une seule session par lancement dans le terminal. |
| Bornes de durée | Choisies par conception, modifiables dans `modes.py`. |
| Taille de la fenêtre | Environ 900 pixels de haut avec les polices de la machine de développement : elle peut dépasser un écran de faible hauteur. |
| Rendu | Pas de coins arrondis, d'ombres ni de dégradés : limites de Tkinter. |
| Polices | Inter et JetBrains Mono de la charte sont remplacées lorsqu'elles ne sont pas installées. |
| Plateformes | Testé à la main uniquement sous Ubuntu 24.04 avec Python 3.12.3. Les autres systèmes et versions de Python sont vérifiés par l'intégration continue : leurs résultats sont dans l'onglet Actions du dépôt. |
| Installation | Pas de paquet installable : le programme se lance depuis la racine du dépôt. Les versions des outils de vérification sont fixées dans `requirements-dev.txt` et se mettent à jour à la main. |
| Fenêtre | Sans Tkinter ou sans écran, la version terminal se lance à la place : la fenêtre n'est pas garantie sur tous les appareils. |
| Licence | Aucune licence n'est fournie dans le dépôt ; elle reste à choisir par l'auteur. |
