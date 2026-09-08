# 🛡️ Smart Crime Intelligence, Real-Time CCTV AI Surveillance & Predictive Policing Command System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL pgvector](https://img.shields.io/badge/Database-PostgreSQL_pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Leaflet.js](https://img.shields.io/badge/GIS-Leaflet.js-199900?logo=leaflet&logoColor=white)](https://leafletjs.com/)

> An enterprise-grade, multi-page AI command and control platform engineered for municipal police headquarters. Unifies real-time facial vector recognition, live CCTV surveillance, spatial GIS hotspot mapping, criminal syndicate link analysis, and zero-leakage spatio-temporal machine learning crime forecasting into a centralized web architecture.

---

## 📌 Key System Innovations

1. **128D Deep Facial Vector ML Classifier**:
   - Normalized facial embeddings extracted via OpenCV and projected into $\mathbb{R}^{128}$ space.
   - High-speed Cosine distance queries accelerated via PostgreSQL `pgvector` IVFFlat indexing achieving **sub-120ms** similarity search.
2. **Real-Time Live CCTV AI Surveillance Pipeline**:
   - Non-blocking stream proxy engine handling RTSP/IP cameras (and mobile IP webcam streams for demonstration).
   - Real-time video frame capture and automated facial verification against wanted fugitive records with audio-visual alarms.
3. **Zero-Leakage Spatio-Temporal Crime Risk Predictor**:
   - Supervised `RandomForestRegressor` ensemble (100 Decision Trees) trained across 157,300 historical FIR sliding-window records (2022–2025).
   - **Strict Chronological Temporal Partitioning** (70% Train / 15% Val / 15% Unseen Test) guaranteeing zero future data leakage.
   - Verified unseen test benchmark: **MAE: 0.2258**, **RMSE: 0.3600** (outperforming rolling baseline averages).
4. **Interactive GIS GeoJSON Hotspot Mapping**:
   - Dynamic Leaflet.js choropleth maps rendering 110 police station boundaries color-coded by empirical risk levels (`LOW`, `MODERATE`, `HIGH`, `VERY HIGH`).
5. **Algorithmic Modus Operandi (MO) Matcher & Syndicate Network Graph**:
   - Multi-parametric crime scene solver matching weapons, entry methods, and premises against known offenders.
   - Interactive Vis.js graph network visualizing kingpins, lieutenants, and enforcers.
6. **Mobile Field PWA & 1-Tap Citizen SOS**:
   - Mobile-responsive scanner for beat officers and Haversine-based geodesic distance closest-unit dispatch.
   - Citizen distress panic dispatch and anonymous crime tip registration portal.

---

## 🏛️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                            PRESENTATION / FRONTEND LAYER                          |
|   - Multi-Page Command HQ (HTML5, CSS3 Slate Minimalist System, ES6+ JS)          |
|   - Spatial GIS Mapping (Leaflet.js GeoJSON Boundaries & Heatmaps)                |
|   - Syndicate Network Graph (Vis.js Interactive Physics-based Network)            |
|   - Operational Dashboards (Chart.js Trends, Clearance Ratios, Financial Audits)  |
+-----------------------------------------------------------------------------------+
                                         │  HTTP / REST APIs / MJPEG Video Streams
+-----------------------------------------------------------------------------------+
|                             APPLICATION & BACKEND LAYER                           |
|   - Python 3.11 / Flask WSGI Core (12 Dedicated Page Routes)                      |
|   - Video Stream Proxy Engine (urllib + ssl + basic auth handler)                 |
|   - Algorithmic Modus Operandi (MO) Matcher Engine                                |
|   - Haversine Geodesic Distance Matrix Calculator                                 |
+-----------------------------------------------------------------------------------+
                                         │
+-----------------------------------------------------------------------------------+
|                             AI & DATA PERSISTENCE LAYER                           |
|   - 128D Facial Feature Vector Extractor (OpenCV / PIL / Scikit-Learn Cosine)     |
|   - Spatio-Temporal Future Crime Predictor (crime_risk_model.pkl)                 |
|   - PostgreSQL 16 with 'pgvector' Vector Index (SQLite3 local fallback)           |
|   - 157,300 Temporal FIR Historical Sliding-Window Samples (2022–2025)            |
+-----------------------------------------------------------------------------------+
```

---

## 🗂️ 12 Core Command Portals

| Route | Portal Name | Operational Capability |
| :--- | :--- | :--- |
| `/dashboard` | **Command HQ** | City-wide KPI summary counters, station risk radar, monthly crime trend curves. |
| `/cctv-surveillance` | **Live CCTV Surveillance** | Multi-camera RTSP/IP grid with automated facial recognition threat alarms. |
| `/criminal-database` | **Criminal Dossier Vault** | 5,500+ searchable criminal dossiers with a 20-field registration modal. |
| `/face-recognition` | **Face Detection AI** | Photo upload vector matcher returning top candidate matches with confidence scores. |
| `/police-patrols` | **Patrol Fleet Command** | GPS beat patrol map with active duty status and 1-click radio dispatch. |
| `/fir-vault` | **FIR Case Vault** | Audits 20,000+ FIR records, stolen property valuations, and clearance rates. |
| `/network-graph` | **Gang Link Graph** | Vis.js interactive syndicate link graph mapping leader-subordinate ties. |
| `/crime-pattern` | **MO Pattern Matcher** | Solves crime scene entry methods, weapon types, and suspect styles. |
| `/proximity-scanner` | **Proximity Radar** | Radar scanning registered offenders within a 1 to 15 km radius. |
| `/risk-predictor` | **Future Risk Predictor** | Machine Learning forecasting 24-hour crime counts per jurisdiction. |
| `/field-scanner` | **Mobile Field Scanner** | Lightweight PWA camera scanner for officers on physical beat patrol. |
| `/citizen-portal` | **Citizen SOS & Tips** | 1-tap emergency panic dispatch and anonymous crime tip portal. |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/suyashwaghule/crimeintelligence.git
cd crimeintelligence
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or install core dependencies directly: `pip install flask scikit-learn opencv-python pillow pandas numpy joblib`)*

### 4. Run the Web Command Center
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000/dashboard`**

---

## ⚖️ Academic Privacy & Ethical Compliance Statement

> **IMPORTANT NOTE**: In strict compliance with India's **Digital Personal Data Protection (DPDP) Act (2023)**, the **Information Technology Act (2000)**, and the **Indian Official Secrets Act (1923)**, **no authentic civilian personal data, classified police FIRs, or real citizen surveillance videos were used**.
>
> 100% of the relational data, FIR logs, criminal names, and phone numbers are **synthetic dummy records** mathematically synthesized via `generate_dataset.py` modeled after empirical National Crime Records Bureau (NCRB) distributions across 110 police station jurisdictions in Pune, Maharashtra. Facial recognition feature extraction was validated using the standard academic open-source benchmark dataset **Labeled Faces in the Wild (LFW)**.

---

## 👨‍💻 Author & Academic Project Details

* **Author**: Suyash Waghule
* **Degree**: Bachelor of Engineering (B.E.) in Information Technology
* **Academic Year**: 2025 – 2026
* **Target Domain**: Municipal Police Command Center / Metropolitan Law Enforcement
