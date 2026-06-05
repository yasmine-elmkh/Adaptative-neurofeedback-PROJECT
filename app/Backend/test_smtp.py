"""Test rapide de la connexion SMTP Brevo — à supprimer après debug."""
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

HOST     = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
PORT     = int(os.getenv("SMTP_PORT", "587"))
USER     = os.getenv("SMTP_USER", "")
PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM     = os.getenv("SMTP_FROM", "")

print(f"Host    : {HOST}:{PORT}")
print(f"User    : {USER}")
print(f"From    : {FROM}")
print(f"Pass    : {'*' * len(PASSWORD)} ({len(PASSWORD)} chars)")
print()

try:
    with smtplib.SMTP(HOST, PORT, timeout=10) as server:
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USER, PASSWORD)
        print("\n✅ Connexion SMTP OK — identifiants valides")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentification échouée : {e}")
    print("→ Vérifiez SMTP_USER et SMTP_PASSWORD dans .env")
except Exception as e:
    print(f"\n❌ Erreur : {e}")
