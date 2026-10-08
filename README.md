# Unprompted

Entraînement à la prise de parole, en fenêtre ou en terminal. Le programme tire un sujet au hasard selon le mode et le thème choisis, puis chronomètre un temps de préparation (ou de recherche) et un temps de prise de parole. Un signal marque la fin de chaque temps.

## Démarrage rapide

```bash
git clone https://github.com/Alvi16/unprompted.git
cd unprompted
python3 -m unprompted.gui
```

La fenêtre demande Python 3.12 et Tkinter. Les détails, les autres systèmes et le dépannage sont plus bas.

## Installation

### Prérequis

| Élément | Version | Nécessaire pour | Remarque |
|---|---|---|---|
| Python | 3.12 (testé avec 3.12.3) | tout | Les autres versions n'ont pas été testées |
| Tkinter | celui de votre Python | la fenêtre uniquement | Voir ci-dessous |
| Git | testé avec 2.43.0 | récupérer le code | Facultatif si vous téléchargez l'archive du dépôt |
| `pytest`, `ruff` | voir `requirements-dev.txt` | les vérifications uniquement | Inutiles pour utiliser le programme |

Le programme n'a aucune dépendance tierce : il n'utilise que la bibliothèque standard de Python.

### Récupérer le code

```bash
git clone https://github.com/Alvi16/unprompted.git
cd unprompted
```

Toutes les commandes de ce document se lancent depuis ce dossier, celui qui contient `pyproject.toml`.

### Installer Tkinter

Tkinter est nécessaire pour la fenêtre. La version terminal n'en a pas besoin.

| Système | Marche à suivre | Vérifié |
|---|---|---|
| Debian, Ubuntu | `sudo apt install python3-tk` | oui, sur Ubuntu 24.04 |
| Windows, macOS | Tkinter est normalement inclus dans l'installateur de Python publié sur python.org | non |
| Autres systèmes Linux | Installer le paquet Tkinter de votre distribution | non |

Pour contrôler l'installation : `python3 -c "import tkinter"`. Aucune sortie signifie que Tkinter est présent.

## Lancer le programme

Depuis la racine du dépôt.

Interface graphique :

```bash
python3 -m unprompted.gui
```

Terminal :

```bash
python3 -m unprompted
```

Sous Windows, remplacez `python3` par `python` ou `py` (non testé).

Dans le terminal, `Ctrl+C` interrompt la session : le programme affiche « Session interrompue. » et se termine avec le code 130.

## Dépannage

| Message ou symptôme | Cause | Solution |
|---|---|---|
| `No module named unprompted` | La commande est lancée hors de la racine du dépôt | Se placer dans le dossier qui contient `pyproject.toml` |
| « Tkinter est introuvable » | Tkinter n'est pas installé | Voir « Installer Tkinter », ou utiliser `python3 -m unprompted` |
| « Impossible d'ouvrir la fenêtre : no display name… » | Aucun écran disponible (session distante sans affichage, par exemple) | Lancer la commande sur une machine avec écran, ou utiliser `python3 -m unprompted` |
| `python3: command not found` | Python n'est pas installé, ou s'appelle autrement (Windows) | Installer Python 3.12, ou essayer `python` ou `py` |
| Aucun son à la fin d'une phase | Le bip du système est coupé ou muet sur votre environnement | Le message « Temps de … écoulé ! » et le chrono rouge signalent aussi la fin |

Lorsque la fenêtre ne peut pas s'ouvrir (Tkinter absent ou aucun écran), la commande se termine avec le code 1.

## Vocabulaire

| Terme | Sens dans ce projet |
|---|---|
| Mode | Type d'entraînement : improvisé ou recherche. |
| Thème | Domaine dans lequel le sujet est tiré, par exemple Informatique ou Nature. |
| Sujet | Mot ou expression courte tirée au hasard dans un thème, par exemple « Wi-Fi » ou « Latence ». |
| Phase | Un des deux temps chronométrés : préparation (ou recherche), puis prise de parole. |
| Signal | Fin d'une phase : trois bips du système, et le message « Temps de … écoulé ! ». |

## Déroulement d'une session

