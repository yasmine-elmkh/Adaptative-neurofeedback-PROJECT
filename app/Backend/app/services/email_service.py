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


def _html_calibration(first_name: str, profile: dict) -> str:
    greeting = f"Bonjour {first_name}" if first_name else "Bonjour"
    palier   = profile.get("palier_initial", "P1")
    ptype    = profile.get("profile_type",   "B")
    iapf     = profile.get("iapf",           "—")
    erd      = profile.get("erd_pct",        "—")
    p_alpha  = profile.get("p_alpha_ref",    None)
    p_alpha_str = f"{p_alpha:.4f}" if isinstance(p_alpha, float) else "—"
    palier_desc = {
        "P1": "Initiation — feedback sonore uniquement",
        "P2": "Apprentissage — son + visuel",
        "P3": "Maîtrise — feedback complet + jeux",
        "P4": "Autonomie progressive",
    }.get(palier, palier)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0e1a;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #1e2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#6c63ff,#00b4d8);padding:32px 40px;text-align:center;">
            <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px;">NeuroCap</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.75);margin-top:4px;">Calibration EEG complétée ✓</div>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <h2 style="margin:0 0 8px;color:#f0f4ff;font-size:20px;">{greeting}, votre profil EEG est prêt !</h2>
            <p style="margin:0 0 28px;color:#8899aa;font-size:14px;line-height:1.6;">
              La calibration individuelle a été complétée avec succès. Voici votre profil neurophysiologique
              qui personnalisera l'ensemble de votre programme de neurofeedback.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#0a0e1a;border-radius:12px;border:1px solid #1e2a3a;margin-bottom:28px;">
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Profil cognitif</td>
                <td style="padding:12px 16px;color:#c8d8ff;font-weight:700;font-size:13px;text-align:right;">Type {ptype}</td>
              </tr>
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Fréquence alpha individuelle (IAPF)</td>
                <td style="padding:12px 16px;color:#c8d8ff;font-weight:700;font-size:13px;text-align:right;">{iapf} Hz</td>
              </tr>
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Puissance alpha de référence</td>
                <td style="padding:12px 16px;color:#c8d8ff;font-weight:700;font-size:13px;text-align:right;">{p_alpha_str}</td>
              </tr>
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">ERD alpha (blocage visuel)</td>
                <td style="padding:12px 16px;color:#c8d8ff;font-weight:700;font-size:13px;text-align:right;">{erd}%</td>
              </tr>
              <tr>
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Palier de départ</td>
                <td style="padding:12px 16px;color:#a78bfa;font-weight:700;font-size:13px;text-align:right;">{palier} — {palier_desc}</td>
              </tr>
            </table>

            <div style="background:#1e2a3a;border-left:3px solid #6c63ff;border-radius:8px;
                        padding:16px 20px;margin-bottom:28px;">
              <p style="margin:0;color:#c8d8e8;font-size:13px;line-height:1.6;">
                Votre protocole de 15 séances est maintenant débloqué et personnalisé selon votre profil.
                Les séances S2–S15 sont accessibles depuis votre tableau de bord.
              </p>
            </div>

            <div style="text-align:center;margin-bottom:24px;">
              <a href="http://localhost:5173/protocol"
                 style="display:inline-block;background:linear-gradient(135deg,#6c63ff,#00b4d8);
                        color:#fff;font-weight:700;font-size:15px;padding:14px 36px;
                        border-radius:12px;text-decoration:none;letter-spacing:0.3px;">
                Voir mon programme →
              </a>
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #1e2a3a;text-align:center;">
            <div style="color:#4a5568;font-size:11px;">© 2026 NeuroCap — Easy Medical Device</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send_calibration_blocking(to_email: str, first_name: str, profile: dict) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "NeuroCap — Votre profil EEG et protocole personnalisé"
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to_email
    plain = (
        f"Bonjour {first_name},\n\n"
        f"Votre calibration NeuroCap est terminée.\n"
        f"Profil : Type {profile.get('profile_type','B')} · Palier {profile.get('palier_initial','P1')} · IAPF {profile.get('iapf','—')} Hz\n\n"
        f"Connectez-vous sur http://localhost:5173/protocol pour voir votre programme.\n\nL'équipe NeuroCap"
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(_html_calibration(first_name, profile), "html", "utf-8"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo(); server.starttls(); server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError("Identifiants SMTP Brevo invalides.")
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailSendError(f"Échec SMTP : {exc}")


async def send_calibration_email(to_email: str, first_name: str, profile: dict) -> None:
    """Envoie l'email de résultat de calibration avec le profil EEG et le protocole suggéré."""
    if not settings.SMTP_USER:
        logger.warning("⚠️  SMTP_USER non configuré — EMAIL CALIBRATION pour %s (dev mode)", to_email)
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_calibration_blocking, to_email, first_name, profile)
    logger.info("✅ Email calibration envoyé à %s", to_email)


# ─────────────────────────────────────────────────────────────────────
# Email rapport de séance
# ─────────────────────────────────────────────────────────────────────

_PROFILE_DESC = {
    "A": "profil cognitif de type A (alpha dominant, forte réactivité à la relaxation)",
    "B": "profil cognitif de type B (équilibre alpha/beta, réponse mixte)",
    "C": "profil cognitif de type C (beta dominant, activation cognitive élevée)",
}

_ACQUISITION_DESC = {
    "eeg_live":    "acquisition EEG en direct (OpenBCI/ESP32)",
    "manual":      "saisie manuelle des données EEG",
    "file_upload": "téléversement de fichier EEG (.csv/.edf)",
}

_PALIER_LABELS = {
    "P1": "Initiation — feedback sonore",
    "P2": "Apprentissage — son + visuel",
    "P3": "Maîtrise — feedback complet",
    "P4": "Autonomie progressive",
}


def _build_points(
    blocs: list[float],
    score: int,
    success_rate: float,
    profile_type: str,
    session_number: int,
    palier_before: str,
    palier_after: str,
    acquisition_type: str,
    subjective_pre: dict | None,
    subjective_post: dict | None,
) -> tuple[list[str], list[str]]:
    """Calcule les points forts et faibles adaptés au profil, séance, et type d'acquisition."""
    forts, faibles = [], []

    avg_sr = sum(blocs) / max(len(blocs), 1)
    best_bloc  = max(blocs) if blocs else 0
    worst_bloc = min(blocs) if blocs else 0

    # ── Points forts ──────────────────────────────────────────────────
    if avg_sr >= 0.65:
        forts.append(f"Excellent taux de succès moyen ({avg_sr*100:.0f}%) sur l'ensemble des blocs.")
    if best_bloc >= 0.75:
        forts.append(f"Bloc exceptionnel détecté ({best_bloc*100:.0f}%) — maintien prolongé de l'état cible.")
    if palier_after > palier_before:
        forts.append(f"Progression de palier confirmée : {palier_before} → {palier_after}. Votre cerveau s'adapte.")
    if score >= 70:
        forts.append(f"Score global élevé ({score}/100) — performance au-dessus de la médiane du protocole.")
    if session_number >= 5:
        forts.append("Régularité maintenue — les effets neurofonctionnels commencent à se consolider.")
    if profile_type == "A" and avg_sr >= 0.6:
        forts.append("Profil A : vos ondes alpha répondent très bien à la détente guidée.")
    elif profile_type == "C" and avg_sr >= 0.55:
        forts.append("Profil C : la régulation beta montre une amélioration significative.")
    if subjective_post and subjective_pre:
        if (subjective_post.get("calme", 5) - subjective_pre.get("stress", 5)) > 1:
            forts.append("Réduction subjective du stress confirmée par le questionnaire post-séance.")
    if not forts:
        forts.append("Vous avez complété l'intégralité des blocs — engagement total de la session.")

    # ── Points faibles ────────────────────────────────────────────────
    if avg_sr < 0.45:
        faibles.append(f"Taux de succès faible ({avg_sr*100:.0f}%) — le seuil alpha cible était difficile à maintenir.")
    if worst_bloc < 0.3:
        faibles.append(f"Un bloc difficile détecté ({worst_bloc*100:.0f}%) — possible fatigue mentale ou artefact EEG.")
    if len([b for b in blocs if b < 0.4]) >= 3:
        faibles.append("Plusieurs blocs consécutifs sous le seuil — pensez à améliorer les conditions (calme, position).")
    if score < 50:
        faibles.append(f"Score global en dessous de 50 ({score}/100) — attendez la récupération avant la prochaine séance.")
    if acquisition_type == "eeg_live" and avg_sr < 0.5:
        faibles.append("Acquisition live : vérifiez le placement des électrodes et la conductivité du gel.")
    elif acquisition_type == "file_upload":
        faibles.append("Données téléversées : assurez-vous que l'enregistrement couvre bien toute la durée des blocs.")
    if subjective_pre and subjective_pre.get("fatigue", 5) >= 7:
        faibles.append("Fatigue initiale élevée signalée — idéalement programmer la séance en matinée.")
    if not faibles:
        faibles.append("Aucune faiblesse critique détectée — continuez sur cette lancée.")

    return forts, faibles


def _html_session_report(
    first_name: str,
    session_number: int,
    score: int,
    success_rate: float,
    blocs: list[float],
    profile_type: str,
    palier_before: str,
    palier_after: str,
    palier_reason: str,
    next_date: str,
    acquisition_type: str,
    subjective_pre: dict | None,
    subjective_post: dict | None,
) -> str:
    greeting = f"Bonjour {first_name}" if first_name else "Bonjour"
    forts, faibles = _build_points(
        blocs, score, success_rate, profile_type, session_number,
        palier_before, palier_after, acquisition_type, subjective_pre, subjective_post
    )
    acq_label  = _ACQUISITION_DESC.get(acquisition_type, acquisition_type)
    prof_label = _PROFILE_DESC.get(profile_type, f"profil {profile_type}")
    pal_label  = _PALIER_LABELS.get(palier_after, palier_after)
    next_fmt   = ""
    try:
        from datetime import datetime
        next_fmt = datetime.fromisoformat(next_date).strftime("%A %d %B %Y")
    except Exception:
        next_fmt = next_date

    palier_badge = ""
    if palier_after != palier_before:
        palier_badge = f"""
        <div style="background:#1e2a3a;border-left:3px solid #a78bfa;border-radius:8px;
                    padding:12px 16px;margin-bottom:20px;">
          <p style="margin:0;color:#c8d8e8;font-size:13px;">
            Progression de palier : <strong style="color:#a78bfa;">{palier_before} → {palier_after}</strong>
            — {palier_reason or 'critères de passage atteints'}
          </p>
        </div>"""

    def _list_html(items: list[str], color: str) -> str:
        return "".join(
            f'<li style="margin-bottom:6px;color:#c8d8e8;font-size:13px;line-height:1.5;">'
            f'<span style="color:{color};margin-right:6px;">•</span>{item}</li>'
            for item in items
        )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0e1a;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #1e2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#00b4d8,#0077b6);padding:28px 40px;text-align:center;">
            <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-0.5px;">NeuroCap</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.75);margin-top:4px;">
              Rapport de Séance {session_number}
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px 20px;">

            <h2 style="margin:0 0 6px;color:#f0f4ff;font-size:20px;">
              Bravo {first_name} !
            </h2>
            <p style="margin:0 0 24px;color:#8899aa;font-size:14px;line-height:1.6;">
              Vous venez de compléter la <strong style="color:#f0f4ff;">Séance {session_number}</strong>
              avec succès ({acq_label}).
              Votre {prof_label}.
            </p>

            <!-- Score global -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#0a0e1a;border-radius:12px;border:1px solid #1e2a3a;margin-bottom:24px;">
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Score global</td>
                <td style="padding:12px 16px;color:#00d4ff;font-weight:800;font-size:18px;text-align:right;">{score}/100</td>
              </tr>
              <tr style="border-bottom:1px solid #1e2a3a;">
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Taux de succès moyen</td>
                <td style="padding:12px 16px;color:#34d399;font-weight:700;font-size:13px;text-align:right;">{success_rate*100:.0f}%</td>
              </tr>
              <tr>
                <td style="padding:12px 16px;color:#8899aa;font-size:13px;">Palier actuel</td>
                <td style="padding:12px 16px;color:#a78bfa;font-weight:700;font-size:13px;text-align:right;">{palier_after} — {pal_label}</td>
              </tr>
            </table>

            {palier_badge}

            <!-- Points forts -->
            <h3 style="margin:0 0 10px;color:#34d399;font-size:14px;font-weight:700;">Points forts</h3>
            <ul style="margin:0 0 24px;padding:0;list-style:none;">
              {_list_html(forts, '#34d399')}
            </ul>

            <!-- Points faibles -->
            <h3 style="margin:0 0 10px;color:#fb923c;font-size:14px;font-weight:700;">Points à améliorer</h3>
            <ul style="margin:0 0 24px;padding:0;list-style:none;">
              {_list_html(faibles, '#fb923c')}
            </ul>

            <!-- Prochain RDV -->
            <div style="background:#1e2a3a;border-left:3px solid #00b4d8;border-radius:8px;
                        padding:16px 20px;margin-bottom:28px;">
              <p style="margin:0 0 4px;color:#00d4ff;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">
                Prochain rendez-vous recommandé
              </p>
              <p style="margin:0;color:#f0f4ff;font-size:15px;font-weight:700;">{next_fmt}</p>
              <p style="margin:4px 0 0;color:#8899aa;font-size:12px;">
                Délai minimum respecté selon le protocole ({acq_label}).
              </p>
            </div>

            <div style="text-align:center;margin-bottom:16px;">
              <a href="http://localhost:5173/protocol"
                 style="display:inline-block;background:linear-gradient(135deg,#00b4d8,#0077b6);
                        color:#fff;font-weight:700;font-size:14px;padding:12px 32px;
                        border-radius:12px;text-decoration:none;">
                Voir mon programme →
              </a>
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 40px;border-top:1px solid #1e2a3a;text-align:center;">
            <div style="color:#4a5568;font-size:11px;">© 2026 NeuroCap — Easy Medical Device</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send_session_report_blocking(
    to_email: str, first_name: str, session_number: int, score: int,
    success_rate: float, blocs: list[float], profile_type: str,
    palier_before: str, palier_after: str, palier_reason: str,
    next_date: str, acquisition_type: str,
    subjective_pre: dict | None, subjective_post: dict | None,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"NeuroCap — Rapport Séance {session_number} · Score {score}/100"
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to_email

    forts, faibles = _build_points(
        blocs, score, success_rate, profile_type, session_number,
        palier_before, palier_after, acquisition_type, subjective_pre, subjective_post
    )
    plain = (
        f"Bonjour {first_name},\n\n"
        f"Rapport de la Séance {session_number} — Score : {score}/100 · Taux succès : {success_rate*100:.0f}%\n\n"
        f"Points forts :\n" + "\n".join(f"  • {p}" for p in forts) + "\n\n"
        f"Points à améliorer :\n" + "\n".join(f"  • {p}" for p in faibles) + "\n\n"
        f"Prochain rendez-vous recommandé : {next_date}\n\nL'équipe NeuroCap"
    )
    html = _html_session_report(
        first_name, session_number, score, success_rate, blocs,
        profile_type, palier_before, palier_after, palier_reason,
        next_date, acquisition_type, subjective_pre, subjective_post
    )
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo(); server.starttls(); server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError("Identifiants SMTP Brevo invalides.")
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailSendError(f"Échec SMTP : {exc}")


async def send_session_report_email(
    to_email: str,
    first_name: str,
    session_number: int,
    score: int,
    success_rate: float,
    blocs: list[float],
    profile_type: str,
    palier_before: str,
    palier_after: str,
    palier_reason: str,
    next_date: str,
    acquisition_type: str = "eeg_live",
    subjective_pre: dict | None = None,
    subjective_post: dict | None = None,
) -> None:
    """Envoie le rapport d'évaluation post-séance avec points forts/faibles."""
    if not settings.SMTP_USER:
        logger.warning("⚠️  SMTP_USER non configuré — RAPPORT SÉANCE %d pour %s (dev mode)", session_number, to_email)
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, _send_session_report_blocking,
        to_email, first_name, session_number, score, success_rate, blocs,
        profile_type, palier_before, palier_after, palier_reason,
        next_date, acquisition_type, subjective_pre, subjective_post,
    )
    logger.info("✅ Email rapport séance %d envoyé à %s", session_number, to_email)


def _html_consent(patient_name: str) -> str:
    first_name = patient_name.split()[0] if patient_name else "Participant"
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0e1a;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #1e2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#00b4d8,#0077b6);padding:32px 40px;text-align:center;">
            <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px;">NeuroCap</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:4px;">Consentement éclairé confirmé ✓</div>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <h2 style="margin:0 0 8px;color:#f0f4ff;font-size:20px;">Bonjour {first_name},</h2>
            <p style="margin:0 0 24px;color:#8899aa;font-size:14px;line-height:1.6;">
              Votre consentement éclairé pour le programme NeuroCap a bien été enregistré.
              Vous trouverez ci-joint le document de consentement personnalisé en pièce jointe.
            </p>
            <div style="background:#1e2a3a;border-left:3px solid #00b4d8;border-radius:8px;
                        padding:16px 20px;margin-bottom:28px;">
              <p style="margin:0;color:#c8d8e8;font-size:13px;line-height:1.6;">
                Vous pouvez vous retirer de l'étude à tout moment, sans justification
                et sans aucune conséquence. Pour toute question, contactez votre thérapeute NeuroCap.
              </p>
            </div>
            <div style="text-align:center;margin-bottom:24px;">
              <a href="http://localhost:5173/dashboard"
                 style="display:inline-block;background:linear-gradient(135deg,#00b4d8,#0077b6);
                        color:#fff;font-weight:700;font-size:15px;padding:14px 36px;
                        border-radius:12px;text-decoration:none;letter-spacing:0.3px;">
                Accéder à mon espace →
              </a>
            </div>
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


def _send_consent_blocking(to_email: str, patient_name: str, pdf_bytes: bytes) -> None:
    from email.mime.application import MIMEApplication

    msg = MIMEMultipart("mixed")
    msg["Subject"] = "NeuroCap — Confirmation de votre consentement éclairé"
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to_email

    body = MIMEMultipart("alternative")
    first_name = patient_name.split()[0] if patient_name else "Participant"
    plain = (
        f"Bonjour {first_name},\n\n"
        "Votre consentement éclairé NeuroCap a bien été enregistré.\n"
        "Veuillez trouver votre document de consentement en pièce jointe.\n\n"
        "Vous pouvez vous retirer de l'étude à tout moment sans justification.\n\n"
        "L'équipe NeuroCap"
    )
    body.attach(MIMEText(plain, "plain", "utf-8"))
    body.attach(MIMEText(_html_consent(patient_name), "html", "utf-8"))
    msg.attach(body)

    filename = f"NeuroCap_Consentement_{patient_name.replace(' ', '_')}.pdf"
    pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_part.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(pdf_part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo(); server.starttls(); server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailSendError("Identifiants SMTP Brevo invalides.")
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailSendError(f"Échec SMTP : {exc}")


async def send_consent_email(to_email: str, patient_name: str, pdf_bytes: bytes) -> None:
    """Envoie la confirmation de consentement avec le PDF personnalisé en pièce jointe."""
    if not settings.SMTP_USER:
        logger.warning(
            "⚠️  SMTP_USER non configuré — EMAIL CONSENTEMENT pour %s (dev mode)", to_email
        )
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_consent_blocking, to_email, patient_name, pdf_bytes)
    logger.info("✅ Email consentement envoyé à %s", to_email)


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
