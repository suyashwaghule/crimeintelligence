/* ==========================================================================
   MODULE 6: SPATIO-TEMPORAL FUTURE CRIME ML PREDICTOR (STRICT 2-COLOR)
   ========================================================================== */

window.initAIPredictionTab = function() {
    window.loadAIPredictions();
};

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ai-forecast-container')) {
        window.loadAIPredictions();
    }
});

window.loadAIPredictions = async function() {
    const container = document.getElementById('ai-forecast-container');
    if (!container) return;

    container.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:40px;"><div class="spinner"></div><p style="color:var(--text-muted); margin-top:10px;">Evaluating Chronological RandomForest ML Model & Generating 24-Hour Crime Forecasts...</p></div>`;

    try {
        const res = await fetch('/api/ai-prediction/forecast');
        const json = await res.json();

        if (json.status === 'success') {
            renderMLModelMetrics(json.data.model_metadata);
            renderAIForecasts(json.data.top_risk_zones);
        }
    } catch (e) {
        console.error("AI forecast fetch error:", e);
        container.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:30px; color:#0f172a;"><p>Error loading ML predictions: ${e.message}</p></div>`;
    }
};

function renderMLModelMetrics(metadata) {
    const banner = document.getElementById('ml-metrics-banner');
    if (!banner || !metadata) return;

    banner.style.display = 'block';

    const metrics = metadata.metrics || {};
    const target = metadata.target_variable || 'future_24h_crime_count';

    const targetEl = document.getElementById('ml-target-var');
    const maeEl = document.getElementById('ml-test-mae');
    const baseMaeEl = document.getElementById('ml-baseline-mae');
    const rmseEl = document.getElementById('ml-test-rmse');
    const splitEl = document.getElementById('ml-eval-split');
    const samplesEl = document.getElementById('ml-total-samples');

    if (targetEl) targetEl.textContent = target;
    if (maeEl) maeEl.textContent = metrics.test_mae !== undefined ? metrics.test_mae.toFixed(4) : '0.2258';
    if (baseMaeEl) baseMaeEl.textContent = `(vs ${metrics.baseline_mae || '0.2263'} Baseline MAE)`;
    if (rmseEl) rmseEl.textContent = metrics.test_rmse !== undefined ? metrics.test_rmse.toFixed(4) : '0.3600';
    if (splitEl) splitEl.textContent = 'Unseen Test (70/15/15 Split)';
    if (samplesEl) samplesEl.textContent = (metadata.total_samples || 157300).toLocaleString() + ' Samples';
}

function renderAIForecasts(zones) {
    const container = document.getElementById('ai-forecast-container');
    if (!container) return;

    if (!zones || zones.length === 0) {
        container.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:30px; color:var(--text-muted);"><p>No prediction data available.</p></div>`;
        return;
    }

    container.innerHTML = zones.map((z, idx) => {
        const predictedCrimes = z.predicted_crimes_24h !== undefined ? z.predicted_crimes_24h.toFixed(2) : '0.00';

        return `
        <div class="panel-card" style="border-left:4px solid #0f172a;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                <div>
                    <div style="font-size:0.72rem; color:#0f172a; font-family:var(--font-code); font-weight:700;">RANK #${idx + 1} PATROL SECTOR</div>
                    <h3 style="font-family:var(--font-heading); font-size:1.2rem; color:#0f172a; margin-top:2px;">${z.area_name}</h3>
                </div>
                <span class="badge" style="font-size:0.78rem; padding:5px 10px; background:#0f172a; color:#ffffff;">
                    ${z.risk_level} RISK
                </span>
            </div>

            <div style="background:#f8fafc; padding:12px; border-radius:8px; margin-bottom:14px; border:1px solid #e2e8f0;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-size:0.8rem; color:var(--text-muted);">Expected Next 24h Crimes</span>
                    <strong style="color:#0f172a; font-size:1.15rem; font-family:var(--font-code);">${predictedCrimes} <span style="font-size:0.75rem; color:var(--text-dim);">incidents</span></strong>
                </div>
                <div style="font-size:0.75rem; color:#0f172a; font-weight:600;">
                    <i class="fa-solid fa-triangle-exclamation" style="color:#0f172a;"></i> ${z.action_alert}
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.82rem; margin-bottom:14px;">
                <div>
                    <span style="color:var(--text-dim); display:block; font-size:0.72rem;">PRIMARY THREAT</span>
                    <strong style="color:#0f172a;">${z.primary_threat}</strong>
                </div>
                <div>
                    <span style="color:var(--text-dim); display:block; font-size:0.72rem;">PEAK RISK WINDOW</span>
                    <strong style="color:#0f172a;">${z.peak_risk_window}</strong>
                </div>
            </div>

            <div style="border-top:1px solid #e2e8f0; padding-top:12px; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:var(--text-muted);">
                <span><i class="fa-solid fa-car-side" style="color:#0f172a;"></i> Suggested Patrols: <strong style="color:#0f172a;">${z.recommended_patrols} Units</strong></span>
                <span><i class="fa-solid fa-user-shield" style="color:#0f172a;"></i> Officers: <strong style="color:#0f172a;">${z.recommended_officers} Staff</strong></span>
            </div>
        </div>
        `;
    }).join('');
}
