"""
NeuroCap — Génération rapport session via LLM (DeepSeek → Groq fallback)
"""

import logging
from typing import Optional
from openai import AsyncOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


async def _call_llm(prompt: str, max_tokens: int = 400) -> Optional[str]:
    """
    Appelle le meilleur LLM disponible dans cet ordre :
      1. DeepSeek API (si DEEPSEEK_API_KEY configurée et solde > 0)
      2. Groq API    (si GROQ_API_KEY configurée — gratuit, 14 400 req/jour)
    Retourne None si les deux sont indisponibles.
    """
    settings = get_settings()

    # ── 1. DeepSeek ──────────────────────────────────────────────────────
    if settings.DEEPSEEK_API_KEY:
        try:
            client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )
            response = await client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("DeepSeek API indisponible (%s) — essai Groq", e)

    # ── 2. Groq (fallback gratuit) ────────────────────────────────────────
    if settings.GROQ_API_KEY:
        try:
            client = AsyncOpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
            model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
            response = await client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Groq API erreur : %s", e)

    logger.warning("Aucun LLM disponible — rapport non généré (configurer GROQ_API_KEY ou DEEPSEEK_API_KEY)")
    return None


async def generate_session_report(session_data: dict) -> Optional[str]:
    """
    Génère un rapport de séance de neurofeedback en français via DeepSeek API.

    session_data attendu :
        duration_min        float
        items_played        int
        items_efficaces     int
        delta_alpha_global  float
        delta_beta_global   float
        session_success     bool
        objective           str   (concentration | relaxation)
        patient_profile     dict  {profile_type, palier, session_number}
        media_played        list  [{type, filename, efficace}]
    """
    prof = session_data.get("patient_profile", {})
    profile_type = prof.get("profile_type", "B")
    palier = prof.get("palier", 1)
    session_num = prof.get("session_number", "?")

    delta_a = session_data.get("delta_alpha_global", 0)
    delta_b = session_data.get("delta_beta_global", 0)
    success = session_data.get("session_success", False)
    items_ok = session_data.get("items_efficaces", 0)
    items_total = session_data.get("items_played", 0)
    duration = session_data.get("duration_min", 0)
    objective = session_data.get("objective", "concentration")

    media_summary = ""
    for m in session_data.get("media_played", [])[:5]:
        eff = "efficace" if m.get("efficace") else "neutre"
        media_summary += f"  - {m.get('type', '?')} {m.get('filename', '')} → {eff}\n"

    prompt = f"""Tu es un expert en neurofeedback EEG clinique. Génère un rapport de séance concis en français (150-200 mots) structuré en 3 parties numérotées.

DONNÉES DE LA SÉANCE #{session_num} :
- Profil EEG : Type {profile_type}, Palier P{palier}
- Objectif : {objective}
- Durée : {duration:.1f} minutes
- Médias présentés : {items_total} dont {items_ok} efficaces ({round(items_ok/max(items_total,1)*100)}%)
- Delta alpha global : {delta_a:+.3f} (positif = amélioration relax)
- Delta beta global : {delta_b:+.3f} (négatif = réduction stress)
- Succès global : {"OUI" if success else "NON"}
- Médias présentés :
{media_summary or "  - Aucun média enregistré"}

STRUCTURE OBLIGATOIRE :
1. RÉSUMÉ EEG OBJECTIF : Interprète les deltas alpha/beta avec des données chiffrées précises.
2. CE QUI A FONCTIONNÉ : Identifie les médias et moments de concentration réussie.
3. RECOMMANDATIONS : Conseils personnalisés pour la prochaine séance selon le profil {profile_type} palier P{palier}.

Ton : professionnel mais encourageant. Ne commence pas par "Dans cette séance"."""

    return await _call_llm(prompt, max_tokens=400)


