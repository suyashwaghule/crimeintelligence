/* ==========================================================================
   MODULE 4: AREA-WISE CRIMINAL PREDICTION & PROXIMITY SCANNER
   ========================================================================== */

let areaRadarMap = null;
let radarCircle = null;
let radarMarkers = [];

window.initAreaScanner = function() {
    const picker = document.getElementById('area-picker');
    const slider = document.getElementById('radius-slider');
    const radiusVal = document.getElementById('radius-val');
    const scanBtn = document.getElementById('btn-scan-area');

    if (slider) {
        slider.addEventListener('input', (e) => {
            radiusVal.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }

    if (scanBtn) {
        scanBtn.addEventListener('click', () => runAreaScan());
    }

    if (!areaRadarMap) {
        setTimeout(initRadarMap, 200);
    }
};

function initRadarMap() {
    const container = document.getElementById('area-radar-map');
    if (!container || areaRadarMap) return;

    // Default center Pune Shivajinagar
    areaRadarMap = L.map('area-radar-map').setView([18.5308, 73.8475], 13);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 18
    }).addTo(areaRadarMap);

    runAreaScan();
}

async function runAreaScan() {
    const areaName = document.getElementById('area-picker').value;
    const radiusKm = parseFloat(document.getElementById('radius-slider').value);

    try {
        const res = await fetch('/api/area-prediction/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ area_name: areaName, radius_km: radiusKm })
        });

        const json = await res.json();

        if (json.status === 'success') {
            const info = json.data.area_info;
            const suspects = json.data.suspects;

            updateRadarMap(info.latitude, info.longitude, radiusKm, suspects);
            renderNearbySuspects(suspects);
        }
    } catch (e) {
        console.error("Area scan error:", e);
    }
}

function updateRadarMap(lat, lng, radiusKm, suspects) {
    if (!areaRadarMap) return;

    areaRadarMap.setView([lat, lng], 13);

    // Clear previous elements
    if (radarCircle) areaRadarMap.removeLayer(radarCircle);
    radarMarkers.forEach(m => areaRadarMap.removeLayer(m));
    radarMarkers = [];

    // Draw scanning radius circle
    radarCircle = L.circle([lat, lng], {
        color: '#00f2fe',
        fillColor: '#00f2fe',
        fillOpacity: 0.12,
        radius: radiusKm * 1000
    }).addTo(areaRadarMap);

    // Add markers for nearby suspects
    suspects.forEach(s => {
        const marker = L.circleMarker([lat + (Math.random() - 0.5) * 0.02, lng + (Math.random() - 0.5) * 0.02], {
            radius: 7,
            fillColor: s.wanted_status ? '#ff0055' : (s.risk_level === 'High' ? '#ffb703' : '#00f2fe'),
            color: '#fff',
            weight: 1.5,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(areaRadarMap);

        marker.bindPopup(`
            <div style="font-family:sans-serif; color:#000;">
                <strong>${s.full_name}</strong><br>
                Risk: ${s.risk_level} | Dist: ${s.distance_km} km<br>
                <button onclick="openCriminalModal('${s.criminal_id}')" style="margin-top:6px; background:#00f2fe; border:none; padding:4px 8px; border-radius:4px; font-weight:bold; cursor:pointer;">View Dossier</button>
            </div>
        `);
        radarMarkers.push(marker);
    });
}

function renderNearbySuspects(suspects) {
    const list = document.getElementById('area-suspects-list');
    if (!list) return;

    if (suspects.length === 0) {
        list.innerHTML = `<p style="text-align:center; color:var(--text-muted); padding:30px;">No registered criminals within this scan radius.</p>`;
        return;
    }

    list.innerHTML = suspects.map(s => `
        <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px; cursor:pointer;" onclick="openCriminalModal('${s.criminal_id}')">
            <img src="/output_dataset/${s.mugshot_image}" style="width:50px; height:55px; object-fit:cover; border-radius:6px;">
            <div style="flex:1;">
                <div style="display:flex; justify-content:space-between;">
                    <div style="font-weight:700; color:#fff; font-size:0.92rem;">${s.full_name}</div>
                    <span class="badge badge-${s.risk_level.toLowerCase()}">${s.risk_level}</span>
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">
                    Distance: <strong style="color:var(--primary);">${s.distance_km} km</strong> | Primary: ${s.most_common_crime}
                </div>
                <div style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">${s.address}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-weight:800; color:var(--accent-red); font-size:0.95rem;">${s.suspect_score}</div>
                <div style="font-size:0.68rem; color:var(--text-dim);">PROXIMITY SCORE</div>
            </div>
        </div>
    `).join('');
}