1. Choix du mode.
2. Choix du thème.
3. Tirage aléatoire d'un sujet dans ce thème, parmi ceux du mode choisi, affiché avec son thème.
4. Choix de la durée de la première phase, puis de celle de la prise de parole.
5. Chrono de la première phase, puis signal de fin.
6. Chrono de la prise de parole, puis signal de fin.

Le programme ne capte pas le discours : pendant la prise de parole, il affiche seulement le chrono.

## Interface graphique

La fenêtre suit le déroulement ci-dessus :
- deux boutons pour le mode ;
- un bouton par thème : aucun n'est présélectionné, et « Tirer un sujet » reste grisé tant qu'aucun thème n'est choisi ;
- un bouton « Tirer un sujet », qui fait défiler quelques sujets du thème avant d'afficher le tirage ;
- deux listes déroulantes pour les durées, dont les valeurs sont celles permises par le mode ;
- un grand chrono, une barre de progression, et les boutons « Démarrer », « Pause » ou « Reprendre », et « Réinitialiser ».

Le chrono et la barre passent au rouge pendant les 10 dernières secondes d'une phase. Pendant que le chrono tourne, le choix du mode, du thème, le tirage et les durées sont verrouillés. À la fin, le bouton devient « Recommencer ».

## Thèmes et sujets

Les deux modes partagent les mêmes thèmes, mais pas les mêmes sujets. Chaque thème compte dix sujets courts par mode, et aucun sujet n'est commun aux deux modes.

- **Improvisé :** sujets simples, dont on peut parler sur le vif.
- **Recherche :** notions approfondies, qu'il faut étudier avant de les expliquer.

| Thème | Improvisé (exemples) | Recherche (exemples) |
|---|---|---|
| Informatique | Wi-Fi, Mot de passe, Jeu en ligne | LLM, Latence, Théorème CAP |
| Nature | Mangrove, Compost, Érosion | Eutrophisation, Chaîne trophique, Albédo |
| Sciences | Gravité, Feu, Électricité | Mécanique quantique, Supraconductivité, Thermodynamique |
| Santé | Sommeil, Vaccin, Paludisme | Épigénétique, Neuroplasticité, ARN messager |
| Économie | Inflation, Salaire, Mobile money | Théorie des jeux, Coût d'opportunité, Dette souveraine |
| Société | Éducation, Démocratie, Vie privée | Contrat social, Anomie, Capital social |
| Espace | Orbite, Exoplanète, Big Bang | Matière noire, Ondes gravitationnelles, Zone habitable |
| Culture | Jeu vidéo, Manga, Architecture | Contrepoint, Narratologie, Sémiotique |

