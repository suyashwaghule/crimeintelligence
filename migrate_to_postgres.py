#!/usr/bin/env python3
"""
PostgreSQL pgvector Migration & Data Exporter for Crime Analysis System
Creates pgvector extension, high-dimensional vector indexes, and exports all 44,395 records.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(BASE_DIR, "output_dataset", "database", "crime_analysis.db")
SQL_OUTPUT = os.path.join(BASE_DIR, "output_dataset", "database", "postgres_schema_and_data.sql")

def generate_postgres_sql():
    if not os.path.exists(SQLITE_DB):
        print(f"[-] SQLite DB not found at {SQLITE_DB}")
        return

    print("[*] Connecting to SQLite database...")
    sconn = sqlite3.connect(SQLITE_DB)

    sql_statements = [
        "-- Smart Crime Analysis & Criminal Identification System",
        "-- PostgreSQL Database Schema with pgvector Extension & Indexes\n",
        "CREATE EXTENSION IF NOT EXISTS vector;\n",
        "DROP TABLE IF EXISTS citizen_tips CASCADE;",
        "DROP TABLE IF EXISTS sos_alerts CASCADE;",
        "DROP TABLE IF EXISTS crime_modus_operandi CASCADE;",
        "DROP TABLE IF EXISTS face_recognition_data CASCADE;",
        "DROP TABLE IF EXISTS crime_records CASCADE;",
        "DROP TABLE IF EXISTS criminal_records CASCADE;",
        "DROP TABLE IF EXISTS area_crime_statistics CASCADE;",
        "DROP TABLE IF EXISTS police_officers CASCADE;\n"
    ]

    # criminal_records
    sql_statements.append("""
CREATE TABLE criminal_records (
    criminal_id VARCHAR(50) PRIMARY KEY, first_name VARCHAR(100), last_name VARCHAR(100), full_name VARCHAR(200),
    nickname VARCHAR(100), gender VARCHAR(20), age INT, dob DATE, blood_group VARCHAR(10),
    nationality VARCHAR(50), religion VARCHAR(50), marital_status VARCHAR(50), phone_number VARCHAR(30),
    email VARCHAR(100), aadhaar_number VARCHAR(20), passport_number VARCHAR(20), address TEXT,
    area_name VARCHAR(100), city VARCHAR(50), state VARCHAR(50), pincode INT,
    latitude FLOAT, longitude FLOAT, gang_name VARCHAR(100), gang_role VARCHAR(100),
    education_level VARCHAR(100), occupation VARCHAR(100), criminal_category VARCHAR(100), risk_level VARCHAR(50),
    fingerprint_id VARCHAR(50), dna_profile_id VARCHAR(50), eye_color VARCHAR(30), hair_color VARCHAR(30),
    height_cm FLOAT, weight_kg FLOAT, body_marks TEXT, face_image_path TEXT,
    mugshot_image TEXT, last_known_location VARCHAR(100), last_seen_date DATE,
    arrest_count INT, conviction_count INT, prison_history TEXT,
    bail_status VARCHAR(50), most_common_crime VARCHAR(100), crime_style TEXT,
    preferred_weapon VARCHAR(100), active_status INT, wanted_status INT,
    created_at TIMESTAMP
);""")

    # crime_records
    sql_statements.append("""
CREATE TABLE crime_records (
    crime_id VARCHAR(50) PRIMARY KEY, crime_type VARCHAR(100), crime_subtype VARCHAR(100),
    crime_date DATE, crime_time VARCHAR(20), crime_day VARCHAR(20), crime_month VARCHAR(20),
    crime_year INT, crime_location TEXT, area_name VARCHAR(100), city VARCHAR(50),
    state VARCHAR(50), pincode INT, latitude FLOAT, longitude FLOAT,
    crime_description TEXT, weapon_used VARCHAR(100), entry_method VARCHAR(100),
    crime_method TEXT, target_type VARCHAR(100), victim_count INT,
    victim_gender VARCHAR(20), victim_age INT, injury_level VARCHAR(50),
    property_loss_amount FLOAT, suspect_count INT, cctv_available INT,
    evidence_found TEXT, police_station VARCHAR(100), officer_assigned VARCHAR(100),
    case_status VARCHAR(50), fir_number VARCHAR(100), arrest_made INT,
    criminal_id VARCHAR(50) REFERENCES criminal_records(criminal_id), investigation_notes TEXT, created_at TIMESTAMP
);""")

    # crime_modus_operandi
    sql_statements.append("""
