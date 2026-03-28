"""Konfiguration fuer den Family Activity Scout."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "activities.db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
PORT = 8092
HOST = "0.0.0.0"

# ---------------------------------------------------------------------------
# Credentials aus ~/.stock_scanner_credentials laden
# ---------------------------------------------------------------------------
CREDENTIALS_FILE = Path.home() / ".stock_scanner_credentials"


def load_credentials() -> dict[str, str]:
    """Liest KEY=VALUE Paare aus der Credentials-Datei."""
    creds: dict[str, str] = {}
    if CREDENTIALS_FILE.exists():
        for line in CREDENTIALS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                creds[key.strip()] = value.strip()
    return creds


_creds = load_credentials()

# Primaer: AscontiLab Bot, Fallback: alter TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_TOKEN = _creds.get("ASCONTILAB_BOT_TOKEN", "") or _creds.get("TELEGRAM_BOT_TOKEN", "")
# FAMILY_CHAT_ID = Maik's Chat-ID (identisch mit ASCONTILAB_CHAT_ID)
FAMILY_CHAT_ID = _creds.get("ASCONTILAB_CHAT_ID", "") or _creds.get("FAMILY_CHAT_ID", "")
OPENWEATHER_API_KEY = _creds.get("OPENWEATHER_API_KEY", "")

# ---------------------------------------------------------------------------
# Standort (Berlin Mitte als Default)
# ---------------------------------------------------------------------------
HOME_LAT = 52.5200
HOME_LON = 13.4050

# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------
ALL_TAGS = [
    "outdoor", "indoor", "kreativ", "abenteuer", "sport", "kultur",
    "natur", "tiere", "essen", "wasser", "wissenschaft", "musik",
    "theater", "handwerk", "spiel", "kostenlos",
]

# ---------------------------------------------------------------------------
# Scoring-Konstanten
# ---------------------------------------------------------------------------
SCORE_BASE = 50.0
SCORE_WEATHER_INDOOR_BONUS = 20.0
SCORE_DONE_PENALTY = -8.0  # Leicht runterstufen, nicht ausblenden — man geht gern nochmal hin
SCORE_SPECIAL_BONUS = 15.0
SCORE_FRESHNESS_BONUS = 10.0         # fuer Eintraege < 3 Tage alt
SCORE_DISTANCE_PENALTY_PER_5KM = -1.0
SCORE_EXPIRY_URGENCY_BONUS = 20.0    # Event endet in < 3 Tagen
SCORE_LIKE_WEIGHT_DELTA = 0.15
SCORE_DISLIKE_WEIGHT_DELTA = -0.10
SCORE_WEIGHT_FLOOR = 0.1
SCORE_WEIGHT_CEILING = 3.0

# ---------------------------------------------------------------------------
# Altersfilter
# ---------------------------------------------------------------------------
CHILDREN_AGE = 9  # wird im Juli 2026 auf 10 aktualisiert

# ---------------------------------------------------------------------------
# Wetter-Schwellen
# ---------------------------------------------------------------------------
RAIN_THRESHOLD = 60        # Regenwahrscheinlichkeit in %
COLD_THRESHOLD = 5         # Grad Celsius
HOT_THRESHOLD = 25         # Grad Celsius — Wasser-Aktivitaeten boosten

# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------
SCRAPE_USER_AGENT = (
    "Mozilla/5.0 (compatible; FamilyActivityScout/1.0; +https://github.com/AscontiLab)"
)
SCRAPE_TIMEOUT = 30  # Sekunden
