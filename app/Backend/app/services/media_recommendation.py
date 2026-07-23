"""
NeuroCap — Service de recommandation média adaptatif EEG

Logique centrale : scorer les médias selon l'état EEG temps réel, le profil
du patient (A/B/C), son palier (P1–P4) et son historique de préférences.
"""

import logging
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from supabase import AsyncClient

logger = logging.getLogger(__name__)

# ── Constantes métier ─────────────────────────────────────────────────────────

# Profil cognitif → catégories de médias préférées
PROFILE_CATEGORIES: dict[str, list[str]] = {
    "A": ["nature", "binaural", "meditation", "calming", "ambient"],   # Hyperactif
    "B": ["nature", "focus", "relaxation", "ambient", "classical"],    # Standard
    "C": ["rhythmic", "energetic", "focus", "stimulating", "upbeat"],  # Hypoactif
}

# Plage tempo BPM adaptée au palier
PALIER_TEMPO: dict[str, tuple[float, float]] = {
    "P1": (60.0, 80.0),
    "P2": (70.0, 90.0),
    "P3": (80.0, 100.0),
    "P4": (40.0, 120.0),  # variable
}

# Durée max (secondes) par palier — règle métier critique
PALIER_MAX_DURATION: dict[str, Optional[int]] = {
    "P1": 180,
    "P2": 300,
    "P3": 600,
    "P4": None,
}

# Catégories apaisantes pour injection prioritaire en cas de stress prolongé
CALMING_CATEGORIES = frozenset(["nature", "binaural", "meditation", "calming", "relaxation", "ambient"])

# Délai d'expiration des recommandations (7 jours)
REC_EXPIRY_DAYS = 7


# ── État EEG ──────────────────────────────────────────────────────────────────

def determine_eeg_state(concentration_rate: float, stress_rate: float) -> str:
    if stress_rate > 0.6:
        return "stress"
    if concentration_rate > 0.7:
        return "focus"
    return "neutral"


def get_profile_categories(profile_type: str) -> list[str]:
    return PROFILE_CATEGORIES.get(profile_type, PROFILE_CATEGORIES["B"])


# ── Scoring d'un média ────────────────────────────────────────────────────────

def _score_illusion(media: dict, eeg_state: str) -> float:
    """
    Scoring neurophysiologique pour les illusions optiques HTML internes.

    Mécanismes :
      - mouvement_percu       → focus / transition (contre-indiqué stress)
      - ambiguite_figure_fond → focus (flexibilité cognitive)
      - distorsion_geometrique→ focus soutenu
      - couleur_complementaire→ transition / relax actif

    Retourne un score [0, 1].
    """
    mecanisme = (media.get("mecanisme") or "").lower()
    intensite = float(media.get("intensite_effet") or 3)
    contre_stress = str(media.get("contre_indique_stress") or "False").lower() == "true"
    target = (media.get("target_state") or "transition").lower()

    if eeg_state == "stress":
        if contre_stress or mecanisme == "mouvement_percu" and intensite >= 4:
            return 0.0
        if mecanisme == "couleur_complementaire":
            return 0.70
        if target == "transition" and intensite <= 2:
            return 0.55
        return 0.35

    elif eeg_state == "focus":
        if mecanisme in ("ambiguite_figure_fond", "distorsion_geometrique"):
            score = 0.60 + min(intensite / 5.0, 1.0) * 0.30
        elif mecanisme == "mouvement_percu":
            score = 0.50 + min(intensite / 5.0, 1.0) * 0.20
        else:
            score = 0.40
        return min(score, 1.0)

    else:  # relax / transition / neutral
        if mecanisme in ("mouvement_percu", "couleur_complementaire"):
            score = 0.65
        elif mecanisme == "ambiguite_figure_fond":
            score = 0.45
        else:
            score = 0.40
        # Bonus si intensité faible (moins d'arousal)
        if intensite <= 2:
            score += 0.15
        return min(score, 1.0)


