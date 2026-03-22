#!/bin/bash
# Family Activity Scout — Scraper Cron-Wrapper
cd "$(dirname "$0")"
python3 -c "
from models import init_db, deactivate_expired
from scrapers import run_all_scrapers
init_db()
expired = deactivate_expired()
if expired:
    print(f'[Cleanup] {expired} abgelaufene Events deaktiviert')
results = run_all_scrapers()
total = sum(v for v in results.values() if v > 0)
print(f'[Scraper] Fertig: {total} Aktivitaeten aktualisiert')
"
