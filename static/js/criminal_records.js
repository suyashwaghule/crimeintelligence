/* ==========================================================================
   MODULE 1: CRIMINAL RECORD MANAGEMENT, COMPREHENSIVE FORM & EDITOR
   ========================================================================== */

let criminalDataCache = [];

window.loadCriminalRecords = async function() {
    const searchInput = document.getElementById('criminal-search-input');
    const categorySelect = document.getElementById('filter-category');
    const riskSelect = document.getElementById('filter-risk');
    const wantedSelect = document.getElementById('filter-wanted');
    const openAddBtn = document.getElementById('btn-open-add-modal');
    const closeAddBtn = document.getElementById('btn-close-add-modal');
    const addModal = document.getElementById('add-criminal-modal');
    const addForm = document.getElementById('add-criminal-form');
    
    if (searchInput && !searchInput.dataset.initialized) {
        searchInput.dataset.initialized = 'true';
        searchInput.addEventListener('input', debounce(fetchCriminals, 300));
        categorySelect.addEventListener('change', fetchCriminals);
        riskSelect.addEventListener('change', fetchCriminals);
        wantedSelect.addEventListener('change', fetchCriminals);
        
        if (openAddBtn && addModal) {
            openAddBtn.addEventListener('click', () => openAddCriminalModal());
        }
        if (closeAddBtn && addModal) {
            closeAddBtn.addEventListener('click', () => addModal.classList.add('hidden'));
        }
        if (addModal) {
            addModal.addEventListener('click', (e) => {
                if (e.target === addModal) addModal.classList.add('hidden');
            });
        }
        if (addForm) {
            addForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await handleSaveCriminalSubmit(addForm, addModal);
            });
        }
    }

    await fetchCriminals();
};

function openAddCriminalModal() {
    const modal = document.getElementById('add-criminal-modal');
    const form = document.getElementById('add-criminal-form');
    const title = document.getElementById('modal-form-title');
    const editIdInput = document.getElementById('editing_criminal_id');

    form.reset();
    editIdInput.value = '';
    title.innerHTML = `<i class="fa-solid fa-user-plus" style="color:var(--primary);"></i> Register New Criminal Dossier`;
    modal.classList.remove('hidden');
}

window.openEditCriminalModal = async function(criminalId) {
    const modal = document.getElementById('add-criminal-modal');
    const form = document.getElementById('add-criminal-form');
    const title = document.getElementById('modal-form-title');
    const editIdInput = document.getElementById('editing_criminal_id');
    const viewModal = document.getElementById('criminal-modal');
    
    if (viewModal) viewModal.classList.add('hidden');

    title.innerHTML = `<i class="fa-solid fa-pen-to-square" style="color:var(--primary);"></i> Edit Criminal Dossier — ${criminalId}`;
    editIdInput.value = criminalId;

    try {
        const res = await fetch(`/api/criminals/${criminalId}`);
        const json = await res.json();
        
        if (json.status === 'success') {
            const c = json.data;
            const mo = c.modus_operandi || {};

            setInputValue('form-first_name', c.first_name || '');
            setInputValue('form-last_name', c.last_name || '');
            setInputValue('form-nickname', c.nickname || '');
            setInputValue('form-age', c.age || 28);
            setInputValue('form-gender', c.gender || 'Male');
            setInputValue('form-dob', c.dob || '1996-01-01');
            setInputValue('form-blood_group', c.blood_group || 'O+');
            setInputValue('form-phone_number', c.phone_number || '');
            setInputValue('form-aadhaar_number', c.aadhaar_number || '');
            setInputValue('form-passport_number', c.passport_number || '');
            setInputValue('form-area_name', c.area_name || 'Shivajinagar');
            setInputValue('form-address', c.address || '');
            setInputValue('form-criminal_category', c.criminal_category || 'Violent');
            setInputValue('form-risk_level', c.risk_level || 'High');
            setInputValue('form-gang_name', c.gang_name || '');
            setInputValue('form-gang_role', c.gang_role || '');
            setInputValue('form-height_cm', c.height_cm || 172);
            setInputValue('form-weight_kg', c.weight_kg || 68);
            setInputValue('form-body_marks', c.body_marks || '');
            setInputValue('form-preferred_weapon', c.preferred_weapon || 'Knife');
            setInputValue('form-entry_method', mo.entry_method || 'Door break');
            setInputValue('form-bail_status', c.bail_status || 'On Bail');
            setInputValue('form-crime_style', c.crime_style || '');

            const wantedChk = document.getElementById('form-wanted_status');
            if (wantedChk) wantedChk.checked = c.wanted_status === 1;

            modal.classList.remove('hidden');
        }
    } catch (e) {
        console.error("Error fetching criminal for edit:", e);
    }
};

function setInputValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
}

async function handleSaveCriminalSubmit(form, modal) {
    const formData = new FormData(form);
    const editId = document.getElementById('editing_criminal_id').value;

    const url = editId ? `/api/criminals/edit/${editId}` : '/api/criminals/add';

    try {
        const res = await fetch(url, {
            method: 'POST',
            body: formData
        });

        const json = await res.json();

        if (json.status === 'success') {
            alert(`✅ Criminal Dossier ${json.criminal_id} successfully saved and re-indexed into PostgreSQL pgvector!`);
            modal.classList.add('hidden');
            form.reset();
            await fetchCriminals();
        } else {
            alert(`Error saving criminal: ${json.message}`);
        }
    } catch (e) {
        console.error("Save criminal submit error:", e);
    }
}

async function fetchCriminals() {
    const query = document.getElementById('criminal-search-input').value.trim();
    const category = document.getElementById('filter-category').value;
    const risk = document.getElementById('filter-risk').value;
    const wanted = document.getElementById('filter-wanted').value;

    const url = `/api/criminals?query=${encodeURIComponent(query)}&category=${category}&risk=${risk}&wanted=${wanted}&limit=60`;
    
    try {
        const res = await fetch(url);
        const json = await res.json();
        
        if (json.status === 'success') {
            criminalDataCache = json.data;
            renderCriminalCards(json.data);
        }
    } catch (e) {
        console.error("Error fetching criminals:", e);
    }
}