def score_media(
    media: dict,
    profile_type: str,
    eeg_state: str,
    palier: str,
    liked_media_ids: set[str],
    calming_priority: bool = False,
) -> float:
    """
    Retourne un score [0, 1] pour ce média.

    Formule : base_thompson * profile_weight * state_weight * liked_bonus
    - Filtre dur : durée > max_palier → score 0
    - profile_weight : 1.2 si catégorie alignée au profil, 0.8 sinon
    - state_weight   : boost si média adapté à l'état EEG courant
    - liked_bonus    : 1.3 si le patient a déjà liké ce média
    - Illusions internes : scoring neurophysiologique direct (pas de Thompson)
    """
    # Illusions HTML internes → scoring neurophysiologique direct
    if media.get("type") == "illusion" or media.get("source") == "internal_html":
        base = _score_illusion(media, eeg_state)
        liked_bonus = 1.2 if str(media.get("id", "")) in liked_media_ids else 1.0
        return min(1.0, base * liked_bonus)

    duration = media.get("duration_seconds")
    max_dur = PALIER_MAX_DURATION.get(palier)
    if max_dur and duration and duration > max_dur:
        return 0.0

    # Score de base Thompson sampling (utilise les poids existants de la table medias)
    alpha = max(float(media.get("item_weights_alpha") or 1.0), 0.1)
    beta  = max(float(media.get("item_weights_beta")  or 1.0), 0.1)
    base_score = random.betavariate(alpha, beta)

    # Poids profil
    category = (media.get("category") or "").lower()
    preferred = get_profile_categories(profile_type)
    profile_weight = 1.2 if category in preferred else 0.8

    # Poids état EEG
    brightness = float(media.get("brightness") or 0.5)
    tempo      = float(media.get("tempo_bpm")  or 75.0)
    state_weight = 1.0

    if eeg_state == "stress":
        if category in CALMING_CATEGORIES:
            state_weight = 1.5
        elif brightness < 0.4:
            state_weight = 1.3
    elif eeg_state == "focus":
        t_min, t_max = PALIER_TEMPO.get(palier, (70.0, 90.0))
        if t_min <= tempo <= t_max:
            state_weight = 1.3

    # Priorité calming (stress prolongé 3+ blocs)
    if calming_priority and category in CALMING_CATEGORIES:
        state_weight *= 1.5

    # Bonus mémoriel (déjà liké)
    liked_bonus = 1.3 if str(media.get("id", "")) in liked_media_ids else 1.0

    return min(1.0, base_score * profile_weight * state_weight * liked_bonus)


# ── Récupération des médias likés ─────────────────────────────────────────────

async def get_liked_media_ids(user_id: str, db: AsyncClient) -> set[str]:
    liked: set[str] = set()
    try:
        r1 = await (
            db.table("offline_recommendations")
            .select("media_id")
            .eq("user_id", user_id)
            .eq("liked", True)
            .execute()
        )
        liked.update(str(r["media_id"]) for r in (r1.data or []))

        r2 = await (
            db.table("media_interactions")
            .select("media_id")
            .eq("patient_id", user_id)
            .eq("liked", True)
            .execute()
        )
        liked.update(str(r["media_id"]) for r in (r2.data or []))
    except Exception as exc:
        logger.warning("get_liked_media_ids: %s", exc)
    return liked


# ── Génération des recommandations live ──────────────────────────────────────

async def generate_live_recommendations(
    user_id: str,
    session_id: str,
    eeg_state: str,
    profile_type: str,
    palier: str,
    calming_priority: bool,
    db: AsyncClient,
    top_n: int = 5,
) -> list[dict]:
    """
    Génère le top-N des médias recommandés pour une session live.
    Insère/met à jour dans recommendations_media et retourne les médias.
    """
    # Préférences utilisateur (catégories préférées)
    pref_resp = await (
        db.table("user_media_preferences")
        .select("preferred_categorie")
        .eq("user_id", user_id)
        .execute()
    )
    pref_cats = {r["preferred_categorie"] for r in (pref_resp.data or [])}

    # Pool de médias
    medias_resp = await db.table("medias").select("*").execute()
    all_medias: list[dict] = medias_resp.data or []

    # Filtrer par catégorie préférée si disponible, sinon toute la librairie
    pool = [m for m in all_medias if not pref_cats or (m.get("category") or "").lower() in pref_cats]
    if not pool:
        pool = all_medias

    # Récupérer médias déjà likés (bonus)
    liked_ids = await get_liked_media_ids(user_id, db)

    # Scorer
    scored = [
        (m, score_media(m, profile_type, eeg_state, palier, liked_ids, calming_priority))
        for m in pool
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_n]

    now = datetime.now(timezone.utc)
    expires = (now + timedelta(days=REC_EXPIRY_DAYS)).isoformat()
    reason = f"session_live|eeg={eeg_state}|profil={profile_type}|palier={palier}"

    # Upsert dans recommendations_media
    results = []
    for media, score in top:
        if score <= 0:
            continue
        rec = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "media_id": str(media["id"]),
            "score": round(score, 4),
            "reason": reason,
            "generated_at": now.isoformat(),
            "expires_at": expires,
            "is_clicked": False,
        }
        try:
            await (
                db.table("recommendations_media")
                .upsert(rec, on_conflict="user_id,media_id")
                .execute()
            )
        except Exception as exc:
            logger.warning("upsert recommendations_media: %s", exc)
        results.append(media)

    return results


