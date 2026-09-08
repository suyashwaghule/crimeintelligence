/* ==========================================================================
   FEATURE: REAL CCTV SURVEILLANCE & STREAM FRAME ANALYZER (WITH BASIC AUTH)
   ========================================================================== */

let webcamStream = null;
let mobilePollInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    // Lazy initialized when tab opens
});

window.initCCTVSurveillanceTab = function() {
    const uploadBtn = document.getElementById('btn-cctv-upload');
    const fileInput = document.getElementById('cctv-file-input');
    const webcamBtn = document.getElementById('btn-cctv-webcam');
    const analyzeBtn = document.getElementById('btn-cctv-analyze-frame');
    const mobileModalBtn = document.getElementById('btn-cctv-mobile-modal');
    const closeMobileBtn = document.getElementById('btn-close-mobile-cctv');
    const startMobileListenBtn = document.getElementById('btn-start-listening-mobile');
    const connectIPWebcamBtn = document.getElementById('btn-connect-ip-webcam');

    if (uploadBtn && fileInput && !uploadBtn.dataset.bound) {
        uploadBtn.dataset.bound = 'true';
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleCCTVFileSelected);
    }

    if (webcamBtn && !webcamBtn.dataset.bound) {
        webcamBtn.dataset.bound = 'true';
        webcamBtn.addEventListener('click', startCCTVWebcam);
    }

    if (connectIPWebcamBtn && !connectIPWebcamBtn.dataset.bound) {
        connectIPWebcamBtn.dataset.bound = 'true';
        connectIPWebcamBtn.addEventListener('click', connectAndroidIPWebcamApp);
    }

    if (mobileModalBtn && !mobileModalBtn.dataset.bound) {
        mobileModalBtn.dataset.bound = 'true';
        mobileModalBtn.addEventListener('click', openMobileCCTVModal);
    }

    if (closeMobileBtn && !closeMobileBtn.dataset.bound) {
        closeMobileBtn.dataset.bound = 'true';
        closeMobileBtn.addEventListener('click', closeMobileCCTVModal);
    }

    if (startMobileListenBtn && !startMobileListenBtn.dataset.bound) {
        startMobileListenBtn.dataset.bound = 'true';
        startMobileListenBtn.addEventListener('click', startListeningToMobileCCTV);
    }

    if (analyzeBtn && !analyzeBtn.dataset.bound) {
        analyzeBtn.dataset.bound = 'true';
        analyzeBtn.addEventListener('click', analyzeCurrentCCTVFrame);
    }
};

function connectAndroidIPWebcamApp() {
    const urlInput = document.getElementById('cctv-ip-webcam-url');
    const userInput = document.getElementById('cctv-ip-username');
    const passInput = document.getElementById('cctv-ip-password');
    const statusTag = document.getElementById('cctv-feed-status');
    const placeholder = document.getElementById('cctv-placeholder');
    const videoPlayer = document.getElementById('cctv-video-player');
    const imgPlayer = document.getElementById('cctv-image-player');

    let rawAddress = urlInput ? urlInput.value.trim() : '192.168.1.35:8080';
    let username = userInput ? userInput.value.trim() : '';
    let password = passInput ? passInput.value.trim() : '';

    if (!rawAddress.startsWith('http://') && !rawAddress.startsWith('https://')) {
        rawAddress = 'http://' + rawAddress;
    }

    if (mobilePollInterval) clearInterval(mobilePollInterval);
    stopWebcamStream();

    placeholder.classList.add('hidden');
    videoPlayer.classList.add('hidden');
    imgPlayer.classList.remove('hidden');

    imgPlayer.onerror = null; // Prevent error loops

    statusTag.textContent = `Status: Connecting to IP Webcam stream (${rawAddress})...`;

    async function updateProxyFrame() {
        const proxyUrl = `/api/cctv/proxy_stream?url=${encodeURIComponent(rawAddress)}&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&t=${Date.now()}`;
        imgPlayer.src = proxyUrl;
        
        try {
            const statusRes = await fetch('/api/cctv/mobile_status');
            const statusJson = await statusRes.json();
            if (statusJson.status === 'success' && statusJson.data) {
                renderRealCCTVResults(statusJson.data);
                document.getElementById('cctv-result-empty').classList.add('hidden');
                document.getElementById('cctv-result-output').classList.remove('hidden');
                statusTag.textContent = `Status: Connected LIVE to Android IP Webcam (${rawAddress})`;
            }
        } catch (e) {
            console.error("Status fetch error:", e);
        }
    }

    updateProxyFrame();
    mobilePollInterval = setInterval(updateProxyFrame, 1000);
}

