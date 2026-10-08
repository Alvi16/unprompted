"""Catalogue des sujets, par mode puis par thème. Données uniquement, aucune logique.

Chaque sujet est un mot ou une expression courte, jamais une phrase.
Les deux modes partagent les mêmes thèmes mais pas les mêmes sujets :
- improvisé : des sujets simples, dont on peut parler sur le vif sans préparation ;
- recherche : des notions plus profondes, qu'il faut étudier avant de les expliquer.
"""

from dataclasses import dataclass

from .modes import Mode


@dataclass(frozen=True)
class Topic:
    text: str
    theme: str


_IMPROVISED: dict[str, tuple[str, ...]] = {
    "Informatique": (
        "Wi-Fi",
        "Mot de passe",
        "Téléphone portable",
        "Jeu en ligne",
        "Messagerie",
        "Cloud",
        "Base de données",
        "Algorithme",
        "Logiciel libre",
        "Cybersécurité",
    ),
    "Nature": (
        "Photosynthèse",
        "Biodiversité",
        "Mangrove",
        "Pollinisation",
        "Érosion",
        "Cycle de l'eau",
        "Déforestation",
        "Écosystème",
        "Migration des oiseaux",
        "Compost",
    ),
    "Sciences": (
        "Gravité",
        "Atome",
        "ADN",
        "Énergie",
        "Feu",
        "Magnétisme",
        "Évolution",
        "Trou noir",
        "Électricité",
        "Lumière",
    ),
    "Santé": (
        "Sommeil",
        "Vaccin",
        "Antibiotique",
        "Système immunitaire",
        "Hydratation",
        "Stress",
        "Paludisme",
        "Nutrition",
        "Santé mentale",
        "Hygiène",
    ),
    "Économie": (
        "Inflation",
        "Salaire",
        "Microcrédit",
        "Mobile money",
        "Budget",
        "Marché",
        "Épargne",
        "Start-up",
        "Chômage",
        "Commerce équitable",
    ),
    "Société": (
        "Éducation",
        "Démocratie",
        "Réseaux sociaux",
        "Télétravail",
        "Jeunesse",
        "Égalité",
        "Urbanisation",
        "Vie privée",
        "Bénévolat",
        "Tradition",
    ),
    "Espace": (
        "Orbite",
        "Satellite",
        "Exoplanète",
        "Lune",
        "Galaxie",
        "Télescope",
        "Fusée",
        "Astéroïde",
        "Station spatiale",
        "Big Bang",
    ),
    "Culture": (
        "Jeu vidéo",
        "Manga",
        "Musique",
        "Cinéma",
        "Photographie",
        "Danse",
        "Littérature",
        "Architecture",
        "Théâtre",
        "Artisanat",
    ),
}

_RESEARCH: dict[str, tuple[str, ...]] = {
    "Informatique": (
        "LLM",
        "Latence",
        "Théorème CAP",
        "Complexité algorithmique",
        "Descente de gradient",
        "Machine de Turing",
        "Table de hachage",
        "Clé publique",
        "Cohérence éventuelle",
        "Calcul quantique",
    ),
    "Nature": (
        "Eutrophisation",
        "Chaîne trophique",
        "Cycle du carbone",
        "Cycle de l'azote",
        "Symbiose mycorhizienne",
        "Succession écologique",
        "Spéciation",
        "Albédo",
        "Dérive des continents",
        "Convergence évolutive",
    ),
    "Sciences": (
        "Mécanique quantique",
        "Principe d'incertitude",
        "Dualité onde-corpuscule",
        "Supraconductivité",
        "Effet photoélectrique",
        "Spectroscopie",
        "Nucléosynthèse",
        "Théorème de Noether",
        "Constante de Planck",
        "Thermodynamique",
    ),
    "Santé": (
        "Immunité collective",
        "Résistance aux antibiotiques",
        "Microbiote intestinal",
        "Épigénétique",
        "Neuroplasticité",
        "Effet placebo",
        "Rythme circadien",
        "Homéostasie",
        "Cellules souches",
        "ARN messager",
    ),
    "Économie": (
        "Théorie des jeux",
        "Coût d'opportunité",
        "Avantage comparatif",
        "Rendements décroissants",
        "Asymétrie d'information",
        "Bulle spéculative",
        "Dette souveraine",
        "Politique monétaire",
        "Effet de levier",
        "Économie circulaire",
    ),
    "Société": (
        "Contrat social",
        "Capital social",
        "Dissonance cognitive",
        "Biais de confirmation",
        "Anomie",
        "Division du travail",
        "Mobilité sociale",
        "Souveraineté numérique",
        "Légitimité politique",
        "Société civile",
    ),
    "Espace": (
        "Matière noire",
        "Énergie noire",
        "Relativité générale",
        "Fond diffus cosmologique",
        "Lentille gravitationnelle",
        "Ondes gravitationnelles",
        "Orbite géostationnaire",
        "Zone habitable",
        "Naine blanche",
        "Inflation cosmique",
    ),
    "Culture": (
        "Perspective linéaire",
        "Contrepoint",
        "Montage cinématographique",
        "Réalisme magique",
        "Intertextualité",
        "Patrimoine immatériel",
        "Ludologie",
        "Narratologie",
        "Afrofuturisme",
        "Sémiotique",
    ),
}

CATALOGUE: dict[Mode, dict[str, tuple[str, ...]]] = {
    Mode.IMPROVISED: _IMPROVISED,
    Mode.RESEARCH: _RESEARCH,
}

THEMES: tuple[str, ...] = tuple(_IMPROVISED)


def topics_for(mode: Mode, theme: str) -> tuple[Topic, ...]:
    """Les sujets d'un thème pour un mode. Lève ValueError si le thème n'existe pas."""
    by_theme = CATALOGUE[mode]
    if theme not in by_theme:
        raise ValueError(f"Thème inconnu : « {theme} ».")
    return tuple(Topic(text, theme) for text in by_theme[theme])
