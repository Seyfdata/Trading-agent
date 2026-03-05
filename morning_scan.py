"""
Morning Scan v2 — Script principal du Trading Agent (Phase 2).

Ce script est exécuté chaque matin à 13h CET (pre-market).
Il collecte les news, vérifie le calendrier macro,
et t'envoie un rapport complet sur Telegram.

Nouveautés v2 :
- 10 sources RSS (au lieu de 3)
- Filtrage par tickers ET par mots-clés marché (Fed, CPI, earnings...)
- Calendrier macro automatique (détection NFP, FOMC, CPI, Jobless Claims...)
- Recommandation GO / PRUDENCE / NO TRADE

Usage :
    python morning_scan.py
"""

from datetime import datetime
from scrapers.rss_news import fetch_and_filter
from scrapers.macro_calendar import (
    format_macro_section, detect_recurring_events,
    check_earnings_today, get_trading_recommendation
)
from notifications.telegram import send_message
from config.settings import (
    WATCHLIST, EMOJI_NEWS, EMOJI_BULL, EMOJI_WARNING,
    EMOJI_NEUTRAL, EMOJI_CHART, EMOJI_FIRE
)


def format_report(ticker_news, keyword_news, combined, all_count, macro_text):
    """Formate le rapport complet du morning scan pour Telegram."""

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    lines = [
        f"{EMOJI_CHART} *MORNING SCAN v2* — {now}",
        f"Sources : 10 flux RSS scannés",
        f"News totales : {all_count}",
        f"Par tickers : {len(ticker_news)} | Par mots-clés : {len(keyword_news)}",
        f"Pertinentes (unique) : {len(combined)}",
        "",
        "=" * 35,
        "",
    ]

    # === SECTION MACRO ===
    lines.append(macro_text)
    lines.append("")
    lines.append("=" * 35)
    lines.append("")

    # === SECTION NEWS TICKERS ===
    if ticker_news:
        lines.append(f"{EMOJI_FIRE} *NEWS PAR TICKERS*")
        lines.append("")
        for news in ticker_news[:5]:
            tickers = ", ".join(news.get("matched_tickers", []))
            lines.append(f"{EMOJI_BULL} *[{tickers}]* {news['title']}")
            lines.append(f"  _{news['source']}_")
            lines.append("")
    else:
        lines.append(f"{EMOJI_NEUTRAL} Aucune news mentionnant tes tickers.")
        lines.append("")

    # === SECTION NEWS MARCHÉ ===
    ticker_titles = {n["title"] for n in ticker_news}
    keyword_only = [n for n in keyword_news if n["title"] not in ticker_titles]

    if keyword_only:
        lines.append(f"{EMOJI_NEWS} *NEWS MARCHÉ*")
        lines.append("")
        for news in keyword_only[:5]:
            keywords = ", ".join(news.get("matched_keywords", [])[:3])
            lines.append(f"{EMOJI_NEUTRAL} [{keywords}] {news['title']}")
            lines.append(f"  _{news['source']}_")
            lines.append("")

    # === RAPPELS ===
    lines.extend([
        "=" * 35,
        "",
        f"{EMOJI_WARNING} *Checklist pre-market :*",
        "• Confirmer la macro sur ForexFactory.com",
        "• Vérifier SPY/QQQ Daily vs SMA200",
        "• Vérifier VIX (< 20 = GO, 20-25 = prudence, > 25 = stop)",
        "• Préparer les niveaux pendant le pre-market (13h-14h30)",
        "• Killzone : 14h30-16h30 CET uniquement",
    ])

    return "\n".join(lines)


def main():
    """Exécute le morning scan complet."""

    start = datetime.now()
    print(f"[{start.strftime('%H:%M:%S')}] Morning Scan v2 démarré...")
    print(f"  Date : {start.strftime('%A %d/%m/%Y')}")
    print()

    # 1. Calendrier macro
    print("  1. Vérification calendrier macro...")
    macro_text = format_macro_section()
    events = detect_recurring_events()
    earnings = check_earnings_today()
    reco = get_trading_recommendation(events, earnings)
    print(f"     Événements : {len(events)} | Earnings : {len(earnings)}")
    print(f"     Verdict : {reco['verdict']}")
    print()

    # 2. Collecte et filtrage des news
    print("  2. Collecte des news RSS (10 sources)...")
    all_news, ticker_news, keyword_news, combined = fetch_and_filter(
        max_per_feed=5
    )
    print(f"     Total : {len(all_news)} news")
    print(f"     Par tickers : {len(ticker_news)}")
    print(f"     Par mots-clés : {len(keyword_news)}")
    print(f"     Combiné (unique) : {len(combined)}")
    print()

    # 3. Formater le rapport
    report = format_report(
        ticker_news, keyword_news, combined, len(all_news), macro_text
    )

    # 4. Afficher dans le terminal
    print("=" * 55)
    print(report)
    print("=" * 55)

    # 5. Envoyer sur Telegram
    print("\n  Envoi sur Telegram...")
    send_message(report)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Terminé en {elapsed:.1f}s")


if __name__ == "__main__":
    main()
