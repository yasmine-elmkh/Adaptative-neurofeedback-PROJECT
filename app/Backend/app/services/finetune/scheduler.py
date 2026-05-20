"""
NeuroCap — Scheduler APScheduler (vérification nocturne du fine-tuning)
=======================================================================
S'exécute chaque nuit à 02:00 UTC.
Pour chaque patient avec un profil EEG :
  1. Vérifie l'activité récente
  2. Vérifie les conditions de déclenchement
  3. Lance le fine-tuning si nécessaire (asyncio.create_task via runner)
"""
import logging

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    _APSCHEDULER_AVAILABLE = True
except ImportError:
    _APSCHEDULER_AVAILABLE = False
    AsyncIOScheduler = None

from app.core.database import get_db
from .conditions import check_finetune_trigger
from .runner import trigger_finetune

logger = logging.getLogger("NeuroCap.FTScheduler")
_scheduler = AsyncIOScheduler(timezone="UTC") if _APSCHEDULER_AVAILABLE else None


async def _nightly_check():
    logger.info("[FTScheduler] Vérification nocturne des conditions fine-tuning")
    try:
        db = await get_db()

        # Tous les profils EEG patients
        resp = await db.table("eeg_profiles").select(
            "user_id, finetuned_version, finetuned_model_checkpoint, "
            "last_finetune_at, calibrated_at, last_20_sessions_accuracy"
        ).execute()
        profiles = resp.data or []
        logger.info(f"[FTScheduler] {len(profiles)} profil(s) à vérifier")

        triggered = 0
        for prof in profiles:
            pid = prof.get("user_id")
            if not pid:
                continue
            try:
                should, reason, ttype = await check_finetune_trigger(pid, prof, db)
                if should:
                    # Vérifier qu'aucun job n'est déjà en cours
                    running = await db.table("finetuning_jobs") \
                        .select("id", count="exact") \
                        .eq("patient_id", pid) \
                        .in_("status", ["pending", "running"]).execute()
                    if (running.count or 0) > 0:
                        logger.info(f"[FTScheduler] {pid[:8]} : job déjà en cours, skip")
                        continue
                    logger.info(f"[FTScheduler] Déclenchement {ttype} — {pid[:8]}: {reason}")
                    await trigger_finetune(pid, ttype, db)
                    triggered += 1
            except Exception as e:
                logger.warning(f"[FTScheduler] Erreur patient {pid[:8]}: {e}")

        logger.info(f"[FTScheduler] {triggered} fine-tuning(s) déclenché(s)")
    except Exception as e:
        logger.error(f"[FTScheduler] Erreur vérification nocturne: {e}", exc_info=True)


def start_scheduler():
    """Ajoute le job nocturne et démarre le scheduler."""
    if not _APSCHEDULER_AVAILABLE or _scheduler is None:
        logger.warning("[FTScheduler] APScheduler non installé — fine-tuning automatique désactivé. "
                       "Installez-le avec : pip install APScheduler")
        return
    _scheduler.add_job(
        _nightly_check,
        trigger="cron",
        hour=2,
        minute=0,
        id="finetune_nightly",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    logger.info("[FTScheduler] Démarré — vérification quotidienne à 02:00 UTC")


def stop_scheduler():
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[FTScheduler] Arrêté")
