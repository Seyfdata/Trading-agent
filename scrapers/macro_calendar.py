"""
Module calendrier macro.
Détecte les événements économiques importants et ajuste les recommandations.

Ce module fonctionne de deux façons :
1. Détection automatique basée sur les patterns récurrents (jour de la semaine, semaine du mois)
2. Scraping du calendrier Investing.com (via RSS) pour les événements spécifiques

Pour l'instant on utilise la méthode 1 (zéro dépendance externe).
"""

from datetime import datetime, timedelta
from config.settings import MACRO_EVENTS, MAG7_EARNINGS, EMOJI_CALENDAR, EMOJI_NO, EMOJI_WARNING, EMOJI_CHECK


def get_today_info():
    """Retourne les infos de base sur aujourd'hui."""
    now = datetime.now()
    return {
        "date": now.strftime("%d/%m/%Y"),
        "day_name": now.strftime("%A"),
        "day_of_week": now.weekday(),       # 0=lundi, 4=vendredi
        "day_of_month": now.day,
        "week_of_month": (now.day - 1) // 7 + 1,  # 1ère, 2ème, 3ème, 4ème semaine
        "month": now.month,
        "is_first_friday": now.weekday() == 4 and now.day <= 7,
        "is_first_business_day": now.weekday() == 0 and now.day <= 3,
    }


def detect_recurring_events(today=None):
    """
    Détecte les événements macro récurrents basés sur la date.
    Retourne une liste d'événements potentiels pour aujourd'hui.
    """
    if today is None:
        today = get_today_info()

    events = []

    # NFP : premier vendredi du mois
    if today["is_first_friday"]:
        events.append({
            "name": "NFP (Non-Farm Payrolls)",
            "impact": "FORT",
            "heure": "14:30 CET",
            "regle": MACRO_EVENTS["NFP (Non-Farm Payrolls)"]["regle"],
        })

    # Jobless Claims : chaque jeudi
    if today["day_of_week"] == 3:  # Jeudi
        events.append({
            "name": "Jobless Claims",
            "impact": "MOYEN",
            "heure": "14:30 CET",
            "regle": MACRO_EVENTS["Jobless Claims"]["regle"],
        })

    # CPI : généralement 2ème ou 3ème semaine, mardi ou mercredi
    if today["week_of_month"] in [2, 3] and today["day_of_week"] in [1, 2]:
        events.append({
            "name": "CPI (potentiel)",
            "impact": "FORT",
            "heure": "14:30 CET",
            "regle": "Vérifier sur ForexFactory si c'est bien aujourd'hui !",
        })

    # ISM Manufacturing : premier jour ouvré du mois
    if today["is_first_business_day"]:
        events.append({
            "name": "ISM Manufacturing",
            "impact": "MOYEN",
            "heure": "16:00 CET",
            "regle": MACRO_EVENTS["ISM Manufacturing"]["regle"],
        })

    # PCE : dernière semaine du mois, vendredi
    if today["day_of_month"] >= 25 and today["day_of_week"] == 4:
        events.append({
            "name": "PCE (potentiel)",
            "impact": "MOYEN-FORT",
            "heure": "14:30 CET",
            "regle": "Vérifier sur ForexFactory si c'est bien aujourd'hui !",
        })

    # GDP : fin de mois, souvent jeudi
    if today["day_of_month"] >= 25 and today["day_of_week"] == 3:
        if today["month"] in [1, 4, 7, 10]:  # Mois de publication trimestrielle
            events.append({
                "name": "GDP (potentiel)",
                "impact": "MOYEN-FORT",
                "heure": "14:30 CET",
                "regle": "Vérifier sur ForexFactory.",
            })

    return events


def check_earnings_today():
    """
    Vérifie si un de tes Mag7 publie ses earnings aujourd'hui.
    Retourne la liste des tickers en earnings.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    earnings_today = []

    for ticker, data in MAG7_EARNINGS.items():
        for quarter, date in data.items():
            if quarter == "note":
                continue
            if date == today_str:
                earnings_today.append(ticker)

    return earnings_today


def get_trading_recommendation(events, earnings):
    """
    Génère une recommandation de trading basée sur les événements du jour.
    """
    has_high_impact = any(e["impact"] == "FORT" for e in events)
    has_earnings = len(earnings) > 0
    has_medium_impact = any("MOYEN" in e["impact"] for e in events)

    if has_high_impact or has_earnings:
        return {
            "verdict": "NO TRADE",
            "emoji": EMOJI_NO,
            "raison": "Événement FORT aujourd'hui" if has_high_impact else f"Earnings {', '.join(earnings)}",
            "risque": "0%",
        }
    elif has_medium_impact:
        return {
            "verdict": "PRUDENCE",
            "emoji": EMOJI_WARNING,
            "raison": "Événement MOYEN — risque réduit",
            "risque": "0.5% max",
        }
    else:
        return {
            "verdict": "GO",
            "emoji": EMOJI_CHECK,
            "raison": "Pas d'événement majeur détecté",
            "risque": "1% normal",
        }


def format_macro_section():
    """
    Génère la section macro complète pour le morning scan.
    Retourne un string formaté pour Telegram.
    """
    today = get_today_info()
    events = detect_recurring_events(today)
    earnings = check_earnings_today()
    reco = get_trading_recommendation(events, earnings)

    lines = [
        f"{EMOJI_CALENDAR} *MACRO DU JOUR* — {today['date']}",
        "",
    ]

    # Événements détectés
    if events:
        for event in events:
            impact_emoji = EMOJI_NO if event["impact"] == "FORT" else EMOJI_WARNING
            lines.append(f"{impact_emoji} *{event['name']}*")
            lines.append(f"  Impact : {event['impact']} | {event['heure']}")
            lines.append(f"  Règle : {event['regle']}")
            lines.append("")
    else:
        lines.append("Aucun événement macro récurrent détecté.")
        lines.append("")

    # Earnings
    if earnings:
        lines.append(f"{EMOJI_NO} *EARNINGS AUJOURD'HUI* : {', '.join(earnings)}")
        lines.append("  Règle : NE PAS trader ces actions aujourd'hui.")
        lines.append("")

    # Recommandation
    lines.append(f"{reco['emoji']} *VERDICT : {reco['verdict']}*")
    lines.append(f"  {reco['raison']}")
    lines.append(f"  Risque autorisé : {reco['risque']}")

    # Rappel ForexFactory
    lines.append("")
    lines.append("  Toujours vérifier ForexFactory.com pour confirmer !")

    return "\n".join(lines)


# === TEST ===
if __name__ == "__main__":
    print("=== TEST CALENDRIER MACRO ===\n")
    print(format_macro_section())
