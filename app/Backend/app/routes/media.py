"""
NeuroCap — Routes Media
GET /api/media/list          → liste des assets feedback depuis table medias
GET /api/media/illusions     → illusions optiques (images Supabase)
GET /api/media/features      → features extraites (Feedback_METADATA CSVs) par filename
"""

import csv
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import AsyncClient

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/media", tags=["Media"])

_optional_bearer = HTTPBearer(auto_error=False)

# ── Load Feedback_METADATA CSVs into memory once at import time ───────────────
_FEATURES: dict[str, dict] = {}

def _load_features_csv():
    project_root = Path(__file__).parents[4]
    meta_dir = project_root / "Feedback_METADATA"
    csvs = [
        "audio_features.csv",
        "image_features.csv",
        "video_features_v2.csv",
        "games_features_clean.csv",
    ]
    for name in csvs:
        path = meta_dir / name
        if not path.exists():
            logger.warning("Feedback_METADATA CSV introuvable : %s", path)
            continue
        try:
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    fname = row.get("filename", "").strip()
                    if fname:
                        _FEATURES[fname] = dict(row)
            logger.info("Chargé %s (%d entrées)", name, sum(1 for k in _FEATURES))
        except Exception as e:
            logger.error("Erreur lecture %s : %s", name, e)

_load_features_csv()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _numeric(val: str) -> float | str:
    try:
        return float(val)
    except (TypeError, ValueError):
        return val


def _slim_features(row: dict) -> dict:
    """Return only the most interpretable features for the frontend guide."""
    keys_audio = [
        "filename", "condition", "type", "duration_s", "tempo_bpm", "tempo_stability",
        "spec_centroid_mean", "energy_sub_bass", "energy_bass", "energy_mid",
        "energy_high_mid", "energy_high", "zcr_mean", "rms_mean",
        "onset_strength_mean", "harm_perc_ratio", "spectral_stationarity",
    ]
    keys_image = [
        "filename", "condition", "type", "hue_mean", "saturation_mean",
        "brightness_mean", "contrast", "warm_cold_ratio", "entropy",
        "symmetry", "spatial_freq_hf_ratio", "edge_density",
    ]
    keys_video = [
        "filename", "condition", "type", "duration_s", "optical_flow_mean",
        "optical_flow_std", "motion_regularity", "scene_change_rate",
        "flicker_rate", "color_temp_k", "color_temp_category",
        "edge_density_mean", "brightness_mean", "saturation_mean",
        "lum_skewness", "lum_range",
    ]
    keys_game = ["filename", "type", "categorie", "game_folder", "features_json"]

    media_type = row.get("type", "")
    if media_type == "audio":
        keys = keys_audio
    elif media_type == "image":
        keys = keys_image
    elif media_type == "video":
        keys = keys_video
    elif media_type == "game":
        keys = keys_game
    else:
        keys = list(row.keys())

    return {k: _numeric(row[k]) for k in keys if k in row}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/list")
async def get_media_list(
    media_type: Optional[str] = Query(None, description="audio | image | game | video"),
    eeg_state:  Optional[str] = Query(None, description="stress | focus | neutral | illusion"),
    _creds: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    db: AsyncClient = Depends(get_db),
):
    """
    Retourne la liste des assets feedback.
    Filtre optionnel par type et/ou état EEG cible.
    Accepte eeg_state=illusion pour les illusions optiques.
    """
    query = db.table("medias").select("*")

    if media_type and media_type in ("audio", "image", "game", "video"):
        query = query.eq("type", media_type)

    if eeg_state:
        if eeg_state == "illusion":
            query = query.eq("eeg_target_state", "illusion")
        elif eeg_state in ("stress", "focus", "neutral"):
            query = query.in_("eeg_target_state", [eeg_state, "all"])

    resp = await query.order("created_at", desc=True).execute()
    return resp.data or []


@router.get("/illusions")
async def get_illusions(
    _creds: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    db: AsyncClient = Depends(get_db),
):
    """Retourne toutes les illusions optiques (images Supabase)."""
    resp = await (
        db.table("medias")
        .select("id,filename,url,eeg_target_state,category")
        .eq("type", "image")
        .eq("eeg_target_state", "illusion")
        .execute()
    )
    return resp.data or []


@router.get("/features")
async def get_media_features(
    filename: str = Query(..., description="Nom de fichier exact (ex: REL_001.wav)"),
    slim: bool = Query(True, description="Retourner seulement les features interprétables"),
):
    """
    Retourne les features extraites depuis Feedback_METADATA pour un fichier donné.
    Combine nom de fichier + features CSV (audio, image, vidéo, jeux).
    """
    row = _FEATURES.get(filename)
    if not row:
        # Try without extension
        stem = Path(filename).stem
        row = next((v for k, v in _FEATURES.items() if Path(k).stem == stem), None)

    if not row:
        raise HTTPException(status_code=404, detail=f"Features introuvables pour '{filename}'")

    return _slim_features(row) if slim else {k: _numeric(v) for k, v in row.items()}