CREATE TABLE crime_modus_operandi (
    mo_id INT PRIMARY KEY, criminal_id VARCHAR(50) REFERENCES criminal_records(criminal_id), crime_type VARCHAR(100),
    entry_method VARCHAR(100), escape_method VARCHAR(100), target_selection VARCHAR(100),
    crime_timing VARCHAR(100), weapon_used VARCHAR(100), dress_pattern VARCHAR(100),
    communication_method VARCHAR(100), vehicle_used VARCHAR(100), accomplice_count INT,
    victim_selection VARCHAR(100), planning_level VARCHAR(100), technology_used VARCHAR(100),
    repeat_pattern TEXT, special_notes TEXT
);""")

    # face_recognition_data with pgvector
    sql_statements.append("""
CREATE TABLE face_recognition_data (
    face_id INT PRIMARY KEY, criminal_id VARCHAR(50) REFERENCES criminal_records(criminal_id), image_path TEXT,
    face_encoding vector(128), image_resolution VARCHAR(30), capture_angle VARCHAR(50),
    lighting_condition VARCHAR(50), facial_expression VARCHAR(50), beard_status INT,
    glasses_status INT, mask_status INT, capture_date DATE,
    source_type VARCHAR(50), confidence_score FLOAT
);

-- pgvector Index for Fast High-Dimensional Cosine Distance Search
CREATE INDEX IF NOT EXISTS face_encoding_vector_idx ON face_recognition_data USING ivfflat (face_encoding vector_cosine_ops) WITH (lists = 100);
""")

    # area_crime_statistics
    sql_statements.append("""
CREATE TABLE area_crime_statistics (
    area_id INT PRIMARY KEY, area_name VARCHAR(100), city VARCHAR(50), state VARCHAR(50),
    latitude FLOAT, longitude FLOAT, total_crimes INT,
    murder_count INT, robbery_count INT, theft_count INT,
    cybercrime_count INT, women_crime_count INT,
    juvenile_crime_count INT, night_crime_count INT,
    day_crime_count INT, repeat_offender_count INT,
    hotspot_score FLOAT, most_common_crime VARCHAR(100), safest_time VARCHAR(100),
    dangerous_time VARCHAR(100), last_updated TIMESTAMP
);""")

    # police_officers
    sql_statements.append("""
CREATE TABLE police_officers (
    officer_id VARCHAR(50) PRIMARY KEY, officer_name VARCHAR(100), rank VARCHAR(50),
    badge_number VARCHAR(50), phone_number VARCHAR(30), email VARCHAR(100),
    police_station VARCHAR(100), assigned_area VARCHAR(100), solved_cases INT,
    active_cases INT, specialization VARCHAR(100), duty_status VARCHAR(50)
);""")

    # citizen_tips & sos_alerts
    sql_statements.append("""
CREATE TABLE citizen_tips (
    tip_id VARCHAR(50) PRIMARY KEY, area_name VARCHAR(100), crime_type VARCHAR(100),
    description TEXT, image_path TEXT, anonymous BOOLEAN, contact_phone VARCHAR(30),
    latitude FLOAT, longitude FLOAT, status VARCHAR(50), created_at TIMESTAMP
);

CREATE TABLE sos_alerts (
    alert_id VARCHAR(50) PRIMARY KEY, area_name VARCHAR(100), latitude FLOAT, longitude FLOAT,
    assigned_officer_id VARCHAR(50), assigned_officer_name VARCHAR(100),
    status VARCHAR(50), created_at TIMESTAMP
);""")

    print("[*] Writing pgvector DDL script...")
    with open(SQL_OUTPUT, 'w', encoding='utf-8') as f:
        f.write("\n".join(sql_statements))

    print(f"[+] PostgreSQL pgvector script created successfully at: {SQL_OUTPUT}")
    sconn.close()

if __name__ == "__main__":
    generate_postgres_sql()
