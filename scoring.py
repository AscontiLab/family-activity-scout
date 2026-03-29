"""Scoring-Engine: Berechnet personalisierte Relevanz-Scores fuer Aktivitaeten."""

import json
import math
from datetime import date, datetime, timezone, timedelta

from config import (
    HOME_LAT, HOME_LON, CHILDREN_AGE,
    SCORE_BASE, SCORE_WEATHER_INDOOR_BONUS, SCORE_DONE_PENALTY,
    SCORE_SPECIAL_BONUS, SCORE_FRESHNESS_BONUS,
    SCORE_DISTANCE_PENALTY_PER_5KM, SCORE_EXPIRY_URGENCY_BONUS,
)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Entfernung in km zwischen zwei Koordinaten (Haversine)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_scores(
    activities: list[dict],
    preferences: dict[str, float],
    weather: dict | None = None,
    done_ids: set[int] | None = None,
) -> list[dict]:
    """
    Berechnet Scores fuer alle Aktivitaeten und sortiert absteigend.

    Jede Aktivitaet bekommt ein zusaetzliches Feld 'score'.
    """
    if done_ids is None:
        done_ids = set()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    is_rainy = False
    is_cold = False
    is_hot = False
    if weather:
        is_rainy = weather.get("rain_prob", 0) > 60
        is_cold = weather.get("temp", 15) < 5
        is_hot = weather.get("temp", 15) > 25

    scored = []
    for act in activities:
        # Qualitaetsfilter: Generische Eintraege, Blogposts, Linklisten raus
        title = act.get("title", "")
        title_lower = title.lower()
        if len(title) < 5:
            continue
        # Datums-Eintraege
        if any(title.startswith(d) for d in ["Sonntag ", "Samstag ", "Montag ", "Dienstag ", "Mittwoch ", "Donnerstag ", "Freitag "]):
            continue
        # Generische Listikel / Blogposts (keine echten Events)
        skip_patterns = [
            "top-adressen", "die besten", "die 10 ", "die 5 ", "tipps für",
            "tipps fürs", "tipps im ", "kostenlos in", "mehr", "alle ",
            "newsletter", "gewinnspiel", "mini-tipps",
        ]
        if any(p in title_lower for p in skip_patterns):
            continue

        # Altersfilter
        age_min = act.get("age_min", 0) or 0
        age_max = act.get("age_max", 99) or 99
        if not (age_min <= CHILDREN_AGE <= age_max):
            continue

        score = SCORE_BASE
        tags = act.get("tags", [])
        if isinstance(tags, str):
            tags = json.loads(tags)

        # 1. Tag-Weight-Matching
        for tag in tags:
            weight = preferences.get(tag, 1.0)
            score += weight * 5.0

        # 2. Weather Bonus
        if is_rainy or is_cold:
            if "indoor" in tags:
                score += SCORE_WEATHER_INDOOR_BONUS
            elif "outdoor" in tags:
                score -= 10.0
        if is_hot and "wasser" in tags:
            score += 15.0

        # 3. Done: Leicht runterstufen, nicht ausblenden
        if act["id"] in done_ids:
            score += SCORE_DONE_PENALTY  # -8 statt -50

        # 4. Event vs. Permanent: Einmalige Events bevorzugen
        if act.get("is_permanent"):
            score -= 25.0  # Dauerhafte runterstufen — kann man jederzeit machen
        else:
            score += 20.0  # Zeitlich begrenzte Events hochstufen

        if act.get("is_special") and not act.get("is_permanent"):
            score += SCORE_SPECIAL_BONUS  # Nur nicht-permanente Specials boosten

        # 5. Freshness Bonus (neu gescrapt in den letzten 3 Tagen)
        scraped = act.get("scraped_at", "")
        if scraped:
            try:
                scraped_dt = datetime.fromisoformat(scraped)
                if (now - scraped_dt) < timedelta(days=3):
                    score += SCORE_FRESHNESS_BONUS
            except (ValueError, TypeError):
                pass

        # 6. Distance Penalty
        if act.get("lat") and act.get("lon"):
            dist_km = _haversine_km(HOME_LAT, HOME_LON, act["lat"], act["lon"])
            score += (dist_km / 5.0) * SCORE_DISTANCE_PENALTY_PER_5KM
            act["distance_km"] = round(dist_km, 1)
        else:
            act["distance_km"] = None

        # 7. Expiry Urgency — Event endet in < 3 Tagen
        date_end = act.get("date_end")
        if date_end:
            try:
                end_dt = datetime.fromisoformat(date_end)
                days_left = (end_dt - now).days
                if 0 <= days_left <= 3:
                    score += SCORE_EXPIRY_URGENCY_BONUS
            except (ValueError, TypeError):
                pass

        act["score"] = round(score, 1)
        scored.append(act)

    scored.sort(key=lambda a: a["score"], reverse=True)
    return scored


