/* ==========================================================================
   FEATURE: LIVE POLICE PATROL & FLEET TRACKING COMMAND (300 OFFICERS DATASET)
   ========================================================================== */

let patrolMap = null;
let patrolMarkersGroup = null;

document.addEventListener('DOMContentLoaded', () => {
    // Lazy initialized when tab opens
});

window.initPolicePatrolsTab = async function() {
    initPatrolMap();
    await loadPatrolOfficers();
    
    const stationFilter = document.getElementById('patrol-station-filter');
    const statusFilter = document.getElementById('patrol-status-filter');
    
    if (stationFilter && !stationFilter.dataset.bound) {
        stationFilter.dataset.bound = 'true';
        stationFilter.addEventListener('change', loadPatrolOfficers);
        if (statusFilter) statusFilter.addEventListener('change', loadPatrolOfficers);
    }
};

function initPatrolMap() {
    if (patrolMap) return;
    
    const mapEl = document.getElementById('patrol-fleet-map');
    if (!mapEl) return;
    
    patrolMap = L.map('patrol-fleet-map').setView([18.5204, 73.8567], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 18
    }).addTo(patrolMap);
    
    patrolMarkersGroup = L.layerGroup().addTo(patrolMap);
}

async function loadPatrolOfficers() {
    const station = document.getElementById('patrol-station-filter')?.value || 'All';
    const dutyStatus = document.getElementById('patrol-status-filter')?.value || 'All';
    const listContainer = document.getElementById('patrol-officers-list');

    try {
        const res = await fetch(`/api/patrols/officers?station=${encodeURIComponent(station)}&duty_status=${dutyStatus}`);
        const json = await res.json();

        if (json.status === 'success') {
            const officers = json.data;
            renderPatrolMarkers(officers);
            renderPatrolList(officers);
        }
    } catch (e) {
        console.error("Error loading patrol officers:", e);
    }
}

function renderPatrolMarkers(officers) {
    if (!patrolMarkersGroup) return;
    patrolMarkersGroup.clearLayers();

    officers.forEach(o => {
        const isPatrol = o.duty_status === 'Active' || o.duty_status === 'On Patrol';
        const color = isPatrol ? '#00f2fe' : (o.duty_status === 'Responding' ? '#ff0055' : '#94a3b8');
        
        const icon = L.divIcon({
            className: 'custom-officer-pin',
            html: `<div style="background:${color}; width:12px; height:12px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px ${color};"></div>`,
            iconSize: [12, 12]
        });

        const marker = L.marker([o.latitude, o.longitude], { icon: icon });
        marker.bindPopup(`
            <div style="font-size:0.85rem; color:#000;">
                <strong>${o.rank} ${o.officer_name}</strong><br>
                Badge: ${o.badge_number} | Station: ${o.police_station}<br>
                Vehicle: <b>${o.vehicle_assigned}</b><br>
                Phone: ${o.phone_number}<br>
                Status: <span style="color:${color}; font-weight:bold;">${o.duty_status}</span>
            </div>
        `);
        patrolMarkersGroup.addLayer(marker);
    });
}

function renderPatrolList(officers) {
    const container = document.getElementById('patrol-officers-list');
    if (!container) return;

    if (officers.length === 0) {
        container.innerHTML = `<p style="text-align:center; padding:20px; color:var(--text-muted);">No active patrol units match filters.</p>`;
        return;
    }

    container.innerHTML = officers.map(o => `
        <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); padding:10px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-weight:700; color:#fff; font-size:0.88rem;">${o.rank} ${o.officer_name}</div>
                <div style="font-size:0.75rem; color:var(--text-muted);">${o.police_station} | Vehicle: <span style="color:var(--primary);">${o.vehicle_assigned}</span></div>
                <div style="font-size:0.72rem; color:var(--text-dim);"><i class="fa-solid fa-phone"></i> ${o.phone_number}</div>
            </div>
            <div style="text-align:right;">
                <span class="badge ${o.duty_status === 'Active' || o.duty_status === 'On Patrol' ? 'badge-low' : (o.duty_status === 'Responding' ? 'badge-wanted' : 'badge-medium')}">${o.duty_status}</span>
                <button class="btn btn-primary btn-sm mt-1" style="display:block; font-size:0.7rem; padding:3px 8px;" onclick="alert('Radio Dispatch signal transmitted to Officer ${o.badge_number} (${o.phone_number})')">
                    <i class="fa-solid fa-radio"></i> Dispatch
                </button>
            </div>
        </div>
    `).join('');
}
