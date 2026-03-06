"""
Module Market Data — Données de marché en temps réel via yfinance.

3 niveaux :
  1. Market Context : SPY, QQQ, VIX, DXY, US10Y
  2. Watchlist Scanner : prix, variation, SMA200, volume relatif
  3. Setup Candidates : tickers à regarder en priorité

Prérequis :
  pip install yfinance

Note : yfinance utilise Yahoo Finance (gratuit, pas d'API key).
Les données sont en léger différé (~15 min) — suffisant pour le pre-market.
"""

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

from config.settings import (
    WATCHLIST, EMOJI_CHART, EMOJI_BULL, EMOJI_BEAR, EMOJI_NEUTRAL,
    EMOJI_WARNING, EMOJI_FIRE, EMOJI_CHECK, EMOJI_NO
)


# =============================================
# NIVEAU 1 — MARKET CONTEXT
# =============================================

MACRO_TICKERS = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "^VIX": "VIX (Fear Index)",
    "DX-Y.NYB": "Dollar (DXY)",
    "^TNX": "US 10Y Yield",
}


def get_market_context():
    """
    Récupère le contexte macro : SPY, QQQ, VIX, DXY, US10Y.
    Retourne un dict avec prix, variation, et interprétation.
    """
    if not YF_AVAILABLE:
        return None

    context = {}

    for ticker, name in MACRO_TICKERS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="5d")

            if hist.empty or len(hist) < 2:
                continue

            current = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]
            change_pct = ((current - prev) / prev) * 100

            context[ticker] = {
                "name": name,
                "price": round(current, 2),
                "change_pct": round(change_pct, 2),
            }

        except Exception as e:
            context[ticker] = {"name": name, "error": str(e)}

    return context


def interpret_vix(vix_price):
    """Interprète le niveau du VIX."""
    if vix_price < 15:
        return "CALME", EMOJI_CHECK, "Marché serein — trading normal"
    elif vix_price < 20:
        return "NORMAL", EMOJI_CHECK, "Volatilité normale — GO"
    elif vix_price < 25:
        return "ÉLEVÉ", EMOJI_WARNING, "Prudence — risque 0.5% max"
    elif vix_price < 30:
        return "HAUT", EMOJI_NO, "VIX > 25 — risque réduit ou NO TRADE"
    else:
        return "EXTRÊME", EMOJI_NO, "VIX > 30 — NE PAS TRADER"


def format_market_context(context):
    """Formate la section Market Context pour Telegram."""
    if context is None:
        return None

    lines = [f"{EMOJI_CHART} *MARKET CONTEXT*", ""]

    for ticker in ["SPY", "QQQ", "^VIX", "DX-Y.NYB", "^TNX"]:
        info = context.get(ticker)
        if not info or "error" in info:
            continue

        price = info["price"]
        change = info["change_pct"]
        name = info["name"]

        if change > 0:
            emoji = EMOJI_BULL
            arrow = "↑"
        elif change < 0:
            emoji = EMOJI_BEAR
            arrow = "↓"
        else:
            emoji = EMOJI_NEUTRAL
            arrow = "→"

        lines.append(f"{emoji} *{name}* : {price} ({arrow}{change:+.2f}%)")

    # Interprétation VIX
    vix_info = context.get("^VIX")
    if vix_info and "price" in vix_info:
        level, vix_emoji, vix_msg = interpret_vix(vix_info["price"])
        lines.append("")
        lines.append(f"{vix_emoji} *VIX {level}* — {vix_msg}")

    # Verdict marché
    spy_info = context.get("SPY")
    vix_info = context.get("^VIX")
    if spy_info and vix_info and "price" in vix_info:
        spy_change = spy_info.get("change_pct", 0)
        vix_price = vix_info["price"]

        if vix_price > 25:
            verdict = f"{EMOJI_NO} *MARCHÉ : DANGER* — VIX trop haut"
        elif vix_price > 20 and spy_change < -1:
            verdict = f"{EMOJI_WARNING} *MARCHÉ : PRUDENCE* — VIX élevé + SPY en baisse"
        elif spy_change > 0.5 and vix_price < 20:
            verdict = f"{EMOJI_CHECK} *MARCHÉ : FAVORABLE* — SPY haussier, VIX bas"
        else:
            verdict = f"{EMOJI_NEUTRAL} *MARCHÉ : NEUTRE* — Pas de signal clair"

        lines.append(verdict)

    return "\n".join(lines)


