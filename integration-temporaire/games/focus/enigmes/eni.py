"""
NeuroCap — Génération des Énigmes
===================================
40 énigmes JSON : 8 énigmes × 5 niveaux
Condition : focus | EEG target : gamma (intégration multimodale)

Progression : Langage → Logique → Mathématique → Intégration pure
Justification : gamma_demand corrélé à l'intégration multimodale
                (Onton et al. 2005 — gamma préfrontal pendant raisonnement)

Usage : python enigmes.py
→ génère 40 JSON + enigmes_features.csv dans games/focus/enigmes/
"""

import json
import csv
from pathlib import Path

BASE_DIR = Path(r"C:\neurocap_dataset\games\focus\enigmes")

# ─── Banque d'énigmes par niveau ──────────────────────────────────────────────
ENIGMES = {
    1: [
        {
            "q": "J'ai 3 pommes. J'en mange 1. Combien m'en reste-t-il ?",
            "r": 2, "etapes": 1, "type": "arithmetique_simple"
        },
        {
            "q": "Tu as 2 mains. Combien de doigts en tout ?",
            "r": 10, "etapes": 1, "type": "arithmetique_simple"
        },
        {
            "q": "Dans une semaine il y a 7 jours. Combien de jours dans 2 semaines ?",
            "r": 14, "etapes": 1, "type": "multiplication_contexte"
        },
        {
            "q": "Si j'achète 2 bonbons à 1€ chacun, combien je paie ?",
            "r": 2, "etapes": 1, "type": "arithmetique_simple"
        },
        {
            "q": "Un chien a 4 pattes. Combien de pattes pour 2 chiens ?",
            "r": 8, "etapes": 1, "type": "multiplication_contexte"
        },
        {
            "q": "Il est 14h. Dans 3 heures, quelle heure sera-t-il ?",
            "r": 17, "etapes": 1, "type": "calcul_temporel"
        },
        {
            "q": "J'ai 10 euros. J'achète un livre à 5 euros. Que me reste-t-il ?",
            "r": 5, "etapes": 1, "type": "arithmetique_simple"
        },
        {
            "q": "Combien de demi-heures dans 1 heure ?",
            "r": 2, "etapes": 1, "type": "division_simple"
        },
    ],
    2: [
        {
            "q": "Le double de mon âge est 24. Quel est mon âge ?",
            "r": 12, "etapes": 2, "type": "equation_simple"
        },
        {
            "q": "J'achète 3 gâteaux à 2€ et 1 jus à 3€. Total ?",
            "r": 9, "etapes": 2, "type": "multi_operations"
        },
        {
            "q": "Un bus a 10 passagers. 3 descendent, 5 montent. Combien à bord ?",
            "r": 12, "etapes": 2, "type": "sequence_operations"
        },
        {
            "q": "Je suis le tiers de 27. Qui suis-je ?",
            "r": 9, "etapes": 2, "type": "division_contexte"
        },
        {
            "q": "Marie a 15 ans. Son petit frère a la moitié de son âge. Quel est l'âge du frère ?",
            "r": 8, "etapes": 2, "type": "division_contexte"
        },
        {
            "q": "Combien de minutes dans 2 heures et 10 minutes ?",
            "r": 130, "etapes": 2, "type": "conversion_temporelle"
        },
        {
            "q": "Si 2 stylos coûtent 4€, combien coûtent 5 stylos ?",
            "r": 10, "etapes": 2, "type": "proportionnalite"
        },
        {
            "q": "J'ai 3 douzaines d'œufs. Combien d'œufs ai-je ?",
            "r": 36, "etapes": 2, "type": "multiplication_contexte"
        },
    ],
    3: [
        {
            "q": "J'ai le double de l'âge que tu avais quand j'avais l'âge que tu as. Tu as 12 ans. Quel âge ai-je ?",
            "r": 16, "etapes": 3, "type": "raisonnement_ages"
        },
        {
            "q": "Un escargot grimpe 3m le jour et redescend 2m la nuit. Mur de 10m. Quel jour arrive-t-il en haut ?",
            "r": 8, "etapes": 3, "type": "sequence_logique"
        },
        {
            "q": "Si 3 chats attrapent 3 souris en 3 minutes, combien de chats pour 100 souris en 100 minutes ?",
            "r": 3, "etapes": 3, "type": "proportionnalite_complexe"
        },
        {
            "q": "Une brique pèse 1 kg plus la moitié de son poids. Combien pèse la brique ?",
            "r": 2, "etapes": 3, "type": "equation_implicite"
        },
        {
            "q": "Un nénuphar double de taille chaque jour. Il couvre le lac en 20 jours. Quel jour couvre-t-il la moitié ?",
            "r": 19, "etapes": 2, "type": "logique_inverse"
        },
        {
            "q": "8, 5, 4, 9, 1, 7, 6, 3, 2... Quel chiffre manque dans cette suite ?",
            "r": 0, "etapes": 3, "type": "suite_logique"
        },
        {
            "q": "Chaque jour je gagne le double de la veille. Jour 1 = 1€. Combien en tout après 8 jours ?",
            "r": 255, "etapes": 3, "type": "progression_geometrique"
        },
        {
            "q": "J'ai 2 fois l'âge que tu avais quand j'avais l'âge que tu as. J'ai 40 ans. Quel âge as-tu ?",
            "r": 30, "etapes": 4, "type": "raisonnement_ages"
        },
    ],
    4: [
        {
            "q": "Une horloge sonne 6 heures en 5 secondes. Combien de temps pour sonner midi ?",
            "r": 11, "etapes": 4, "type": "logique_intervalle"
        },
        {
            "q": "5 ouvriers font 5 pièces en 5 heures. Combien pour 100 pièces avec 100 ouvriers ?",
            "r": 5, "etapes": 4, "type": "proportionnalite_complexe"
        },
        {
            "q": "Le père de Sophie a 4 fois son âge. Dans 20 ans il aura le double. Quel est l'âge actuel de Sophie ?",
            "r": 10, "etapes": 4, "type": "equation_ages"
        },
        {
            "q": "Combien de fois la petite aiguille d'une horloge est dépassée par la grande en 12 heures ?",
            "r": 11, "etapes": 4, "type": "logique_circulaire"
        },
        {
            "q": "Un cycliste roule à 20km/h. Un autre part 1h après à 30km/h. Quand le 2ème rattrape-t-il le 1er ?",
            "r": 2, "etapes": 4, "type": "vitesse_rattrapage"
        },
        {
            "q": "Si 1=5, 2=25, 3=125, 4=625, combien vaut 5 selon cette règle ?",
            "r": 1, "etapes": 4, "type": "logique_pure"
        },
        {
            "q": "J'ai des billes. Je donne 1/3 à Paul et 1/4 du reste à Pierre. Il m'en reste 10. Combien au départ ?",
            "r": 20, "etapes": 4, "type": "fractions_sequentielles"
        },
        {
            "q": "Un train de longueur inconnue traverse un tunnel de 1km à 60km/h en 1min30s. Longueur du train ?",
            "r": 500, "etapes": 4, "type": "physique_appliquee"
        },
    ],
    5: [
        {
            "q": "1000 personnes dans un château. 99% partent. Combien restent ?",
            "r": 10, "etapes": 3, "type": "piege_pourcentage"
        },
        {
            "q": "Suite : 1, 11, 21, 1211, 111221. Quel est le terme suivant ?",
            "r": 312211, "etapes": 5, "type": "suite_descriptive"
        },
        {
            "q": "3 allumettes forment 1 triangle. Combien pour 8 triangles adjacents partageant les côtés ?",
            "r": 18, "etapes": 5, "type": "geometrie_combinatoire"
        },
        {
            "q": "Trouve le nombre : 1er=1, 2ème=3, 3ème=6, 4ème=10. Que vaut le 10ème terme ?",
            "r": 55, "etapes": 4, "type": "nombres_triangulaires"
        },
        {
            "q": "Si A+B=C et C+D=B et A=5, que vaut D ?",
            "r": -5, "etapes": 5, "type": "algebre_symbolique"
        },
        {
            "q": "Un avion s'écrase exactement à la frontière entre deux pays. Où enterre-t-on les survivants ?",
            "r": 0, "etapes": 1, "type": "piege_logique",
            "explication": "On n'enterre pas les survivants — ils sont vivants"
        },
        {
            "q": "Problème de Monty Hall : 3 portes, 1 voiture, 2 chèvres. Tu choisis, l'animateur ouvre une chèvre. Dois-tu changer ? (1=oui, 0=non)",
            "r": 1, "etapes": 5, "type": "probabilite_conditionnelle"
        },
        {
            "q": "Un bâton est brisé en 3 morceaux aléatoirement. Quelle est la probabilité de former un triangle ? (répondre en %) ",
            "r": 25, "etapes": 5, "type": "probabilite_geometrique"
        },
    ],
}

