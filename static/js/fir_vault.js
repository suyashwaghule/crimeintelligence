/* ==========================================================================
   FEATURE: FIR CASE DOSSIER & FINANCIAL FRAUD VAULT (50,000+ FIR DATASET)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Lazy loaded when tab opens
});

window.initFIRVaultTab = async function() {
    await loadFIRStats();
    await loadFIRRecords();

    const searchInput = document.getElementById('fir-search-input');
    const typeSelect = document.getElementById('fir-type-filter');
    const statusSelect = document.getElementById('fir-status-filter');

    if (searchInput && !searchInput.dataset.bound) {
        searchInput.dataset.bound = 'true';
        searchInput.addEventListener('input', debounceFIR(loadFIRRecords, 300));
        if (typeSelect) typeSelect.addEventListener('change', loadFIRRecords);
        if (statusSelect) statusSelect.addEventListener('change', loadFIRRecords);
    }
};

async function loadFIRStats() {
    try {
        const res = await fetch('/api/fir/stats');
        const json = await res.json();

        if (json.status === 'success') {
            const data = json.data;
            document.getElementById('fir-total-count').textContent = data.total_firs.toLocaleString();
            document.getElementById('fir-stolen-inr').textContent = '₹ ' + Math.round(data.total_stolen_value_inr / 100000).toLocaleString() + ' Lakhs';
            document.getElementById('fir-recovered-inr').textContent = '₹ ' + Math.round(data.total_recovered_value_inr / 100000).toLocaleString() + ' Lakhs';
            document.getElementById('fir-recovery-rate').textContent = data.recovery_rate_pct + '%';
        }
    } catch (e) {
        console.error("Error loading FIR stats:", e);
    }
}

async function loadFIRRecords() {
    const query = document.getElementById('fir-search-input')?.value.trim() || '';
    const crimeType = document.getElementById('fir-type-filter')?.value || 'All';
    const caseStatus = document.getElementById('fir-status-filter')?.value || 'All';
    const container = document.getElementById('fir-table-body');

    if (!container) return;
    container.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px;"><div class="spinner"></div>Searching 50,000+ FIR Case Records...</td></tr>`;

    try {
        const res = await fetch(`/api/fir/records?query=${encodeURIComponent(query)}&crime_type=${crimeType}&case_status=${caseStatus}&limit=40`);
        const json = await res.json();

        if (json.status === 'success') {
            renderFIRTable(json.data);
        }
    } catch (e) {
        console.error("Error loading FIR records:", e);
    }
}

function renderFIRTable(firs) {
    const container = document.getElementById('fir-table-body');
    if (!container) return;

    if (firs.length === 0) {
        container.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:var(--text-muted);">No FIR records matched query.</td></tr>`;
        return;
    }

    container.innerHTML = firs.map(f => `
        <tr style="border-bottom:1px solid var(--border-color); font-size:0.83rem;">
            <td style="padding:10px; font-family:var(--font-code); color:var(--primary); font-weight:700;">${f.fir_number}</td>
            <td style="padding:10px; color:#fff;"><strong>${f.crime_type}</strong><br><span style="font-size:0.75rem; color:var(--text-muted);">${f.crime_subtype}</span></td>
            <td style="padding:10px;">${f.area_name}</td>
            <td style="padding:10px;">${f.crime_date} ${f.crime_time || ''}</td>
            <td style="padding:10px; color:var(--accent-red); font-weight:700;">₹ ${(f.stolen_property_value || 0).toLocaleString()}</td>
            <td style="padding:10px; color:var(--accent-green); font-weight:700;">₹ ${(f.recovered_property_value || 0).toLocaleString()}</td>
            <td style="padding:10px;">
                <span class="badge ${f.case_status === 'Solved' ? 'badge-low' : 'badge-wanted'}">${f.case_status}</span>
            </td>
        </tr>
    `).join('');
}

function debounceFIR(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
