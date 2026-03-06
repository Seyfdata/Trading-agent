"""
Morning Scan v3 — PRO Brief

Rapport complet pre-market pour swing trader SMC :
1. Calendrier macro (événements + verdict GO/PRUDENCE/NO TRADE)
2. Market Context (SPY, QQQ, VIX, DXY, US10Y + verdict marché)
3. Watchlist Scanner (10 tickers : prix, variation, SMA200, volume)
4. Setup Candidates (tickers à regarder en priorité sur TradingView)
5. Reddit Buzz (13 subreddits : sentiment + tickers qui buzzent)
6. News par tickers + news marché (10 flux RSS)
7. Checklist pre-market

Usage :
    python morning_scan.py
"""

from datetime import datetime
from scrapers.rss_news import fetch_and_filter
from scrapers.macro_calendar import (
    format_macro_section, detect_recurring_events,
    check_earnings_today, get_trading_recommendation
)
from scrapers.reddit import format_reddit_section
from scrapers.market_data import get_full_market_brief
from notifications.telegram import send_message
from config.settings import (
    WATCHLIST, EMOJI_NEWS, EMOJI_BULL, EMOJI_WARNING,
    EMOJI_NEUTRAL, EMOJI_CHART, EMOJI_FIRE
)


def format_report(
    macro_text,
    market_text, watchlist_text, candidates_text,
    reddit_text,
    ticker_news, keyword_news, combined, all_count
):
    """Formate le rapport complet PRO Brief."""

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    lines = [
        f"{EMOJI_CHART} *MORNING BRIEF PRO* — {now}",
        "",
        "=" * 35,
        "",
    ]

    # 1. MACRO
    lines.append(macro_text)
    lines.append("")
    lines.append("=" * 35)
    lines.append("")

    # 2. MARKET CONTEXT
    if market_text:
        lines.append(market_text)
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

    # 3. WATCHLIST SCANNER
    if watchlist_text:
        lines.append(watchlist_text)
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

    # 4. SETUP CANDIDATES
    if candidates_text:
        lines.append(candidates_text)
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

    # 5. REDDIT BUZZ
    if reddit_text:
        lines.append(reddit_text)
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

    # 6. NEWS
    if ticker_news:
        lines.append(f"{EMOJI_FIRE} *NEWS TICKERS*")
        lines.append("")
        for news in ticker_news[:5]:
            tickers = ", ".join(news.get("matched_tickers", []))
            lines.append(f"{EMOJI_BULL} *[{tickers}]* {news['title']}")
            lines.append(f"  _{news['source']}_")
            lines.append("")

    ticker_titles = {n["title"] for n in ticker_news}
    keyword_only = [n for n in keyword_news if n["title"] not in ticker_titles]
    if keyword_only:
        lines.append(f"{EMOJI_NEWS} *NEWS MARCHÉ*")
        lines.append("")
        for news in keyword_only[:3]:
            keywords = ", ".join(news.get("matched_keywords", [])[:3])
            lines.append(f"{EMOJI_NEUTRAL} [{keywords}] {news['title']}")
            lines.append(f"  _{news['source']}_")
            lines.append("")

    # 7. CHECKLIST
    lines.extend([
        "=" * 35,
        "",
        f"{EMOJI_WARNING} *Checklist pre-market :*",
        "• Confirmer la macro sur ForexFactory.com",
        "• Analyser les Setup Candidates sur TradingView",
        "• Préparer les niveaux (OB, FVG, liquidité)",
        "• Pre-market : 13h-14h30 CET (analyse)",
        "• Killzone : 14h30-16h30 CET (exécution)",
        "• Risque max selon verdict macro",
    ])

    return "\n".join(lines)


def main():
    """Exécute le Morning Brief PRO complet."""

    start = datetime.now()
    print(f"[{start.strftime('%H:%M:%S')}] Morning Brief PRO démarré...")
    print(f"  Date : {start.strftime('%A %d/%m/%Y')}")
    print()

    # 1. Calendrier macro
    print("  1. Calendrier macro...")
    macro_text = format_macro_section()
    events = detect_recurring_events()
    earnings = check_earnings_today()
    reco = get_trading_recommendation(events, earnings)
    print(f"     Verdict : {reco['verdict']}")
    print()

    # 2. Market Data (3 niveaux)
    print("  2. Market Data...")
    market_text, watchlist_text, candidates_text = get_full_market_brief()
    print()

    # 3. Reddit buzz
    print("  3. Reddit Buzz...")
    reddit_text = None
    try:
        reddit_text = format_reddit_section()
        if reddit_text:
            print("     Reddit OK")
        else:
            print("     Reddit skip")
    except Exception as e:
        print(f"     Reddit erreur : {e}")
    print()

    # 4. News RSS
    print("  4. News RSS (10 sources)...")
    all_news, ticker_news, keyword_news, combined = fetch_and_filter(max_per_feed=5)
    print(f"     {len(all_news)} news → {len(ticker_news)} tickers + {len(keyword_news)} keywords")
    print()

    # 5. Formater
    report = format_report(
        macro_text,
        market_text, watchlist_text, candidates_text,
        reddit_text,
        ticker_news, keyword_news, combined, len(all_news)
    )

    # 6. Afficher
    print("=" * 60)
    print(report)
    print("=" * 60)

    # 7. Envoyer sur Telegram
    # Telegram a une limite de 4096 caractères par message
    print("\n  Envoi sur Telegram...")
    if len(report) > 4000:
        # Couper en 2 messages si trop long
        mid = report.find("NEWS TICKERS")
        if mid > 0:
            part1 = report[:mid].rstrip()
            part2 = report[mid:]
            send_message(part1)
            send_message(part2)
        else:
            send_message(report[:4000])
            send_message(report[4000:])
    else:
        send_message(report)

    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Morning Brief PRO terminé en {elapsed:.1f}s")


if __name__ == "__main__":
    main()
