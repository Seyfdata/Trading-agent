"""
Module de notification Telegram.
Envoie des messages formatés sur ton téléphone via un bot Telegram.

Pour configurer :
1. Parle à @BotFather sur Telegram → /newbot → copie le TOKEN
2. Envoie un message à ton bot
3. Va sur https://api.telegram.org/bot<TOKEN>/getUpdates
4. Copie ton chat_id
5. Mets les deux dans le fichier .env
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    """Envoie un message texte sur Telegram."""
    if not TOKEN or not CHAT_ID:
        print("[Telegram] TOKEN ou CHAT_ID manquant dans .env")
        print("[Telegram] Message non envoyé :")
        print(text)
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[Telegram] Message envoyé avec succès")
            return True
        else:
            print(f"[Telegram] Erreur {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("[Telegram] Timeout — Telegram ne répond pas")
        return False
    except Exception as e:
        print(f"[Telegram] Erreur inattendue : {e}")
        return False


# === TEST ===
if __name__ == "__main__":
    # Exécute ce fichier seul pour tester : python notifications/telegram.py
    send_message("🤖 Test du bot Trading Agent — ça marche !")
