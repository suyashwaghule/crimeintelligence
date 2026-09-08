/* ==========================================================================
   MODULE 5: ANALYTICS DASHBOARD & GEOJSON POLICE JURISDICTION MAPPING
   ========================================================================== */

let puneMap = null;
let heatmapLayer = null;
let markersLayer = null;
let geojsonLayer = null;

window.initDashboardAnalytics = async function() {
    initPuneMap();
    await loadHeatmapData();
    await loadGeoJSONBoundaries();
    await loadChartAnalytics();
};

function initPuneMap() {
    if (puneMap) return;
    
    const mapEl = document.getElementById('pune-map');
    if (!mapEl) return;
    
    puneMap = L.map('pune-map').setView([18.5204, 73.8567], 12);
    
    // Light Map Basemap Tile Layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 18
    }).addTo(puneMap);

    markersLayer = L.layerGroup().addTo(puneMap);
    
    document.getElementById('btn-toggle-heatmap')?.addEventListener('click', (e) => {
        e.target.classList.toggle('active');
        if (heatmapLayer) {
            if (puneMap.hasLayer(heatmapLayer)) puneMap.removeLayer(heatmapLayer);
            else puneMap.addLayer(heatmapLayer);
        }
    });

    document.getElementById('btn-toggle-markers')?.addEventListener('click', (e) => {
        e.target.classList.toggle('active');
        if (markersLayer) {
            if (puneMap.hasLayer(markersLayer)) puneMap.removeLayer(markersLayer);
            else puneMap.addLayer(markersLayer);
        }
    });
}

async function loadGeoJSONBoundaries() {
    try {
        const res = await fetch('/api/geojson/boundaries');
        const data = await res.json();

        if (data && data.features && data.features.length > 0 && puneMap) {
            if (geojsonLayer) puneMap.removeLayer(geojsonLayer);

            geojsonLayer = L.geoJSON(data, {
                style: function(feature) {
                    return {
                        color: '#0f172a',
                        weight: 2,
                        opacity: 0.85,
                        fillColor: '#0f172a',
                        fillOpacity: 0.12
                    };
                },
                onEachFeature: function(feature, layer) {
                    const props = feature.properties;
                    layer.bindPopup(`
                        <div style="font-size:0.85rem; color:#0f172a;">
                            <strong>POLICE STATION JURISDICTION: ${props.area_name}</strong><br>
                            Hotspot Score: <b>${props.hotspot_score} / 10</b><br>
                            Total Crimes: ${props.total_crimes}<br>
                            Primary Crime: ${props.most_common_crime}<br>
                            Peak Risk Hours: ${props.dangerous_time}
                        </div>
                    `);
                }
            }).addTo(puneMap);
        }
    } catch (e) {
        console.error("Error loading GeoJSON boundaries:", e);
    }
}

async function loadHeatmapData() {
    try {
        const res = await fetch('/api/areas');
        const json = await res.json();
        
        if (json.status === 'success' && puneMap) {
            const areas = json.data;
            
            const heatPoints = areas.map(a => [a.latitude, a.longitude, a.hotspot_score / 10.0]);
            
            if (heatmapLayer) puneMap.removeLayer(heatmapLayer);
            
            if (window.L && L.heatLayer) {
                heatmapLayer = L.heatLayer(heatPoints, {
                    radius: 25,
                    blur: 15,
                    maxZoom: 17,
                    gradient: { 0.4: '#94a3b8', 0.7: '#475569', 1.0: '#0f172a' }
                }).addTo(puneMap);
            }

            markersLayer.clearLayers();
            areas.forEach(a => {
                const marker = L.circleMarker([a.latitude, a.longitude], {
                    radius: 6 + (a.hotspot_score * 0.8),
                    fillColor: '#0f172a',
                    color: '#ffffff',
                    weight: 1.5,
                    opacity: 1,
                    fillOpacity: 0.85
                });
                
                marker.bindPopup(`
                    <div style="font-size:0.85rem; color:#0f172a;">
                        <strong style="font-size:0.95rem;">${a.area_name}</strong><br>
                        <span>Hotspot Score: <b>${a.hotspot_score} / 10</b></span><br>
                        <span>Total Crimes: ${a.total_crimes}</span><br>
                        <span>Top Crime: ${a.most_common_crime}</span><br>
                        <span>High Risk Window: ${a.dangerous_time}</span>
                    </div>
                `);
                
                markersLayer.addLayer(marker);
            });
        }
    } catch (e) {
        console.error("Failed to load map heatmap:", e);
    }
}

async function loadChartAnalytics() {
    try {
        const res = await fetch('/api/analytics/charts');
        const json = await res.json();
        
        if (json.status === 'success') {
            const d = json.data;
            renderCrimeTypesChart(d.crime_types);
            renderMonthlyTrendChart(d.monthly_trend);
            renderTopAreasChart(d.top_areas);
            renderDayNightChart(d.day_night);
        }
    } catch (e) {
        console.error("Failed to load charts data:", e);
    }
}

function renderCrimeTypesChart(data) {
    const ctx = document.getElementById('chart-crime-types')?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(i => i.crime_type),
            datasets: [{
                data: data.map(i => i.count),
                backgroundColor: ['#0f172a', '#1e293b', '#334155', '#475569', '#64748b', '#94a3b8', '#cbd5e1', '#e2e8f0']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right', labels: { color: '#0f172a', font: { family: 'Inter' } } } }
        }
    });
}

function renderMonthlyTrendChart(data) {
    const ctx = document.getElementById('chart-monthly-trend')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(i => `${i.crime_year}-${i.crime_month.toString().padStart(2, '0')}`),
            datasets: [{
                label: 'Incidents Reported',
                data: data.map(i => i.count),
                borderColor: '#0f172a',
                backgroundColor: 'rgba(15, 23, 42, 0.08)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#475569' }, grid: { color: 'rgba(15,23,42,0.06)' } },
                y: { ticks: { color: '#475569' }, grid: { color: 'rgba(15,23,42,0.06)' } }
            }
        }
    });
}

function renderTopAreasChart(data) {
    const ctx = document.getElementById('chart-top-areas')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(i => i.area_name),
            datasets: [{
                label: 'Total Crimes',
                data: data.map(i => i.total_crimes),
                backgroundColor: '#0f172a',
                borderColor: '#0f172a',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#475569' }, grid: { color: 'rgba(15,23,42,0.06)' } },
                y: { ticks: { color: '#475569' }, grid: { color: 'rgba(15,23,42,0.06)' } }
            }
        }
    });
}

function renderDayNightChart(data) {
    const ctx = document.getElementById('chart-day-night')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Day Time (6 AM - 6 PM)', 'Night Time (6 PM - 6 AM)'],
            datasets: [{
                data: [data.day_total || 45, data.night_total || 55],
                backgroundColor: ['#0f172a', '#64748b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#0f172a' } } }
        }
    });
}
