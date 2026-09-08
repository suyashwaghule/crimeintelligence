/* ==========================================================================
   MODULE 3: CRIME PATTERN ANALYSIS (MODUS OPERANDI MATCHING)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('mo-matching-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runMOMatch();
        });
    }
});

async function runMOMatch() {
    const crimeType = document.getElementById('mo-crime-type').value;
    const weapon = document.getElementById('mo-weapon').value;
    const entry = document.getElementById('mo-entry').value;
    const target = document.getElementById('mo-target').value;
    const timing = document.getElementById('mo-timing').value;

    const payload = {
        crime_type: crimeType,
        weapon_used: weapon,
        entry_method: entry,
        target_selection: target,
        crime_timing: timing
    };

    const container = document.getElementById('mo-results-container');
    container.innerHTML = `<div style="text-align:center; padding:40px;"><div class="spinner"></div><p>Matching Crime Scene MO Attributes Against Database...</p></div>`;

    try {
        const res = await fetch('/api/crime-pattern/match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const json = await res.json();

        if (json.status === 'success') {
            renderMOResults(json.suspects);
        }
    } catch (e) {
        console.error("MO match error:", e);
    }
}

function renderMOResults(suspects) {
    const container = document.getElementById('mo-results-container');
    if (!container) return;

    if (!suspects || suspects.length === 0) {
        container.innerHTML = `<p style="text-align:center; color:var(--text-muted); padding:30px;">No suspects matched this MO criteria.</p>`;
        return;
    }

    container.innerHTML = suspects.map((s, idx) => `
        <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:10px; padding:16px; margin-bottom:14px; display:flex; gap:16px; align-items:flex-start; cursor:pointer;" onclick="openCriminalModal('${s.criminal_id}')">
            <div style="font-weight:800; font-size:1.2rem; color:var(--primary); min-width:28px;">#${idx + 1}</div>
            <img src="/output_dataset/${s.mugshot_image}" style="width:70px; height:80px; object-fit:cover; border-radius:6px;">
            
            <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-family:var(--font-heading); color:#fff; font-size:1.1rem;">${s.full_name} ${s.nickname ? '("' + s.nickname + '")' : ''}</h4>
                    <span class="badge badge-primary" style="background:var(--primary-gradient); color:#000; font-weight:800; font-size:0.85rem;">${s.mo_similarity_score}% MO MATCH</span>
                </div>

                <div style="font-size:0.82rem; color:var(--primary); margin:4px 0;">ID: ${s.criminal_id} | Resident: ${s.criminal_area}</div>

                <div style="display:flex; flex-wrap:wrap; gap:6px; margin:8px 0;">
                    ${s.match_reasons.map(r => `<span style="background:rgba(0,242,254,0.1); border:1px solid rgba(0,242,254,0.2); color:#fff; font-size:0.72rem; padding:2px 8px; border-radius:4px;"><i class="fa-solid fa-check" style="color:var(--primary);"></i> ${r}</span>`).join('')}
                </div>

                <p style="font-size:0.8rem; color:var(--text-muted); line-height:1.4;">${s.repeat_pattern}</p>
            </div>
        </div>
    `).join('');
}
