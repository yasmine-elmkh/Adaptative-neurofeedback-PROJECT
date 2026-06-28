"""
NeuroCap — Runner de fine-tuning DualClassifier
=================================================
Fine-tune les 2 modèles personnels du patient (même architecture qu'en inférence) :

  1. EEGNet concentration  — DL FULL  (AUC=0.751, S=0.789, #1 CdC §4.5)
     Base : models/Regression/DL/EEGNet/conc/EEGNet_conc_FULL_best.pt
     Input : (B, 1, 1, 1000) — Conv2d monocanal Fp2 @ 250 Hz

  2. EEGNet stress         — TL LayerReplacement FULL  (AUC=0.607, S=0.525)
     Base : models/Regression/TL/EEGNet_LayerReplacement/stress/EEGNet_LR_stress_FULL_best.pt
     Input : (B, 1, 1, 1000) — Conv2d monocanal Fp2 @ 250 Hz

Stratégie commune : geler tout le backbone EEGNet, entraîner uniquement model.fc
  - Optimizer : Adam, lr=1e-4, weight_decay=1e-5
  - Loss      : MSELoss (régression 0–10)
  - Epochs    : 30 passes sur les données patient

Données requises dans training_epochs :
  - epoch_filtered  : list[float], 1000 samples filtrés
  - conc_score      : float 0–10  — label régression concentration
  - stress_score    : float 0–10  — label régression stress

Flow :
  1. Récupère les époques (is_high_confidence=True, used_in_finetuning=False)
  2. Fine-tune EEGNet/conc  FC si ≥ MIN_EPOCHS disponibles
  3. Fine-tune EEGNet/stress FC si ≥ MIN_EPOCHS disponibles
  4. Sauvegarde checkpoints dans models/personal/
  5. Met à jour eeg_profiles (conc_checkpoint + stress_checkpoint + version)
  6. Marque les époques utilisées + complète le job
"""
import uuid
import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("NeuroCap.FineTune")

# ── Chemins modèles de base (identiques à dual_classifier.py) ──────────────────
_PROJECT_ROOT    = Path(__file__).resolve().parents[5]
_BASE_CONC_PT    = (_PROJECT_ROOT / "models" / "Regression"
                    / "DL" / "EEGNet" / "conc" / "EEGNet_conc_FULL_best.pt")
_BASE_STRESS_PT  = (_PROJECT_ROOT / "models" / "Regression"
                    / "TL" / "EEGNet_LayerReplacement" / "stress"
                    / "EEGNet_LR_stress_FULL_best.pt")
_PERSONAL_DIR    = _PROJECT_ROOT / "models" / "personal"
_PERSONAL_DIR.mkdir(parents=True, exist_ok=True)

MAX_EPOCHS_FETCH = 5000
MIN_EPOCHS       = 50     # EEGNet a peu de paramètres → 50 époques suffisent
EPOCH_SAMP       = 1000
SCORE_THR        = 5.0


def _sigmoid_pct(x):
    """
    Même normalisation que dual_classifier._sigmoid_score() × 10.
    Mappe la sortie brute du modèle (R) vers (0, 100).
    Utilisée pendant le fine-tuning pour que la loss MSE soit cohérente
    avec les labels pct (0-100) stockés dans training_epochs.
    """
    import torch
    return 100.0 / (1.0 + torch.exp(-(x - SCORE_THR) / 2.0))


# ═══════════════════════════════════════════════════════════════════════════════
# API publique
# ═══════════════════════════════════════════════════════════════════════════════

async def trigger_finetune(patient_id: str, trigger_type: str, db):
    """Crée un job Supabase et lance le fine-tuning en arrière-plan."""
    profile_r = await db.table("eeg_profiles") \
        .select("finetuned_version") \
        .eq("user_id", patient_id).limit(1).execute()
    current_v = (profile_r.data[0].get("finetuned_version") or 0) if profile_r.data else 0
    new_v     = current_v + 1

    job_id = str(uuid.uuid4())
    await db.table("finetuning_jobs").insert({
        "id":           job_id,
        "patient_id":   patient_id,
        "trigger_type": trigger_type,
        "version":      new_v,
        "status":       "pending",
        "started_at":   datetime.now(timezone.utc).isoformat(),
    }).execute()

    asyncio.create_task(_run_job(job_id, patient_id, db))
    logger.info(f"[FineTune] Job {job_id[:8]} créé — patient {patient_id[:8]}, type={trigger_type}")


# ═══════════════════════════════════════════════════════════════════════════════
# Orchestration interne
# ═══════════════════════════════════════════════════════════════════════════════