async def generate_bilan_recommendation(
    profile_type: str,
    n_sessions: int,
    avg_success: float,
    score_evolution: list,
    current_palier: str,
    alpha_trend: float,
    iapf: float = 10.0,
    alpha_lo: float = 8.0,
    alpha_hi: float = 12.0,
) -> Optional[str]:
    """
    Génère une recommandation de bilan (S5/S10/S15) via DeepSeek API.
    """
    trend_str = "en hausse" if alpha_trend > 0.01 else ("en baisse" if alpha_trend < -0.01 else "stable")
    scores_str = ", ".join(str(s) for s in score_evolution[-5:]) if score_evolution else "N/A"

    prompt = f"""Tu es un expert en neurofeedback EEG clinique. Génère une recommandation de bilan en français (120-160 mots) pour un patient.

DONNÉES DU BILAN :
- Profil EEG : Type {profile_type}, Palier {current_palier}
- Séances complétées : {n_sessions}
- Taux de succès moyen : {avg_success*100:.0f}%
- Scores récents : {scores_str}
- IAPF : {iapf:.1f} Hz (bande alpha personnalisée : {alpha_lo}-{alpha_hi} Hz)
- Tendance alpha : {trend_str} (Δ={alpha_trend:+.4f})

STRUCTURE OBLIGATOIRE :
1. BILAN OBJECTIF : Résumé chiffré des progrès.
2. POINTS FORTS : Ce qui s'améliore pour ce profil {profile_type}.
3. PROCHAINES ÉTAPES : Recommandations concrètes pour les séances suivantes.

Ton : professionnel, motivant, précis."""

    return await _call_llm(prompt, max_tokens=350)