LEVEL_LABELS = {
    1: "Très facile",
    2: "Facile",
    3: "Moyen",
    4: "Difficile",
    5: "Expert",
}


def compute_features(level, enigme):
    """Features statiques de l'énigme pour le système de recommandation."""
    return {
        "gamma_demand":          round(0.30 + level * 0.14, 2),
        "cognitive_steps":       enigme["etapes"],
        "mental_workload_index": round(level / 5, 2),
        "operation_type":        enigme["type"],
        "difficulty_index":      round(level / 5, 2),
        "integration_score":     round(enigme["etapes"] * (level / 5), 2),
    }


def generate_enigmes():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 55)
    print("NeuroCap — Génération Énigmes (Focus - Gamma)")
    print("=" * 55)

    for level, questions in ENIGMES.items():
        print(f"\nNiveau {level} — {LEVEL_LABELS[level]}")

        for i, enigme in enumerate(questions, start=1):
            enigme_id = f"ENI_NIV{level}_{i:03d}"
            filepath  = BASE_DIR / f"{enigme_id}.json"
            feats     = compute_features(level, enigme)

            # Type de réponse
            if isinstance(enigme["r"], float):
                type_rep = "float"
            elif isinstance(enigme["r"], int):
                type_rep = "integer"
            else:
                type_rep = "texte"

            data = {
                "id":               enigme_id,
                "filename":         f"{enigme_id}.json",
                "level":            level,
                "label":            LEVEL_LABELS[level],
                "condition":        "focus",
                "eeg_target":       "gamma_integration",
                "question":         enigme["q"],
                "reponse_attendue": enigme["r"],
                "type_reponse":     type_rep,
                "type_enigme":      enigme["type"],
                "etapes_mentales":  enigme["etapes"],
                "explication":      enigme.get("explication", ""),
                "features":         feats,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total += 1
            print(f"  [{total:02d}] {enigme_id}  "
                  f"étapes={enigme['etapes']}  "
                  f"gamma={feats['gamma_demand']:.2f}  "
                  f"type={enigme['type']}")

            all_metadata.append({
                "filename":            f"{enigme_id}.json",
                "condition":           "focus",
                "level":               level,
                "label":               LEVEL_LABELS[level],
                "eeg_target":          "gamma_integration",
                "type_enigme":         enigme["type"],
                "etapes_mentales":     enigme["etapes"],
                "gamma_demand":        feats["gamma_demand"],
                "cognitive_steps":     feats["cognitive_steps"],
                "mental_workload_index": feats["mental_workload_index"],
                "difficulty_index":    feats["difficulty_index"],
                "integration_score":   feats["integration_score"],
            })

    # Export CSV features
    meta_path = BASE_DIR / "enigmes_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*55}")
    print(f"Terminé : {total} énigmes générées")
    print(f"CSV     : {meta_path}")
    print(f"Dossier : {BASE_DIR}")
    print(f"{'='*55}")


if __name__ == "__main__":
    generate_enigmes()