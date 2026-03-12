"""
Configuration centralisée du Trading Agent.
Les valeurs sensibles (clés API) sont dans .env
Ici on met les paramètres de trading et les listes.

Les valeurs WATCHLIST, TICKER_ALIASES et les règles de trading sont chargées
depuis config/config.yaml si ce fichier existe, sinon les valeurs en dur
ci-dessous servent de fallback.
"""

from config.loader import (
    get_watchlist,
    get_aliases,
    get_killzone,
    get_trading_rules,
    get_dashboard_config,
)

# === WATCHLIST ===
# Chargée depuis config.yaml (fallback : valeurs en dur ci-dessous)
WATCHLIST = get_watchlist()

# Noms complets et aliases pour capter les news qui n'utilisent pas le ticker
# Format : "nom dans l'article" → "ticker affiché dans le rapport"
TICKER_ALIASES = get_aliases()


# === FLUX RSS ===
# Sources de news à scanner (classées par fiabilité)
RSS_FEEDS = {
    # --- Tier 1 : Sources institutionnelles ---
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters Tech": "https://feeds.reuters.com/reuters/technologyNews",
    "AP Business": "https://rsshub.app/apnews/topics/business",

    # --- Tier 2 : Médias financiers majeurs ---
    "CNBC Top News": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "CNBC Tech": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "MarketWatch Top": "http://feeds.marketwatch.com/marketwatch/topstories/",
    "MarketWatch Stocks": "http://feeds.marketwatch.com/marketwatch/marketpulse/",

    # --- Tier 3 : Analyse et opinions ---
    "Seeking Alpha Market News": "https://seekingalpha.com/market_currents.xml",

    # --- Tier 4 : Institutionnel / Fed ---
    "Fed Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
}

# Mots-clés supplémentaires à détecter (en plus des tickers)
# Si un de ces mots apparaît, la news est considérée comme pertinente
MARKET_KEYWORDS = [
    "Fed", "FOMC", "interest rate", "inflation", "CPI", "NFP",
    "jobs report", "unemployment", "GDP", "earnings",
    "S&P 500", "Nasdaq", "Dow Jones", "Wall Street",
    "semiconductor", "chip", "AI stocks", "tech stocks",
    "tariff", "trade war", "sanctions",
]

# === CALENDRIER MACRO ===
# Événements récurrents à vérifier
# Format : "description" : {"impact": FORT/MOYEN, "heure_cet": "HH:MM"}
MACRO_EVENTS = {
    "FOMC": {
        "impact": "FORT",
        "heure_cet": "20:00",
        "regle": "NO TRADE le jour J. Analyser J+1 à J+2.",
        "frequence": "8x par an",
    },
    "NFP (Non-Farm Payrolls)": {
        "impact": "FORT",
        "heure_cet": "14:30",
        "regle": "NO TRADE le jour J. Setups post-NFP J+1.",
        "frequence": "1er vendredi du mois",
    },
    "CPI (Inflation)": {
        "impact": "FORT",
        "heure_cet": "14:30",
        "regle": "NO TRADE le jour J. Attendre la réaction.",
        "frequence": "Mensuel, ~2ème semaine",
    },
    "PPI (Prix producteurs)": {
        "impact": "MOYEN",
        "heure_cet": "14:30",
        "regle": "Risque réduit 0.5%. Éviter 15 min autour de l'annonce.",
        "frequence": "Mensuel",
    },
    "Jobless Claims": {
        "impact": "MOYEN",
        "heure_cet": "14:30",
        "regle": "Risque réduit 0.5%. Attention si chiffre surprise.",
        "frequence": "Chaque jeudi",
    },
    "Retail Sales": {
        "impact": "MOYEN",
        "heure_cet": "14:30",
        "regle": "Risque réduit 0.5%.",
        "frequence": "Mensuel",
    },
    "PCE (dépenses conso)": {
        "impact": "MOYEN-FORT",
        "heure_cet": "14:30",
        "regle": "Indicateur favori de la Fed. Prudence.",
        "frequence": "Mensuel, dernière semaine",
    },
    "GDP (PIB)": {
        "impact": "MOYEN-FORT",
        "heure_cet": "14:30",
        "regle": "Risque réduit 0.5%.",
        "frequence": "Trimestriel",
    },
    "ISM Manufacturing": {
        "impact": "MOYEN",
        "heure_cet": "16:00",
        "regle": "Risque réduit si < 50 (contraction).",
        "frequence": "1er jour ouvré du mois",
    },
}

# Earnings des Magnificent 7 (dates approximatives par trimestre)
# À mettre à jour chaque trimestre !
# Mettre la date au format "YYYY-MM-DD" ou "TBD" si pas encore annoncé
MAG7_EARNINGS = {
    "AAPL": {"Q1_2026": "TBD", "note": "Généralement fin janvier / fin avril / fin juillet / fin octobre"},
    "MSFT": {"Q1_2026": "TBD", "note": "Généralement fin janvier / fin avril / fin juillet / fin octobre"},
    "GOOGL": {"Q1_2026": "TBD", "note": "Généralement fin janvier / fin avril / fin juillet / fin octobre"},
    "AMZN": {"Q1_2026": "TBD", "note": "Généralement début février / fin avril / début août / fin octobre"},
    "NVDA": {"Q1_2026": "TBD", "note": "Généralement fin février / fin mai / fin août / fin novembre"},
    "META": {"Q1_2026": "TBD", "note": "Généralement fin janvier / fin avril / fin juillet / fin octobre"},
    "TSLA": {"Q1_2026": "TBD", "note": "Généralement fin janvier / fin avril / fin juillet / fin octobre"},
}

# === TRADING RULES ===
# Chargées depuis config.yaml
_trading = get_trading_rules()
RISK_PCT_MIN = _trading["risk_pct_min"]
RISK_PCT_MAX = _trading["risk_pct_max"]
RR_MINIMUM = _trading["rr_minimum"]
MAX_TRADES_PER_DAY = _trading["max_trades_per_day"]
MAX_EXPOSURE_PCT = _trading["max_exposure_pct"]

# Killzone (heure CET)
_kz = get_killzone()
_kz_start = _kz.get("start", "14:30").split(":")
_kz_end = _kz.get("end", "16:30").split(":")
KILLZONE_START_HOUR = int(_kz_start[0])
KILLZONE_START_MIN = int(_kz_start[1])
KILLZONE_END_HOUR = int(_kz_end[0])
KILLZONE_END_MIN = int(_kz_end[1])
KILLZONE_TEST_MODE = False   # Mettre True pour forcer la killzone en dev

# === TELEGRAM ===
_dashboard = get_dashboard_config()
TELEGRAM_ENABLED = _dashboard.get("telegram_enabled", False)

# Format des messages
EMOJI_BULL = "🟢"
EMOJI_BEAR = "🔴"
EMOJI_NEUTRAL = "⚪"
EMOJI_WARNING = "⚠️"
EMOJI_NEWS = "📰"
EMOJI_CHART = "📊"
EMOJI_CALENDAR = "📅"
EMOJI_FIRE = "🔥"
EMOJI_NO = "🚫"
EMOJI_CHECK = "✅"
