"""Basis-Klasse fuer alle Scraper."""

import hashlib
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Abstrakte Basis-Klasse fuer Event-Scraper."""

    name: str = "unknown"

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Gibt Liste von Activity-Dicts zurueck."""

    def deduplicate_key(self, item: dict) -> str:
        """Erzeugt einen eindeutigen Schluessel zur Deduplizierung."""
        raw = f"{item.get('title', '')}|{item.get('location_name', '')}|{item.get('date_start', '')}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
