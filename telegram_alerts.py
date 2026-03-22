"""Telegram-Alerts: Freitags Top-5 + Sonder-Alerts fuer besondere Events."""

import httpx
from config import TELEGRAM_BOT_TOKEN, FAMILY_CHAT_ID


def _send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Sendet eine Telegram-Nachricht."""
    if not TELEGRAM_BOT_TOKEN or not FAMILY_CHAT_ID:
        print("[Telegram] Kein Bot-Token oder Chat-ID konfiguriert")
        return False

    try:
        resp = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": FAMILY_CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] Fehler: {e}")
        return False


def send_weekend_tips(suggestions: list[dict]) -> bool:
    """Freitags-Push: Top-5 Familien-Vorschlaege fuer das Wochenende."""
    if not suggestions:
        return _send_message("🎉 <b>Wochenend-Tipps</b>\n\nKeine neuen Vorschlaege diese Woche.")

    lines = ["🎉 <b>Familien-Wochenend-Tipps</b>\n"]
    for i, s in enumerate(suggestions[:5], 1):
        tags_str = " ".join(f"#{t}" for t in s.get("tags", [])[:3])
        distance = s.get("distance_km")
        dist_str = f" ({distance} km)" if distance else ""
        price = s.get("price_info", "")
        price_str = f" — {price}" if price else ""

        lines.append(
            f"{i}. <b>{s['title']}</b>{dist_str}\n"
            f"   📍 {s.get('location_name', '?')}{price_str}\n"
            f"   {tags_str}"
        )

    lines.append("\n💡 Mehr Vorschlaege auf dem Dashboard!")
    return _send_message("\n".join(lines))


def send_special_alert(activity: dict) -> bool:
    """Sonder-Alert: Besonderes Event in den naechsten 3 Tagen."""
    return _send_message(
        f"⭐ <b>Besonderer Tipp!</b>\n\n"
        f"<b>{activity['title']}</b>\n"
        f"📍 {activity.get('location_name', '?')}\n"
        f"📅 {activity.get('time_info', activity.get('date_start', '?'))}\n"
        f"💰 {activity.get('price_info', '?')}\n\n"
        f"{activity.get('description', '')[:200]}"
    )