async def _run_job(job_id: str, patient_id: str, db):
    await db.table("finetuning_jobs") \
        .update({"status": "running"}) \
        .eq("id", job_id).execute()
    try:
        await _do_finetune(job_id, patient_id, db)
    except Exception as e:
        logger.error(f"[FineTune] Job {job_id[:8]} FAILED: {e}", exc_info=True)
        await db.table("finetuning_jobs").update({
            "status":        "failed",
            "error_message": str(e)[:500],
            "completed_at":  datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()


async def _do_finetune(job_id: str, patient_id: str, db):
    # ── 1. Charger les données ────────────────────────────────────────────────
    resp = await db.table("training_epochs") \
        .select("id, features, epoch_filtered, conc_score, stress_score") \
        .eq("patient_id", patient_id) \
        .eq("is_high_confidence", True) \
        .eq("used_in_finetuning", False) \
        .order("created_at") \
        .limit(MAX_EPOCHS_FETCH).execute()

    rows = resp.data or []
    if not rows:
        raise ValueError("Aucune époque disponible pour le fine-tuning")

    # ── 2. Profil patient (checkpoints personnels précédents) ─────────────────
    profile_r = await db.table("eeg_profiles") \
        .select("finetuned_version, conc_checkpoint, stress_checkpoint") \
        .eq("user_id", patient_id).limit(1).execute()
    profile     = profile_r.data[0] if profile_r.data else {}
    new_version = (profile.get("finetuned_version") or 0) + 1

    # ── 3. Fine-tuning EEGNet/conc ────────────────────────────────────────────
    conc_result = await _finetune_eegnet(
        patient_id, new_version, rows, profile,
        task="conc",
        score_key="conc_score",
        base_pt=_BASE_CONC_PT,
        prev_ckpt_key="conc_checkpoint",
        label="EEGNet/conc (DL FULL)",
    )

    # ── 4. Fine-tuning EEGNet/stress ──────────────────────────────────────────
    stress_result = await _finetune_eegnet(
        patient_id, new_version, rows, profile,
        task="stress",
        score_key="stress_score",
        base_pt=_BASE_STRESS_PT,
        prev_ckpt_key="stress_checkpoint",
        label="EEGNet_LR/stress (TL FULL)",
    )

    # ── 5. Mettre à jour eeg_profiles ─────────────────────────────────────────
    update_data = {
        "finetuned_version": new_version,
        "last_finetune_at":  datetime.now(timezone.utc).isoformat(),
    }
    if conc_result.get("checkpoint"):
        update_data["conc_checkpoint"] = conc_result["checkpoint"]
    if stress_result.get("checkpoint"):
        update_data["stress_checkpoint"] = stress_result["checkpoint"]

    await db.table("eeg_profiles").update(update_data) \
        .eq("user_id", patient_id).execute()

    # ── 6. Marquer les époques utilisées (batch 100 — limite Supabase IN) ─────
    epoch_ids = [r["id"] for r in rows]
    for i in range(0, len(epoch_ids), 100):
        await db.table("training_epochs") \
            .update({"used_in_finetuning": True}) \
            .in_("id", epoch_ids[i:i + 100]).execute()

    # ── 7. Compléter le job ────────────────────────────────────────────────────
    checkpoints = []
    if conc_result.get("checkpoint"):
        checkpoints.append(f"conc={Path(conc_result['checkpoint']).name}")
    if stress_result.get("checkpoint"):
        checkpoints.append(f"stress={Path(stress_result['checkpoint']).name}")

    await db.table("finetuning_jobs").update({
        "status":                "completed",
        "n_epochs_used":         len(rows),
        "accuracy_before":       conc_result.get("loss_before"),
        "accuracy_after":        conc_result.get("loss_after"),
        "model_checkpoint_path": " | ".join(checkpoints),
        "completed_at":          datetime.now(timezone.utc).isoformat(),
    }).eq("id", job_id).execute()

    logger.info(
        f"[FineTune] Patient {patient_id[:8]} v{new_version} terminé — "
        f"{len(rows)} époques | "
        f"EEGNet/conc={conc_result.get('status','?')} | "
        f"EEGNet_LR/stress={stress_result.get('status','?')}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Fine-tuning EEGNet — couche FC uniquement (même logique pour conc et stress)
# ═══════════════════════════════════════════════════════════════════════════════

async def _finetune_eegnet(
    patient_id: str,
    version: int,
    rows: list,
    profile: dict,
    *,
    task: str,
    score_key: str,
    base_pt: Path,
    prev_ckpt_key: str,
    label: str,
) -> dict:
    """
    Fine-tune la couche FC de EEGNet sur les scores du patient.

    Architecture EEGNet : Conv2d dépthwise séparable, Input (B, 1, 1, 1000).
    Stratégie           : geler tout le backbone, entraîner seulement model.fc.
    Modèles de base     :
      conc   → DL/EEGNet/conc/EEGNet_conc_FULL_best.pt    (AUC=0.751)
      stress → TL/EEGNet_LayerReplacement/stress/EEGNet_LR_stress_FULL_best.pt (AUC=0.607)
    """
    task_rows = [
        r for r in rows
        if r.get("epoch_filtered") and r.get(score_key) is not None
    ]
    if len(task_rows) < MIN_EPOCHS:
        logger.info(
            f"[FineTune] {label} skip : {len(task_rows)} époques "
            f"(minimum {MIN_EPOCHS})"
        )
        return {"status": f"skip ({len(task_rows)}/{MIN_EPOCHS})", "checkpoint": None}

    try:
        import torch
        import torch.nn as nn
        import sys

        if str(_PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(_PROJECT_ROOT))

        from app.services.eeg.dsp.dual_classifier import _build_eegnet
        model = _build_eegnet(n_out=1)
        if model is None:
            return {"status": "error: torch indisponible", "checkpoint": None}

        # Charger les poids : checkpoint personnel (v-1) ou modèle FULL de base
        prev_ckpt = profile.get(prev_ckpt_key)
        if prev_ckpt and Path(prev_ckpt).exists():
            sd = torch.load(prev_ckpt, map_location="cpu", weights_only=True)
            logger.info(f"[FineTune] {label} ← checkpoint personnel {Path(prev_ckpt).name}")
        elif base_pt.exists():
            sd = torch.load(base_pt, map_location="cpu", weights_only=True)
            logger.info(f"[FineTune] {label} ← modèle FULL de base ({base_pt.name})")
        else:
            return {"status": f"error: modèle introuvable ({base_pt.name})", "checkpoint": None}

        model.load_state_dict(sd)

        # Geler tout le backbone — entraîner seulement la tête FC
        for name, param in model.named_parameters():
            param.requires_grad = name.startswith("fc")

        # ── Préparer les données ───────────────────────────────────────────────
        X_np = np.array(
            [r["epoch_filtered"][:EPOCH_SAMP] for r in task_rows],
            dtype=np.float32,
        )
        y_np = np.array([float(r[score_key]) for r in task_rows], dtype=np.float32)

        # Z-score par époque (identique au prétraitement inférence)
        means = X_np.mean(axis=1, keepdims=True)
        stds  = X_np.std(axis=1, keepdims=True) + 1e-10
        X_np  = (X_np - means) / stds

        # (N, 1, 1, 1000) — EEGNet Conv2d (même shape qu'en inférence)
        X_t = torch.FloatTensor(X_np).reshape(-1, 1, 1, EPOCH_SAMP)
        y_t = torch.FloatTensor(y_np).unsqueeze(1)

        # MSE avant fine-tuning (sortie sigmoid 0-100 vs labels 0-100)
        model.eval()
        with torch.no_grad():
            mse_before = float(nn.MSELoss()(_sigmoid_pct(model(X_t)), y_t).item())

        # ── Entraînement FC uniquement ─────────────────────────────────────────
        # Labels y_t : pct 0-100 (stockés dans training_epochs.conc_score / stress_score)
        # Sortie modèle : valeur brute pré-sigmoid → applique _sigmoid_pct pour MSE cohérente
        optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=1e-4, weight_decay=1e-5,
        )
        loss_fn = nn.MSELoss()
        dataset = torch.utils.data.TensorDataset(X_t, y_t)
        loader  = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

        model.train()
        for _ in range(30):
            for xb, yb in loader:
                optimizer.zero_grad()
                loss_fn(_sigmoid_pct(model(xb)), yb).backward()
                optimizer.step()

        model.eval()
        with torch.no_grad():
            mse_after = float(nn.MSELoss()(_sigmoid_pct(model(X_t)), y_t).item())

        # ── Sauvegarder le checkpoint personnel ───────────────────────────────
        out_pt = _PERSONAL_DIR / f"patient_{patient_id[:8]}_{task}_v{version}.pt"
        torch.save(model.state_dict(), out_pt)

        logger.info(
            f"[FineTune] {label} OK — {len(task_rows)} époques — "
            f"MSE: {mse_before:.3f} → {mse_after:.3f} — {out_pt.name}"
        )
        return {
            "status":      "ok",
            "checkpoint":  str(out_pt),
            "n_epochs":    len(task_rows),
            "loss_before": round(mse_before, 4),
            "loss_after":  round(mse_after,  4),
        }

    except Exception as e:
        logger.error(f"[FineTune] {label} erreur: {e}", exc_info=True)
        return {"status": f"error: {e}", "checkpoint": None}
