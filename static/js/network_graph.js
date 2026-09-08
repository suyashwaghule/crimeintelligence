/* ==========================================================================
   FEATURE: GANG NETWORK & LINK ANALYSIS GRAPH (STRICT 2-COLOR LIGHT THEME)
   ========================================================================== */

let networkInstance = null;
let rawNodesCache = [];
let rawEdgesCache = [];
let isPhysicsEnabled = true;

window.initNetworkGraphTab = async function() {
    await initGangNetworkGraph();
};

window.initGangNetworkGraph = async function() {
    const container = document.getElementById('network-graph-container');
    const gangSelect = document.getElementById('network-gang-select');
    const roleSelect = document.getElementById('network-role-filter');
    const recenterBtn = document.getElementById('btn-graph-recenter');
    const physicsBtn = document.getElementById('btn-graph-physics');

    if (!container) return;

    if (gangSelect && !gangSelect.dataset.bound) {
        gangSelect.dataset.bound = 'true';
        gangSelect.addEventListener('change', () => loadGangNetworkData());
    }

    if (roleSelect && !roleSelect.dataset.bound) {
        roleSelect.dataset.bound = 'true';
        roleSelect.addEventListener('change', filterNetworkNodes);
    }

    if (recenterBtn && !recenterBtn.dataset.bound) {
        recenterBtn.dataset.bound = 'true';
        recenterBtn.addEventListener('click', () => {
            if (networkInstance) networkInstance.fit({ animation: { duration: 600 } });
        });
    }

    if (physicsBtn && !physicsBtn.dataset.bound) {
        physicsBtn.dataset.bound = 'true';
        physicsBtn.addEventListener('click', toggleGraphPhysics);
    }

    await loadGangNetworkData();
};

async function loadGangNetworkData() {
    const gangSelect = document.getElementById('network-gang-select');
    const selectedGang = gangSelect ? gangSelect.value : 'All';

    try {
        const res = await fetch(`/api/graph/network?gang=${encodeURIComponent(selectedGang)}&limit=150`);
        const json = await res.json();

        if (json.status === 'success') {
            const data = json.data;
            populateGangDropdown(data.gangs);
            rawNodesCache = data.nodes || [];
            rawEdgesCache = data.edges || [];
            filterNetworkNodes();
        }
    } catch (e) {
        console.error("Gang network graph load error:", e);
    }
}

function populateGangDropdown(gangs) {
    const select = document.getElementById('network-gang-select');
    if (!select || select.children.length > 1) return;

    gangs.forEach(g => {
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = `Gang: ${g}`;
        select.appendChild(opt);
    });
}

