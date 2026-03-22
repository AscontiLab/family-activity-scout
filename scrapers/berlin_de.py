"""Scraper fuer berlin.de/events — Offizieller Veranstaltungskalender."""

import httpx
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from config import SCRAPE_USER_AGENT, SCRAPE_TIMEOUT


class BerlinDeScraper(BaseScraper):
    """Scrapt Familien-Events von berlin.de."""

    name = "berlin_de"
    BASE_URL = "https://www.berlin.de/tickets/kinder/"

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
            print(f"[berlin.de] Fehler beim Laden: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # berlin.de nutzt Artikelkarten fuer Events
        for card in soup.select("article, .event-item, .teaser, .searchresult"):
            title_el = card.select_one("h2, h3, .title, .heading")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            link_el = card.select_one("a[href]")
            link = ""
            if link_el:
                href = link_el.get("href", "")
                link = href if href.startswith("http") else f"https://www.berlin.de{href}"

            desc_el = card.select_one("p, .text, .description, .teaser-text")
            desc = desc_el.get_text(strip=True) if desc_el else ""

            location_el = card.select_one(".location, .venue, .ort")
            location = location_el.get_text(strip=True) if location_el else ""

            date_el = card.select_one("time, .date, .datum")
            date_text = ""
            date_start = None
            if date_el:
                date_text = date_el.get_text(strip=True)
                date_start = date_el.get("datetime")

            items.append({
                "source_id": self.deduplicate_key({"title": title, "location_name": location, "date_start": date_start}),
                "title": title,
                "description": desc,
                "source_url": link,
                "location_name": location,
                "date_start": date_start,
                "time_info": date_text,
                "tags": ["indoor", "kultur"],  # Default, manuell verfeinern
                "age_min": 3,
                "age_max": 14,
                "is_special": 0,
            })

        return items