# =============================================
# NIVEAU 2 — WATCHLIST SCANNER
# =============================================

def scan_watchlist(tickers=None):
    """
    Scanne chaque ticker de la watchlist :
    - Prix actuel
    - Variation jour (%)
    - Variation semaine (%)
    - Position vs SMA200
    - Volume relatif (vs moyenne 20j)
    """
    if not YF_AVAILABLE:
        return None

    if tickers is None:
        tickers = WATCHLIST

    results = []

    for ticker in tickers:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1y")

            if hist.empty or len(hist) < 10:
                continue

            current = hist["Close"].iloc[-1]
            prev_day = hist["Close"].iloc[-2]
            prev_week = hist["Close"].iloc[-6] if len(hist) > 6 else prev_day

            # Variations
            change_day = ((current - prev_day) / prev_day) * 100
            change_week = ((current - prev_week) / prev_week) * 100

            # SMA200
            if len(hist) >= 200:
                sma200 = hist["Close"].rolling(200).mean().iloc[-1]
                dist_sma200 = ((current - sma200) / sma200) * 100
                above_sma200 = current > sma200
            else:
                sma200 = None
                dist_sma200 = None
                above_sma200 = None

            # Volume relatif (aujourd'hui vs moyenne 20j)
            vol_today = hist["Volume"].iloc[-1]
            vol_avg_20 = hist["Volume"].tail(20).mean()
            vol_relative = vol_today / vol_avg_20 if vol_avg_20 > 0 else 1.0

            results.append({
                "ticker": ticker,
                "price": round(current, 2),
                "change_day": round(change_day, 2),
                "change_week": round(change_week, 2),
                "sma200": round(sma200, 2) if sma200 else None,
                "dist_sma200": round(dist_sma200, 1) if dist_sma200 else None,
                "above_sma200": above_sma200,
                "vol_relative": round(vol_relative, 2),
                "vol_today": int(vol_today),
            })

        except Exception as e:
            results.append({"ticker": ticker, "error": str(e)})

    return results


def format_watchlist_scanner(scan_results):
    """Formate la section Watchlist Scanner pour Telegram."""
    if scan_results is None:
        return None

    lines = [f"{EMOJI_CHART} *WATCHLIST SCANNER*", ""]

    for r in scan_results:
        if "error" in r:
            continue

        ticker = r["ticker"]
        price = r["price"]
        day = r["change_day"]
        week = r["change_week"]
        vol = r["vol_relative"]
        sma = r.get("above_sma200")
        dist = r.get("dist_sma200")

        # Emoji direction
        if day > 1:
            emoji = EMOJI_BULL
        elif day < -1:
            emoji = EMOJI_BEAR
        else:
            emoji = EMOJI_NEUTRAL

        # SMA200 indicator
        sma_text = ""
        if sma is not None:
            sma_icon = "✅" if sma else "⚠️"
            sma_text = f" | SMA200:{sma_icon}{dist:+.1f}%"

        # Volume alert
        vol_text = ""
        if vol > 1.5:
            vol_text = f" | Vol:🔥x{vol:.1f}"
        elif vol > 1.2:
            vol_text = f" | Vol:↑x{vol:.1f}"

        lines.append(f"{emoji} *{ticker}* {price}$ | J:{day:+.1f}% | S:{week:+.1f}%{sma_text}{vol_text}")

    return "\n".join(lines)


# =============================================
# NIVEAU 3 — SETUP CANDIDATES
# =============================================

