"""
Configuration centralisée du Trading Agent.
Les valeurs sensibles (clés API) sont dans .env
Ici on met les paramètres de trading et les listes.
"""

# === WATCHLIST ===
# Actions que tu surveilles activement
WATCHLIST = [
    "AAPL",   # Apple
    "NVDA",   # Nvidia
    "TSLA",   # Tesla
    "MSFT",   # Microsoft
    "META",   # Meta (Facebook)
    "AMZN",   # Amazon
    "GOOGL",  # Google
    "AMD",    # AMD
    "AVGO",   # Broadcom
    "QCOM",   # Qualcomm
]

# === FLUX RSS ===
# Sources de news à scanner
RSS_FEEDS = {
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "CNBC Top News": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
}

# === TRADING RULES ===
# Les core rules — ne jamais modifier sans raison
RISK_PCT_MIN = 0.5      # Risque minimum par trade (%)
RISK_PCT_MAX = 1.0       # Risque maximum par trade (%)
RR_MINIMUM = 2.5         # R:R minimum accepté
MAX_TRADES_PER_DAY = 2   # Maximum de trades par jour
MAX_EXPOSURE_PCT = 3.0   # Exposition max simultanée (%)

# Killzone (heure CET)
KILLZONE_START_HOUR = 14
KILLZONE_START_MIN = 30
KILLZONE_END_HOUR = 16
KILLZONE_END_MIN = 30

# === TELEGRAM ===
# Format des messages
EMOJI_BULL = "🟢"
EMOJI_BEAR = "🔴"
EMOJI_NEUTRAL = "⚪"
EMOJI_WARNING = "⚠️"
EMOJI_NEWS = "📰"
EMOJI_CHART = "📊"
