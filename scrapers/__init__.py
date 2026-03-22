"""Scraper-Registry: Alle Scraper automatisch laden und ausfuehren."""

from scrapers.base import BaseScraper
from scrapers.static_places import StaticPlacesScraper
from scrapers.berlin_de import BerlinDeScraper
from scrapers.berlinmitkind import BerlinMitKindScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    StaticPlacesScraper,
    BerlinDeScraper,
    BerlinMitKindScraper,
]


def run_all_scrapers() -> dict[str, int]:
    """Fuehrt alle Scraper aus und gibt Anzahl neuer/aktualisierter Eintraege zurueck."""
    from models import upsert_activity

    results: dict[str, int] = {}
    for scraper_cls in ALL_SCRAPERS:
        scraper = scraper_cls()
        name = scraper.name
        try:
            items = scraper.scrape()
            count = 0
            for item in items:
                item["source"] = name
                if not item.get("source_id"):
                    item["source_id"] = scraper.deduplicate_key(item)
                upsert_activity(item)
                count += 1
            results[name] = count
            print(f"[Scraper] {name}: {count} Aktivitaeten")
        except Exception as e:
            print(f"[Scraper] {name}: FEHLER — {e}")
            results[name] = -1

    return results
