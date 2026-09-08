#!/usr/bin/env python3
"""
=============================================================================
SMART CRIME INTELLIGENCE — SPATIO-TEMPORAL FUTURE CRIME ML TRAINING SYSTEM
=============================================================================
Fast Vectorized Trainer: Trains a genuine Random Forest Regressor model on 20,000 
historical FIR records (2022-2025) to forecast actual 24-hour future crime incident counts.
"""

import os
import json
import sqlite3
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "output_dataset", "database", "crime_analysis.db")
MODEL_PATH = os.path.join(BASE_DIR, "output_dataset", "database", "crime_risk_model.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "output_dataset", "database", "crime_risk_metrics.json")

def build_spatiotemporal_dataset_fast():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    print("[*] Connecting to SQLite database & loading historical FIR records...")
    conn = sqlite3.connect(DB_PATH)
    
    firs_df = pd.read_sql_query("""
        SELECT crime_id, crime_type, crime_date, crime_time, area_name, latitude, longitude
        FROM crime_records
        WHERE crime_date IS NOT NULL AND area_name IS NOT NULL
    """, conn)
    
    areas_df = pd.read_sql_query("""
        SELECT area_name, latitude, longitude
        FROM area_crime_statistics
    """, conn)
    conn.close()

    area_coords = dict(zip(areas_df["area_name"], zip(areas_df["latitude"].astype(float), areas_df["longitude"].astype(float))))

    firs_df["crime_date"] = pd.to_datetime(firs_df["crime_date"])
    firs_df["crime_type_lower"] = firs_df["crime_type"].str.lower()
    firs_df["time_str"] = firs_df["crime_time"].astype(str)

    min_date = firs_df["crime_date"].min()
    max_date = firs_df["crime_date"].max()

    # Pre-calculate category indicators
    firs_df["is_theft"] = firs_df["crime_type_lower"].str.contains("theft|burglary|robbery", regex=True).astype(int)
    firs_df["is_robbery"] = firs_df["crime_type_lower"].str.contains("robbery|extortion|chain", regex=True).astype(int)
    firs_df["is_murder"] = firs_df["crime_type_lower"].str.contains("murder|assault|homicide", regex=True).astype(int)
    firs_df["is_cyber"] = firs_df["crime_type_lower"].str.contains("cyber|fraud|phishing", regex=True).astype(int)
    firs_df["is_women"] = firs_df["crime_type_lower"].str.contains("women|harassment|molestation", regex=True).astype(int)
    firs_df["is_night"] = firs_df["time_str"].str.startswith(('22', '23', '00', '01', '02', '03', '04')).astype(int)

    # Daily aggregation by Area and Date
    daily = firs_df.groupby(["area_name", "crime_date"]).agg(
        total_crimes=('crime_id', 'count'),
        theft_count=('is_theft', 'sum'),
        robbery_count=('is_robbery', 'sum'),
        murder_count=('is_murder', 'sum'),
        cyber_count=('is_cyber', 'sum'),
        women_count=('is_women', 'sum'),
        night_count=('is_night', 'sum')
    ).reset_index()

    # Full Area x Date grid
    all_areas = firs_df["area_name"].unique()
    full_dates = pd.date_range(min_date, max_date, freq='D')
    idx = pd.MultiIndex.from_product([all_areas, full_dates], names=['area_name', 'crime_date'])
    
    grid = daily.set_index(['area_name', 'crime_date']).reindex(idx, fill_value=0).reset_index()
    grid = grid.sort_values(['area_name', 'crime_date']).reset_index(drop=True)

    print("[*] Computing vectorized rolling window features (Strict Temporal Separation)...")
    
    # Vectorized Rolling Features grouped by area (shifted by 1 day to exclude current date!)
    grouped = grid.groupby('area_name')

    grid['crimes_prev_24h'] = grouped['total_crimes'].shift(1).fillna(0)
    grid['crimes_prev_7d'] = grouped['total_crimes'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['crimes_prev_30d'] = grouped['total_crimes'].transform(lambda x: x.shift(1).rolling(30, min_periods=1).sum()).fillna(0)
    
    grid['theft_prev_7d'] = grouped['theft_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['robbery_prev_7d'] = grouped['robbery_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['murder_prev_7d'] = grouped['murder_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['cyber_prev_7d'] = grouped['cyber_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['women_prev_7d'] = grouped['women_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)
    grid['night_prev_7d'] = grouped['night_count'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum()).fillna(0)

    grid['day_of_week'] = grid['crime_date'].dt.dayofweek
    grid['month'] = grid['crime_date'].dt.month
    grid['is_weekend'] = grid['day_of_week'].isin([5, 6]).astype(int)

    grid['latitude'] = grid['area_name'].map(lambda a: area_coords.get(a, (18.5204, 73.8567))[0])
    grid['longitude'] = grid['area_name'].map(lambda a: area_coords.get(a, (18.5204, 73.8567))[1])

    # Target: actual crimes occurring on current date (the following 24 hours)
    grid['target_future_24h_crimes'] = grid['total_crimes'].astype(float)

    # Filter out initial 30 warm-up days per area
    eval_start_date = min_date + pd.Timedelta(days=30)
    valid_dataset = grid[grid['crime_date'] >= eval_start_date].copy().reset_index(drop=True)

    print(f"[+] Spatio-Temporal Dataset Samples Ready: {len(valid_dataset)} rows")
    return valid_dataset

def train_and_evaluate():
    df = build_spatiotemporal_dataset_fast()
    
    # Chronological sort across all areas
    df = df.sort_values("crime_date").reset_index(drop=True)

    feature_cols = [
        "crimes_prev_24h", "crimes_prev_7d", "crimes_prev_30d",
        "theft_prev_7d", "robbery_prev_7d", "murder_prev_7d", "cyber_prev_7d",
        "women_prev_7d", "night_prev_7d", "day_of_week", "month", "is_weekend",
        "latitude", "longitude"
    ]
    target_col = "target_future_24h_crimes"

    X = df[feature_cols].values
    y = df[target_col].values
    dates = df["crime_date"].dt.strftime("%Y-%m-%d").values

    N = len(df)
    train_idx = int(N * 0.70)
    val_idx = int(N * 0.85)

    # --- STRICT CHRONOLOGICAL TEMPORAL SPLIT ---
    X_train, y_train = X[:train_idx], y[:train_idx]
    X_val, y_val = X[train_idx:val_idx], y[train_idx:val_idx]
    X_test, y_test = X[val_idx:], y[val_idx:]

    train_dates = (dates[0], dates[train_idx-1])
    val_dates = (dates[train_idx], dates[val_idx-1])
    test_dates = (dates[val_idx], dates[-1])

    print("\n--- CHRONOLOGICAL DATA SPLIT ---")
    print(f"Training Set   ({len(X_train)} samples): {train_dates[0]} to {train_dates[1]}")
    print(f"Validation Set ({len(X_val)} samples): {val_dates[0]} to {val_dates[1]}")
    print(f"Testing Set    ({len(X_test)} samples): {test_dates[0]} to {test_dates[1]}")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # --- NAIVE HISTORICAL BASELINE MODEL (Predict 7-day daily average) ---
    baseline_test_pred = X_test[:, 1] / 7.0
    baseline_mae = float(mean_absolute_error(y_test, baseline_test_pred))
    baseline_rmse = float(root_mean_squared_error(y_test, baseline_test_pred))

    # --- TRAIN RANDOM FOREST REGRESSOR ---
    print("\n[*] Training RandomForestRegressor (100 Decision Trees, max_depth=12)...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_scaled, y_train)

    y_train_pred = rf_model.predict(X_train_scaled)
    y_val_pred = rf_model.predict(X_val_scaled)
    y_test_pred = rf_model.predict(X_test_scaled)

    r2_train = float(r2_score(y_train, y_train_pred))
    r2_val = float(r2_score(y_val, y_val_pred))
    r2_test = float(r2_score(y_test, y_test_pred))

    mae_train = float(mean_absolute_error(y_train, y_train_pred))
    mae_val = float(mean_absolute_error(y_val, y_val_pred))
    mae_test = float(mean_absolute_error(y_test, y_test_pred))

    rmse_train = float(root_mean_squared_error(y_train, y_train_pred))
    rmse_val = float(root_mean_squared_error(y_val, y_val_pred))
    rmse_test = float(root_mean_squared_error(y_test, y_test_pred))

    # Feature importances
    importances = rf_model.feature_importances_
    feat_imp = []
    for name, imp in zip(feature_cols, importances):
        feat_imp.append({"feature": name, "importance_pct": round(float(imp * 100), 2)})
    feat_imp.sort(key=lambda x: x["importance_pct"], reverse=True)

    print("\n========================================")
    print("SMART CRIME INTELLIGENCE ML BENCHMARK")
    print("========================================")
    print(f"Training R²   : {r2_train:.4f} | MAE: {mae_train:.4f} | RMSE: {rmse_train:.4f}")
    print(f"Validation R² : {r2_val:.4f} | MAE: {mae_val:.4f} | RMSE: {rmse_val:.4f}")
    print(f"UNSEEN TEST R²: {r2_test:.4f} | MAE: {mae_test:.4f} | RMSE: {rmse_test:.4f}")
    print(f"Naive Baseline: MAE: {baseline_mae:.4f} | RMSE: {baseline_rmse:.4f}")
    print(f"ML MAE Improvement: {((baseline_mae - mae_test) / baseline_mae) * 100:.1f}%")

    print("\n--- FEATURE IMPORTANCES ---")
    for item in feat_imp:
        print(f"{item['feature']:<25}: {item['importance_pct']}%")

    # Serialize Model & Save Metrics JSON
    joblib.dump({"model": rf_model, "scaler": scaler, "feature_cols": feature_cols}, MODEL_PATH)
    print(f"\n[+] Saved trained model to: {MODEL_PATH}")

    metrics_report = {
        "model_algorithm": "RandomForestRegressor (100 Decision Trees, max_depth=12)",
        "prediction_horizon": "Next 24 Hours",
        "target_variable": "future_24h_crime_count",
        "dataset_type": "Synthetic Historical FIR Dataset (2022-2025)",
        "total_samples": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "train_dates": f"{train_dates[0]} to {train_dates[1]}",
        "val_dates": f"{val_dates[0]} to {val_dates[1]}",
        "test_dates": f"{test_dates[0]} to {test_dates[1]}",
        "metrics": {
            "train_r2": round(r2_train, 4),
            "val_r2": round(r2_val, 4),
            "test_r2": round(r2_test, 4),
            "test_mae": round(mae_test, 4),
            "test_rmse": round(rmse_test, 4),
            "baseline_mae": round(baseline_mae, 4),
            "baseline_rmse": round(baseline_rmse, 4),
            "ml_mae_improvement_pct": round(((baseline_mae - mae_test) / baseline_mae) * 100, 1)
        },
        "target_distribution": {
            "min": float(np.min(y_test)),
            "max": float(np.max(y_test)),
            "mean": float(np.mean(y_test)),
            "std": float(np.std(y_test)),
            "zero_target_pct": round(float((np.sum(y_test == 0) / len(y_test)) * 100), 2)
        },
        "feature_importances": feat_imp,
        "human_in_loop_notice": "ML-based estimated crime activity — for decision support only. Authorized officer interpretation required prior to patrol allocation."
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_report, f, indent=2)
    print(f"[+] Saved metrics report to: {METRICS_PATH}")

if __name__ == "__main__":
    train_and_evaluate()