function openMobileCCTVModal() {
    const modal = document.getElementById('mobile-cctv-modal');
    const urlEl = document.getElementById('mobile-cctv-url');
    if (modal) {
        const fullUrl = window.location.origin + '/mobile-cctv';
        urlEl.textContent = fullUrl;
        urlEl.href = fullUrl;
        modal.classList.remove('hidden');
    }
}

function closeMobileCCTVModal() {
    const modal = document.getElementById('mobile-cctv-modal');
    if (modal) modal.classList.add('hidden');
}

function startListeningToMobileCCTV() {
    closeMobileCCTVModal();
    const videoPlayer = document.getElementById('cctv-video-player');
    const imgPlayer = document.getElementById('cctv-image-player');
    const placeholder = document.getElementById('cctv-placeholder');
    const statusTag = document.getElementById('cctv-feed-status');

    placeholder.classList.add('hidden');
    videoPlayer.classList.add('hidden');
    imgPlayer.classList.remove('hidden');
    stopWebcamStream();

    statusTag.textContent = "Status: Receiving Live Mobile Phone CCTV Stream...";

    if (mobilePollInterval) clearInterval(mobilePollInterval);

    mobilePollInterval = setInterval(async () => {
        try {
            imgPlayer.src = '/api/cctv/get_mobile_frame?t=' + Date.now();

            const statusRes = await fetch('/api/cctv/mobile_status');
            const statusJson = await statusRes.json();

            if (statusJson.status === 'success' && statusJson.data) {
                renderRealCCTVResults(statusJson.data);
                document.getElementById('cctv-result-empty').classList.add('hidden');
                document.getElementById('cctv-result-output').classList.remove('hidden');
            }
        } catch (e) {
            console.error("Mobile poll error:", e);
        }
    }, 1000);
}

function handleCCTVFileSelected(e) {
    if (!e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];
    const videoPlayer = document.getElementById('cctv-video-player');
    const imgPlayer = document.getElementById('cctv-image-player');
    const placeholder = document.getElementById('cctv-placeholder');
    const statusTag = document.getElementById('cctv-feed-status');

    placeholder.classList.add('hidden');
    stopWebcamStream();
    if (mobilePollInterval) clearInterval(mobilePollInterval);

    if (file.type.startsWith('video/')) {
        imgPlayer.classList.add('hidden');
        videoPlayer.classList.remove('hidden');
        videoPlayer.src = URL.createObjectURL(file);
        videoPlayer.play();
        statusTag.textContent = `Status: Playing Video "${file.name}"`;
    } else {
        videoPlayer.classList.add('hidden');
        imgPlayer.classList.remove('hidden');
        imgPlayer.src = URL.createObjectURL(file);
        statusTag.textContent = `Status: Loaded Image "${file.name}"`;
    }
}

async function startCCTVWebcam() {
    const videoPlayer = document.getElementById('cctv-video-player');
    const imgPlayer = document.getElementById('cctv-image-player');
    const placeholder = document.getElementById('cctv-placeholder');
    const statusTag = document.getElementById('cctv-feed-status');

    try {
        stopWebcamStream();
        if (mobilePollInterval) clearInterval(mobilePollInterval);

        webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        placeholder.classList.add('hidden');
        imgPlayer.classList.add('hidden');
        videoPlayer.classList.remove('hidden');
        videoPlayer.srcObject = webcamStream;
        videoPlayer.play();
        statusTag.textContent = "Status: Connected Live Device Camera";
    } catch (e) {
        alert("Could not connect to device camera: " + e.message);
    }
}

function stopWebcamStream() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
}

