/* ==========================================================================
   MODULE 2: REAL FACE RECOGNITION (USER UPLOADED PHOTO MATCHING)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('face-drop-zone');
    const selectBtn = document.getElementById('btn-select-face-file');
    const fileInput = document.getElementById('face-file-input');
    const resetBtn = document.getElementById('btn-reset-face');
    const previewBox = document.getElementById('face-preview-box');

    if (selectBtn && fileInput) {
        selectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleUserPhotoUpload(e.target.files[0]);
            }
        });
    }

    if (dropZone) {
        dropZone.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--primary)';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'rgba(0, 242, 254, 0.3)';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleUserPhotoUpload(e.dataTransfer.files[0]);
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            previewBox.classList.add('hidden');
            dropZone.classList.remove('hidden');
            document.getElementById('face-match-output').classList.add('hidden');
            document.getElementById('face-match-empty').classList.remove('hidden');
            if (fileInput) fileInput.value = '';
        });
    }
});

async function handleUserPhotoUpload(file) {
    const loading = document.getElementById('face-match-loading');
    const empty = document.getElementById('face-match-empty');
    const output = document.getElementById('face-match-output');
    const previewBox = document.getElementById('face-preview-box');
    const previewImg = document.getElementById('face-preview-img');
    const dropZone = document.getElementById('face-drop-zone');

    // Display local file preview immediately
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImg.src = e.target.result;
        dropZone.classList.add('hidden');
        previewBox.classList.remove('hidden');
    };
    reader.readAsDataURL(file);

    empty.classList.add('hidden');
    output.classList.add('hidden');
    loading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('image', file);

    try {
        const res = await fetch('/api/face-recognition/match', {
            method: 'POST',
            body: formData
        });
        
        const json = await res.json();
        loading.classList.add('hidden');

        if (json.status === 'success' && json.top_match) {
            renderFaceResults(json.top_match, json.matches || []);
            output.classList.remove('hidden');
        }
    } catch (e) {
        console.error("User face upload error:", e);
        loading.classList.add('hidden');
        empty.classList.remove('hidden');
    }
}

function renderFaceResults(top, matches) {
    const topCard = document.getElementById('top-match-card');
    const candidatesList = document.getElementById('candidates-list');

    topCard.innerHTML = `
        <img src="/output_dataset/${top.mugshot_image}" class="top-match-img" alt="${top.full_name}">
        <div style="flex:1;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h3 style="font-family:var(--font-heading); font-size:1.4rem; color:#fff;">${top.full_name}</h3>
                    <p style="color:var(--primary); font-family:var(--font-code); font-size:0.85rem;">ID: ${top.criminal_id} ${top.nickname ? '("' + top.nickname + '")' : ''}</p>
                </div>
                ${top.is_alert ? '<span class="badge badge-wanted" style="font-size:0.8rem; padding:6px 12px;"><i class="fa-solid fa-bell"></i> MATCH ALERT</span>' : ''}
            </div>

            <div style="margin-top:10px;">
                <span class="confidence-gauge">${top.match_confidence}% AI MATCH CONFIDENCE</span>
            </div>

            <div style="display:flex; gap:10px; margin-top:12px; font-size:0.85rem; color:var(--text-muted);">
                <span><i class="fa-solid fa-shield"></i> ${top.criminal_category}</span>
                <span><i class="fa-solid fa-triangle-exclamation"></i> ${top.risk_level} Risk</span>
                <span><i class="fa-solid fa-ruler-horizontal"></i> Vector Dist: ${top.euclidean_distance}</span>
            </div>

            <button class="btn btn-primary btn-sm mt-3" onclick="openCriminalModal('${top.criminal_id}')">
                <i class="fa-solid fa-id-card"></i> Inspect Full Dossier
            </button>
        </div>
    `;

    candidatesList.innerHTML = matches.slice(1, 4).map(c => `
        <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); padding:12px; border-radius:8px; display:flex; align-items:center; gap:12px; margin-top:10px; cursor:pointer;" onclick="openCriminalModal('${c.criminal_id}')">
            <img src="/output_dataset/${c.mugshot_image}" style="width:50px; height:50px; object-fit:cover; border-radius:6px;">
            <div style="flex:1;">
                <div style="font-weight:700; color:#fff; font-size:0.9rem;">${c.full_name}</div>
                <div style="font-size:0.78rem; color:var(--text-muted);">${c.criminal_id} | ${c.criminal_category}</div>
            </div>
            <div style="font-weight:800; color:var(--primary); font-size:0.95rem;">${c.match_confidence}%</div>
        </div>
    `).join('');
}