function toggleGraphPhysics() {
    const icon = document.getElementById('icon-graph-physics');
    const physicsBtn = document.getElementById('btn-graph-physics');

    isPhysicsEnabled = !isPhysicsEnabled;
    if (networkInstance) {
        networkInstance.setOptions({ physics: { enabled: isPhysicsEnabled } });
    }

    if (isPhysicsEnabled) {
        if (icon) icon.className = 'fa-solid fa-pause';
        if (physicsBtn) physicsBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Freeze Physics`;
    } else {
        if (icon) icon.className = 'fa-solid fa-play';
        if (physicsBtn) physicsBtn.innerHTML = `<i class="fa-solid fa-play"></i> Enable Physics`;
    }
}

function filterNetworkNodes() {
    const roleFilter = document.getElementById('network-role-filter')?.value || 'All';

    let filteredNodes = rawNodesCache;

    if (roleFilter === 'Leader') {
        filteredNodes = rawNodesCache.filter(n => 
            n.group === 'Gang' || (n.title && n.title.toLowerCase().includes('leader'))
        );
    } else if (roleFilter === 'Wanted') {
        filteredNodes = rawNodesCache.filter(n => 
            n.group === 'Gang' || n.wanted_status === 1
        );
    } else if (roleFilter === 'HighRisk') {
        filteredNodes = rawNodesCache.filter(n => 
            n.group === 'Gang' || (n.risk_level === 'Critical' || n.risk_level === 'High')
        );
    }

    const validNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = rawEdgesCache.filter(e => validNodeIds.has(e.from) && validNodeIds.has(e.to));

    renderVisNetwork(filteredNodes, filteredEdges);
}

function renderVisNetwork(nodesArray, edgesArray) {
    const container = document.getElementById('network-graph-container');
    if (!container) return;

    // Strict 2-Color Node Encodings (#0f172a Navy & #ffffff White)
    const styledNodes = nodesArray.map(node => {
        if (node.group === 'Gang') {
            return {
                ...node,
                size: 32,
                font: { color: '#0f172a', face: 'Outfit', size: 13, bold: true },
                color: { background: '#ffffff', border: '#0f172a' }
            };
        }

        const isLeader = node.title && node.title.toLowerCase().includes('leader');

        return {
            ...node,
            size: isLeader ? 28 : 22,
            borderWidth: isLeader ? 3 : 2,
            color: {
                border: '#0f172a',
                background: '#ffffff'
            },
            font: { color: '#0f172a', face: 'Inter', size: 11 }
        };
    });

    const nodes = new vis.DataSet(styledNodes);
    const edges = new vis.DataSet(edgesArray);

    const data = { nodes: nodes, edges: edges };

    const options = {
        nodes: {
            shape: 'circularImage',
            borderWidthSelected: 4,
            color: {
                highlight: { border: '#0f172a', background: '#f1f5f9' }
            }
        },
        edges: {
            width: 1.5,
            color: { color: 'rgba(15, 23, 42, 0.4)', highlight: '#0f172a' },
            smooth: { type: 'continuous' }
        },
        physics: {
            enabled: isPhysicsEnabled,
            stabilization: { iterations: 100 },
            barnesHut: {
                gravitationalConstant: -2500,
                centralGravity: 0.3,
                springLength: 90
            }
        },
        interaction: { hover: true, tooltipDelay: 150 }
    };

    if (networkInstance) networkInstance.destroy();
    networkInstance = new vis.Network(container, data, options);

    networkInstance.on("selectNode", function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            renderNodeIntelCard(nodeId, styledNodes, edgesArray);
        }
    });

    networkInstance.on("doubleClick", function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            if (!nodeId.startsWith('gang_') && window.openCriminalModal) {
                window.openCriminalModal(nodeId);
            }
        }
    });
}

function renderNodeIntelCard(nodeId, nodes, edges) {
    const emptyBox = document.getElementById('graph-intel-empty');
    const detailsBox = document.getElementById('graph-intel-details');
    if (!detailsBox) return;

    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    emptyBox.classList.add('hidden');
    detailsBox.classList.remove('hidden');

    if (node.group === 'Gang') {
        const memberEdges = edges.filter(e => e.to === nodeId || e.from === nodeId);
        detailsBox.innerHTML = `
            <div style="background:#f8fafc; border:1px solid #0f172a; padding:16px; border-radius:var(--radius-md); margin-bottom:14px; text-align:center;">
                <i class="fa-solid fa-hexagon" style="font-size:2.5rem; color:#0f172a; margin-bottom:8px;"></i>
                <h3 style="color:#0f172a; font-family:var(--font-heading); font-size:1.3rem;">${node.label}</h3>
                <p style="font-size:0.82rem; color:var(--text-muted);">Active Gang Syndicate in Pune</p>
                <div style="margin-top:10px; font-weight:700; color:#0f172a;">${memberEdges.length} Identified Members</div>
            </div>

            <h4 style="font-size:0.85rem; color:var(--text-muted); margin-bottom:8px;">Syndicate Roster:</h4>
            <div style="flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:6px;">
                ${memberEdges.map(e => {
                    const memberId = e.from === nodeId ? e.to : e.from;
                    const memberNode = nodes.find(n => n.id === memberId);
                    if (!memberNode) return '';
                    return `
                        <div style="background:#ffffff; border:1px solid #e2e8f0; padding:8px 10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="openCriminalModal('${memberNode.id}')">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <img src="${memberNode.image}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;">
                                <div>
                                    <div style="font-weight:600; color:#0f172a; font-size:0.82rem;">${memberNode.label}</div>
                                    <div style="font-size:0.72rem; color:#0f172a;">${e.label || 'Member'}</div>
                                </div>
                            </div>
                            <i class="fa-solid fa-chevron-right" style="color:#0f172a; font-size:0.75rem;"></i>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } else {
        const connectedEdges = edges.filter(e => e.from === nodeId || e.to === nodeId);
        detailsBox.innerHTML = `
            <div style="background:#ffffff; border:1px solid #e2e8f0; padding:14px; border-radius:var(--radius-md); margin-bottom:14px;">
                <div style="display:flex; gap:12px; align-items:center; margin-bottom:12px;">
                    <img src="${node.image}" style="width:65px; height:75px; object-fit:cover; border-radius:var(--radius-sm); border:2px solid #0f172a;">
                    <div>
                        <h4 style="color:#0f172a; font-family:var(--font-heading); font-size:1.1rem; margin-bottom:2px;">${node.label}</h4>
                        <div style="font-family:var(--font-code); font-size:0.78rem; color:#0f172a;">ID: ${node.id}</div>
                        <div style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">Risk Level: <strong style="color:#0f172a;">${node.risk_level}</strong></div>
                    </div>
                </div>

                <div style="font-size:0.8rem; color:var(--text-muted); display:flex; flex-direction:column; gap:4px; border-top:1px solid #e2e8f0; padding-top:10px;">
                    <div><i class="fa-solid fa-diagram-nested" style="color:#0f172a;"></i> Connected Links: <strong>${connectedEdges.length} accomplices</strong></div>
                </div>

                <button class="btn btn-primary btn-sm btn-block mt-3" onclick="openCriminalModal('${node.id}')">
                    <i class="fa-solid fa-passport"></i> Open Full Criminal Dossier
                </button>
            </div>

            <h4 style="font-size:0.85rem; color:var(--text-muted); margin-bottom:8px;">Linked Connections:</h4>
            <div style="flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:6px;">
                ${connectedEdges.map(e => {
                    const otherId = e.from === nodeId ? e.to : e.from;
                    const otherNode = nodes.find(n => n.id === otherId);
                    if (!otherNode) return '';
                    return `
                        <div style="background:#ffffff; border:1px solid #e2e8f0; padding:8px 10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="if('${otherNode.id}'.startsWith('gang_')) {} else { openCriminalModal('${otherNode.id}'); }">
                            <div style="display:flex; align-items:center; gap:8px;">
                                ${otherNode.group === 'Gang' ? '<i class="fa-solid fa-hexagon" style="color:#0f172a; font-size:1.2rem;"></i>' : `<img src="${otherNode.image}" style="width:30px; height:30px; border-radius:50%; object-fit:cover;">`}
                                <div>
                                    <div style="font-weight:600; color:#0f172a; font-size:0.8rem;">${otherNode.label}</div>
                                    <div style="font-size:0.7rem; color:#0f172a;">${e.label || 'Connection'}</div>
                                </div>
                            </div>
                            <i class="fa-solid fa-chevron-right" style="color:#0f172a; font-size:0.75rem;"></i>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
}
