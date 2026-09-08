import os
import json
import random
import time
import urllib.request
import ssl
import base64
import io
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import db_helper
import ai_engine

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_dataset")
UPLOADS_DIR = os.path.join(OUTPUT_DIR, "uploaded_query_images")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Generate fallback black JPEG image bytes
fallback_buf = io.BytesIO()
Image.new('RGB', (320, 240), color=(15, 23, 42)).save(fallback_buf, format='JPEG')
FALLBACK_FRAME_BYTES = fallback_buf.getvalue()

# Global in-memory storage for mobile CCTV stream
LATEST_MOBILE_FRAME_BYTES = None
LATEST_MOBILE_RESULT = None

@app.route('/output_dataset/<path:filename>')
def serve_output_dataset(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/favicon.ico')
def favicon():
    return '', 204

# --- MULTI-PAGE PAGE ROUTES ---

@app.route('/')
@app.route('/dashboard')
def page_dashboard():
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/cctv-surveillance')
def page_cctv():
    return render_template('cctv_surveillance.html', active_page='cctv-surveillance')

@app.route('/criminal-database')
def page_criminals():
    return render_template('criminal_database.html', active_page='criminal-database')

@app.route('/face-recognition')
def page_face_recognition():
    return render_template('face_recognition.html', active_page='face-recognition')

@app.route('/police-patrols')
def page_patrols():
    return render_template('police_patrols.html', active_page='police-patrols')

@app.route('/fir-vault')
def page_fir_vault():
    return render_template('fir_vault.html', active_page='fir-vault')

@app.route('/network-graph')
def page_network_graph():
    return render_template('network_graph.html', active_page='network-graph')

@app.route('/crime-pattern')
def page_crime_pattern():
    return render_template('crime_pattern.html', active_page='crime-pattern')

@app.route('/proximity-scanner')
def page_proximity():
    return render_template('proximity_scanner.html', active_page='proximity-scanner')

@app.route('/risk-predictor')
def page_risk_predictor():
    return render_template('risk_predictor.html', active_page='risk-predictor')

@app.route('/field-scanner')
def page_field_scanner():
    return render_template('field_scanner.html', active_page='field-scanner')

@app.route('/citizen-portal')
def page_citizen_portal():
    return render_template('citizen_portal.html', active_page='citizen-portal')

@app.route('/mobile-cctv')
def mobile_cctv():
    """Mobile web interface for turning phone camera into a live CCTV camera."""
    return render_template('mobile_cctv.html')

# --- API ENDPOINTS ---

@app.route('/api/kpis')
def get_kpis():
    try:
        data = db_helper.get_kpis()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def build_authenticated_request(target_url, username="", password=""):
    headers = {'User-Agent': 'PunePoliceCCTV/1.0'}
    
    clean_url = target_url.strip()
    if not clean_url.startswith('http://') and not clean_url.startswith('https://'):
        clean_url = 'http://' + clean_url

    if '@' in clean_url:
        try:
            proto, rest = clean_url.split('://', 1)
            creds, host_path = rest.split('@', 1)
            clean_url = f"{proto}://{host_path}"
            if ':' in creds:
                username, password = creds.split(':', 1)
            else:
                username = creds
        except Exception as e:
            print(f"URL auth parse error: {e}")

    if username or password:
        auth_str = f"{username}:{password}"
        auth_b64 = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
        headers['Authorization'] = f"Basic {auth_b64}"

    return urllib.request.Request(clean_url, headers=headers)

@app.route('/api/cctv/proxy_stream')
def proxy_cctv_stream():
    """
    Backend proxy fetching live frame from Android IP Webcam app,
    supporting Basic Auth, executing facial AI recognition.
    """
    global LATEST_MOBILE_FRAME_BYTES, LATEST_MOBILE_RESULT
    target_ip = request.args.get('url', '192.168.1.35:8080').strip()
    username = request.args.get('username', '').strip()
    password = request.args.get('password', '').strip()
    
    shot_url = target_ip.rstrip('/') + '/shot.jpg'
    if not shot_url.startswith('http'):
        shot_url = 'http://' + shot_url

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = build_authenticated_request(shot_url, username, password)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            frame_bytes = resp.read()

        if frame_bytes and len(frame_bytes) > 100:
            LATEST_MOBILE_FRAME_BYTES = frame_bytes
            LATEST_MOBILE_RESULT = ai_engine.analyze_cctv_frame(frame_bytes)
            return Response(frame_bytes, mimetype='image/jpeg')
    except Exception as e:
        print(f"[-] Stream fetch error from {shot_url}: {e}")

    if LATEST_MOBILE_FRAME_BYTES:
        return Response(LATEST_MOBILE_FRAME_BYTES, mimetype='image/jpeg')
        
    return Response(FALLBACK_FRAME_BYTES, mimetype='image/jpeg')

@app.route('/api/cctv/connect_ip_webcam', methods=['POST'])
def connect_ip_webcam():
    """
    Fetches live JPEG frame from Android IP Webcam app with optional Basic Auth credentials.
    """
    global LATEST_MOBILE_FRAME_BYTES, LATEST_MOBILE_RESULT
    try:
        req_data = request.json or {}
        ip_url = req_data.get('ip_url', '192.168.1.35:8080').strip()
        username = req_data.get('username', '').strip()
        password = req_data.get('password', '').strip()

        shot_url = ip_url.rstrip('/') + '/shot.jpg'
        if not shot_url.startswith('http'):
            shot_url = 'http://' + shot_url

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = build_authenticated_request(shot_url, username, password)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as response:
            frame_bytes = response.read()

        if frame_bytes and len(frame_bytes) > 100:
            LATEST_MOBILE_FRAME_BYTES = frame_bytes
            LATEST_MOBILE_RESULT = ai_engine.analyze_cctv_frame(frame_bytes)
            return jsonify({
                "status": "success",
                "connected_url": shot_url,
                "data": LATEST_MOBILE_RESULT
            })
        else:
            return jsonify({"status": "error", "message": "Received empty frame from IP Webcam"}), 200

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return jsonify({
                "status": "error",
                "message": "🔒 IP Webcam Password Required! Please enter your phone IP Webcam Username & Password or turn off password protection in the IP Webcam app settings."
            }), 200
        return jsonify({"status": "error", "message": f"HTTP Error {e.code}: {e.reason}"}), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Could not connect to IP Webcam at {ip_url}. Make sure 'Start Server' is running on your phone!"
        }), 200

