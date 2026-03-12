"""
Chargement de la configuration depuis config.yaml.
Fournit des fonctions utilitaires pour accéder aux paramètres.
"""

import os
import yaml

_CONFIG = None
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def get_config() -> dict:
    """Charge et retourne la configuration complète (singleton)."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_config()
    return _CONFIG


def _load_config() -> dict:
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        print("[OK] Config chargee depuis config.yaml")
        return cfg
    else:
        print("[WARN] config.yaml non trouve, utilisation des valeurs par defaut")
        return {}


# --- Fonctions utilitaires ---

_WATCHLIST_FALLBACK = [
    "AAPL", "NVDA", "TSLA", "MSFT", "META", "AMZN", "GOOGL",
    "AMD", "AVGO", "QCOM", "INTC", "PLTR", "SMCI", "MU",
    "ASML", "TWLO", "BABA", "ZS", "MRVL", "CRM", "SNOW", "TSM",
]

_ALIASES_FALLBACK = {
    "Apple": "AAPL", "iPhone": "AAPL", "Nvidia": "NVDA", "GeForce": "NVDA",
    "Tesla": "TSLA", "Elon Musk": "TSLA", "Microsoft": "MSFT", "Azure": "MSFT",
    "Meta Platforms": "META", "Facebook": "META", "Instagram": "META",
    "Zuckerberg": "META", "Amazon": "AMZN", "AWS": "AMZN",
    "Alphabet": "GOOGL", "Google": "GOOGL", "Advanced Micro": "AMD",
    "Broadcom": "AVGO", "Qualcomm": "QCOM", "Snapdragon": "QCOM",
    "Intel": "INTC", "Palantir": "PLTR", "Super Micro": "SMCI",
    "SuperMicro": "SMCI", "Micron": "MU", "ASML": "ASML", "Twilio": "TWLO",
    "Alibaba": "BABA", "Jack Ma": "BABA", "Zscaler": "ZS", "Marvell": "MRVL",
    "Salesforce": "CRM", "Snowflake": "SNOW", "TSMC": "TSM",
    "Taiwan Semiconductor": "TSM",
}


def get_watchlist() -> list[str]:
    """Retourne la liste des tickers : ['AAPL', 'NVDA', ...]"""
    cfg = get_config()
    items = cfg.get("watchlist", [])
    if items:
        return [item["ticker"] for item in items]
    return _WATCHLIST_FALLBACK


def get_watchlist_with_names() -> list[dict]:
    """Retourne la liste de dicts : [{'ticker': 'AAPL', 'name': 'Apple'}, ...]"""
    cfg = get_config()
    items = cfg.get("watchlist", [])
    if items:
        return [{"ticker": item["ticker"], "name": item["name"]} for item in items]
    return [{"ticker": t, "name": t} for t in _WATCHLIST_FALLBACK]


def get_aliases() -> dict:
    """Retourne le dict d'aliases : {'Apple': 'AAPL', ...}"""
    cfg = get_config()
    aliases = cfg.get("ticker_aliases", {})
    if aliases:
        return aliases
    return _ALIASES_FALLBACK


def get_killzone() -> dict:
    """Retourne les paramètres de la killzone."""
    cfg = get_config()
    return cfg.get("killzone", {
        "start": "14:30",
        "end": "16:30",
        "timezone": "CET",
        "scan_interval_minutes": 5,
        "news_interval_minutes": 15,
    })


def get_alert_thresholds() -> dict:
    """Retourne les seuils d'alertes."""
    cfg = get_config()
    return cfg.get("alerts", {
        "volume_breakout_multiplier": 2.0,
        "sma200_proximity_pct": 1.5,
        "strong_move_pct": 3.0,
        "breaking_news_window_minutes": 30,
    })


def get_scoring_weights() -> dict:
    """Retourne les poids du scoring."""
    cfg = get_config()
    return cfg.get("scoring", {
        "sma200_weight": 25,
        "volume_weight": 25,
        "reddit_weight": 25,
        "news_weight": 25,
    })


def get_trading_rules() -> dict:
    """Retourne les règles de trading."""
    cfg = get_config()
    return cfg.get("trading", {
        "risk_pct_min": 0.5,
        "risk_pct_max": 1.0,
        "rr_minimum": 2.5,
        "max_trades_per_day": 2,
        "max_exposure_pct": 3.0,
    })


def get_dashboard_config() -> dict:
    """Retourne la configuration du dashboard."""
    cfg = get_config()
    return cfg.get("dashboard", {
        "port": 8000,
        "auto_refresh_seconds": 300,
        "telegram_enabled": False,
    })