def find_setup_candidates(scan_results):
    """
    Identifie les tickers à regarder EN PRIORITÉ sur TradingView.
    Ce ne sont PAS des signaux — ce sont des candidats.

    Critères :
    - Discount : baisse > 3% sur la semaine (potentiel rebond sur OB)
    - Volume anormal : > 1.5x la moyenne 20j (les institutions bougent)
    - Sous SMA200 qui remonte : potentiel retournement
    """
    if scan_results is None:
        return None

    candidates = []

    for r in scan_results:
        if "error" in r:
            continue

        reasons = []
        priority = 0

        # Critère 1 : En discount (baisse semaine > 3%)
        if r["change_week"] < -3:
            reasons.append(f"Discount {r['change_week']:.1f}% sur la semaine")
            priority += 2

        # Critère 2 : Volume anormal
        if r["vol_relative"] > 1.5:
            reasons.append(f"Volume x{r['vol_relative']:.1f} vs moy. 20j")
            priority += 2

        # Critère 3 : Rebond sur SMA200 (prix proche de la SMA200, dans les 3%)
        if r.get("dist_sma200") is not None:
            dist = abs(r["dist_sma200"])
            if dist < 3 and r.get("above_sma200"):
                reasons.append(f"Proche SMA200 ({r['dist_sma200']:+.1f}%) — support")
                priority += 1

        # Critère 4 : Sous SMA200 (bearish context, prudence)
        if r.get("above_sma200") is False:
            reasons.append(f"Sous SMA200 ({r['dist_sma200']:+.1f}%) — prudence")
            priority += 1

        # Critère 5 : Forte hausse jour (momentum)
        if r["change_day"] > 3:
            reasons.append(f"Momentum +{r['change_day']:.1f}% aujourd'hui")
            priority += 1

        if reasons:
            candidates.append({
                "ticker": r["ticker"],
                "price": r["price"],
                "priority": priority,
                "reasons": reasons,
            })

    # Trier par priorité
    candidates.sort(key=lambda x: x["priority"], reverse=True)
    return candidates


def format_setup_candidates(candidates):
    """Formate la section Setup Candidates pour Telegram."""
    if candidates is None:
        return None

    high_priority = [c for c in candidates if c["priority"] >= 2]
    low_priority = [c for c in candidates if c["priority"] < 2]

    lines = [f"{EMOJI_FIRE} *SETUP CANDIDATES* (à vérifier sur TradingView)", ""]

    if not high_priority and not low_priority:
        lines.append("Aucun candidat détecté aujourd'hui.")
        lines.append("Pas de signal = pas de trade forcé. Patience = edge.")
        return "\n".join(lines)

    if high_priority:
        lines.append("*Priorité HAUTE :*")
        for c in high_priority[:3]:
            ticker = c["ticker"]
            price = c["price"]
            reasons = " + ".join(c["reasons"])
            lines.append(f"  {EMOJI_FIRE} *{ticker}* ({price}$)")
            lines.append(f"    → {reasons}")
        lines.append("")

    if low_priority:
        lines.append("*À surveiller :*")
        for c in low_priority[:3]:
            ticker = c["ticker"]
            reasons = c["reasons"][0]  # Juste la première raison
            lines.append(f"  👀 *{ticker}* — {reasons}")

    lines.extend([
        "",
        f"{EMOJI_WARNING} *Ces candidats ne sont PAS des trades.*",
        "Ouvre TradingView → analyse SMC → setup valide = trade.",
    ])

    return "\n".join(lines)


# =============================================
# FONCTION TOUT-EN-UN
# =============================================

def get_full_market_brief():
    """
    Lance les 3 niveaux et retourne les textes formatés.
    Retourne (market_text, watchlist_text, candidates_text) ou (None, None, None).
    """
    if not YF_AVAILABLE:
        print("  [Market] yfinance non installé. Lance : pip install yfinance")
        return None, None, None

    # Niveau 1
    print("     Niveau 1 : Market Context...")
    context = get_market_context()
    market_text = format_market_context(context)

    # Niveau 2
    print("     Niveau 2 : Watchlist Scanner...")
    scan = scan_watchlist()
    watchlist_text = format_watchlist_scanner(scan)

    # Niveau 3
    print("     Niveau 3 : Setup Candidates...")
    candidates = find_setup_candidates(scan)
    candidates_text = format_setup_candidates(candidates)

    return market_text, watchlist_text, candidates_text


# === TEST ===
if __name__ == "__main__":
    print("=== TEST MARKET DATA ===\n")

    if not YF_AVAILABLE:
        print("yfinance non installé. Lance : pip install yfinance")
    else:
        market, watchlist, candidates = get_full_market_brief()

        if market:
            print(market)
            print()
        if watchlist:
            print(watchlist)
            print()
        if candidates:
            print(candidates)
