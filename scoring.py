"""Scoring-Engine: Berechnet personalisierte Relevanz-Scores fuer Aktivitaeten."""

import json
import math
from datetime import datetime, timezone, timedelta

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

        # 3. Done Penalty
        if act["id"] in done_ids:
            score += SCORE_DONE_PENALTY

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
    Waehlt einen Mix aus Vorschlaegen:
    Prioritaet: Zeitlich begrenzte Events > Geheimtipps > 1 Tagesausflug > Dauerhafte als Auffueller.
    """
    events = [a for a in scored_activities if not a.get("is_permanent")]
    day_trips = [a for a in scored_activities
                 if a.get("is_permanent") and (a.get("distance_km") or 0) > 30]
    permanent = [a for a in scored_activities if a.get("is_permanent")]

    mix: list[dict] = []
    seen_ids: set[int] = set()

    def _add(source: list[dict], n: int):
        for item in source:
            if len(mix) >= count or n <= 0:
                return
            if item["id"] not in seen_ids:
                mix.append(item)
                seen_ids.add(item["id"])
                n -= 1

    # 1. Einmalige Events zuerst (so viele wie moeglich)
    _add(events, max(count - 2, 3))
    # 2. Ein Brandenburg-Tagesausflug
    _add(day_trips, 1)
    # 3. Auffuellen mit Dauerhaften
    _add(permanent, count - len(mix))

    return mix[:count]
