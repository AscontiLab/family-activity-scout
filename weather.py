"""OpenWeatherMap Integration fuer Wetter-basierte Vorschlaege."""

import time
import httpx

from config import OPENWEATHER_API_KEY, HOME_LAT, HOME_LON

_cache: dict = {}
_cache_ttl = 3600  # 1 Stunde


def get_forecast() -> dict:
    """
    Gibt aktuelles Wetter + Vorhersage zurueck.

    Returns:
        {
            "temp": float,          # aktuelle Temperatur in Celsius
            "rain_prob": float,     # Regenwahrscheinlichkeit 0-100
            "description": str,     # z.B. "Bewölkt"
            "icon": str,            # OpenWeather Icon Code
        }
    """
    now = time.time()
    if _cache.get("data") and now - _cache.get("fetched_at", 0) < _cache_ttl:
        return _cache["data"]

    if not OPENWEATHER_API_KEY:
        return {"temp": 15.0, "rain_prob": 0, "description": "Kein API-Key", "icon": "01d"}

    try:
        resp = httpx.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": HOME_LAT,
                "lon": HOME_LON,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "de",
                "cnt": 8,  # naechste 24h (3h-Intervalle)
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        entries = data.get("list", [])
        if not entries:
            return {"temp": 15.0, "rain_prob": 0, "description": "Keine Daten", "icon": "01d"}

        current = entries[0]
        temp = current.get("main", {}).get("temp", 15.0)
        rain_prob = max(e.get("pop", 0) for e in entries) * 100
        desc = current.get("weather", [{}])[0].get("description", "")
        icon = current.get("weather", [{}])[0].get("icon", "01d")

        result = {
            "temp": round(temp, 1),
            "rain_prob": round(rain_prob),
            "description": desc.capitalize(),
            "icon": icon,
        }

        _cache["data"] = result
        _cache["fetched_at"] = now
        return result

    except Exception as e:
        print(f"[Wetter] Fehler: {e}")
        return {"temp": 15.0, "rain_prob": 0, "description": "Fehler", "icon": "01d"}
