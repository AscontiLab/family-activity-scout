# Family Activity Scout

Personalisierter Familien-Ausflugs-Planer fuer Berlin + Brandenburg.

Schlaegt Veranstaltungen, Ausfluege und Aktivitaeten vor — lernt aus Feedback, priorisiert einmalige Events und sorgt fuer Vielfalt statt 10x Theater.

## Features

- **81 Aktivitaeten** — 33 kuratierte Attraktionen + gescrapte Events von berlin.de und berlinmitkind.de
- **Lernfaehig** — Thumbs up/down passt Tag-Gewichtungen an (outdoor, kreativ, abenteuer, etc.)
- **Diversity-Filter** — Max 2 pro Kategorie (Auffuehrung, Museum, Klettern, ...) fuer abwechslungsreiche Vorschlaege
- **Events zuerst** — Zeitlich begrenzte Veranstaltungen werden gegenueber Dauerbrennern bevorzugt
- **Wetter-Check** — Bei Regen Indoor-Vorschlaege, bei Hitze Wasser-Aktivitaeten
- **"Schon gemacht"-Tracker** — Besuchte Orte werden leicht runtergestuft, nicht versteckt (man faehrt gern nochmal zu Karls)
- **Auto-Ablauf** — Events ohne Enddatum verschwinden nach 14 Tagen, Permanente bleiben
- **Leaflet-Karte** — Alle Vorschlaege auf einer interaktiven Karte
- **Kalender** — 14-Tage-Vorschau mit Filtern
- **Dark+Gold Design** — Einheitliches Design wie alle AscontiLab-Dashboards

## Bestandteile

- `app.py` — FastAPI-App, Routen, Templates
- `models.py` — SQLAlchemy-Modelle, DB-Init
- `scoring.py` — Scoring-Algorithmus, Diversity-Filter
- `config.py` — Konfiguration, API-Keys (Credentials via `scanner-common`-Paket)
- `weather.py` — OpenWeatherMap-Integration
- `telegram_alerts.py` — Telegram-Bot-Benachrichtigungen
- `run_scraper.sh` — Scraper-Wrapper

## Tech-Stack

| Komponente | Technologie |
|---|---|
| Backend | Python 3.12, FastAPI |
| Datenbank | SQLite |
| Frontend | Jinja2, Leaflet.js |
| Wetter | OpenWeatherMap API |
| Alerts | Telegram Bot API |
| Port | 8092 (Standalone) |

## Kuratierte Attraktionen (Auswahl)

**Klettern & Abenteuer:** MountMitte, Waldhochseilgarten Jungfernheide, BergWerk Indoor-Klettern, Boulderklub, Escape Room fuer Kinder

**Wasser & Natur:** Strandbad Wannsee, Hauptstadtfloss (Floss bauen!), Kanu Mueggelspree, BVG Faehre F10, Spreewald Kahnfahrt

**Tagesausfluege Brandenburg:** Tropical Islands, Filmpark Babelsberg, Biosphaere Potsdam, Karls Erdbeerhof, Irrlandia Storkow, Barfusspark Beelitz, Schiffshebewerk Niederfinow

**Indoor:** MACHmit! Museum, Labyrinth Kindermuseum, FEZ Berlin, JUMP House, Technikmuseum, Naturkundemuseum

## Scraper-Quellen

| Quelle | Typ | Eintraege |
|---|---|---|
| `static_places` | Kuratierte Dauerbrenner | 33 |
| `berlin.de/tickets/kinder` | Offizielle Kinder-Events | ~18 |
| `berlinmitkind.de` | Familien-Veranstaltungen | ~44 |

## Scoring-Algorithmus

```
score = 50 (Basis)
      + Tag-Gewichtung (z.B. outdoor × 5.0)
      + 20 fuer zeitlich begrenzte Events
      - 25 fuer permanente Attraktionen
      + 15 fuer besondere/einmalige Events
      + 10 fuer frisch gescrapte Eintraege
      - 8 fuer "schon gemacht"
      + 20 bei Wetter-Match (indoor bei Regen)
      + 20 wenn Event in < 3 Tagen endet
      - Entfernung (1 Punkt pro 5 km)
```

Diversity-Filter: Max 2 pro Kategorie (Auffuehrung, Museum, Klettern, etc.)

## Setup

```bash
# Abhaengigkeiten (in venv oder mit --break-system-packages)
pip install -r requirements.txt

# API Keys in ~/.stock_scanner_credentials (geladen via scanner-common):
# OPENWEATHER_API_KEY=...
# TELEGRAM_BOT_TOKEN=...
# FAMILY_CHAT_ID=...

# DB initialisieren + Scraper laufen lassen
python3 -c "from models import init_db; init_db()"
bash run_scraper.sh

# Dashboard starten
python3 app.py  # Port 8092
```

## Cron

```cron
# Taeglich Scraper + Cleanup
0 6 * * * cd /home/claude-agent/family-activity-scout && bash run_scraper.sh

# Freitags Telegram-Push (noch nicht konfiguriert)
# 0 16 * * 5 cd /home/claude-agent/family-activity-scout && python3 -c "..."
```

## Unified Dashboard

Eingebunden unter `https://agents.umzwei.de/dashboard/family/` mit Navigation "Family" + "Kalender".

## Roadmap

- [ ] Weitere Scraper: tip-berlin.de, visitberlin.de, kindaling.de
- [ ] Telegram Freitags-Push konfigurieren
- [ ] Geocoding fuer gescrapte Events (Koordinaten aus Adresse)
- [ ] Saisonale Boost-Logik (Freibad im Sommer, Eislaufen im Winter)
- [ ] Familien-Profil: Individuelle Praeferenzen pro Person
