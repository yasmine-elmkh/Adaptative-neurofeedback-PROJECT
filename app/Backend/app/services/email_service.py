"""
Service d'envoi d'emails — NeuroCap
=====================================
Utilise Brevo (ex-Sendinblue) via SMTP — gratuit, 300 emails/jour, aucun domaine requis.

Configuration dans .env :
  SMTP_USER=votre_email@brevo.com    ← login affiché dans Brevo SMTP settings
  SMTP_PASSWORD=xsmtpsib-xxxx        ← "Master password" dans Brevo SMTP settings
  (SMTP_HOST, SMTP_PORT, SMTP_FROM ont des valeurs par défaut correctes)

Comment obtenir les identifiants Brevo (3 minutes) :
  1. Créer un compte sur https://brevo.com
  2. Menu gauche → SMTP & API → onglet "SMTP"
  3. Copier : Login (votre email Brevo) + Master password
  4. Coller dans .env : SMTP_USER=... SMTP_PASSWORD=...

Mode dev : si SMTP_USER est vide → le code s'affiche dans la réponse API (bandeau jaune).
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailSendError(Exception):
    """Levée quand l'envoi d'email échoue."""
    pass


def _html_body(code: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0e1a;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #1e2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#00b4d8,#0077b6);padding:32px 40px;text-align:center;">
            <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px;">NeuroCap</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:4px;">Easy Medical Device</div>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <h2 style="margin:0 0 8px;color:#f0f4ff;font-size:20px;">Vérification de votre email</h2>
            <p style="margin:0 0 32px;color:#8899aa;font-size:14px;line-height:1.6;">
              Utilisez ce code à 8 chiffres pour finaliser la création de votre compte NeuroCap.
            </p>
            <div style="background:#0a0e1a;border:2px solid #00b4d8;border-radius:12px;
                        padding:28px;text-align:center;margin-bottom:32px;">
              <div style="font-family:monospace;font-size:40px;font-weight:800;
                          letter-spacing:14px;color:#00d4ff;">{code}</div>
            </div>
            <p style="margin:0 0 8px;color:#8899aa;font-size:13px;">
              ⏱️ Ce code expire dans <strong style="color:#f0f4ff;">10 minutes</strong>.
            </p>
            <p style="margin:0;color:#8899aa;font-size:13px;">
              Si vous n'avez pas demandé ce code, ignorez cet email.
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #1e2a3a;text-align:center;">
            <div style="color:#4a5568;font-size:11px;">
              © 2026 NeuroCap — Easy Medical Device · Tous droits réservés
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send_smtp_blocking(to_email: str, code: str) -> None:
    """Envoi SMTP synchrone — à appeler via run_in_executor."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "NeuroCap — Code de vérification"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    msg.attach(MIMEText(f"Votre code NeuroCap : {code}\nValable 10 minutes.", "plain", "utf-8"))
    msg.attach(MIMEText(_html_body(code), "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError(
            "Identifiants SMTP Brevo invalides. Vérifiez SMTP_USER et SMTP_PASSWORD dans .env."
        )
    except smtplib.SMTPException as exc:
        raise EmailSendError(f"Échec SMTP : {exc}")
    except OSError as exc:
        raise EmailSendError(f"Impossible de joindre le serveur SMTP ({settings.SMTP_HOST}:{settings.SMTP_PORT}) : {exc}")


def _html_reminder(first_name: str, days_inactive: int, admin_message: str) -> str:
    greeting = f"Bonjour {first_name}" if first_name else "Bonjour"
    inactivity = (
        f"Cela fait <strong style='color:#f0f4ff;'>{days_inactive} jours</strong> que vous n'avez pas effectué de session NeuroCap."
        if days_inactive > 0
        else "Vous n'avez encore effectué aucune session NeuroCap."
    )
    custom_block = ""
    if admin_message:
        custom_block = f"""
        <div style="background:#1e2a3a;border-left:3px solid #00b4d8;border-radius:8px;
                    padding:16px 20px;margin-bottom:24px;">
          <p style="margin:0;color:#c8d8e8;font-size:14px;line-height:1.6;font-style:italic;">
            "{admin_message}"
          </p>
          <p style="margin:8px 0 0;color:#4a6080;font-size:12px;">— L'équipe NeuroCap</p>
        </div>"""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0e1a;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #1e2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#00b4d8,#0077b6);padding:32px 40px;text-align:center;">
            <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px;">NeuroCap</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:4px;">Easy Medical Device</div>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <h2 style="margin:0 0 8px;color:#f0f4ff;font-size:20px;">
              Vos séances NeuroCap vous manquent !
            </h2>
            <p style="margin:0 0 24px;color:#8899aa;font-size:14px;line-height:1.6;">
              {greeting}, {inactivity}
              Reprendre vos entraînements cognitifs régulièrement améliore significativement les résultats.
            </p>
            {custom_block}
            <div style="text-align:center;margin-bottom:32px;">
              <a href="http://localhost:5173/eeg"
                 style="display:inline-block;background:linear-gradient(135deg,#00b4d8,#0077b6);
                        color:#fff;font-weight:700;font-size:15px;padding:14px 36px;
                        border-radius:12px;text-decoration:none;letter-spacing:0.3px;">
                Reprendre ma session →
              </a>
            </div>
            <p style="margin:0;color:#8899aa;font-size:12px;text-align:center;">
              Si vous ne souhaitez plus recevoir ces rappels, contactez votre thérapeute.
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #1e2a3a;text-align:center;">
            <div style="color:#4a5568;font-size:11px;">
              © 2026 NeuroCap — Easy Medical Device · Tous droits réservés
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send_reminder_blocking(to_email: str, first_name: str, days_inactive: int, admin_message: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "NeuroCap — Reprenez vos sessions de neurofeedback"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    plain = (
        f"Bonjour {first_name},\n\n"
        f"Cela fait {days_inactive} jours sans session NeuroCap. Revenez nous voir !\n\n"
        + (f"Message de votre équipe : {admin_message}\n\n" if admin_message else "")
        + "Connectez-vous sur http://localhost:5173\n\nL'équipe NeuroCap"
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(_html_reminder(first_name, days_inactive, admin_message), "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError("Identifiants SMTP Brevo invalides.")
    except smtplib.SMTPException as exc:
        raise EmailSendError(f"Échec SMTP : {exc}")
    except OSError as exc:
        raise EmailSendError(f"Serveur SMTP inaccessible : {exc}")


async def send_reminder_email(to_email: str, first_name: str, days_inactive: int, admin_message: str = "") -> None:
    """
    Envoie un email de rappel à un utilisateur inactif.
    - Si SMTP_USER vide → log seulement (mode dev).
    - Lève EmailSendError si l'envoi échoue.
    """
    if not settings.SMTP_USER:
        logger.warning("⚠️  SMTP_USER non configuré — RAPPEL pour %s (dev mode)", to_email)
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_reminder_blocking, to_email, first_name, days_inactive, admin_message)
    logger.info("✅ Email de rappel envoyé à %s via Brevo", to_email)


async def send_verification_email(to_email: str, code: str) -> None:
    """
    Envoie le code de vérification via Brevo SMTP.
    - Si SMTP_USER est configuré → vrai email envoyé.
    - Si SMTP_USER est vide → mode dev, code loggué (rien n'est envoyé).
    Lève EmailSendError si l'envoi échoue.
    """
    if not settings.SMTP_USER:
        logger.warning(
            "⚠️  SMTP_USER non configuré — CODE VÉRIFICATION pour %s : %s",
            to_email, code
        )
        return

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_smtp_blocking, to_email, code)
    logger.info("✅ Email de vérification envoyé à %s via Brevo", to_email)
