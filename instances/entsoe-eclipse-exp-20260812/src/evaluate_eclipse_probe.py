#!/usr/bin/env python3
import os
import sys
import json
import argparse
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime, timezone

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_instance_dir():
    # Anchor to script location, never hardcode absolute home paths!
    src_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(src_dir)

def bind_timestamp_col(df):
    for col in ['SETTLEMENTDATE', 'startTime', 'timestamp', 'index']:
        if col in df.columns:
            return col
    time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()]
    if time_cols:
        return time_cols[0]
    raise ValueError(f"Unable to find timestamp column. Columns: {list(df.columns)}")

def evaluate_eclipse_probe(instance_dir=None):
    if instance_dir is None:
        instance_dir = get_instance_dir()

    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")

    with open(params_path) as f:
        content = f.read()
        json_str = content[content.find('{'):content.rfind('}')+1]
        params = json.loads(json_str)

    q_ref = float(params.get('q_ref', 0.90))
    s_thresh_pct = float(params.get('s_thresh_pct', 20.0))
    s_thresh_frac = s_thresh_pct / 100.0
    floor_pct = float(params.get('completeness_floor_pct', 80.0))
    max_control_crossings = int(params.get('max_control_crossings_allowed', 2))

    comp_zones = params.get('comparison_zones', ["ES", "PT", "FR", "DE_LU", "NL"])
    event_win = params.get('event_utc_window', {})
    control_wins = params.get('control_utc_windows', [])
    b_bounds = params.get('baseline_utc_bounds', {})

    inputs_dir = os.path.join(instance_dir, 'inputs')
    inputs_manifest_path = os.path.join(inputs_dir, 'MANIFEST.json')
    inputs_manifest_sha256 = compute_sha256(inputs_manifest_path) if os.path.exists(inputs_manifest_path) else None

    print(f"========================================================================")
    print(f"  PRE-REGISTERED SOLAR ECLIPSE PROBE EVALUATOR ({params.get('instance_id')})")
    print(f"========================================================================")
    print(f"Instance Dir   : {instance_dir}")
    print(f"Event Window   : {event_win.get('start')} to {event_win.get('end')} ({event_win.get('duration_minutes')} min)")
    print(f"Control Days   : {len(control_wins)} baseline control windows (2026-08-05 to 2026-08-11)")
    print(f"Target Zones   : {', '.join(comp_zones)}")
    print(f"Threshold      : q = {q_ref:.2f} | S_thresh = {s_thresh_pct:.1f}% ({params.get('s_thresh_discrete_intervals')})")
    print(f"========================================================================\n")

    zone_results = {}
    n_elevated_by_event = 0

    for z in comp_zones:
        filepath = os.path.join(inputs_dir, f'imbalance_{z}.feather')
        if not os.path.exists(filepath):
            print(f"Zone {z:6s} | Status: DATA_PENDING (File not yet fetched: {os.path.basename(filepath)})")
            zone_results[z] = {"status": "DATA_PENDING"}
            continue

        df = pd.read_feather(filepath)
        t_col = bind_timestamp_col(df)
        df[t_col] = pd.to_datetime(df[t_col], utc=True)
        df = df.set_index(t_col).sort_index()

        val_col = [c for c in df.columns if 'price' in c.lower() or 'imbalance' in c.lower() or 'val' in c.lower()][0]

        # 1. Baseline R_z calculation (12M rolling P90)
        b_slice = df.loc[b_bounds['start']:b_bounds['end']][val_col].dropna()
        if len(b_slice) == 0:
            raise ValueError(f"Baseline empty for zone {z}")
        r_val = float(np.percentile(b_slice, q_ref * 100.0, method='linear'))

        # 2. Event window measurement
        e_slice = df.loc[event_win['start']:event_win['end']][val_col]
        e_valid = e_slice.dropna()
        nominal_mtus = event_win.get('nominal_15min_mtus', 10)
        admitted_mtus = len(e_valid)
        missing_mtus = nominal_mtus - admitted_mtus
        comp_pct = (admitted_mtus / nominal_mtus) * 100.0

        q_count = (e_valid >= r_val).sum()
        exp_lower = (q_count) / nominal_mtus
        exp_upper = (q_count + missing_mtus) / nominal_mtus

        event_elevated = (exp_lower >= s_thresh_frac)

        # 3. Control days measurements
        control_crossings = 0
        control_details = []

        for c_win in control_wins:
            c_slice = df.loc[c_win['start']:c_win['end']][val_col].dropna()
            c_nom = nominal_mtus
            c_q_count = (c_slice >= r_val).sum() if len(c_slice) > 0 else 0
            c_m1_pct = (c_q_count / c_nom) * 100.0 if c_nom > 0 else 0.0
            crossed = (c_m1_pct >= s_thresh_pct)
            if crossed:
                control_crossings += 1
            control_details.append({
                "date": c_win['date'],
                "M1_pct": round(c_m1_pct, 2),
                "crossed_thresh": crossed
            })

        # Classification rule
        is_elevated_by_event = event_elevated and (control_crossings <= max_control_crossings)
        if is_elevated_by_event:
            n_elevated_by_event += 1

        zone_results[z] = {
            "status": "EVALUATED",
            "R_val": round(r_val, 2),
            "event_M1_pct": round((q_count / admitted_mtus) * 100.0, 2) if admitted_mtus > 0 else 0.0,
            "completeness_pct": round(comp_pct, 2),
            "exposure_lower_pct": round(exp_lower * 100.0, 2),
            "exposure_upper_pct": round(exp_upper * 100.0, 2),
            "event_elevated": event_elevated,
            "control_crossings": control_crossings,
            "max_control_crossings_allowed": max_control_crossings,
            "is_elevated_by_event": is_elevated_by_event,
            "control_details": control_details
        }

        print(f"Zone {z:6s} | R_z = {r_val:7.2f} | Event M1 = {zone_results[z]['event_M1_pct']:6.2f}% | Control Crossings: {control_crossings}/7 | Verdict: {'ELEVATED_BY_EVENT' if is_elevated_by_event else 'NOT_ELEVATED'}")

    all_pending = all(v.get('status') == 'DATA_PENDING' for v in zone_results.values())
    if all_pending:
        print("\nProbe evaluation state: SPREMNO ZA EVALUACIJU (Specification Frozen, Awaiting Telemetry Download).")
        return {"status": "SPREMNO ZA EVALUACIJU", "inputs_manifest_sha256": inputs_manifest_sha256}

    final_verdict = "ELEVATED_BY_EVENT" if n_elevated_by_event > 0 else "NULL"
    print(f"\nFinal Global Probe Verdict: {final_verdict} (Elevated zones: {n_elevated_by_event}/{len(comp_zones)})")

    return {"status": "EVALUATED", "verdict": final_verdict, "zone_results": zone_results}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate Pre-Registered Eclipse Probe")
    parser.add_argument('--instance', type=str, default=None, help='Instance directory')
    args = parser.parse_args()

    evaluate_eclipse_probe(args.instance)
