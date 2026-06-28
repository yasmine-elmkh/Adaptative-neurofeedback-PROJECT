"""
Base de connaissances NeuroCap (in-memory).
Utilisée en fallback si Supabase knowledge_documents n'est pas peuplée.
10 documents couvrant : TBR, concentration, stress, alpha, profils A/B/C,
protocole 15 séances, paliers P1-P4, score, conseils.
"""

from typing import Dict, List

KNOWLEDGE_BASE: List[Dict] = [
    {
        "id": -1,
        "title": "TBR (Theta/Beta Ratio) – Indicateur clé d'attention",
        "content": (
            "TBR = Theta ÷ Beta. "
            "TBR < 0.5 = très concentré. "
            "TBR 0.5–2.0 = normal. "
            "TBR > 2.0 = difficulté d'attention ou stress. "
            "Votre TBR baseline est établi lors de la calibration S1."
        ),
        "category": "concentration",
    },
    {
        "id": -2,
        "title": "Pourcentage de Concentration – Interprétation",
        "content": (
            "80%+ = excellente session. "
            "60–80% = bonne session. "
            "40–60% = session moyenne. "
            "<40% = session difficile. "
            "Calculé par les modèles DL (GRU_Att) sur vos données EEG personnelles."
        ),
        "category": "concentration",
    },
    {
        "id": -3,
        "title": "Pourcentage de Stress – Interprétation",
        "content": (
            "<15% = état détendu. "
            "15–30% = stress normal. "
            "30–50% = stress modéré. "
            ">50% = stress élevé. "
            "Le stress EEG est détecté via beta haute-fréquence et asymétrie alpha frontale."
        ),
        "category": "stress",
    },
    {
        "id": -4,
        "title": "Bande Alpha (8–13 Hz) – Relaxation alerte",
        "content": (
            "Alpha forte = calme, yeux fermés. "
            "Alpha faible = concentration active. "
            "L'IAPF est votre fréquence alpha personnelle, mesurée lors de la calibration S1."
        ),
        "category": "eeg_basics",
    },
    {
        "id": -5,
        "title": "Profils EEG A/B/C",
        "content": (
            "Profil A: répondeur rapide, alpha/beta >1.5, ERD >30%, 12 séances. "
            "Profil B: standard, alpha/beta 0.8–1.5, 15 séances. "
            "Profil C: progressif, alpha/beta <0.8, phase 1 étendue."
        ),
        "category": "adaptation",
    },
    {
        "id": -6,
        "title": "Protocole 15 séances – 3 phases",
        "content": (
            "Phase 1 (S1–S5): calibration + découverte, 1/semaine. "
            "Phase 2 (S6–S10): entraînement actif, 2/semaine. "
            "Phase 3 (S11–S15): consolidation + transfer, 2/semaine."
        ),
        "category": "adaptation",
    },
    {
        "id": -7,
        "title": "Paliers P1–P4",
        "content": (
            "P1 Initiation: seuils accessibles. "
            "P2 Apprentissage: seuils modérés. "
            "P3 Maîtrise: seuils exigeants. "
            "P4 Autonomie: auto-régulation. "
            "Passage selon taux de succès (règle 40/60%)."
        ),
        "category": "adaptation",
    },
    {
        "id": -8,
        "title": "Score de séance – Lecture",
        "content": (
            "70%+ = excellente séance. "
            "50–70% = bonne séance. "
            "<50% = séance difficile, normal en début. "
            "La tendance compte plus qu'un score isolé."
        ),
        "category": "concentration",
    },
    {
        "id": -9,
        "title": "Conseils pour réduire le stress",
        "content": (
            "1. Respiration cohérente 5s-5s pendant 5 min. "
            "2. Éviter café 2h avant. "
            "3. Scan corporel. "
            "4. Arriver 10 min avant. "
            "5. TBR >2.5x baseline = respiration abdominale."
        ),
        "category": "stress",
    },
    {
        "id": -10,
        "title": "Conseils pour améliorer la concentration",
        "content": (
            "1. Créneau 9h–11h optimal. "
            "2. Bien s'hydrater. "
            "3. Fixer un objectif précis avant chaque bloc. "
            "4. 7–8h de sommeil améliore le TBR de 15–20%. "
            "5. 30min d'exercice/jour."
        ),
        "category": "concentration",
    },
]


def fmt_kb(docs: List[Dict]) -> str:
    """Formate les documents KB pour l'injection dans le prompt LLM."""
    if not docs:
        return ""
    parts = ["# BASE DE CONNAISSANCES NEUROCAP\n"]
    for d in docs:
        score = d.get("final_score") or d.get("similarity", 0)
        parts.append(f"## {d['title']} (pertinence: {score:.2f})\n{d['content']}\n")
    return "\n".join(parts)
