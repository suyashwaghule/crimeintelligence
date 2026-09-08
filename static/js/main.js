/* ==========================================================================
   MAIN SYSTEM ROUTER & AUTO-INITIALIZER (MULTI-PAGE ARCHITECTURE)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    startLiveClock();
    fetchSystemKPIs();
    initializeActivePageModule();
});

function startLiveClock() {
    const clockEl = document.getElementById('live-clock');
    if (!clockEl) return;
    
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('en-US', { hour12: false }) + " IST";
    }, 1000);
}

async function fetchSystemKPIs() {
    try {
        const res = await fetch('/api/kpis');
        const json = await res.json();
        if (json.status === 'success' && json.data) {
            const data = json.data;
            updateElementText('kpi-total-crimes', (data.total_crimes || 0).toLocaleString());
            updateElementText('kpi-criminals', (data.total_criminals || 0).toLocaleString());
            updateElementText('kpi-solve-rate', (data.solve_rate || 0) + '%');
            updateElementText('kpi-wanted', (data.wanted_criminals || 0).toLocaleString());
            updateElementText('kpi-high-risk', (data.high_risk_zones || 0).toLocaleString());
        }
    } catch (e) {
        console.error("KPI fetch error:", e);
    }
}

function updateElementText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function initializeActivePageModule() {
    const path = window.location.pathname.toLowerCase();

    console.log("[*] Initializing page module for route:", path);

    if (path === '/' || path.includes('/dashboard')) {
        if (window.initDashboardAnalytics) window.initDashboardAnalytics();
        else if (window.initAnalyticsDashboardTab) window.initAnalyticsDashboardTab();
    } else if (path.includes('/cctv-surveillance')) {
        if (window.initCCTVSurveillanceTab) window.initCCTVSurveillanceTab();
    } else if (path.includes('/criminal-database')) {
        if (window.loadCriminalRecords) window.loadCriminalRecords();
        else if (window.initCriminalRecordsTab) window.initCriminalRecordsTab();
    } else if (path.includes('/face-recognition')) {
        if (window.initFaceRecognitionTab) window.initFaceRecognitionTab();
    } else if (path.includes('/police-patrols')) {
        if (window.initPolicePatrolsTab) window.initPolicePatrolsTab();
    } else if (path.includes('/fir-vault')) {
        if (window.initFIRVaultTab) window.initFIRVaultTab();
    } else if (path.includes('/network-graph')) {
        if (window.initNetworkGraphTab) window.initNetworkGraphTab();
    } else if (path.includes('/crime-pattern')) {
        if (window.initCrimePatternTab) window.initCrimePatternTab();
    } else if (path.includes('/proximity-scanner')) {
        if (window.initAreaPredictionTab) window.initAreaPredictionTab();
    } else if (path.includes('/risk-predictor')) {
        if (window.initAIPredictionTab) window.initAIPredictionTab();
    } else if (path.includes('/field-scanner')) {
        if (window.initFieldOfficerTab) window.initFieldOfficerTab();
    } else if (path.includes('/citizen-portal')) {
        if (window.initCitizenPortalTab) window.initCitizenPortalTab();
    }
}
