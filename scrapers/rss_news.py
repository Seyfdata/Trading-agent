"""
Module de collecte de news via flux RSS.
Récupère les dernières news financières et filtre par tickers.

Phase 2 : c'est le premier module que tu fais tourner.
"""

import feedparser
from config.settings import RSS_FEEDS, WATCHLIST


def fetch_all_news(max_per_feed=5):
    """
    Récupère les dernières news de tous les flux RSS.
    
    Retourne une liste de dicts :
    [{"source": "Reuters", "title": "...", "link": "...", "summary": "..."}]
    """
    all_news = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:max_per_feed]:
                all_news.append({
                    "source": source_name,
                    "title": entry.get("title", "Sans titre"),
                    "summary": entry.get("summary", "")[:300],
                    "link": entry.get("link", ""),
                })

        except Exception as e:
            print(f"[RSS] Erreur sur {source_name}: {e}")

    return all_news


def filter_by_tickers(news_list, tickers=None):
    """
    Filtre les news qui mentionnent un de tes tickers.
    
    Retourne les news pertinentes avec les tickers trouvés.
    """
    if tickers is None:
        tickers = WATCHLIST

    relevant = []

    for news in news_list:
        # Chercher dans le titre et le résumé
        text = (news["title"] + " " + news["summary"]).upper()

        matched = [t for t in tickers if t in text]

        if matched:
            news["matched_tickers"] = matched
            relevant.append(news)

    return relevant


# === TEST ===
if __name__ == "__main__":
    # Exécute ce fichier seul pour tester : python scrapers/rss_news.py
    print("Récupération des news...")
    news = fetch_all_news(max_per_feed=3)
    print(f"Total : {len(news)} news récupérées\n")

    for n in news[:5]:
        print(f"[{n['source']}] {n['title']}")
        print(f"  {n['link']}\n")

    print("\nFiltrage par tickers...")
    relevant = filter_by_tickers(news)
    print(f"{len(relevant)} news pertinentes\n")

    for n in relevant:
        print(f"[{', '.join(n['matched_tickers'])}] {n['title']}")