function renderCriminalCards(criminals) {
    const container = document.getElementById('criminal-cards-container');
    if (!container) return;
    
    if (criminals.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <i class="fa-solid fa-user-slash" style="font-size: 2.5rem; color: var(--text-dim); margin-bottom: 12px;"></i>
                <p>No criminal records matched the search filters.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = criminals.map(c => `
        <div class="criminal-card">
            <div class="card-top" onclick="openCriminalModal('${c.criminal_id}')">
                <img src="/output_dataset/${c.mugshot_image || c.face_image_path}" 
                     alt="${c.full_name}" 
                     onerror="this.src='https://via.placeholder.com/250x250/0f172a/94a3b8?text=No+Photo'">
                <div class="card-badges">
                    ${c.wanted_status ? '<span class="badge badge-wanted">WANTED</span>' : ''}
                    <span class="badge badge-${(c.risk_level || 'low').toLowerCase()}">${c.risk_level || 'Low'} Risk</span>
                </div>
            </div>
            
            <div class="card-body">
                <div onclick="openCriminalModal('${c.criminal_id}')">
                    <h4 class="card-name">${c.full_name}</h4>
                    <div class="card-alias">${c.nickname ? 'Alias: "' + c.nickname + '"' : 'ID: ' + c.criminal_id}</div>
                </div>

                <div class="card-meta">
                    <div class="card-meta-item"><i class="fa-solid fa-cake-candles"></i> Age: ${c.age || 'N/A'}</div>
                    <div class="card-meta-item"><i class="fa-solid fa-handcuffs"></i> Arrests: ${c.arrest_count || 0}</div>
                    <div class="card-meta-item"><i class="fa-solid fa-masks-theater"></i> ${c.most_common_crime || 'General'}</div>
                    <div class="card-meta-item"><i class="fa-solid fa-location-dot"></i> ${c.area_name || 'Pune'}</div>
                </div>

                <div style="display:flex; gap:8px; margin-top:10px;">
                    <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="openCriminalModal('${c.criminal_id}')">
                        <i class="fa-solid fa-passport"></i> View
                    </button>
                    <button class="btn btn-primary btn-sm" style="flex:1;" onclick="openEditCriminalModal('${c.criminal_id}')">
                        <i class="fa-solid fa-pen-to-square"></i> Edit
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

window.openCriminalModal = async function(criminalId) {
    const modal = document.getElementById('criminal-modal');
    const content = document.getElementById('modal-content');
    
    modal.classList.remove('hidden');
    content.innerHTML = `<div style="text-align:center; padding:40px;"><div class="spinner"></div><p>Retrieving Criminal Profile ${criminalId}...</p></div>`;

    try {
        const res = await fetch(`/api/criminals/${criminalId}`);
        const json = await res.json();
        
        if (json.status === 'success') {
            const c = json.data;
            const mo = c.modus_operandi || {};
            const crimes = c.crimes || [];
            
            content.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
                    <div style="display:flex; gap:20px; align-items:flex-start;">
                        <img src="/output_dataset/${c.mugshot_image}" style="width:150px; height:170px; object-fit:cover; border-radius:10px; border:2px solid var(--primary);">
                        <div>
                            <h2 style="font-family:var(--font-heading); color:#fff; font-size:1.5rem;">${c.full_name} ${c.nickname ? '("' + c.nickname + '")' : ''}</h2>
                            <p style="color:var(--primary); font-family:var(--font-code); font-size:0.85rem; margin-bottom:8px;">ID: ${c.criminal_id} | Aadhaar: ${c.aadhaar_number || 'N/A'}</p>
                            <div style="display:flex; gap:8px; margin-bottom:10px;">
                                ${c.wanted_status ? '<span class="badge badge-wanted">WANTED</span>' : ''}
                                <span class="badge badge-${(c.risk_level || 'low').toLowerCase()}">${c.risk_level} Risk Level</span>
                                <span class="badge badge-medium">${c.criminal_category}</span>
                            </div>
                            <p style="font-size:0.82rem; color:var(--text-muted);"><i class="fa-solid fa-house"></i> ${c.address}</p>
                        </div>
                    </div>

                    <button class="btn btn-primary btn-sm" onclick="openEditCriminalModal('${c.criminal_id}')">
                        <i class="fa-solid fa-pen-to-square"></i> Edit Dossier
                    </button>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px; background:rgba(255,255,255,0.03); padding:14px; border-radius:8px; font-size:0.85rem;">
                    <div><strong>Gender / Age:</strong> ${c.gender}, ${c.age} yrs (DOB: ${c.dob || 'N/A'})</div>
                    <div><strong>Blood Group:</strong> ${c.blood_group || 'O+'}</div>
                    <div><strong>Height / Weight:</strong> ${c.height_cm || 172} cm / ${c.weight_kg || 70} kg</div>
                    <div><strong>Gang Affiliation:</strong> ${c.gang_name ? c.gang_name + ' (' + c.gang_role + ')' : 'None'}</div>
                    <div><strong>Arrests / Convictions:</strong> ${c.arrest_count} / ${c.conviction_count}</div>
                    <div><strong>Bail Status:</strong> ${c.bail_status || 'Released'}</div>
                    <div style="grid-column: 1 / -1;"><strong>Body Marks / Scars:</strong> ${c.body_marks || 'None recorded'}</div>
                </div>

                <h4 style="color:var(--primary); margin-bottom:8px;"><i class="fa-solid fa-brain"></i> Modus Operandi (MO) Profile</h4>
                <div style="background:rgba(0,242,254,0.04); border:1px solid rgba(0,242,254,0.2); padding:12px; border-radius:8px; margin-bottom:16px; font-size:0.83rem; line-height:1.5;">
                    <div><strong>Preferred Crime:</strong> ${mo.crime_type || c.most_common_crime}</div>
                    <div><strong>Weapon Used:</strong> ${mo.weapon_used || c.preferred_weapon} | <strong>Entry Method:</strong> ${mo.entry_method || 'N/A'}</div>
                    <div><strong>Timing:</strong> ${mo.crime_timing || 'Night'} | <strong>Vehicle:</strong> ${mo.vehicle_used || 'Bike'}</div>
                    <div><strong>Repeat Behavior:</strong> ${mo.repeat_pattern || c.crime_style}</div>
                </div>

                <h4 style="color:#fff; margin-bottom:8px;"><i class="fa-solid fa-history"></i> Recent FIR History (${crimes.length} offenses)</h4>
                <div style="max-height:160px; overflow-y:auto; display:flex; flex-direction:column; gap:6px;">
                    ${crimes.map(cr => `
                        <div style="background:rgba(255,255,255,0.03); padding:8px; border-radius:6px; font-size:0.8rem; display:flex; justify-content:space-between;">
                            <div>
                                <strong style="color:var(--primary);">${cr.fir_number}</strong> — ${cr.crime_type} (${cr.crime_subtype})
                                <div style="color:var(--text-muted); font-size:0.75rem;">${cr.area_name} on ${cr.crime_date}</div>
                            </div>
                            <span class="badge ${cr.case_status === 'Solved' ? 'badge-low' : 'badge-wanted'}">${cr.case_status}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (e) {
        console.error("Error opening criminal modal:", e);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('criminal-modal');
    const closeBtn = document.getElementById('btn-close-modal');
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    }
});

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
