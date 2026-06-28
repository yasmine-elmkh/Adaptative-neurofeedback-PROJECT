"""
NeuroCap — Initialisation de la Knowledge Base dans Supabase
=============================================================
Ce script est à exécuter UNE SEULE FOIS après avoir appliqué
le fichier sql/init_knowledge_base.sql dans Supabase.

Usage (depuis le dossier Backend/) :
    python -m scripts.init_kb

Prérequis :
    1. Ollama démarré  : ollama serve
    2. Modèle embeddings disponible : ollama pull nomic-embed-text
    3. Variables .env  : SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
    4. SQL appliqué    : sql/init_knowledge_base.sql exécuté dans Supabase
"""

import os
import sys
import time

# Ajouter le répertoire parent au path pour accéder à app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY  = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
OLLAMA_URL    = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL   = "nomic-embed-text"
EMBED_DIM     = 768

# ── Documents de la base de connaissances ─────────────────────────────────────

KNOWLEDGE_DOCS = [
    {
        "title": "Bande Alpha (8–13 Hz) – Relaxation alerte",
        "content": (
            "La bande alpha (8–13 Hz) reflète un état de détente consciente. "
            "Elle est forte quand vous fermez les yeux ou êtes calme, et chute "
            "lorsque vous vous concentrez sur une tâche. "
            "Une alpha élevée au repos est signe d'un cerveau bien équilibré. "
            "L'IAPF (Individual Alpha Peak Frequency) est votre fréquence alpha personnelle, "
            "généralement entre 8 et 12 Hz. Elle est stable chez un individu sain."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "Bande Beta (13–30 Hz) – Concentration et éveil",
        "content": (
            "La bande beta (13–30 Hz) est associée à la concentration, à la résolution "
            "de problèmes et à l'état d'éveil actif. "
            "Un beta modéré (15–20 Hz) est signe de bonne attention. "
            "Un beta très élevé (> 25 Hz) peut indiquer de l'anxiété ou du stress mental. "
            "Le neurofeedback vise à augmenter le beta dans les plages 15–18 Hz "
            "pour améliorer la concentration sans stress."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "Bande Theta (4–8 Hz) – Somnolence et créativité",
        "content": (
            "La bande theta (4–8 Hz) est présente lors de la somnolence, de la rêverie "
            "ou d'une tâche cognitive très difficile. "
            "Un theta élevé pendant une tâche d'attention signale une difficulté à se concentrer. "
            "Theta augmente aussi en méditation profonde ou lors de créativité. "
            "L'objectif du neurofeedback est de réduire le theta excessif lors des tâches cognitives."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "Bande Delta (0.5–4 Hz) – Sommeil profond",
        "content": (
            "La bande delta (0.5–4 Hz) domine pendant le sommeil profond (stade N3). "
            "Un delta élevé en état d'éveil peut indiquer une fatigue profonde ou "
            "des artefacts (mouvements, clignements des yeux). "
            "NeuroCap rejette automatiquement les époques contaminées par des artefacts delta."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "TBR (Theta/Beta Ratio) – Indicateur clé d'attention",
        "content": (
            "TBR = Puissance Theta ÷ Puissance Beta. "
            "C'est l'indicateur central de la concentration dans NeuroCap. "
            "TBR < 0.5 → Très concentré. "
            "TBR 0.5–2.0 → Attention normale. "
            "TBR > 2.0 → Difficulté d'attention, somnolence ou stress. "
            "Votre TBR de référence (baseline) est mesuré lors de la calibration S1. "
            "L'objectif du programme est de réduire le TBR vers la baseline ou en-dessous."
        ),
        "category": "concentration",
    },
    {
        "title": "Pourcentage de Concentration – Interprétation",
        "content": (
            "Le pourcentage de concentration indique la proportion des époques EEG "
            "(fenêtres de 4 secondes) classifiées comme état de concentration par l'IA. "
            "80 %+ = Excellente session, très focalisée. "
            "60–80 % = Bonne session, quelques moments de décrochage normaux. "
            "40–60 % = Session moyenne, variabilité importante. "
            "< 40 % = Session difficile – fatigue ou forte distractibilité. "
            "Ce chiffre est calculé par un modèle LightGBM personnalisé à vos données."
        ),
        "category": "concentration",
    },
    {
        "title": "Pourcentage de Stress – Interprétation",
        "content": (
            "Le pourcentage de stress mesure la proportion des époques avec des signaux "
            "de stress dans l'EEG (beta haute fréquence et asymétrie alpha perturbée). "
            "< 15 % = État détendu, très bon. "
            "15–30 % = Léger stress situationnel, normal. "
            "30–50 % = Stress modéré ; pratiquez des exercices de respiration. "
            "> 50 % = Stress élevé ; une pause ou une séance de relaxation est conseillée. "
            "Un stress EEG élevé peut refléter l'anxiété de performance."
        ),
        "category": "stress",
    },
    {
        "title": "IAPF – Fréquence Alpha Individuelle",
        "content": (
            "L'IAPF (Individual Alpha Peak Frequency) est la fréquence alpha dominante "
            "propre à chaque personne. Elle varie entre 7 et 13 Hz. "
            "IAPF > 10 Hz → souvent associée à une meilleure performance cognitive. "
            "IAPF < 9 Hz → peut indiquer une fatigue chronique ou un déficit attentionnel. "
            "Votre IAPF est mesurée lors de la calibration S1 et sert à personnaliser "
            "les seuils de neurofeedback."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "Profil EEG A – Répondeur Rapide",
        "content": (
            "Profil A : cerveau très réactif au neurofeedback. "
            "Ratio alpha/beta au repos > 1.5 et réactivité ERD > 30 %. "
            "Vous progressez rapidement, démarrez directement au Palier P2. "
            "Programme optimisé en 12 séances. "
            "Vous avez d'excellentes prédispositions – continuez vos efforts !"
        ),
        "category": "adaptation",
    },
    {
        "title": "Profil EEG B – Répondeur Standard",
        "content": (
            "Profil B : programme standard de 15 séances avec 4 paliers progressifs. "
            "Ratio alpha/beta entre 0.8 et 1.5. "
            "Progression régulière avec adaptation dynamique des seuils. "
            "La grande majorité des patients sont profil B. "
            "Restez régulier : des améliorations mesurables apparaissent dès la phase 2."
        ),
        "category": "adaptation",
    },
    {
        "title": "Profil EEG C – Répondeur Progressif",
        "content": (
            "Profil C : le cerveau a besoin de plus de temps pour apprendre le neurofeedback. "
            "Ratio alpha/beta < 0.8. Les seuils sont très accessibles au début. "
            "La phase 1 est étendue à 5 séances pour consolider les bases. "
            "Sans progression à S10, une consultation spécialisée est recommandée. "
            "Soyez patient : les bénéfices arrivent plus tard mais sont durables."
        ),
        "category": "adaptation",
    },
    {
        "title": "Paliers P1 à P4 – Progression de difficulté",
        "content": (
            "P1 Initiation : seuils très accessibles, objectif de découverte du neurofeedback. "
            "P2 Apprentissage : seuils modérés, apprentissage actif de la régulation cérébrale. "
            "P3 Maîtrise : seuils exigeants, consolidation des acquis. "
            "P4 Autonomie : niveau expert, auto-régulation sans feedback externe. "
            "Passage automatique entre paliers selon taux de succès (règle 40/60 % sur 3 séances)."
        ),
        "category": "adaptation",
    },
    {
        "title": "Score de séance – Comment le lire",
        "content": (
            "Le score de séance (0–100 %) résume la performance globale. "
            "Il combine : taux de succès des blocs (TBR sous le seuil), "
            "qualité du signal EEG, et évolution du TBR par rapport à la baseline. "
            "70 %+ = Excellente séance. "
            "50–70 % = Bonne séance avec marges de progression. "
            "< 50 % = Séance difficile, normal en début de programme. "
            "La tendance sur plusieurs séances compte plus qu'un score isolé."
        ),
        "category": "concentration",
    },
    {
        "title": "Protocole 15 séances – Les 3 phases",
        "content": (
            "Phase 1 (S1–S5) : Calibration et découverte (1 séance/semaine). "
            "S1 = calibration EEG individuelle 30 min. S2–S5 = apprentissage de base. "
            "Phase 2 (S6–S10) : Entraînement actif (2 séances/semaine). "
            "Adaptation dynamique des seuils selon vos progrès. "
            "Phase 3 (S11–S15) : Consolidation (2 séances/semaine). "
            "Réduction progressive du feedback et transfer vers la vie quotidienne."
        ),
        "category": "adaptation",
    },
    {
        "title": "Conseils pour réduire le stress avant une séance",
        "content": (
            "1. Respiration cohérente cardiaque : inspirez 5 sec, expirez 5 sec, répétez 5 min. "
            "2. Scan corporel : fermez les yeux, relâchez chaque groupe musculaire. "
            "3. Arrivez 10 minutes avant la séance, évitez le téléphone. "
            "4. Évitez le café 2 h avant la séance. "
            "5. Si TBR > 2.5 × baseline, faites 5 min de respiration abdominale. "
            "Ces techniques renforcent l'efficacité du neurofeedback."
        ),
        "category": "stress",
    },
    {
        "title": "Conseils pour améliorer la concentration",
        "content": (
            "1. Choisissez un créneau où vous êtes naturellement alerte (souvent 9h–11h). "
            "2. Hydratez-vous bien : le cerveau a besoin d'eau pour fonctionner. "
            "3. Fixez un objectif précis avant chaque bloc. "
            "4. Après chaque séance, notez ce qui a bien fonctionné. "
            "5. 7–8 h de sommeil améliorent le TBR de 15–20 % en moyenne. "
            "6. 30 min d'exercice physique quotidien augmente la plasticité cérébrale."
        ),
        "category": "concentration",
    },
    {
        "title": "Qualité du signal EEG et artefacts",
        "content": (
            "La qualité du signal influence la fiabilité des résultats. "
            "Artefacts courants : clignements des yeux, mâchoire, tension cervicale. "
            "Taux d'artefacts > 30 % = réduction de la précision de l'analyse. "
            "Pour minimiser : restez immobile, évitez de parler, mâcher, tourner la tête. "
            "NeuroCap rejette automatiquement les époques avec artefacts. "
            "Taux d'acceptation < 50 % peut signaler un problème d'électrode."
        ),
        "category": "eeg_basics",
    },
    {
        "title": "Comment fonctionne le neurofeedback",
        "content": (
            "Le neurofeedback est un entraînement cérébral basé sur le biofeedback. "
            "1. Capteurs EEG mesurent votre activité cérébrale en temps réel. "
            "2. Un algorithme IA analyse et classe chaque seconde d'activité. "
            "3. Un feedback visuel ou sonore indique si votre cerveau est dans l'état cible. "
            "4. Votre cerveau apprend progressivement à se réguler (plasticité neuronale). "
            "L'apprentissage est largement inconscient – il suffit de rester attentif."
        ),
        "category": "adaptation",
    },
    {
        "title": "Progression attendue sur 15 séances",
        "content": (
            "Résultats typiques pour un profil B : "
            "S1–S3 : Familiarisation, scores variables (40–65 %), tout à fait normal. "
            "S4–S7 : Premiers progrès visibles, TBR commence à diminuer. "
            "S8–S10 : Amélioration nette, score moyen > 65 % attendu. "
            "S11–S15 : Consolidation, transfert vers la vie quotidienne. "
            "15–20 % des patients progressent plus lentement (profil C) — c'est normal."
        ),
        "category": "adaptation",
    },
    {
        "title": "Habitudes quotidiennes bénéfiques pour le cerveau",
        "content": (
            "Sommeil : 7–9 h par nuit, horaires réguliers, éviter les écrans 1 h avant. "
            "Exercice : 30 min/jour améliore plasticité cérébrale et réduit le TBR. "
            "Alimentation : oméga-3 (poissons gras, noix) soutiennent les membranes neuronales. "
            "Méditation : 10 min/jour amplifie les effets du neurofeedback. "
            "Gestion du stress chronique : identifier les sources et les réduire. "
            "Ces habitudes multiplient l'efficacité du programme par 1.5–2×."
        ),
        "category": "stress",
    },
]


# ── Fonctions utilitaires ──────────────────────────────────────────────────────

def check_ollama() -> bool:
    """Vérifie qu'Ollama est démarré et que nomic-embed-text est disponible."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            return False
        models = [m["name"] for m in resp.json().get("models", [])]
        return any("nomic-embed-text" in m for m in models)
    except Exception:
        return False


def embed(text: str) -> list[float] | None:
    """Génère un vecteur 768d via Ollama nomic-embed-text."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        if resp.status_code == 200:
            vec = resp.json().get("embedding")
            if vec and len(vec) == EMBED_DIM:
                return vec
            print(f"  ⚠ Dimension inattendue : {len(vec) if vec else 'None'} (attendu {EMBED_DIM})")
    except Exception as e:
        print(f"  ✗ Erreur embedding : {e}")
    return None


# ── Script principal ───────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  NeuroCap — Initialisation Knowledge Base (Supabase)")
    print("=" * 60)

    # Vérifications préalables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n✗ Variables manquantes dans .env :")
        print("  SUPABASE_URL            =", SUPABASE_URL or "(vide)")
        print("  SUPABASE_SERVICE_ROLE_KEY =", "***" if SUPABASE_KEY else "(vide)")
        sys.exit(1)

    print("\n[1/3] Vérification Ollama…")
    if not check_ollama():
        print("  ✗ Ollama non disponible ou nomic-embed-text non installé.")
        print("  Exécutez : ollama serve && ollama pull nomic-embed-text")
        sys.exit(1)
    print(f"  ✓ Ollama disponible — modèle : {EMBED_MODEL}")

    print("\n[2/3] Connexion Supabase…")
    try:
        db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test de connexion : la table doit exister
        db.table("knowledge_documents").select("id").limit(1).execute()
        print(f"  ✓ Connecté à {SUPABASE_URL}")
    except Exception as e:
        print(f"  ✗ Connexion Supabase échouée : {e}")
        print("  Avez-vous exécuté sql/init_knowledge_base.sql dans Supabase ?")
        sys.exit(1)

    print(f"\n[3/3] Indexation de {len(KNOWLEDGE_DOCS)} documents…\n")
    success = 0
    failed  = 0

    for i, doc in enumerate(KNOWLEDGE_DOCS, 1):
        label = f"[{i:02d}/{len(KNOWLEDGE_DOCS)}] {doc['title'][:55]}"

        # Embedder le titre + contenu concatenés
        text = f"{doc['title']}. {doc['content']}"
        vec  = embed(text)

        if vec is None:
            print(f"  ✗ {label} — embedding échoué, ignoré")
            failed += 1
            continue

        try:
            db.table("knowledge_documents").upsert(
                {
                    "title":    doc["title"],
                    "content":  doc["content"],
                    "category": doc["category"],
                    "embedding": vec,           # liste Python → JSON array → vector(768) en PG
                },
                on_conflict="title",            # mise à jour si le titre existe déjà
            ).execute()
            print(f"  ✓ {label}")
            success += 1
        except Exception as e:
            print(f"  ✗ {label} — erreur Supabase : {e}")
            failed += 1

        # Pause courte pour ne pas saturer Ollama
        time.sleep(0.3)

    print(f"\n{'=' * 60}")
    print(f"  Résultat : {success} ✓ insérés  |  {failed} ✗ échoués")
    if failed == 0:
        print("  🎉 Knowledge Base prête ! Vous pouvez démarrer le backend.")
    else:
        print("  ⚠ Relancez le script pour réessayer les documents échoués.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
