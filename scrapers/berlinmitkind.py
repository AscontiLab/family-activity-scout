"""Scraper fuer berlinmitkind.de — Familien-Events und Tipps."""

import httpx
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from config import SCRAPE_USER_AGENT, SCRAPE_TIMEOUT


class BerlinMitKindScraper(BaseScraper):
    """Scrapt Familien-Events von berlinmitkind.de."""

    name = "berlinmitkind"
    BASE_URL = "https://berlinmitkind.de/veranstaltungen/"

    def scrape(self) -> list[dict]:
        items = []
        try:
            resp = httpx.get(
                self.BASE_URL,
                headers={"User-Agent": SCRAPE_USER_AGENT},
                timeout=SCRAPE_TIMEOUT,
                follow_redirects=True,
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"[berlinmitkind] Fehler beim Laden: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select("article, .event-card, .post, .entry, .tribe-events-single"):
            title_el = card.select_one("h2, h3, .tribe-events-list-event-title, .entry-title")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            link_el = card.select_one("a[href]")
            link = link_el.get("href", "") if link_el else ""

            desc_el = card.select_one(".tribe-events-list-event-description, .entry-content, p")
            desc = desc_el.get_text(strip=True)[:300] if desc_el else ""

            venue_el = card.select_one(".tribe-venue, .venue, .location")
            venue = venue_el.get_text(strip=True) if venue_el else ""

            date_el = card.select_one("time, .tribe-event-schedule-details, .date")
            date_text = ""
            date_start = None
            if date_el:
                date_text = date_el.get_text(strip=True)
                date_start = date_el.get("datetime")

            # Tag-Heuristik basierend auf Titel/Beschreibung
            tags = _infer_tags(title + " " + desc)

            items.append({
                "source_id": self.deduplicate_key({"title": title, "location_name": venue, "date_start": date_start}),
                "title": title,
                "description": desc,
                "source_url": link,
                "location_name": venue,
                "date_start": date_start,
                "time_info": date_text,
                "tags": tags,
                "age_min": 3,
                "age_max": 14,
                "is_special": 0,
            })

        return items


def _infer_tags(text: str) -> list[str]:
    """Leitet Tags aus Titel/Beschreibung ab."""
    text_lower = text.lower()
    tags = []
    mapping = {
        "outdoor": ["draussen", "park", "wald", "garten", "spielplatz", "wandern"],
        "indoor": ["museum", "theater", "kino", "halle", "werkstatt"],
        "kreativ": ["basteln", "malen", "kreativ", "kunst", "workshop"],
        "abenteuer": ["klettern", "escape", "schatzsuche", "abenteuer", "entdecken"],
        "sport": ["sport", "schwimmen", "radtour", "turnen", "tanzen"],
        "kultur": ["museum", "ausstellung", "theater", "lesung", "fuehrung"],
        "natur": ["natur", "wald", "tiere", "garten", "bio"],
        "tiere": ["tiere", "zoo", "bauernhof", "pferde", "streichel"],
        "essen": ["kochen", "backen", "essen", "kulinarisch"],
        "wasser": ["schwimmen", "see", "pool", "wasser", "boot", "kanu"],
        "wissenschaft": ["experiment", "forschung", "labor", "wissenschaft"],
        "musik": ["musik", "konzert", "band", "singen"],
        "theater": ["theater", "puppentheater", "clown", "zirkus"],
        "handwerk": ["handwerk", "toepfern", "schmieden", "naehen", "holz"],
        "spiel": ["spielen", "spiel", "brettspiel", "spielplatz"],
        "kostenlos": ["kostenlos", "eintritt frei", "gratis"],
    }
    for tag, keywords in mapping.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags or ["indoor", "kultur"]
