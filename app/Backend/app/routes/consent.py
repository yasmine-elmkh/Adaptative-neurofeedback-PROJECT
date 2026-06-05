"""
NeuroCap — Routes Consentement Éclairé
Préfixe : /api/consent

POST /api/consent/accept  → Enregistre le consentement + envoie le PDF par email
GET  /api/consent/pdf     → Télécharge le PDF de consentement personnalisé
"""
import io
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.consent_service import generate_consent_pdf
from app.services.email_service import send_consent_email, EmailSendError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/consent", tags=["Consentement"])


class ConsentRequest(BaseModel):
    accepted: bool


def _build_patient_name(user: dict) -> str:
    first = (user.get("first_name") or "").strip()
    last  = (user.get("last_name")  or "").strip()
    name  = f"{first} {last}".strip()
    return name or user.get("email", "Participant")


@router.post("/accept")
async def accept_consent(
    data: ConsentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Enregistre l'acceptation du consentement, génère le PDF et l'envoie par email.
    Met à jour consent_accepted + consent_date dans la table users.
    """
    if not data.accepted:
        raise HTTPException(status_code=400, detail="Le consentement doit être accepté.")

    patient_name  = _build_patient_name(current_user)
    patient_email = current_user["email"]
    user_id       = current_user["id"]

    # Générer le PDF
    pdf_bytes = generate_consent_pdf(patient_name)

    # Persister dans Supabase
    now = datetime.now(timezone.utc).isoformat()
    await db.table("users").update({
        "consent_accepted": True,
        "consent_date": now,
    }).eq("id", user_id).execute()

    # Envoyer l'email — non bloquant sur erreur (ne pas pénaliser l'UX)
    try:
        await send_consent_email(patient_email, patient_name, pdf_bytes)
    except (EmailSendError, Exception) as exc:
        logger.warning("Email consentement non envoyé pour %s : %s", patient_email, exc, exc_info=True)

    return {"status": "ok", "message": "Consentement enregistré et email envoyé."}


@router.get("/pdf")
async def download_consent_pdf(
    current_user: dict = Depends(get_current_user),
):
    """Télécharge le PDF de consentement personnalisé pour le patient connecté."""
    patient_name = _build_patient_name(current_user)
    pdf_bytes    = generate_consent_pdf(patient_name)
    filename     = f"NeuroCap_Consentement_{patient_name.replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