async function analyzeCurrentCCTVFrame() {
    const videoPlayer = document.getElementById('cctv-video-player');
    const imgPlayer = document.getElementById('cctv-image-player');
    const statusTag = document.getElementById('cctv-feed-status');
    const emptyBox = document.getElementById('cctv-result-empty');
    const outputBox = document.getElementById('cctv-result-output');

    statusTag.textContent = "Status: Analyzing video frame against database...";

    let blob = null;

    if (!imgPlayer.classList.contains('hidden') && imgPlayer.src) {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = imgPlayer.naturalWidth || imgPlayer.width || 640;
            canvas.height = imgPlayer.naturalHeight || imgPlayer.height || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(imgPlayer, 0, 0, canvas.width, canvas.height);
            blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
        } catch (e) {
            console.log("Canvas taint fallback, fetching frame via backend proxy...");
            const urlInput = document.getElementById('cctv-ip-webcam-url');
            const userInput = document.getElementById('cctv-ip-username');
            const passInput = document.getElementById('cctv-ip-password');

            const ipAddress = urlInput ? urlInput.value.trim() : '192.168.1.35:8080';
            const username = userInput ? userInput.value.trim() : '';
            const password = passInput ? passInput.value.trim() : '';

            const res = await fetch('/api/cctv/connect_ip_webcam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip_url: ipAddress, username: username, password: password })
            });
            const json = await res.json();
            if (json.status === 'success') {
                renderRealCCTVResults(json.data);
                emptyBox.classList.add('hidden');
                outputBox.classList.remove('hidden');
                statusTag.textContent = "Status: Analysis Complete";
                return;
            } else {
                alert(json.message);
                return;
            }
        }
    } else if (!videoPlayer.classList.contains('hidden')) {
        const canvas = document.appendCanvas ? document.createElement('canvas') : document.createElement('canvas');
        canvas.width = videoPlayer.videoWidth || 640;
        canvas.height = videoPlayer.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
        blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    }

    if (!blob) {
        alert("Please upload a video/image file or connect a camera stream first.");
        return;
    }

    const formData = new FormData();
    formData.append('image', blob);

    try {
        const res = await fetch('/api/cctv/analyze', {
            method: 'POST',
            body: formData
        });

        const json = await res.json();
        statusTag.textContent = "Status: Analysis Complete";

        if (json.status === 'success') {
            renderRealCCTVResults(json.data);
            emptyBox.classList.add('hidden');
            outputBox.classList.remove('hidden');
        }
    } catch (e) {
        console.error("CCTV frame analysis error:", e);
    }
}

function renderRealCCTVResults(data) {
    const outputBox = document.getElementById('cctv-result-output');
    const top = data.top_match;

    if (data.threat_detected && top) {
        outputBox.innerHTML = `
            <div style="background:rgba(255,0,85,0.12); border:2px solid var(--accent-red); padding:14px; border-radius:8px;">
                <div style="color:var(--accent-red); font-weight:800; font-size:1.1rem; margin-bottom:8px;">
                    <i class="fa-solid fa-triangle-exclamation fa-bounce"></i> WANTED FUGITIVE MATCH DETECTED!
                </div>
                
                <div style="display:flex; gap:12px; align-items:center;">
                    <img src="/output_dataset/${top.mugshot_image}" style="width:65px; height:75px; object-fit:cover; border-radius:6px; border:2px solid var(--accent-red);">
                    <div style="flex:1;">
                        <h4 style="color:#fff; margin:0; font-size:1.05rem;">${top.full_name}</h4>
                        <div style="color:var(--primary); font-size:0.8rem;">ID: ${top.criminal_id} ${top.nickname ? '("' + top.nickname + '")' : ''}</div>
                        <div style="font-size:0.8rem; color:var(--accent-red); font-weight:700;">${top.risk_level} RISK LEVEL | WANTED</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:900; color:var(--accent-red); font-size:1.3rem;">${top.match_confidence}%</div>
                        <div style="font-size:0.68rem; color:var(--text-dim);">${data.processing_latency_ms}ms</div>
                    </div>
                </div>

                <button class="btn btn-primary btn-sm btn-block mt-3" onclick="openCriminalModal('${top.criminal_id}')">
                    <i class="fa-solid fa-passport"></i> Open Full Dossier File
                </button>
            </div>
        `;
    } else if (top) {
        outputBox.innerHTML = `
            <div style="background:rgba(0,242,254,0.06); border:1px solid var(--primary); padding:14px; border-radius:8px;">
                <div style="color:var(--primary); font-weight:700; font-size:0.95rem; margin-bottom:8px;">
                    <i class="fa-solid fa-circle-info"></i> Closest Database Candidate Match
                </div>
                <div style="display:flex; gap:12px; align-items:center;">
                    <img src="/output_dataset/${top.mugshot_image}" style="width:55px; height:60px; object-fit:cover; border-radius:6px;">
                    <div style="flex:1;">
                        <h4 style="color:#fff; margin:0; font-size:0.95rem;">${top.full_name}</h4>
                        <div style="color:var(--text-muted); font-size:0.78rem;">ID: ${top.criminal_id} | ${top.criminal_category}</div>
                    </div>
                    <div style="font-weight:800; color:var(--primary); font-size:1.1rem;">${top.match_confidence}%</div>
                </div>
                <button class="btn btn-secondary btn-sm btn-block mt-2" onclick="openCriminalModal('${top.criminal_id}')">
                    <i class="fa-solid fa-folder-open"></i> Inspect Dossier
                </button>
            </div>
        `;
    }
}
