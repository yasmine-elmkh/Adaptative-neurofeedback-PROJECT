"""
Prompts et formateurs de contexte pour NeuroCoach.
"""

from typing import Dict

# ── Prompt système ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es NeuroCoach, l'assistant personnel bienveillant de NeuroCap.
Tu accompagnes les patients dans leur programme de neurofeedback EEG de 15 séances.

Règles :
- Réponds TOUJOURS en français, ton chaleureux et professionnel
- Explique les termes techniques simplement (jamais de jargon sans explication)
- Personnalise avec les données réelles du patient quand disponibles
- Ne formule JAMAIS de diagnostic médical
- Cite les sources : "D'après votre profil…", "Selon la base de connaissances…"
- Sois concis (3–5 phrases) sauf si une explication détaillée est demandée
- Encourage toujours, même face à de mauvais résultats"""


def fmt_patient(ctx: Dict) -> str:
    """
    Formate le contexte patient (données Supabase) pour injection dans le prompt.
    Seules les valeurs non-None sont incluses.
    """
    if not ctx:
        return ""

    lines = ["# DONNÉES DU PATIENT (source: Supabase)"]

    def add(label: str, val, suffix: str = "") -> None:
        if val is not None:
            lines.append(f"- {label} : {val}{suffix}")

    add("Séances complétées",   ctx.get("total_sessions"),         "/15")
    add("Phase actuelle",       ctx.get("current_phase"))
    add("Palier",               ctx.get("palier"))
    add("Profil EEG",           ctx.get("profile"))

    if ctx.get("iapf"):
        lines.append(f"- IAPF : {ctx['iapf']:.1f} Hz")
    if ctx.get("avg_score"):
        lines.append(f"- Score moyen : {ctx['avg_score']:.1f} %")
    if ctx.get("score_trend") is not None:
        arrow = "↑" if ctx["score_trend"] > 0 else "↓"
        lines.append(f"- Tendance : {arrow} {abs(ctx['score_trend']):.1f} %")
    if ctx.get("baseline_tbr"):
        lines.append(f"- TBR baseline S1 : {ctx['baseline_tbr']:.3f}")
    if ctx.get("last_avg_tbr"):
        lines.append(f"- TBR dernière séance : {ctx['last_avg_tbr']:.3f}")
    if ctx.get("avg_concentration_pct"):
        lines.append(f"- Concentration moy. : {ctx['avg_concentration_pct']:.1f} %")
    if ctx.get("avg_stress_pct"):
        lines.append(f"- Stress moyen : {ctx['avg_stress_pct']:.1f} %")
    if ctx.get("last_dominant_state"):
        labels = {"concentration": "concentration", "stress": "stress", "neutral": "neutre"}
        state  = labels.get(ctx["last_dominant_state"], ctx["last_dominant_state"])
        lines.append(f"- État dominant (dernière analyse) : {state}")
    if ctx.get("last_concentration_pct"):
        lines.append(f"- Concentration dernière analyse : {ctx['last_concentration_pct']:.1f} %")
    if ctx.get("last_stress_pct"):
        lines.append(f"- Stress dernière analyse : {ctx['last_stress_pct']:.1f} %")
    if ctx.get("n_epochs_accepted") and ctx.get("n_epochs_total"):
        pct = 100 * ctx["n_epochs_accepted"] / max(ctx["n_epochs_total"], 1)
        lines.append(f"- Taux acceptation époques : {pct:.0f} %")
    if ctx.get("predicted_next_score"):
        lines.append(f"- Score prédit prochaine séance : {ctx['predicted_next_score']:.1f} %")

    return "\n".join(lines)
