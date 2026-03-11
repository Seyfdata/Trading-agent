"""
Base de données SQLite — historique des scores et du contexte marché.
Fichier DB : database/trading_agent.db
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "trading_agent.db"


# ── Initialisation ──────────────────────────────────────────────────────────

def init_db(db_path: Path = DB_PATH) -> None:
    """Crée les tables si elles n'existent pas."""
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scores_history (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT NOT NULL,
                ticker        TEXT NOT NULL,
                total_score   INTEGER NOT NULL,
                sma200_score  INTEGER NOT NULL,
                volume_score  INTEGER NOT NULL,
                reddit_score  INTEGER NOT NULL,
                news_score    INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS market_context_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                regime      TEXT NOT NULL,
                score       INTEGER NOT NULL,
                vix         REAL,
                spy_change  REAL,
                dxy         REAL
            );
        """)


# ── Écriture ────────────────────────────────────────────────────────────────

def save_scores(date: str, scores_list: list[dict], db_path: Path = DB_PATH) -> None:
    """
    Sauvegarde les scores de tous les tickers pour une date donnée.

    Paramètres
    ----------
    date        : "YYYY-MM-DD"
    scores_list : liste de dicts retournés par scoring.score_ticker()
    """
    rows = [
        (
            date,
            s["ticker"],
            s["total_score"],
            s["sma200_score"],
            s["volume_score"],
            s["reddit_score"],
            s["news_score"],
        )
        for s in scores_list
    ]
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO scores_history
                (date, ticker, total_score, sma200_score, volume_score, reddit_score, news_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def save_market_context(date: str, context_dict: dict, db_path: Path = DB_PATH) -> None:
    """
    Sauvegarde le contexte marché pour une date donnée.

    Paramètres
    ----------
    date         : "YYYY-MM-DD"
    context_dict : dict retourné par scoring.score_market_context()
    """
    details = context_dict.get("details", {})
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_context_history
                (date, regime, score, vix, spy_change, dxy)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                date,
                context_dict["regime"],
                context_dict["score"],
                details.get("vix"),
                details.get("spy_change"),
                details.get("dxy"),
            ),
        )


# ── Lecture ─────────────────────────────────────────────────────────────────

def get_score_history(ticker: str, days: int = 30, db_path: Path = DB_PATH) -> list[dict]:
    """
    Retourne l'historique des scores d'un ticker sur N jours.

    Retourne une liste de dicts triés du plus récent au plus ancien.
    """
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT date, total_score, sma200_score, volume_score, reddit_score, news_score
            FROM scores_history
            WHERE ticker = ? AND date >= ?
            ORDER BY date DESC
            """,
            (ticker, since),
        ).fetchall()
    return [dict(row) for row in rows]


def get_score_trend(ticker: str, days: int = 7, db_path: Path = DB_PATH) -> dict:
    """
    Retourne la tendance du score sur N jours.

    Retourne un dict avec :
        - trend   : "HAUSSE" / "BAISSE" / "STABLE"
        - delta   : variation du score (dernier - premier)
        - history : liste des (date, total_score)
    """
    history = get_score_history(ticker, days=days, db_path=db_path)

    if len(history) < 2:
        return {"trend": "STABLE", "delta": 0, "history": history}

    # history est trié du plus récent au plus ancien
    latest = history[0]["total_score"]
    oldest = history[-1]["total_score"]
    delta = latest - oldest

    if delta >= 5:
        trend = "HAUSSE"
    elif delta <= -5:
        trend = "BAISSE"
    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "delta": delta,
        "history": [(row["date"], row["total_score"]) for row in history],
    }


# ── Test basique ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    # DB de test temporaire
    test_db = Path(__file__).parent / "test_trading_agent.db"
    if test_db.exists():
        test_db.unlink()

    print("=== Test database/models.py ===\n")

    init_db(test_db)
    print(f"[OK] DB créée : {test_db}")

    # Données de test — J-2
    scores_j2 = [
        {"ticker": "NVDA", "total_score": 62, "sma200_score": 22, "volume_score": 25, "reddit_score": 10, "news_score": 5},
        {"ticker": "AAPL", "total_score": 45, "sma200_score": 13, "volume_score": 5,  "reddit_score": 12, "news_score": 15},
        {"ticker": "PLTR", "total_score": 70, "sma200_score": 5,  "volume_score": 18, "reddit_score": 25, "news_score": 22},
    ]
    save_scores("2026-03-07", scores_j2, test_db)

    # Données de test — J-1
    scores_j1 = [
        {"ticker": "NVDA", "total_score": 68, "sma200_score": 22, "volume_score": 25, "reddit_score": 15, "news_score": 6},
        {"ticker": "AAPL", "total_score": 42, "sma200_score": 13, "volume_score": 5,  "reddit_score": 9,  "news_score": 15},
        {"ticker": "PLTR", "total_score": 65, "sma200_score": 5,  "volume_score": 18, "reddit_score": 20, "news_score": 22},
    ]
    save_scores("2026-03-08", scores_j1, test_db)

    # Données de test — aujourd'hui
    scores_today = [
        {"ticker": "NVDA", "total_score": 75, "sma200_score": 25, "volume_score": 25, "reddit_score": 15, "news_score": 10},
        {"ticker": "AAPL", "total_score": 38, "sma200_score": 13, "volume_score": 5,  "reddit_score": 5,  "news_score": 15},
        {"ticker": "PLTR", "total_score": 58, "sma200_score": 5,  "volume_score": 10, "reddit_score": 20, "news_score": 23},
    ]
    save_scores("2026-03-09", scores_today, test_db)
    print("[OK] Scores insérés (3 jours × 3 tickers)")

    context = {
        "regime": "NEUTRAL",
        "score": 52,
        "details": {"vix": 18.5, "spy_change": 0.3, "dxy": 103.2},
    }
    save_market_context("2026-03-09", context, test_db)
    print("[OK] Contexte marché inséré")

    # Lecture
    history = get_score_history("NVDA", days=30, db_path=test_db)
    print(f"\nHistorique NVDA ({len(history)} entrées) :")
    for row in history:
        print(f"  {row['date']} → score {row['total_score']}")

    trend = get_score_trend("NVDA", days=7, db_path=test_db)
    print(f"\nTendance NVDA : {trend['trend']} (delta={trend['delta']:+d})")

    trend_aapl = get_score_trend("AAPL", days=7, db_path=test_db)
    print(f"Tendance AAPL : {trend_aapl['trend']} (delta={trend_aapl['delta']:+d})")

    # Nettoyage
    test_db.unlink()
    print("\n[OK] models.py fonctionne correctement.")
