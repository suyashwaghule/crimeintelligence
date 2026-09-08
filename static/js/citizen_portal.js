/* ==========================================================================
   PHASE 2: CITIZEN 1-TAP SOS PANIC BUTTON & ANONYMOUS CRIME TIP PORTAL
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const sosBtn = document.getElementById('btn-trigger-sos');
    const tipForm = document.getElementById('citizen-tip-form');

    if (sosBtn) {
        sosBtn.addEventListener('click', () => triggerSOSAlert());
    }

    if (tipForm) {
        tipForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitAnonymousTip();
        });
    }
});

async function triggerSOSAlert() {
    const output = document.getElementById('sos-dispatch-output');
    output.classList.remove('hidden');
    output.innerHTML = `<div style="text-align:center; padding:10px;"><div class="spinner"></div><p>Broadcasting Emergency GPS Coordinates & Computing Nearest Officer Dispatch...</p></div>`;

    try {
        const res = await fetch('/api/citizen/sos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: 18.5308, longitude: 73.8475, area_name: 'Shivajinagar Chowk' })
        });

        const json = await res.json();

        if (json.status === 'success') {
            const data = json.data;
            const dispatch = data.dispatch;
            const officer = dispatch.assigned_officer;

            output.innerHTML = `
                <div style="color:var(--accent-red); font-weight:800; font-size:1.1rem; margin-bottom:8px;">
                    <i class="fa-solid fa-bell"></i> EMERGENCY DISPATCHED — SOS ID: ${data.sos_id}
                </div>
                <div style="font-size:0.88rem; color:#fff;">
                    <div><strong>Assigned Officer:</strong> ${officer.rank} ${officer.officer_name}</div>
                    <div><strong>Police Station:</strong> ${officer.police_station} (${officer.phone_number})</div>
                    <div><strong>Est. Patrol Arrival:</strong> <span style="color:var(--primary); font-weight:800;">${dispatch.eta_minutes} Minutes</span> (Distance: ${officer.distance_km} km)</div>
                </div>
            `;
        }
    } catch (e) {
        console.error("SOS error:", e);
    }
}

async function submitAnonymousTip() {
    const area = document.getElementById('tip-area').value;
    const desc = document.getElementById('tip-desc').value;
    const msgBox = document.getElementById('tip-success-msg');
    const msgText = document.getElementById('tip-msg-text');

    try {
        const res = await fetch('/api/citizen/tip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ area_name: area, description: desc })
        });

        const json = await res.json();

        if (json.status === 'success') {
            msgText.textContent = `Tip ${json.tip_id} submitted. Thank you for assisting Pune Police.`;
            msgBox.classList.remove('hidden');
            document.getElementById('citizen-tip-form').reset();
        }
    } catch (e) {
        console.error("Tip error:", e);
    }
}