La liste complète est dans `unprompted/topics.py`. La marche à suivre pour la modifier est décrite dans [docs/architecture.md](docs/architecture.md#modifier-le-catalogue).

## Les deux modes

Le mode détermine les sujets tirés, le nom de la première phase et les durées permises.

| | Improvisé | Recherche |
|---|---|---|
| Sujets | Simples | Approfondis |
| Première phase | Préparation, de 15 s à 5 min | Recherche, de 1 min à 60 min |
| Prise de parole | De 1 min à 5 min | De 1 min à 10 min |
| Durées par défaut | 30 s puis 2 min | 10 min puis 3 min |

## Saisie des durées dans le terminal

| Saisie | Résultat |
|---|---|
| `30s`, `30 s`, `45 sec` | secondes |
| `5m`, `5 min` | minutes |
| `5` (sans unité) | minutes |

La casse est ignorée. Les nombres décimaux (`1.5`), les autres unités (`5h`), les valeurs négatives et tout autre texte sont refusés. Une durée hors des bornes du mode est refusée aussi. Dans les deux cas le programme explique l'erreur et repose la question. L'interface graphique n'a pas besoin de cette saisie : elle propose des valeurs fixes.

## Exemple de session dans le terminal

Le sujet est tiré au hasard : il change d'une session à l'autre. Pendant un chrono, l'affichage est mis à jour sur une seule ligne ; seule la dernière valeur est reproduite ici.

```text
Quel mode choisissez-vous ?
  1. Improvisé : sujets simples, courte préparation, vous parlez sur le vif.
  2. Recherche : notions approfondies, vous les étudiez puis vous les expliquez.
Votre choix (1-2) : 1

Quel thème choisissez-vous ?
  1. Informatique
  2. Nature
  3. Sciences
  4. Santé
  5. Économie
  6. Société
  7. Espace
  8. Culture
Votre choix (1-8) : 1

Le choix aléatoire est en cours…
Sujet : Messagerie
(Thème : Informatique)

Temps de préparation, de 15 s à 5 min (ex. 30s, 5m ; sans unité = minutes) : abc
Durée illisible : « abc ».
Temps de préparation, de 15 s à 5 min (ex. 30s, 5m ; sans unité = minutes) : 10s
Durée hors limites : choisissez entre 15 s et 5 min.
Temps de préparation, de 15 s à 5 min (ex. 30s, 5m ; sans unité = minutes) : 15s
Temps de prise de parole, de 1 min à 5 min (ex. 30s, 5m ; sans unité = minutes) : 1m

Préparation : 15 s, c'est parti.
Préparation : 00:00
Temps de préparation écoulé !

Prise de parole : 1 min, c'est parti.
Prise de parole : 00:00
Temps de prise de parole écoulé !
Session terminée.
```

## Vérifications

Ces commandes servent à contrôler le code. Elles ne sont pas nécessaires pour utiliser le programme.

### Installer les outils

Depuis la racine du dépôt, dans un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Sous Windows, l'activation se fait avec `.venv\Scripts\activate` (non testé).

`requirements-dev.txt` fixe les versions utilisées lors des vérifications : `pytest` 9.1.1 et `ruff` 0.16.10. Ces versions ne sont pas mises à jour automatiquement : pour les changer, modifier ce fichier puis relancer les vérifications.

### Lancer les vérifications

Tous les tests doivent passer et `ruff` ne doit signaler aucune erreur. Les tests qui ouvrent la fenêtre sont ignorés lorsqu'aucun écran n'est disponible.

```bash
python3 -m pytest
ruff check .
ruff format --check .
```

## Plateformes testées

| Élément | Valeur |
|---|---|
| Système | Ubuntu 24.04 (Linux) |
| Python | 3.12.3 |
| Parcours vérifié | clone du dépôt, environnement virtuel vierge, installation de `requirements-dev.txt`, tests, vérification de style, lancement du terminal |

Windows et macOS n'ont pas été testés.

## Structure du dépôt

```text
pyproject.toml            Réglages de ruff et de pytest
requirements-dev.txt      Outils de vérification, versions fixées
.gitignore                Fichiers générés exclus du dépôt
unprompted/               Le programme
  modes.py                Les deux modes, leurs textes, bornes et durées proposées
  topics.py               Le catalogue : thèmes et sujets, par mode
  picker.py               Tirage au hasard d'un sujet
  durations.py            Lecture et affichage des durées
  timer.py                Comptes à rebours (bloquant et non bloquant)
  flow.py                 Étapes d'une session, indépendantes de l'interface
  console.py              Seul module du terminal qui lit le clavier et écrit à l'écran
  prompts.py              Questions posées dans le terminal
  session.py              Déroulement d'une session dans le terminal
  __main__.py             Point d'entrée du terminal
  gui/                    Interface graphique
    palette.py            Couleurs et calcul de contraste
    theme.py              Polices et styles ttk
    widgets.py            Carte à bordure, partagée par les blocs
    mode_view.py          Bloc de choix du mode
    theme_view.py         Bloc de choix du thème
    topic_view.py         Carte du sujet
    duration_view.py      Bloc de choix des durées
    timer_view.py         Bloc du chronomètre
    app.py                Fenêtre principale
    __main__.py           Point d'entrée de la fenêtre
tests/                    Un fichier de tests par module, plus conftest.py
docs/
  architecture.md         Organisation du code, module par module
  choix-techniques.md     Décisions, alternatives écartées, limites connues
```

## Limites connues

Le détail des limites (signal sonore, absence de mémoire entre sessions, taille de la fenêtre, taille du catalogue) figure dans [docs/choix-techniques.md](docs/choix-techniques.md). L'organisation du code est décrite dans [docs/architecture.md](docs/architecture.md).
