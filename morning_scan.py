"""
Morning Scan — Script principal du Trading Agent (Phase 2).

Ce script est exécuté chaque matin à 13h CET (pre-market).
Il collecte les news, les filtre, et t'envoie un résumé sur Telegram.

Usage :
    python morning_scan.py

Automatisation (crontab Linux / Planificateur de tâches Windows) :
    Tous les jours à 13h CET du lundi au vendredi
"""

from datetime import datetime
from scrapers.rss_news import fetch_all_news, filter_by_tickers
from notifications.telegram import send_message
from config.settings import WATCHLIST, EMOJI_NEWS, EMOJI_BULL, EMOJI_WARNING


def format_report(relevant_news, all_news_count):
    """Formate le rapport du morning scan pour Telegram."""

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # En-tête
    lines = [
        f"{EMOJI_NEWS} *MORNING SCAN* — {now}",
        f"News scannées : {all_news_count}",
        f"Pertinentes : {len(relevant_news)}",
        "",
    ]

    if not relevant_news:
        lines.append("Aucune news pertinente ce matin.")
        lines.append("Focus sur l'analyse technique pure.")
    else:
        for news in relevant_news[:5]:  # Max 5 news
            tickers = ", ".join(news.get("matched_tickers", []))
            lines.append(f"{EMOJI_BULL} *[{tickers}]* {news['title']}")
            if news.get("link"):
                lines.append(f"  {news['link']}")
            lines.append("")

    # Rappels
    lines.extend([
        "---",
        f"{EMOJI_WARNING} *Rappels :*",
        "• Vérifier le calendrier macro (ForexFactory)",
        "• Killzone : 14h30-16h30 CET",
        "• Risque max : 1% par trade",
    ])

    return "\n".join(lines)


def main():
    """Exécute le morning scan complet."""

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Morning scan démarré...")

    # 1. Récupérer les news
    print("  Collecte des news RSS...")
    all_news = fetch_all_news(max_per_feed=5)
    print(f"  → {len(all_news)} news récupérées")

    # 2. Filtrer par tickers
    print("  Filtrage par tickers...")
    relevant = filter_by_tickers(all_news, WATCHLIST)
    print(f"  → {len(relevant)} news pertinentes")

    # 3. Formater le rapport
    report = format_report(relevant, len(all_news))

    # 4. Afficher dans le terminal
    print("\n" + "=" * 50)
    print(report)
    print("=" * 50)

    # 5. Envoyer sur Telegram
    print("\n  Envoi sur Telegram...")
    send_message(report)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Morning scan terminé.")


if __name__ == "__main__":
    main()
