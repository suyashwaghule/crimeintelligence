import os
import sqlite3
import struct
import json
import math
from datetime import datetime
import ai_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "output_dataset", "database", "crime_analysis.db")
GEOJSON_PATH = os.path.join(BASE_DIR, "output_dataset", "geojson", "area_hotspots.geojson")
FACES_DIR = os.path.join(BASE_DIR, "output_dataset", "mock_images", "faces")
os.makedirs(FACES_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_kpis():
    conn = get_db_connection()
    c = conn.cursor()
    
    total_crimes = c.execute("SELECT COUNT(*) FROM crime_records").fetchone()[0]
    total_criminals = c.execute("SELECT COUNT(*) FROM criminal_records").fetchone()[0]
    total_officers = c.execute("SELECT COUNT(*) FROM police_officers").fetchone()[0]
    solved_cases = c.execute("SELECT COUNT(*) FROM crime_records WHERE case_status = 'Solved'").fetchone()[0]
    unsolved_cases = c.execute("SELECT COUNT(*) FROM crime_records WHERE case_status = 'Unsolved'").fetchone()[0]
    wanted_criminals = c.execute("SELECT COUNT(*) FROM criminal_records WHERE wanted_status = 1").fetchone()[0]
    high_risk_areas = c.execute("SELECT COUNT(*) FROM area_crime_statistics WHERE hotspot_score >= 7.0").fetchone()[0]
    
    conn.close()
    
    return {
        "total_crimes": total_crimes,
        "total_criminals": total_criminals,
        "total_officers": total_officers,
        "solved_cases": solved_cases,
        "unsolved_cases": unsolved_cases,
        "solve_rate": round((solved_cases / total_crimes * 100), 1) if total_crimes > 0 else 0,
        "wanted_criminals": wanted_criminals,
        "high_risk_areas": high_risk_areas
    }

def get_all_police_officers(station=None, duty_status=None, limit=300):
    conn = get_db_connection()
    c = conn.cursor()
    
    sql = "SELECT * FROM police_officers WHERE 1=1"
    params = []
    
    if station and station != "All":
        sql += " AND (police_station LIKE ? OR assigned_area LIKE ?)"
        params.extend([f"%{station}%", f"%{station}%"])
        
    if duty_status and duty_status != "All":
        sql += " AND duty_status = ?"
        params.append(duty_status)
        
    sql += " LIMIT ?"
    params.append(limit)
    
    rows = c.execute(sql, params).fetchall()
    officers = [dict(r) for r in rows]
    
    areas = c.execute("SELECT area_name, latitude, longitude FROM area_crime_statistics").fetchall()
    area_coords = {a["area_name"]: (a["latitude"], a["longitude"]) for a in areas}
    
    for off in officers:
        alat, alng = area_coords.get(off["assigned_area"], (18.5204, 73.8567))
        off["latitude"] = round(alat + ((hash(off["officer_id"]) % 100 - 50) * 0.0003), 5)
        off["longitude"] = round(alng + ((hash(off["officer_id"] + "lng") % 100 - 50) * 0.0003), 5)
        
    conn.close()
    return officers

def get_fir_records(query=None, crime_type=None, case_status=None, limit=100, offset=0):
    conn = get_db_connection()
    c = conn.cursor()
    
    sql = "SELECT * FROM crime_records WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (fir_number LIKE ? OR area_name LIKE ? OR criminal_id LIKE ? OR victim_gender LIKE ? OR crime_subtype LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern, pattern, pattern])
        
    if crime_type and crime_type != "All":
        sql += " AND crime_type = ?"
        params.append(crime_type)
        
    if case_status and case_status != "All":
        sql += " AND case_status = ?"
        params.append(case_status)
        
    sql += " ORDER BY crime_date DESC, crime_time DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = c.execute(sql, params).fetchall()
    firs = [dict(r) for r in rows]
    conn.close()
    return firs

def get_fir_statistics():
    conn = get_db_connection()
    c = conn.cursor()
    
    total_firs = c.execute("SELECT COUNT(*) FROM crime_records").fetchone()[0]
    total_stolen = c.execute("SELECT SUM(property_loss_amount) FROM crime_records").fetchone()[0] or 0
    solved_firs = c.execute("SELECT COUNT(*) FROM crime_records WHERE case_status = 'Solved'").fetchone()[0]
    solved_property = c.execute("SELECT SUM(property_loss_amount) FROM crime_records WHERE case_status = 'Solved'").fetchone()[0] or 0
    total_victims = c.execute("SELECT SUM(victim_count) FROM crime_records").fetchone()[0] or 0
    
    conn.close()
    return {
        "total_firs": total_firs,
        "total_stolen_value_inr": total_stolen,
        "total_recovered_value_inr": solved_property,
        "recovery_rate_pct": round((solved_property / total_stolen * 100), 1) if total_stolen > 0 else 0,
        "solved_firs": solved_firs,
        "total_witnesses": total_victims
    }

def get_geojson_boundaries():
    if os.path.exists(GEOJSON_PATH):
        with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

def get_criminals(query=None, category=None, risk=None, wanted=None, limit=100, offset=0):
    conn = get_db_connection()
    c = conn.cursor()
    
    sql = "SELECT * FROM criminal_records WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (full_name LIKE ? OR nickname LIKE ? OR criminal_id LIKE ? OR gang_name LIKE ? OR area_name LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern, pattern, pattern])
        
    if category and category != "All":
        sql += " AND criminal_category = ?"
        params.append(category)
        
    if risk and risk != "All":
        sql += " AND risk_level = ?"
        params.append(risk)
        
    if wanted is not None and wanted != "All":
        sql += " AND wanted_status = ?"
        params.append(1 if wanted in [True, "1", "true", "True"] else 0)
        
    sql += " ORDER BY created_at DESC, arrest_count DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = c.execute(sql, params).fetchall()
    criminals = [dict(row) for row in rows]
    
    conn.close()
    return criminals

def get_criminal_by_id(criminal_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    row = c.execute("SELECT * FROM criminal_records WHERE criminal_id = ?", (criminal_id,)).fetchone()
    if not row:
        conn.close()
        return None
        
    criminal = dict(row)
    
    crimes = c.execute(
        "SELECT * FROM crime_records WHERE criminal_id = ? ORDER BY crime_date DESC", 
        (criminal_id,)
    ).fetchall()
    criminal["crimes"] = [dict(r) for r in crimes]
    
    mo_row = c.execute("SELECT * FROM crime_modus_operandi WHERE criminal_id = ?", (criminal_id,)).fetchone()
    criminal["modus_operandi"] = dict(mo_row) if mo_row else {}
    
    face_rows = c.execute("SELECT face_id, image_path, capture_angle, confidence_score, source_type FROM face_recognition_data WHERE criminal_id = ?", (criminal_id,)).fetchall()
    criminal["face_records"] = [dict(r) for r in face_rows]
    
    conn.close()
    return criminal

def add_criminal_record(data, photo_bytes=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    count = c.execute("SELECT COUNT(*) FROM criminal_records").fetchone()[0]
    next_num = count + 1
    criminal_id = f"CRM-IND-{next_num:05d}"
    
    first = data.get("first_name", "Unknown").strip()
    last = data.get("last_name", "Subject").strip()
    full_name = f"{first} {last}"
    nickname = data.get("nickname", "").strip()
    gender = data.get("gender", "Male")
    age = int(data.get("age", 28))
    dob = data.get("dob", "1996-01-01")
    blood_group = data.get("blood_group", "O+")
    nationality = data.get("nationality", "Indian")
    religion = data.get("religion", "Hindu")
    marital_status = data.get("marital_status", "Single")
    phone = data.get("phone_number", "+919876543210")
    email = data.get("email", f"{first.lower()}@pune.gov.in")
    aadhaar = data.get("aadhaar_number", "888877776666")
    passport = data.get("passport_number", "")
    area = data.get("area_name", "Shivajinagar")
    address = data.get("address", f"Pune - {area}")
    pincode = int(data.get("pincode", 411005))
    gang_name = data.get("gang_name", "").strip()
    gang_role = data.get("gang_role", "").strip()
    education_level = data.get("education_level", "Secondary School")
    occupation = data.get("occupation", "Daily Wage Worker")
    category = data.get("criminal_category", "Violent")
    risk = data.get("risk_level", "High")
    eye_color = data.get("eye_color", "Brown")
    hair_color = data.get("hair_color", "Black")
    height_cm = float(data.get("height_cm", 172.0))
    weight_kg = float(data.get("weight_kg", 68.0))
    body_marks = data.get("body_marks", "None recorded").strip()
    arrest_count = int(data.get("arrest_count", 1))
    conviction_count = int(data.get("conviction_count", 0))
    prison_history = data.get("prison_history", "No prior convictions").strip()
    bail_status = data.get("bail_status", "On Bail")
    most_common_crime = data.get("most_common_crime", "Robbery")
    crime_style = data.get("crime_style", "Known offender operating in Pune").strip()
    weapon = data.get("preferred_weapon", "Knife")
    entry_method = data.get("entry_method", "Door break")
    active_status = 1 if str(data.get("active_status")).lower() in ["1", "true", "on", "yes"] else 0
    wanted_status = 1 if str(data.get("wanted_status")).lower() in ["1", "true", "on", "yes"] else 0
    
    areas_info = c.execute("SELECT latitude, longitude FROM area_crime_statistics WHERE area_name = ?", (area,)).fetchone()
    lat = areas_info["latitude"] if areas_info else 18.5204
    lng = areas_info["longitude"] if areas_info else 73.8567
    
    filename = f"{criminal_id}_mugshot.jpg"
    mugshot_rel = f"mock_images/faces/{filename}"
    mugshot_abs = os.path.join(FACES_DIR, filename)
    
    if photo_bytes:
        with open(mugshot_abs, 'wb') as f:
            f.write(photo_bytes)
        vec_128d, _ = ai_engine.extract_face_vector_from_image_bytes(photo_bytes)
    else:
        vec_128d = [0.0] * 128
        
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute("""
        INSERT INTO criminal_records (
            criminal_id, first_name, last_name, full_name, nickname, gender, age, dob, blood_group,
            nationality, religion, marital_status, phone_number, email, aadhaar_number, passport_number,
            address, area_name, city, state, pincode, latitude, longitude, gang_name, gang_role,
            education_level, occupation, criminal_category, risk_level, fingerprint_id, dna_profile_id,
            eye_color, hair_color, height_cm, weight_kg, body_marks, face_image_path, mugshot_image,
            last_known_location, last_seen_date, arrest_count, conviction_count, prison_history,
            bail_status, most_common_crime, crime_style, preferred_weapon, active_status, wanted_status, created_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, 'Pune', 'Maharashtra', ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2026-08-08', ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        criminal_id, first, last, full_name, nickname, gender, age, dob, blood_group,
        nationality, religion, marital_status, phone, email, aadhaar, passport,
        address, area, pincode, lat, lng, gang_name, gang_role,
        education_level, occupation, category, risk, f"FP-{criminal_id}", f"DNA-{criminal_id}",
        eye_color, hair_color, height_cm, weight_kg, body_marks, mugshot_rel, mugshot_rel,
        area, arrest_count, conviction_count, prison_history,
        bail_status, most_common_crime, crime_style, weapon, active_status, wanted_status, created_at
    ))
    
    max_mo = c.execute("SELECT MAX(mo_id) FROM crime_modus_operandi").fetchone()[0] or 0
    c.execute("""
        INSERT INTO crime_modus_operandi (
            mo_id, criminal_id, crime_type, entry_method, escape_method, target_selection,
            crime_timing, weapon_used, dress_pattern, communication_method, vehicle_used,
            accomplice_count, victim_selection, planning_level, technology_used, repeat_pattern, special_notes
        ) VALUES (?, ?, ?, ?, 'Bike escape', 'Shops & Houses', 'Late night (11PM-3AM)', ?, 'Black hoodie', 'Mobile', 'Bike', 1, 'Pedestrians', 'Planned', 'None', ?, 'Registered via system')
    """, (max_mo + 1, criminal_id, most_common_crime, entry_method, weapon, crime_style))
    
    max_face = c.execute("SELECT MAX(face_id) FROM face_recognition_data").fetchone()[0] or 0
    enc_blob = struct.pack('128f', *vec_128d) if len(vec_128d) == 128 else b'\x00'*(128*4)
    c.execute("""
        INSERT INTO face_recognition_data (
            face_id, criminal_id, image_path, face_encoding, image_resolution, capture_angle,
            lighting_condition, facial_expression, beard_status, glasses_status, mask_status,
            capture_date, source_type, confidence_score
        ) VALUES (?, ?, ?, ?, '250x250', 'Front', 'Normal', 'Neutral', 0, 0, 0, '2026-08-08', 'Arrest Photo', 0.95)
    """, (max_face + 1, criminal_id, mugshot_rel, enc_blob))
    
    conn.commit()
    conn.close()
    return criminal_id

def update_criminal_record(criminal_id, data, photo_bytes=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    existing = c.execute("SELECT * FROM criminal_records WHERE criminal_id = ?", (criminal_id,)).fetchone()
    if not existing:
        conn.close()
        return False
        
    first = data.get("first_name", existing["first_name"]).strip()
    last = data.get("last_name", existing["last_name"]).strip()
    full_name = f"{first} {last}"
    nickname = data.get("nickname", existing["nickname"]).strip()
    gender = data.get("gender", existing["gender"])
    age = int(data.get("age", existing["age"]))
    dob = data.get("dob", existing["dob"])
    blood_group = data.get("blood_group", existing["blood_group"])
    nationality = data.get("nationality", existing["nationality"])
    religion = data.get("religion", existing["religion"])
    marital_status = data.get("marital_status", existing["marital_status"])
    phone = data.get("phone_number", existing["phone_number"])
    email = data.get("email", existing["email"])
    aadhaar = data.get("aadhaar_number", existing["aadhaar_number"])
    passport = data.get("passport_number", existing["passport_number"])
    area = data.get("area_name", existing["area_name"])
    address = data.get("address", existing["address"])
    pincode = int(data.get("pincode", existing["pincode"] or 411005))
    gang_name = data.get("gang_name", existing["gang_name"]).strip()
    gang_role = data.get("gang_role", existing["gang_role"]).strip()
    education_level = data.get("education_level", existing["education_level"])
    occupation = data.get("occupation", existing["occupation"])
    category = data.get("criminal_category", existing["criminal_category"])
    risk = data.get("risk_level", existing["risk_level"])
    eye_color = data.get("eye_color", existing["eye_color"])
    hair_color = data.get("hair_color", existing["hair_color"])
    height_cm = float(data.get("height_cm", existing["height_cm"]))
    weight_kg = float(data.get("weight_kg", existing["weight_kg"]))
    body_marks = data.get("body_marks", existing["body_marks"]).strip()
    arrest_count = int(data.get("arrest_count", existing["arrest_count"]))
    conviction_count = int(data.get("conviction_count", existing["conviction_count"]))
    prison_history = data.get("prison_history", existing["prison_history"]).strip()
    bail_status = data.get("bail_status", existing["bail_status"])
    most_common_crime = data.get("most_common_crime", existing["most_common_crime"])
    crime_style = data.get("crime_style", existing["crime_style"]).strip()
    weapon = data.get("preferred_weapon", existing["preferred_weapon"])
    entry_method = data.get("entry_method", "Door break")
    active_status = 1 if str(data.get("active_status")).lower() in ["1", "true", "on", "yes"] else 0
    wanted_status = 1 if str(data.get("wanted_status")).lower() in ["1", "true", "on", "yes"] else 0
    
    areas_info = c.execute("SELECT latitude, longitude FROM area_crime_statistics WHERE area_name = ?", (area,)).fetchone()
    lat = areas_info["latitude"] if areas_info else existing["latitude"]
    lng = areas_info["longitude"] if areas_info else existing["longitude"]
    
    mugshot_rel = existing["mugshot_image"]
    if photo_bytes:
        filename = f"{criminal_id}_mugshot.jpg"
        mugshot_rel = f"mock_images/faces/{filename}"
        mugshot_abs = os.path.join(FACES_DIR, filename)
        with open(mugshot_abs, 'wb') as f:
            f.write(photo_bytes)
        vec_128d, _ = ai_engine.extract_face_vector_from_image_bytes(photo_bytes)
        
        enc_blob = struct.pack('128f', *vec_128d) if len(vec_128d) == 128 else b'\x00'*(128*4)
        c.execute("""
            UPDATE face_recognition_data SET image_path = ?, face_encoding = ? WHERE criminal_id = ?
        """, (mugshot_rel, enc_blob, criminal_id))
        
    c.execute("""
        UPDATE criminal_records SET
            first_name = ?, last_name = ?, full_name = ?, nickname = ?, gender = ?, age = ?, dob = ?,
            blood_group = ?, nationality = ?, religion = ?, marital_status = ?, phone_number = ?,
            email = ?, aadhaar_number = ?, passport_number = ?, address = ?, area_name = ?, pincode = ?,
            latitude = ?, longitude = ?, gang_name = ?, gang_role = ?, education_level = ?, occupation = ?,
            criminal_category = ?, risk_level = ?, eye_color = ?, hair_color = ?, height_cm = ?, weight_kg = ?,
            body_marks = ?, face_image_path = ?, mugshot_image = ?, last_known_location = ?, arrest_count = ?,
            conviction_count = ?, prison_history = ?, bail_status = ?, most_common_crime = ?, crime_style = ?,
            preferred_weapon = ?, active_status = ?, wanted_status = ?
        WHERE criminal_id = ?
    """, (
        first, last, full_name, nickname, gender, age, dob, blood_group, nationality, religion,
        marital_status, phone, email, aadhaar, passport, address, area, pincode, lat, lng,
        gang_name, gang_role, education_level, occupation, category, risk, eye_color, hair_color,
        height_cm, weight_kg, body_marks, mugshot_rel, mugshot_rel, area, arrest_count, conviction_count,
        prison_history, bail_status, most_common_crime, crime_style, weapon, active_status, wanted_status,
        criminal_id
    ))
    
    c.execute("""
        UPDATE crime_modus_operandi SET
            crime_type = ?, entry_method = ?, weapon_used = ?, repeat_pattern = ?
        WHERE criminal_id = ?
    """, (most_common_crime, entry_method, weapon, crime_style, criminal_id))
    
    conn.commit()
    conn.close()
    return True

def get_all_face_encodings():
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("""
        SELECT f.face_id, f.criminal_id, f.image_path, f.face_encoding, f.confidence_score,
               c.full_name, c.nickname, c.risk_level, c.criminal_category, c.wanted_status, c.mugshot_image
        FROM face_recognition_data f
        JOIN criminal_records c ON f.criminal_id = c.criminal_id
    """).fetchall()
    
    face_data = []
    for r in rows:
        blob = r["face_encoding"]
        vec = list(struct.unpack('128f', blob)) if blob and len(blob) == 128 * 4 else [0.0] * 128
        face_data.append({
            "face_id": r["face_id"], "criminal_id": r["criminal_id"], "full_name": r["full_name"],
            "nickname": r["nickname"], "risk_level": r["risk_level"], "criminal_category": r["criminal_category"],
            "wanted_status": r["wanted_status"], "image_path": r["image_path"], "mugshot_image": r["mugshot_image"],
            "encoding": vec
        })
    conn.close()
    return face_data

def get_all_modus_operandi():
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("""
        SELECT mo.*, c.full_name, c.nickname, c.risk_level, c.criminal_category, 
               c.mugshot_image, c.area_name as criminal_area
        FROM crime_modus_operandi mo
        JOIN criminal_records c ON mo.criminal_id = c.criminal_id
    """).fetchall()
    mos = [dict(r) for r in rows]
    conn.close()
    return mos

def get_area_statistics():
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM area_crime_statistics ORDER BY hotspot_score DESC").fetchall()
    areas = [dict(r) for r in rows]
    conn.close()
    return areas

def get_criminals_near(latitude, longitude, radius_km=5.0):
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM criminal_records").fetchall()
    near_criminals = []
    for row in rows:
        crim = dict(row)
        clat, clng = crim["latitude"], crim["longitude"]
        if clat and clng:
            dist = haversine(latitude, longitude, clat, clng)
            if dist <= radius_km:
                crim["distance_km"] = round(dist, 2)
                near_criminals.append(crim)
    near_criminals.sort(key=lambda x: x["distance_km"])
    conn.close()
    return near_criminals

def get_nearest_officers(latitude, longitude, limit=5):
    conn = get_db_connection()
    c = conn.cursor()
    areas = c.execute("SELECT area_name, latitude, longitude FROM area_crime_statistics").fetchall()
    area_coords = {a["area_name"]: (a["latitude"], a["longitude"]) for a in areas}
    officers = c.execute("SELECT * FROM police_officers WHERE duty_status = 'Active'").fetchall()
    officer_list = []
    for o in officers:
        off = dict(o)
        assigned_area = off["assigned_area"]
        alat, alng = area_coords.get(assigned_area, (18.5204, 73.8567))
        dist = haversine(latitude, longitude, alat, alng)
        off["distance_km"] = round(dist, 2)
        officer_list.append(off)
    officer_list.sort(key=lambda x: x["distance_km"])
    conn.close()
    return officer_list[:limit]

def get_network_graph(selected_gang=None, limit_nodes=120):
    conn = get_db_connection()
    c = conn.cursor()
    sql = "SELECT criminal_id, full_name, nickname, gang_name, gang_role, risk_level, criminal_category, mugshot_image FROM criminal_records WHERE gang_name IS NOT NULL AND gang_name != ''"
    params = []
    if selected_gang and selected_gang != "All":
        sql += " AND gang_name = ?"
        params.append(selected_gang)
    sql += " LIMIT ?"
    params.append(limit_nodes)
    criminals = c.execute(sql, params).fetchall()
    nodes, edges, gangs_set = [], [], set()
    for cr in criminals:
        cid, gname, risk = cr["criminal_id"], cr["gang_name"], cr["risk_level"]
        nodes.append({
            "id": cid, "label": cr["full_name"], "group": "Criminal", "risk_level": risk,
            "title": f"<b>{cr['full_name']}</b><br>Role: {cr['gang_role']}<br>Gang: {gname}<br>Risk: {risk}",
            "shape": "circularImage", "image": f"/output_dataset/{cr['mugshot_image']}"
        })
        if gname not in gangs_set:
            gangs_set.add(gname)
            nodes.append({"id": f"gang_{gname}", "label": f"GANG: {gname.upper()}", "group": "Gang", "title": f"<b>Gang: {gname}</b>", "shape": "hexagon", "color": "#ff0055"})
        edges.append({"from": cid, "to": f"gang_{gname}", "label": cr["gang_role"] or "Member", "color": "#4facfe"})
    crim_ids = [c["criminal_id"] for c in criminals]
    for i in range(0, len(crim_ids) - 1, 2):
        if i + 1 < len(crim_ids):
            edges.append({"from": crim_ids[i], "to": crim_ids[i+1], "label": "Accomplice", "color": "rgba(255, 183, 3, 0.6)", "dashes": True})
    conn.close()
    return {"nodes": nodes, "edges": edges, "gangs": sorted(list(gangs_set))}

def get_analytics_charts_data():
    conn = get_db_connection()
    c = conn.cursor()
    crime_types = c.execute("SELECT crime_type, COUNT(*) as count FROM crime_records GROUP BY crime_type ORDER BY count DESC").fetchall()
    monthly_trend = c.execute("SELECT crime_year, crime_month, COUNT(*) as count FROM crime_records GROUP BY crime_year, crime_month ORDER BY crime_year, crime_month").fetchall()
    top_areas = c.execute("SELECT area_name, total_crimes, hotspot_score FROM area_crime_statistics ORDER BY total_crimes DESC LIMIT 10").fetchall()
    weapons = c.execute("SELECT weapon_used, COUNT(*) as count FROM crime_records WHERE weapon_used != 'None' GROUP BY weapon_used ORDER BY count DESC LIMIT 8").fetchall()
    day_night = c.execute("SELECT SUM(day_crime_count) as day_total, SUM(night_crime_count) as night_total FROM area_crime_statistics").fetchone()
    conn.close()
    return {"crime_types": [dict(r) for r in crime_types], "monthly_trend": [dict(r) for r in monthly_trend], "top_areas": [dict(r) for r in top_areas], "weapons": [dict(r) for r in weapons], "day_night": dict(day_night) if day_night else {"day_total": 0, "night_total": 0}}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