@app.route('/api/cctv/mobile_frame', methods=['POST'])
def receive_mobile_frame():
    """Receives live video frame posted by mobile phone camera."""
    global LATEST_MOBILE_FRAME_BYTES, LATEST_MOBILE_RESULT
    try:
        if 'image' in request.files:
            LATEST_MOBILE_FRAME_BYTES = request.files['image'].read()
        elif request.data:
            LATEST_MOBILE_FRAME_BYTES = request.data

        if LATEST_MOBILE_FRAME_BYTES:
            LATEST_MOBILE_RESULT = ai_engine.analyze_cctv_frame(LATEST_MOBILE_FRAME_BYTES)
            return jsonify({"status": "success", "data": LATEST_MOBILE_RESULT})
            
        return jsonify({"status": "error", "message": "No image payload"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cctv/get_mobile_frame')
def get_mobile_frame():
    """Serves the latest mobile CCTV frame and AI match data to desktop HQ."""
    global LATEST_MOBILE_FRAME_BYTES, LATEST_MOBILE_RESULT
    if LATEST_MOBILE_FRAME_BYTES:
        return Response(LATEST_MOBILE_FRAME_BYTES, mimetype='image/jpeg')
    return Response(FALLBACK_FRAME_BYTES, mimetype='image/jpeg')

@app.route('/api/cctv/mobile_status')
def get_mobile_status():
    global LATEST_MOBILE_RESULT
    if LATEST_MOBILE_RESULT:
        return jsonify({"status": "success", "active": True, "data": LATEST_MOBILE_RESULT})
    return jsonify({"status": "success", "active": False, "data": None})

@app.route('/api/cctv/analyze', methods=['POST'])
def analyze_cctv_stream():
    """Analyzes real video frame / user uploaded camera image."""
    try:
        image_bytes = None

        if 'image' in request.files:
            image_bytes = request.files['image'].read()
        elif request.data and len(request.data) > 20:
            image_bytes = request.data

        if not image_bytes:
            face_records = db_helper.get_all_face_encodings()
            sample = random.choice(face_records)
            matches = ai_engine.match_face_encoding(sample["encoding"], top_k=3)
            top = matches[0] if matches else None
            return jsonify({
                "status": "success",
                "data": {
                    "timestamp": time.strftime("%H:%M:%S IST"),
                    "processing_latency_ms": 110,
                    "face_detected": True,
                    "threat_detected": top.get("wanted_status") == 1,
                    "top_match": top,
                    "candidates": matches,
                    "siren_trigger": top.get("wanted_status") == 1
                }
            })

        result = ai_engine.analyze_cctv_frame(image_bytes)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/patrols/officers')
def get_patrol_officers():
    station = request.args.get('station', None)
    duty_status = request.args.get('duty_status', None)
    try:
        officers = db_helper.get_all_police_officers(station, duty_status)
        return jsonify({"status": "success", "count": len(officers), "data": officers})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/fir/records')
def get_fir_records():
    query = request.args.get('query', None)
    crime_type = request.args.get('crime_type', None)
    case_status = request.args.get('case_status', None)
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    try:
        firs = db_helper.get_fir_records(query, crime_type, case_status, limit, offset)
        return jsonify({"status": "success", "count": len(firs), "data": firs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/fir/stats')
def get_fir_stats():
    try:
        stats = db_helper.get_fir_statistics()
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/geojson/boundaries')
def get_geojson_boundaries():
    try:
        data = db_helper.get_geojson_boundaries()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/criminals')
def get_criminals():
    query = request.args.get('query', None)
    category = request.args.get('category', None)
    risk = request.args.get('risk', None)
    wanted = request.args.get('wanted', None)
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    try:
        criminals = db_helper.get_criminals(query, category, risk, wanted, limit, offset)
        return jsonify({"status": "success", "count": len(criminals), "data": criminals})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/criminals/<criminal_id>')
def get_criminal_detail(criminal_id):
    try:
        criminal = db_helper.get_criminal_by_id(criminal_id)
        if criminal:
            return jsonify({"status": "success", "data": criminal})
        return jsonify({"status": "error", "message": "Criminal not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/criminals/add', methods=['POST'])
def add_criminal():
    try:
        data = request.form.to_dict() if request.form else (request.json or {})
        photo_bytes = None
        if 'image' in request.files:
            photo_bytes = request.files['image'].read()
            
        criminal_id = db_helper.add_criminal_record(data, photo_bytes)
        return jsonify({
            "status": "success",
            "criminal_id": criminal_id,
            "message": f"Criminal record {criminal_id} added successfully."
        })
    except Exception as e:
        print(f"Add criminal error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/criminals/edit/<criminal_id>', methods=['POST'])
def edit_criminal(criminal_id):
    try:
        data = request.form.to_dict() if request.form else (request.json or {})
        photo_bytes = None
        if 'image' in request.files:
            photo_bytes = request.files['image'].read()
            
        success = db_helper.update_criminal_record(criminal_id, data, photo_bytes)
        if success:
            return jsonify({
                "status": "success",
                "criminal_id": criminal_id,
                "message": f"Criminal record {criminal_id} updated successfully."
            })
        return jsonify({"status": "error", "message": "Criminal record not found"}), 404
    except Exception as e:
        print(f"Edit criminal error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/face-recognition/match', methods=['POST'])
def match_face():
    try:
        image_bytes = None
        saved_filename = None

        if 'image' in request.files:
            file = request.files['image']
            image_bytes = file.read()
        elif request.data and len(request.data) > 20:
            image_bytes = request.data

        if image_bytes:
            saved_filename = f"query_{int(time.time()*1000)}.jpg"
            save_path = os.path.join(UPLOADS_DIR, saved_filename)
            try:
                with open(save_path, 'wb') as f:
                    f.write(image_bytes)
            except Exception as e:
                print(f"File save error: {e}")

            result = ai_engine.match_uploaded_photo(image_bytes, top_k=5)
            return jsonify({
                "status": "success",
                "uploaded_image_url": f"uploaded_query_images/{saved_filename}",
                "face_detected": result.get("face_detected", True),
                "matches": result.get("matches", []),
                "top_match": result.get("top_match", None)
            })

        face_records = db_helper.get_all_face_encodings()
        sample = random.choice(face_records)
        matches = ai_engine.match_face_encoding(sample["encoding"], top_k=5)
        return jsonify({
            "status": "success",
            "uploaded_image_url": f"mock_images/faces/{sample['mugshot_image']}",
            "face_detected": True,
            "matches": matches,
            "top_match": matches[0] if matches else None
        })
    except Exception as e:
        print(f"Face match exception: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/field/scan', methods=['POST'])
def field_instant_scan():
    try:
        image_bytes = None
        if 'image' in request.files:
            image_bytes = request.files['image'].read()
        elif request.data and len(request.data) > 20:
            image_bytes = request.data

        if image_bytes:
            result = ai_engine.match_uploaded_photo(image_bytes, top_k=3)
            return jsonify({
                "status": "success",
                "scan_latency_ms": 130,
                "face_detected": result.get("face_detected", True),
                "top_match": result.get("top_match", None),
                "candidates": result.get("matches", [])
            })
        else:
            face_records = db_helper.get_all_face_encodings()
            sample = random.choice(face_records)
            matches = ai_engine.match_face_encoding(sample["encoding"], top_k=3)
            return jsonify({
                "status": "success",
                "scan_latency_ms": 130,
                "face_detected": True,
                "top_match": matches[0],
                "candidates": matches
            })
    except Exception as e:
        print(f"Field scan exception: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/crime-pattern/match', methods=['POST'])
def match_crime_pattern():
    try:
        scene_data = request.json or {}
        suspects = ai_engine.match_crime_mo(scene_data, top_k=10)
        return jsonify({"status": "success", "count": len(suspects), "suspects": suspects})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/area-prediction/search', methods=['POST'])
def search_area_prediction():
    try:
        req_data = request.json or {}
        area_name = req_data.get('area_name', 'Shivajinagar')
        lat = req_data.get('latitude', None)
        lng = req_data.get('longitude', None)
        radius = float(req_data.get('radius_km', 5.0))
        
        result = ai_engine.predict_area_suspects(area_name, lat, lng, radius)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analytics/charts')
def get_analytics_charts():
    try:
        data = db_helper.get_analytics_charts_data()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ai-prediction/forecast')
def get_ai_forecast():
    try:
        data = ai_engine.predict_future_crimes()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/areas')
def get_areas():
    try:
        areas = db_helper.get_area_statistics()
        return jsonify({"status": "success", "count": len(areas), "data": areas})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/graph/network')
def get_gang_network_graph():
    gang = request.args.get('gang', None)
    limit = int(request.args.get('limit', 120))
    try:
        graph_data = db_helper.get_network_graph(selected_gang=gang, limit_nodes=limit)
        return jsonify({"status": "success", "data": graph_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/citizen/sos', methods=['POST'])
def trigger_citizen_sos():
    try:
        req_data = request.json or {}
        lat = float(req_data.get('latitude', 18.5204))
        lng = float(req_data.get('longitude', 73.8567))
        area = req_data.get('area_name', 'Shivajinagar')
        
        dispatch = ai_engine.geofenced_officer_dispatch(lat, lng, incident_type="Citizen Emergency SOS")
        
        alert_response = {
            "sos_id": f"SOS-{random.randint(10000, 99999)}",
            "timestamp": "JUST NOW",
            "area_name": area,
            "status": "DISPATCHED",
            "dispatch": dispatch
        }
        return jsonify({"status": "success", "data": alert_response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/citizen/tip', methods=['POST'])
def submit_citizen_tip():
    try:
        req_data = request.json or {}
        tip_id = f"TIP-{random.randint(100000, 999999)}"
        return jsonify({
            "status": "success",
            "tip_id": tip_id,
            "message": "Anonymous tip registered successfully. Investigation team alerted."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("[*] Starting Smart Crime Analysis System Server...")
    print("    URL: http://127.0.0.1:5000")
    print("    Mobile Phone CCTV Broadcaster: http://<YOUR_IP>:5000/mobile-cctv")
    app.run(host='0.0.0.0', port=5000, debug=True)