async def generate_media_guide(
    media: dict,
    eeg_state: str,
    eeg_features: dict = None,
    liked_history: list = None,
) -> Optional[str]:
    """
    Génère un guide d'interaction personnalisé pour un média (2 phrases max).

    media         : {type, filename, category, eeg_target_state, brightness,
                     contrast, saturation, tempo_bpm, difficulty_level, duration_seconds}
    eeg_state     : 'concentration' | 'stress' | 'neutral'
    eeg_features  : {rel_alpha, rel_beta, theta_beta, engagement}
    liked_history : [{'type', 'filename', 'liked', 'efficace', 'note_concentration'}]
    """
    mtype    = media.get("type", "image")
    fname    = (media.get("filename") or "").replace("_", " ").rsplit(".", 1)[0]
    category = media.get("category") or media.get("eeg_target_state", "neutral")
    target   = media.get("eeg_target_state", "all")
    diff     = media.get("difficulty_level", 1)

    # ── Descripteurs visuels / sonores ────────────────────────────
    desc_parts = []

    if mtype in ("image", "video"):
        feat = media.get("features") or {}

        bri = media.get("brightness") or feat.get("brightness_mean") or feat.get("brightness_global")
        con = media.get("contrast") or feat.get("contrast") or feat.get("contrast_mean")
        sat = media.get("saturation") or feat.get("saturation_mean")

        if bri is not None:
            desc_parts.append(
                f"luminosité {'élevée' if bri > 0.6 else 'faible' if bri < 0.4 else 'modérée'} ({bri:.2f})"
            )
        if con is not None:
            desc_parts.append(
                f"contraste {'fort' if con > 0.6 else 'doux' if con < 0.4 else 'moyen'} ({con:.2f})"
            )
        if sat is not None:
            desc_parts.append(
                f"saturation {'riche' if sat > 0.6 else 'désaturée' if sat < 0.35 else 'neutre'}"
            )

        if mtype == "image":
            warm_cold  = feat.get("warm_cold_ratio")
            edge_dens  = feat.get("edge_density") or feat.get("edge_density_mean")
            entropy_v  = feat.get("entropy")
            symmetry_v = feat.get("symmetry")
            hf_ratio   = feat.get("spatial_freq_hf_ratio")

            if warm_cold is not None:
                if warm_cold > 1.3:
                    desc_parts.append("palette chaude (orangés/rouges dominants)")
                elif warm_cold < 0.7:
                    desc_parts.append("palette froide (bleus/verts dominants)")
                else:
                    desc_parts.append("palette neutre équilibrée")

            if edge_dens is not None:
                if edge_dens > 0.25:
                    desc_parts.append("contours denses et détaillés")
                elif edge_dens < 0.08:
                    desc_parts.append("contours doux et minimalistes")
                else:
                    desc_parts.append("contours modérés")

            if entropy_v is not None and symmetry_v is not None:
                if symmetry_v > 0.75 and entropy_v < 5.5:
                    desc_parts.append("motif géométrique symétrique (type mandala)")
                elif hf_ratio is not None and hf_ratio > 0.35 and entropy_v > 6.0:
                    desc_parts.append("composition abstraite complexe")
                else:
                    desc_parts.append("scène naturelle structurée")
            elif entropy_v is not None:
                desc_parts.append("composition abstraite" if entropy_v > 6.5 else "scène naturelle")

    if mtype == "audio":
        feat = media.get("features") or {}

        bpm      = media.get("tempo_bpm") or feat.get("tempo_bpm")
        harm     = feat.get("harm_perc_ratio")
        stationa = feat.get("spectral_stationarity")
        centroid = feat.get("spec_centroid_mean")
        rms      = feat.get("rms_mean")
        e_bass   = feat.get("energy_bass")
        e_high   = feat.get("energy_high_mid")

        if bpm:
            desc_parts.append(
                f"tempo {'rapide' if bpm > 100 else 'lent' if bpm < 60 else 'modéré'} ({bpm:.0f} BPM)"
            )
        if harm is not None:
            if harm > 5:
                desc_parts.append("très harmonique et mélodique")
            elif harm < 0.5:
                desc_parts.append("percussif et rythmique")
            else:
                desc_parts.append("équilibre harmoniques/percussions")
        if stationa is not None:
            if stationa > 60:
                desc_parts.append("spectre stable et continu (type drone/ambient)")
            elif stationa < 15:
                desc_parts.append("spectre très évolutif et varié")
        if centroid is not None:
            if centroid < 1500:
                desc_parts.append("timbre chaud et grave (basses fréquences dominantes)")
            elif centroid > 4000:
                desc_parts.append("timbre brillant et aérien (hautes fréquences)")
            else:
                desc_parts.append("timbre équilibré médium")
        if rms is not None:
            if rms < 0.05:
                desc_parts.append("volume doux et paisible")
            elif rms > 0.15:
                desc_parts.append("volume dense et enveloppant")
        if e_bass is not None and e_high is not None:
            if e_bass > e_high * 2:
                desc_parts.append("énergie concentrée dans les basses")
            elif e_high > e_bass * 2:
                desc_parts.append("énergie dans les médiums-aigus")

    if mtype == "video":
        feat = media.get("features") or {}

        flow       = feat.get("optical_flow_mean")
        regularity = feat.get("motion_regularity")
        scene_chg  = feat.get("scene_change_rate")
        flicker    = feat.get("flicker_rate")
        col_cat    = feat.get("color_temp_category")
        col_k      = feat.get("color_temp_k")

        if flow is not None:
            if flow < 0.5:
                desc_parts.append("image quasi-statique (très peu de mouvement)")
            elif flow > 3.0:
                desc_parts.append("mouvement très dynamique et fluide")
            else:
                desc_parts.append("mouvement lent et apaisant")
        if regularity is not None:
            if regularity > 0.7:
                desc_parts.append("mouvement régulier et prévisible")
            elif regularity < 0.3:
                desc_parts.append("mouvement irrégulier")
        if scene_chg is not None:
            if scene_chg < 0.05:
                desc_parts.append("scène continue sans coupure")
            elif scene_chg > 0.5:
                desc_parts.append("transitions fréquentes entre scènes")
        col_label = col_cat or (
            "chaude" if col_k and col_k > 5500 else
            "froide" if col_k and col_k < 3500 else None
        )
        if col_label:
            desc_parts.append(f"ambiance lumineuse {col_label}")
        if flicker is not None and flicker > 5:
            desc_parts.append("scintillement visuel notable")

    if mtype == "game":
        feat = media.get("features") or {}

        game_type  = feat.get("game_type", "logic")
        cog_load   = feat.get("cognitive_load")
        logic_dem  = feat.get("logic_demand")
        mem_dem    = feat.get("memory_demand")
        difficulty = feat.get("difficulty") or ("facile" if diff <= 1 else "difficile" if diff >= 3 else "moyen")

        type_labels = {
            "logic": "logique/calcul", "memory": "mémoire",
            "puzzle": "puzzle spatial", "coloriage": "coloriage thérapeutique",
            "enigmes": "énigmes", "sudoku": "sudoku",
        }
        desc_parts.append(f"type : {type_labels.get(game_type, game_type)}")
        desc_parts.append(f"difficulté {difficulty} (niveau {diff})")
        if cog_load is not None:
            desc_parts.append(
                f"charge cognitive {'élevée' if cog_load > 0.7 else 'modérée' if cog_load > 0.4 else 'légère'}"
            )
        if logic_dem is not None and mem_dem is not None:
            if logic_dem > mem_dem + 0.2:
                desc_parts.append("priorité raisonnement logique sur mémoire")
            elif mem_dem > logic_dem + 0.2:
                desc_parts.append("priorité mémoire de travail sur logique")

    desc_str = ", ".join(desc_parts) if desc_parts else "propriétés standard"

    # ── Contexte EEG ──────────────────────────────────────────────
    eeg_ctx = f"État EEG actuel : {eeg_state}"
    if eeg_features:
        tbr   = eeg_features.get("theta_beta", 1.0) or 1.0
        alpha = eeg_features.get("rel_alpha",  0.3) or 0.3
        beta  = eeg_features.get("rel_beta",   0.2) or 0.2
        eeg_ctx += (
            f" · Alpha {alpha*100:.0f}% · Beta {beta*100:.0f}%"
            f" · TBR {tbr:.1f}"
        )

    # ── Historique préférences ─────────────────────────────────────
    hist_ctx = ""
    if liked_history:
        liked    = [h for h in liked_history if h.get("liked") is True]
        disliked = [h for h in liked_history if h.get("liked") is False]
        low_conc = [h for h in liked_history if (h.get("note_concentration") or 5) <= 2]
        if liked:
            hist_ctx += f" L'utilisateur a apprécié {len(liked)} média(s) similaire(s)."
        if disliked:
            hist_ctx += f" {len(disliked)} média(s) n'a pas correspondu."
        if low_conc:
            hist_ctx += " La concentration était faible lors des dernières évaluations."

    # ── Types d'instructions selon le média ───────────────────────
    type_hints = {
        "image": (
            "Donne 1 instruction de regard précise adaptée au style visuel décrit "
            "(ex: pour palette chaude → fixer les zones orangées ; pour motif géométrique → suivre les axes de symétrie ; "
            "pour scène naturelle → laisser le regard dériver sur les contours) "
            "et 1 effet neurologique attendu lié aux caractéristiques visuelles."
        ),
        "audio": (
            "Donne 1 instruction d'écoute active adaptée aux caractéristiques sonores décrites "
            "(ex: pour tempo lent → respiration 4s-4s synchronisée ; pour spectre harmonique → se concentrer sur la ligne mélodique principale ; "
            "pour basses dominantes → ressentir les vibrations dans la cage thoracique) "
            "et 1 effet neurologique attendu (synchronisation alpha, cohérence gamma…)."
        ),
        "video": (
            "Donne 1 instruction de regard adaptée au mouvement décrit "
            "(ex: pour image quasi-statique → ancrer le regard au centre sans effort ; "
            "pour mouvement régulier → laisser les yeux suivre passivement le flux) "
            "et 1 effet neurologique attendu sur les ondes thêta-alpha."
        ),
        "game": (
            "Donne 1 conseil de stratégie mentale adapté au type de jeu et à la charge cognitive décrite "
            "(ex: pour jeu logique → décomposer le problème en sous-étapes ; "
            "pour mémoire → visualiser mentalement les éléments avant de répondre) "
            "et 1 effet neurologique attendu (activation préfrontale, renforcement gamma…)."
        ),
    }
    hint = type_hints.get(mtype, type_hints["image"])

    prompt = f"""Tu es expert en neurofeedback EEG clinique. Génère un GUIDE D'INTERACTION pour ce média thérapeutique.

MÉDIA : {mtype.upper()} — « {fname} »
Catégorie : {category} | Cible EEG : {target}
Caractéristiques : {desc_str}
{eeg_ctx}
{hist_ctx}

CONSIGNE : {hint}

RÈGLES STRICTES :
- Exactement 2 phrases courtes (30 mots max chacune).
- Phrase 1 : instruction pratique et concrète pour l'utilisateur (verbe d'action).
- Phrase 2 : effet neurologique attendu (alpha/bêta/theta) en termes simples.
- Ton : direct, bienveillant, scientifiquement précis.
- Langue : français uniquement.
- Ne commence PAS par "Ce média" ou "Cette image".
- N'explique pas, ne justifie pas, donne juste le guide."""

    return await _call_llm(prompt, max_tokens=120)
