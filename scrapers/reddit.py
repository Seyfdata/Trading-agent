"""
Module Reddit — Scraping r/wallstreetbets et r/stocks.
Détecte les actions en buzz et le sentiment retail.

Prérequis :
  pip install praw

Configuration :
  1. Va sur https://www.reddit.com/prefs/apps/
  2. Clique "create another app..." en bas
  3. Nom : trading-agent
  4. Type : "script"
  5. Redirect URI : http://localhost:8080
  6. Clique "create app"
  7. Copie le client_id (sous le nom de l'app) et le secret
  8. Mets-les dans ton .env :
     REDDIT_CLIENT_ID=ton_client_id
     REDDIT_CLIENT_SECRET=ton_client_secret
"""

import os
import re
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# Import conditionnel de praw (pas installé par défaut en Phase 2)
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from config.settings import WATCHLIST, TICKER_ALIASES, EMOJI_FIRE, EMOJI_BULL, EMOJI_BEAR


def get_reddit_client():
    """Crée un client Reddit avec PRAW."""
    if not PRAW_AVAILABLE:
        print("  [Reddit] praw non installé. Lance : pip install praw")
        return None

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("  [Reddit] REDDIT_CLIENT_ID ou REDDIT_CLIENT_SECRET manquant dans .env")
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="trading-agent v1.0 by /u/seyf"
        )
        return reddit
    except Exception as e:
        print(f"  [Reddit] Erreur de connexion : {e}")
        return None


def scan_subreddit(reddit, subreddit_name, limit=50):
    """
    Scanne les posts hot d'un subreddit.
    Retourne les posts et le compteur de tickers.
    """
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    ticker_mentions = Counter()

    # Construire le pattern regex pour les tickers
    # Cherche $AAPL ou AAPL en majuscules isolé
    ticker_pattern = r'\$([A-Z]{1,5})\b'
    known_tickers = set(WATCHLIST)

    for post in subreddit.hot(limit=limit):
        text = post.title + " " + (post.selftext or "")

        # Méthode 1 : tickers avec $ (ex: $AAPL)
        found_tickers = set(re.findall(ticker_pattern, text))

        # Méthode 2 : tickers connus en majuscules (ex: AAPL, NVDA)
        for ticker in known_tickers:
            if re.search(r'\b' + ticker + r'\b', text):
                found_tickers.add(ticker)

        # Méthode 3 : noms d'entreprises (ex: "Nvidia", "Broadcom")
        for alias, ticker in TICKER_ALIASES.items():
            if alias.lower() in text.lower():
                found_tickers.add(ticker)

        for t in found_tickers:
            ticker_mentions[t] += 1

        if found_tickers:
            posts.append({
                "title": post.title[:120],
                "tickers": sorted(found_tickers),
                "score": post.score,
                "comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "subreddit": subreddit_name,
            })

    return posts, ticker_mentions


def scan_all_subreddits(limit_per_sub=50):
    """
    Scanne r/wallstreetbets et r/stocks.
    Retourne les résultats combinés.
    """
    reddit = get_reddit_client()
    if reddit is None:
        return None

    subreddits = ["wallstreetbets", "stocks"]
    all_posts = []
    total_mentions = Counter()

    for sub in subreddits:
        try:
            print(f"  [Reddit] Scan r/{sub}...")
            posts, mentions = scan_subreddit(reddit, sub, limit=limit_per_sub)
            all_posts.extend(posts)
            total_mentions.update(mentions)
            print(f"  [Reddit] r/{sub} : {len(posts)} posts avec tickers")
        except Exception as e:
            print(f"  [Reddit] Erreur r/{sub} : {e}")

    return {
        "posts": all_posts,
        "top_tickers": total_mentions.most_common(10),
        "total_posts_with_tickers": len(all_posts),
    }


def detect_buzz(threshold=3):
    """
    Détecte les actions en buzz (mentionnées >= threshold fois).
    """
    result = scan_all_subreddits()
    if result is None:
        return None

    buzz = [
        {"ticker": ticker, "mentions": count}
        for ticker, count in result["top_tickers"]
        if count >= threshold
    ]

    return {
        "buzz_stocks": buzz,
        "all_mentions": result["top_tickers"],
        "total_posts": result["total_posts_with_tickers"],
    }


def format_reddit_section():
    """
    Génère la section Reddit pour le morning scan.
    Retourne un string formaté ou None si Reddit non configuré.
    """
    result = detect_buzz(threshold=2)

    if result is None:
        return None  # Reddit non configuré, on skip

    lines = [
        f"{EMOJI_FIRE} *REDDIT BUZZ* (r/wallstreetbets + r/stocks)",
        f"Posts analysés avec tickers : {result['total_posts']}",
        "",
    ]

    if result["buzz_stocks"]:
        for stock in result["buzz_stocks"][:5]:
            ticker = stock["ticker"]
            mentions = stock["mentions"]
            # Emoji selon si c'est dans notre watchlist
            emoji = EMOJI_BULL if ticker in WATCHLIST else "👀"
            lines.append(f"{emoji} *{ticker}* — {mentions} mentions")
    else:
        lines.append("Pas de buzz significatif sur tes tickers.")

    # Top mentions globales (même hors watchlist)
    if result["all_mentions"]:
        all_tickers = [f"{t}({c})" for t, c in result["all_mentions"][:5]]
        lines.append("")
        lines.append(f"Top 5 global : {', '.join(all_tickers)}")

    return "\n".join(lines)


# === TEST ===
if __name__ == "__main__":
    print("=== TEST REDDIT SCANNER ===\n")

    if not PRAW_AVAILABLE:
        print("praw non installé.")
        print("Pour installer : pip install praw")
        print("Puis configure REDDIT_CLIENT_ID et REDDIT_CLIENT_SECRET dans .env")
    else:
        section = format_reddit_section()
        if section:
            print(section)
        else:
            print("Reddit non configuré. Vérifie ton .env")