# ── Mise à jour préférences après rating ─────────────────────────────────────

async def update_user_preferences(
    user_id: str,
    media: dict,
    rating_value: float,
    db: AsyncClient,
) -> None:
    """Met à jour user_media_preferences de façon pondérée après notation."""
    category = (media.get("category") or "general").lower()
    now = datetime.now(timezone.utc).isoformat()

    try:
        resp = await (
            db.table("user_media_preferences")
            .select("*")
            .eq("user_id", user_id)
            .eq("preferred_categorie", category)
            .execute()
        )
        new_tempo  = float(media.get("tempo_bpm")   or 75.0)
        new_bright = float(media.get("brightness")  or 0.5)
        new_sat    = float(media.get("saturation")  or 0.5)
        new_cont   = float(media.get("contrast")    or 0.5)
        w = rating_value / 5.0  # poids selon la note (1→0.2, 5→1.0)

        if resp.data:
            pref = resp.data[0]
            pref_vec = pref.get("preferences_vector") or {}
            media_type = media.get("type", "audio")
            pref_vec[media_type] = pref_vec.get(media_type, 0) + 1

            def weighted(old, new):
                return round(float(old or new) * (1 - w) + new * w, 4)

            await (
                db.table("user_media_preferences")
                .update({
                    "avg_tempo_bpm":      weighted(pref.get("avg_tempo_bpm"),   new_tempo),
                    "avg_brightness":     weighted(pref.get("avg_brightness"),  new_bright),
                    "avg_saturation":     weighted(pref.get("avg_saturation"),  new_sat),
                    "avg_contrast":       weighted(pref.get("avg_contrast"),    new_cont),
                    "preferences_vector": pref_vec,
                    "last_updated":       now,
                })
                .eq("user_id", user_id)
                .eq("preferred_categorie", category)
                .execute()
            )
        else:
            await (
                db.table("user_media_preferences")
                .insert({
                    "user_id":             user_id,
                    "preferred_categorie": category,
                    "preferred_type":      media.get("type"),
                    "avg_tempo_bpm":       new_tempo,
                    "avg_brightness":      new_bright,
                    "avg_saturation":      new_sat,
                    "avg_contrast":        new_cont,
                    "preferences_vector":  {media.get("type", "audio"): 1},
                    "last_updated":        now,
                })
                .execute()
            )
    except Exception as exc:
        logger.warning("update_user_preferences: %s", exc)


# ── Recalcul scores après fine-tuning ────────────────────────────────────────

async def recalculate_scores_after_finetuning(
    patient_id: str,
    accuracy_after: float,
    db: AsyncClient,
) -> int:
    """
    Après un fine-tuning, booste/pénalise les scores des recommendations_media.
    Nouveau score = clamp(ancien × (1 + (accuracy_after - 0.5)), 0, 1)
    Retourne le nombre de lignes mises à jour.
    """
    try:
        resp = await (
            db.table("recommendations_media")
            .select("id,score")
            .eq("user_id", patient_id)
            .execute()
        )
        recs = resp.data or []
        if not recs:
            return 0

        factor = 1.0 + (accuracy_after - 0.5)
        updated = 0
        for rec in recs:
            new_score = min(1.0, max(0.0, float(rec["score"]) * factor))
            try:
                await (
                    db.table("recommendations_media")
                    .update({"score": round(new_score, 4)})
                    .eq("id", rec["id"])
                    .execute()
                )
                updated += 1
            except Exception:
                pass
        return updated
    except Exception as exc:
        logger.warning("recalculate_scores_after_finetuning: %s", exc)
        return 0


# ── Purge des recommandations expirées ────────────────────────────────────────

async def purge_expired_recommendations(db: AsyncClient) -> int:
    """Supprime les recommendations_media expirées (> 7 jours)."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        resp = await (
            db.table("recommendations_media")
            .delete()
            .lt("expires_at", now)
            .execute()
        )
        return len(resp.data or [])
    except Exception as exc:
        logger.warning("purge_expired_recommendations: %s", exc)
        return 0
