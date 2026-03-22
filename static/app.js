/* Family Activity Scout — Frontend Logic */

function initMap(suggestions) {
    if (!suggestions || !suggestions.length) return;
    var mapEl = document.getElementById('map');
    if (!mapEl) return;

    var map = L.map('map').setView([52.52, 13.405], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    var bounds = [];
    suggestions.forEach(function(s) {
        if (!s.lat || !s.lon) return;
        var color = s.is_special ? '#ff006e' : (s.is_permanent ? '#00ff88' : '#00f0ff');
        var icon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background:' + color + ';width:12px;height:12px;border-radius:50%;border:2px solid #0a0a1a;box-shadow:0 0 8px ' + color + '"></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });
        var marker = L.marker([s.lat, s.lon], {icon: icon}).addTo(map);
        marker.bindPopup(
            '<b>' + s.title + '</b><br>' +
            (s.location_name || '') +
            (s.distance_km ? '<br>🚗 ' + s.distance_km + ' km' : '') +
            '<br><a href="/activity/' + s.id + '">Details →</a>'
        );
        bounds.push([s.lat, s.lon]);
    });

    if (bounds.length > 1) {
        map.fitBounds(bounds, {padding: [30, 30]});
    }
}

function sendFeedback(activityId, rating, btn) {
    fetch('/api/feedback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({activity_id: activityId, rating: rating})
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.ok) {
            btn.classList.add(rating > 0 ? 'active-like' : 'active-dislike');
            showToast(rating > 0 ? 'Gemerkt — mehr davon!' : 'Verstanden — weniger davon.');
        }
    })
    .catch(function() { showToast('Fehler beim Speichern.'); });
}

function markDone(activityId, btn) {
    fetch('/api/done', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({activity_id: activityId})
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.ok) {
            btn.classList.add('active-done');
            showToast('Als gemacht markiert!');
        }
    })
    .catch(function() { showToast('Fehler beim Speichern.'); });
}

function showToast(msg) {
    var existing = document.querySelector('.toast');
    if (existing) existing.remove();
    var toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 2500);
}
