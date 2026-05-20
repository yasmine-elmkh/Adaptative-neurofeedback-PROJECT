"""
NeuroCap — Runner de fine-tuning LightGBM
==========================================
Entraîne le modèle personnel du patient sur ses époques haute confiance.
Pseudo-labels : prédiction LightGBM avec confiance ≥ 0.85.

Flow :
  1. Récupère les époques non utilisées (is_high_confidence=True, used_in_finetuning=False)
  2. Charge le modèle courant (personnel v(n-1) ou base LOSO)
  3. Fine-tuning LightGBM avec learning_rate réduit (évite l'oubli catastrophique)
  4. Sauvegarde checkpoint dans models/personal/
  5. Met à jour eeg_profiles + marque les époques utilisées
  6. Complète le job dans finetuning_jobs
"""
import uuid
import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("NeuroCap.FineTune")

# Chemins (6 niveaux au-dessus de runner.py : finetune → services → app → Backend → app → EEG_project)
_PROJECT_ROOT   = Path(__file__).resolve().parents[5]
_BASE_MODEL_DIR = _PROJECT_ROOT / "models" / "baseline_FeatEng" / "baseline_models"
_PERSONAL_DIR   = _PROJECT_ROOT / "models" / "personal"
_PERSONAL_DIR.mkdir(parents=True, exist_ok=True)

MAX_EPOCHS_FETCH = 5000
MIN_EPOCHS_NEEDED = 100


async def trigger_finetune(patient_id: str, trigger_type: str, db):
    """Crée le job et lance le fine-tuning en arrière-plan (asyncio.create_task)."""
    profile_r = await db.table("eeg_profiles") \
        .select("finetuned_version") \
        .eq("user_id", patient_id).limit(1).execute()
    current_v = (profile_r.data[0].get("finetuned_version") or 0) if profile_r.data else 0
    new_v = current_v + 1

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
    import joblib
    import lightgbm as lgb

    # ── 1. Données d'entraînement ─────────────────────────────────────────────
    resp = await db.table("training_epochs") \
        .select("id, features, predicted_label") \
        .eq("patient_id", patient_id) \
        .eq("is_high_confidence", True) \
        .eq("used_in_finetuning", False) \
        .order("created_at") \
        .limit(MAX_EPOCHS_FETCH).execute()

    rows = [r for r in (resp.data or []) if r.get("features")]
    if len(rows) < MIN_EPOCHS_NEEDED:
        raise ValueError(
            f"Données insuffisantes : {len(rows)} époques avec features "
            f"(minimum {MIN_EPOCHS_NEEDED})"
        )

    # ── 2. Ordre canonique des features ──────────────────────────────────────
    import sys
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    from src.data.feature_eng import get_feature_names
    feat_names = get_feature_names()

    X = np.array(
        [[r["features"].get(f, 0.0) for f in feat_names] for r in rows],
        dtype=np.float64,
    )
    y = np.array([int(r["predicted_label"]) for r in rows])

    # ── 3. Charger modèle courant ─────────────────────────────────────────────
    profile_r = await db.table("eeg_profiles") \
        .select("finetuned_model_checkpoint, finetuned_version") \
        .eq("user_id", patient_id).limit(1).execute()
    profile = profile_r.data[0] if profile_r.data else {}

    ckpt     = profile.get("finetuned_model_checkpoint")
    scaler   = None
    base_clf = None

    if ckpt and Path(ckpt).exists():
        base_clf = joblib.load(ckpt)
        scaler_p = Path(ckpt).parent / (Path(ckpt).stem + "_scaler.joblib")
        if scaler_p.exists():
            scaler = joblib.load(scaler_p)
        logger.info(f"[FineTune] Modèle personnel chargé: {Path(ckpt).name}")
    else:
        model_p  = _BASE_MODEL_DIR / "LightGBM_concentration_vs_stress.joblib"
        scaler_p = _BASE_MODEL_DIR / "LightGBM_scaler.joblib"
        if not model_p.exists():
            raise FileNotFoundError(f"Modèle de base introuvable: {model_p}")
        base_clf = joblib.load(model_p)
        if scaler_p.exists():
            scaler = joblib.load(scaler_p)
        logger.info("[FineTune] Modèle de base utilisé comme point de départ")

    X_scaled = scaler.transform(X) if scaler is not None else X

    # ── 4. Accuracy avant fine-tuning ─────────────────────────────────────────
    acc_before = None
    try:
        y_pred_base = base_clf.predict(X_scaled)
        acc_before  = float(np.mean(y_pred_base == y))
    except Exception:
        pass

    # ── 5. Fine-tuning LightGBM (sklearn API, init_model) ────────────────────
    new_version = (profile.get("finetuned_version") or 0) + 1
    try:
        new_clf = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.01,
            num_leaves=31,
            min_child_samples=20,
            verbosity=-1,
        )
        new_clf.fit(X_scaled, y, init_model=base_clf)
    except Exception as e:
        logger.warning(f"[FineTune] init_model failed ({e}), training from scratch")
        new_clf = lgb.LGBMClassifier(
            n_estimators=200,
            learning_rate=0.03,
            num_leaves=31,
            min_child_samples=20,
            verbosity=-1,
        )
        new_clf.fit(X_scaled, y)

    # ── 6. Accuracy après fine-tuning ─────────────────────────────────────────
    y_pred_new = new_clf.predict(X_scaled)
    acc_after  = float(np.mean(y_pred_new == y))

    # ── 7. Sauvegarder checkpoint ─────────────────────────────────────────────
    stem       = f"patient_{patient_id[:8]}_v{new_version}"
    out_model  = _PERSONAL_DIR / f"{stem}.joblib"
    out_scaler = _PERSONAL_DIR / f"{stem}_scaler.joblib"
    joblib.dump(new_clf, out_model)
    if scaler is not None:
        joblib.dump(scaler, out_scaler)

    # ── 8. Mettre à jour eeg_profiles ─────────────────────────────────────────
    await db.table("eeg_profiles").update({
        "finetuned_model_checkpoint": str(out_model),
        "finetuned_version":          new_version,
        "last_finetune_at":           datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", patient_id).execute()

    # ── 9. Marquer les époques comme utilisées ────────────────────────────────
    epoch_ids = [r["id"] for r in rows]
    # Batch en tranches de 100 (limite Supabase IN clause)
    for i in range(0, len(epoch_ids), 100):
        batch = epoch_ids[i:i + 100]
        await db.table("training_epochs") \
            .update({"used_in_finetuning": True}) \
            .in_("id", batch).execute()

    # ── 10. Compléter le job ──────────────────────────────────────────────────
    await db.table("finetuning_jobs").update({
        "status":                "completed",
        "n_epochs_used":         len(rows),
        "accuracy_before":       acc_before,
        "accuracy_after":        acc_after,
        "model_checkpoint_path": str(out_model),
        "completed_at":          datetime.now(timezone.utc).isoformat(),
    }).eq("id", job_id).execute()

    gain = f"{(acc_after - acc_before) * 100:+.1f}%" if acc_before is not None else "N/A"
    logger.info(
        f"[FineTune] Patient {patient_id[:8]} v{new_version} OK — "
        f"{len(rows)} époques — acc: {acc_before:.1%}→{acc_after:.1%} ({gain})"
        if acc_before else
        f"[FineTune] Patient {patient_id[:8]} v{new_version} OK — "
        f"{len(rows)} époques — acc: {acc_after:.1%}"
    )
