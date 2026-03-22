"""Family Activity Scout — FastAPI App."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import PORT, HOST, TEMPLATES_DIR, STATIC_DIR, ALL_TAGS
from models import (
    init_db, get_active_activities, get_activity_by_id,
    get_preferences, update_preferences, add_feedback, mark_done,
    get_done_ids, deactivate_expired,
)
from scoring import compute_scores, get_weekend_mix
from weather import get_forecast
from scrapers import run_all_scrapers

app = FastAPI(title="Family Activity Scout")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# DB beim Start initialisieren
init_db()


# ───────────────────────────────────────────────────────────────
# Helper
# ───────────────────────────────────────────────────────────────

def _get_suggestions(count: int = 5) -> list[dict]:
    """Berechnet Top-N personalisierte Vorschlaege."""
    activities = get_active_activities()
    prefs = get_preferences()
    weather = get_forecast()
    done_ids = get_done_ids()
    scored = compute_scores(activities, prefs, weather, done_ids)
    return get_weekend_mix(scored, count)


# ───────────────────────────────────────────────────────────────
# HTML Routes
# ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    weather = get_forecast()
    suggestions = _get_suggestions(5)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "page": "dashboard",
        "weather": weather,
        "suggestions": suggestions,
        "suggestions_json": json.dumps(
            [{"id": s["id"], "title": s["title"], "lat": s.get("lat"), "lon": s.get("lon"),
              "location_name": s.get("location_name", ""), "distance_km": s.get("distance_km"),
              "is_special": s.get("is_special", 0), "is_permanent": s.get("is_permanent", 0)}
             for s in suggestions],
            ensure_ascii=False,
        ),
    })


@app.get("/activity/{activity_id}", response_class=HTMLResponse)
async def activity_detail(request: Request, activity_id: int):
    activity = get_activity_by_id(activity_id)
    if not activity:
        return HTMLResponse("<h1>Nicht gefunden</h1>", status_code=404)

    # Entfernung berechnen
    from scoring import _haversine_km
    from config import HOME_LAT, HOME_LON
    if activity.get("lat") and activity.get("lon"):
        activity["distance_km"] = round(_haversine_km(HOME_LAT, HOME_LON, activity["lat"], activity["lon"]), 1)

    return templates.TemplateResponse("activity.html", {
        "request": request,
        "page": "detail",
        "activity": activity,
    })


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_view(request: Request):
    activities = get_active_activities()
    now = datetime.now(timezone.utc)

    # 14 Tage anzeigen
    days = []
    weekdays_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    for offset in range(14):
        day = now + timedelta(days=offset)
        day_str = day.strftime("%Y-%m-%d")
        day_events = []
        for act in activities:
            # Permanente immer anzeigen (nur Sa/So)
            if act.get("is_permanent") and day.weekday() in (5, 6):
                day_events.append(act)
                continue
            # Events mit Datum pruefen
            if act.get("date_start") and act["date_start"][:10] <= day_str:
                end = act.get("date_end", act["date_start"])[:10] if act.get("date_end") else act["date_start"][:10]
                if day_str <= end:
                    day_events.append(act)

        days.append({
            "date": day_str,
            "date_display": day.strftime("%d.%m."),
            "weekday": weekdays_de[day.weekday()],
            "is_today": offset == 0,
            "events": day_events[:8],  # max 8 pro Tag anzeigen
        })

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "page": "calendar",
        "days": days,
        "all_tags": ALL_TAGS,
    })


@app.get("/preferences", response_class=HTMLResponse)
async def preferences_page(request: Request):
    prefs = get_preferences()

    # Feedback-Historie mit Activity-Titeln
    from models import _connect
    with _connect() as conn:
        rows = conn.execute("""
            SELECT f.activity_id, f.rating, f.rated_at, a.title as activity_title
            FROM feedback f
            JOIN activities a ON a.id = f.activity_id
            ORDER BY f.rated_at DESC
            LIMIT 20
        """).fetchall()
    recent_feedback = [dict(r) for r in rows]

    return templates.TemplateResponse("preferences.html", {
        "request": request,
        "page": "preferences",
        "preferences": prefs,
        "recent_feedback": recent_feedback,
    })


# ───────────────────────────────────────────────────────────────
# API Endpoints
# ───────────────────────────────────────────────────────────────

@app.post("/api/feedback")
async def api_feedback(request: Request):
    data = await request.json()
    activity_id = data.get("activity_id")
    rating = data.get("rating", 0)
    if not activity_id or rating not in (1, -1):
        return JSONResponse({"ok": False, "error": "activity_id und rating (1/-1) erforderlich"}, status_code=400)
    add_feedback(activity_id, rating)
    return JSONResponse({"ok": True})


@app.post("/api/done")
async def api_done(request: Request):
    data = await request.json()
    activity_id = data.get("activity_id")
    notes = data.get("notes", "")
    if not activity_id:
        return JSONResponse({"ok": False, "error": "activity_id erforderlich"}, status_code=400)
    mark_done(activity_id, notes)
    return JSONResponse({"ok": True})


@app.put("/api/preferences")
async def api_update_preferences(request: Request):
    data = await request.json()
    update_preferences(data)
    return JSONResponse({"ok": True})


@app.get("/api/suggestions")
async def api_suggestions(count: int = 5):
    suggestions = _get_suggestions(count)
    return JSONResponse(suggestions)


@app.post("/api/scrape")
async def api_scrape():
    """Manueller Scraper-Trigger."""
    deactivate_expired()
    results = run_all_scrapers()
    return JSONResponse({"ok": True, "results": results})


# ───────────────────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print(f"[Family Scout] Starte auf Port {PORT}...")
    uvicorn.run(app, host=HOST, port=PORT)