def get_weekend_mix(scored_activities: list[dict], count: int = 10) -> list[dict]:
    """
    Waehlt einen diversen Mix aus Vorschlaegen.
    Max 2 pro Kategorie (Theater, Museum, etc.) fuer Vielfalt.
    Prioritaet: Events > Tagesausflug > Dauerhafte.
    """
    MAX_PER_CATEGORY = 2

    events = [a for a in scored_activities if not a.get("is_permanent")]
    day_trips = [a for a in scored_activities
                 if a.get("is_permanent") and (a.get("distance_km") or 0) > 30]
    permanent = [a for a in scored_activities if a.get("is_permanent")]

    mix: list[dict] = []
    seen_ids: set[int] = set()
    category_counts: dict[str, int] = {}  # Diversity-Zaehler

    def _primary_category(item: dict) -> str:
        """Bestimmt die Hauptkategorie einer Aktivitaet."""
        tags = item.get("tags", [])
        title = (item.get("title", "") + " " + (item.get("description", "") or "")).lower()
        source = item.get("source", "")

        # berlin.de/tickets/kinder liefert fast nur Auffuehrungen
        if source == "berlin_de" and set(tags) <= {"indoor", "kultur"}:
            return "auffuehrung"

        # Spezifische Erkennung
        theater_words = [
            "theater", "puppentheater", "maerchen", "märchen", "aufführung",
            "musical", "clown", "zirkus", "galli", "bühne",
            # Bekannte Maerchen-Titel
            "rumpelstilzchen", "aschenputtel", "schneewittchen",
            "rotkäppchen", "hänsel", "hans im glück", "gestiefelte kater",
            "bremer stadtmusikanten", "dornröschen", "froschkönig", "frog prince",
        ]
        if any(w in title for w in theater_words):
            return "auffuehrung"
        if any(w in title for w in ["museum", "ausstellung"]):
            return "museum"
        if any(w in title for w in ["klettern", "hochseil", "kletterpark", "bouldern"]):
            return "klettern"
        if any(w in title for w in ["zoo", "tierpark", "bauernhof", "tiere"]):
            return "tiere"
        if "kreativ" in tags:
            return "kreativ"
        if "abenteuer" in tags:
            return "abenteuer"
        if "outdoor" in tags:
            return "outdoor"
        if "sport" in tags:
            return "sport"
        if "natur" in tags:
            return "natur"
        if "wasser" in tags:
            return "wasser"
        return tags[0] if tags else "sonstiges"

    def _try_add(item: dict) -> bool:
        if item["id"] in seen_ids:
            return False
        cat = _primary_category(item)
        if category_counts.get(cat, 0) >= MAX_PER_CATEGORY:
            return False
        mix.append(item)
        seen_ids.add(item["id"])
        category_counts[cat] = category_counts.get(cat, 0) + 1
        return True

    # 1. Diverse Events zuerst
    for item in events:
        if len(mix) >= count - 2:
            break
        _try_add(item)

    # 2. Ein Brandenburg-Tagesausflug
    for item in day_trips:
        if len(mix) >= count - 1:
            break
        if item["id"] not in seen_ids:
            mix.append(item)
            seen_ids.add(item["id"])
            break

    # 3. Auffuellen mit Dauerhaften (andere Kategorien bevorzugt)
    for item in permanent:
        if len(mix) >= count:
            break
        _try_add(item)

    # 4. Falls immer noch nicht voll: Diversity-Limit lockern
    if len(mix) < count:
        for item in scored_activities:
            if len(mix) >= count:
                break
            if item["id"] not in seen_ids:
                mix.append(item)
                seen_ids.add(item["id"])

    return mix[:count]


def get_upcoming_weekend_dates(reference: datetime | None = None) -> tuple[date, date]:
    """Liefert Samstag und Sonntag fuer das aktuelle oder naechste Wochenende."""
    if reference is None:
        reference = datetime.now(timezone.utc)
    today = reference.date()
    weekday = today.weekday()
    if weekday == 5:
        saturday = today
    elif weekday == 6:
        saturday = today - timedelta(days=1)
    else:
        saturday = today + timedelta(days=5 - weekday)
    return saturday, saturday + timedelta(days=1)


def is_activity_available_on_day(activity: dict, target_day: date) -> bool:
    """Prueft, ob eine Aktivitaet am Zieldatum sinnvoll verfuegbar ist."""
    if activity.get("is_permanent"):
        return target_day.weekday() in (5, 6)

    date_start = (activity.get("date_start") or "")[:10]
    date_end = (activity.get("date_end") or date_start)[:10]
    target_str = target_day.isoformat()

    if date_start:
        return date_start <= target_str <= date_end

    scraped_at = activity.get("scraped_at")
    if not scraped_at:
        return False
    try:
        scraped_dt = datetime.fromisoformat(scraped_at)
    except (TypeError, ValueError):
        return False
    return (datetime.now(timezone.utc) - scraped_dt) <= timedelta(days=14)


def build_weekend_plan(scored_activities: list[dict], weather: dict | None = None) -> list[dict]:
    """Baut einen konkreten Samstag/Sonntag-Plan mit Backup-Idee."""
    saturday, sunday = get_upcoming_weekend_dates()
    weekend_days = [
        {"key": "saturday", "label": "Samstag", "date": saturday},
        {"key": "sunday", "label": "Sonntag", "date": sunday},
    ]
    rainy_weekend = bool(weather and (weather.get("rain_prob", 0) > 60 or weather.get("temp", 15) < 5))
    plan: list[dict] = []
    used_ids: set[int] = set()

    for day in weekend_days:
        available = [
            activity for activity in scored_activities
            if activity["id"] not in used_ids and is_activity_available_on_day(activity, day["date"])
        ]
        if not available:
            continue

        primary = available[0]
        used_ids.add(primary["id"])

        backup = None
        preferred_tag = "indoor" if rainy_weekend else "outdoor"
        for candidate in available[1:]:
            if preferred_tag in candidate.get("tags", []):
                backup = candidate
                break
        if backup is None and len(available) > 1:
            backup = available[1]

        plan.append({
            "key": day["key"],
            "label": day["label"],
            "date_iso": day["date"].isoformat(),
            "date_display": day["date"].strftime("%d.%m."),
            "primary": primary,
            "backup": backup,
            "weather_hint": "Regenfester Backup" if rainy_weekend and backup else ("Outdoor-Backup" if backup else None),
        })

    return plan
