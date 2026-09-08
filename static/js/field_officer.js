/* ==========================================================================
   PHASE 2: FIELD OFFICER MOBILE PWA HANDHELD SCANNER (USER PHOTO UPLOAD)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('btn-field-scan');
    const fieldFileInput = document.getElementById('field-file-input');
    const cameraBox = document.getElementById('field-camera-box');

    if (scanBtn && fieldFileInput) {
        scanBtn.addEventListener('click', () => {
            fieldFileInput.click();
        });
    }

    if (cameraBox && fieldFileInput) {
        cameraBox.addEventListener('click', () => {
            fieldFileInput.click();
        });
    }

    if (fieldFileInput) {
        fieldFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFieldPhotoUpload(e.target.files[0]);
            }
        });
    }
});

async function handleFieldPhotoUpload(file) {
    const resultBox = document.getElementById('field-scan-result');
    const cameraImg = document.getElementById('field-camera-img');
    
    // Preview selected photo inside mobile viewport
    const reader = new FileReader();
    reader.onload = function(e) {
        if (cameraImg) cameraImg.src = e.target.result;
    };
    reader.readAsDataURL(file);

    resultBox.classList.remove('hidden');
    resultBox.innerHTML = `<div style="text-align:center; padding:20px; font-size:0.85rem;"><div class="spinner"></div><p>Scanning uploaded field photo against database...</p></div>`;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const res = await fetch('/api/field/scan', {
            method: 'POST',
            body: formData
        });

        const json = await res.json();

        if (json.status === 'success' && json.top_match) {
            const top = json.top_match;
            resultBox.innerHTML = `
                <div style="background:rgba(0,242,254,0.08); border:1px solid var(--primary); padding:12px; border-radius:8px;">
                    <div style="display:flex; gap:10px; align-items:center;">
                        <img src="/output_dataset/${top.mugshot_image}" style="width:55px; height:60px; object-fit:cover; border-radius:6px;">
                        <div style="flex:1;">
                            <div style="font-weight:800; color:#fff; font-size:0.95rem;">${top.full_name}</div>
                            <div style="font-size:0.75rem; color:var(--primary);">ID: ${top.criminal_id}</div>
                            <div style="font-size:0.75rem; color:var(--accent-red); font-weight:700;">${top.risk_level} RISK | ${top.wanted_status ? 'WANTED' : 'CLEARED'}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:900; color:var(--primary); font-size:1.1rem;">${top.match_confidence}%</div>
                            <div style="font-size:0.65rem; color:var(--text-dim);">${json.scan_latency_ms}ms</div>
                        </div>
                    </div>

                    <button class="btn btn-primary btn-sm btn-block mt-2" onclick="openCriminalModal('${top.criminal_id}')">
                        <i class="fa-solid fa-folder-open"></i> Open Field File
                    </button>
                </div>
            `;
        }
    } catch (e) {
        console.error("Field photo upload error:", e);
    }
}
