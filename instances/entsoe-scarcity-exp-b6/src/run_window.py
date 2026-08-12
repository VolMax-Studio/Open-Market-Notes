#!/usr/bin/env python3
import os
import sys
import json
import argparse
import hashlib
import calendar
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def bind_timestamp_col(df):
    if 'startTime' in df.columns:
        return 'startTime'
    elif 'index' in df.columns:
        return 'index'
    else:
        time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower() or 'index' in c.lower()]
        if time_cols:
            return time_cols[0]
        raise ValueError(f"Unable to find timestamp column in dataframe. Columns: {list(df.columns)}")

def get_window_utc_bounds(window_str, n_baseline_months=6):
    year, month = map(int, window_str.split('-'))
    dt_p_start = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    
    p_start = f"{year:04d}-{month:02d}-01T00:00:00Z"
    p_end = f"{year:04d}-{month:02d}-{last_day:02d}T23:59:59Z"
    
    dt_b_start = dt_p_start - relativedelta(months=n_baseline_months)
    b_start = f"{dt_b_start.year:04d}-{dt_b_start.month:02d}-01T00:00:00Z"
    
    dt_b_end = dt_p_start - relativedelta(days=1)
    b_end = f"{dt_b_end.year:04d}-{dt_b_end.month:02d}-{dt_b_end.day:02d}T23:59:59Z"
    
    return p_start, p_end, b_start, b_end, last_day

def execute_window_run(instance_dir, target_window):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")

    with open(params_path) as f:
        content = f.read()
        json_str = content[content.find('{'):content.rfind('}')+1]
        params = json.loads(json_str)

    q_ref = float(params.get('q_ref', 0.90))
    k_mult = float(params.get('k_multiplier', 1.50))
    s_thresh = k_mult * (1.0 - q_ref)  # 0.150 = 15.0%

    n_low = int(params.get('n_low', 1))
    n_high = int(params.get('n_high', 4))
    n_baseline_months = int(params.get('N', 6))
    floor_pct = float(params.get('completeness_floor_pct', 98.0))

    comp_zones = params.get('comparison_zones', ["AT", "BE", "DK_1", "DK_2", "FR", "NL"])
    companion_zones = params.get('companion_zones', ["GB"])

    inputs_dir = os.path.join(instance_dir, 'inputs')
    inputs_manifest_path = os.path.join(inputs_dir, 'MANIFEST.json')
    inputs_manifest_sha256 = compute_sha256(inputs_manifest_path) if os.path.exists(inputs_manifest_path) else None

    p_start, p_end, b_start, b_end, days_in_month = get_window_utc_bounds(target_window, n_baseline_months)

    zone_metrics = {}
    zone_completeness = {}
    
    all_determinate = True
    any_incomplete = False
    n_elevated_v073 = 0

    for z in comp_zones + companion_zones:
        is_companion = z in companion_zones
        filename = 'gb_system_prices.feather' if is_companion else f'imbalance_{z}.feather'
        filepath = os.path.join(inputs_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file missing: {filepath}")

        col_name = params.get('series_bindings', {}).get(z, {}).get('baseline_col', 'Short' if not is_companion else 'systemSellPrice')
        interval_sec = float(params.get('series_bindings', {}).get(z, {}).get('interval_duration_sec', 900.0 if not is_companion else 1800.0))

        nominal_intervals = int(days_in_month * (86400.0 / interval_sec))
        nominal_seconds = float(nominal_intervals * interval_sec)

        df = pd.read_feather(filepath)
        t_col = bind_timestamp_col(df)
        df[t_col] = pd.to_datetime(df[t_col], utc=True)
        df = df.set_index(t_col).sort_index()

        # Baseline slice
        b_slice = df.loc[b_start:b_end]
        b_series = b_slice[col_name].dropna()
        if len(b_series) == 0:
            raise ValueError(f"Baseline series empty for zone {z} in window {b_start} to {b_end}")
        
        r_val = float(np.percentile(b_series, q_ref * 100.0, method='linear'))

        # Probe slice W
        p_slice = df.loc[p_start:p_end]
        p_valid = p_slice.loc[p_slice[col_name].dropna().index]

        admitted_intervals = len(p_valid)
        admitted_seconds = float(admitted_intervals * interval_sec)
        missing_seconds = float(nominal_seconds - admitted_seconds)
        completeness_pct = (admitted_seconds / nominal_seconds) * 100.0

        qualifying_intervals = int((p_valid[col_name] >= r_val).sum())
        qualifying_seconds = float(qualifying_intervals * interval_sec)

        m1_val = qualifying_seconds / admitted_seconds if admitted_seconds > 0 else 0.0
        m1_pct = round(m1_val * 100.0, 4)

        exp_lower_val = qualifying_seconds / nominal_seconds
        exp_upper_val = (qualifying_seconds + missing_seconds) / nominal_seconds

        exp_lower_pct = round(exp_lower_val * 100.0, 4)
        exp_upper_pct = round(exp_upper_val * 100.0, 4)
        s_thresh_pct = round(s_thresh * 100.0, 4)

        if completeness_pct < floor_pct:
            determinacy = "INCOMPLETE"
            if not is_companion:
                any_incomplete = True
        elif exp_lower_pct >= s_thresh_pct:
            determinacy = "ELEVATED"
            if not is_companion:
                n_elevated_v073 += 1
        elif exp_upper_pct < s_thresh_pct:
            determinacy = "NOT_ELEVATED"
        else:
            determinacy = "INDETERMINATE"
            if not is_companion:
                all_determinate = False

        zone_metrics[z] = {
            "R_val": round(r_val, 4),
            "M1_pct": m1_pct,
            "completeness_pct": round(completeness_pct, 4),
            "missing_fraction_pct": round((missing_seconds / nominal_seconds) * 100.0, 4),
            "exposure_lower_pct": exp_lower_pct,
            "exposure_upper_pct": exp_upper_pct,
            "determinacy": determinacy,
            "is_companion": is_companion
        }

        zone_completeness[z] = {
            "nominal_intervals": nominal_intervals,
            "admitted_intervals": admitted_intervals,
            "missing_intervals": nominal_intervals - admitted_intervals,
            "nominal_seconds": nominal_seconds,
            "admitted_seconds": admitted_seconds,
            "completeness_pct": round(completeness_pct, 4),
            "passes_floor": completeness_pct >= floor_pct
        }

    # Window-level classification
    if any_incomplete:
        evaluation_status = "NOT_EVALUATED — INCOMPLETE_SET"
        label = None
    elif not all_determinate:
        evaluation_status = "NOT_EVALUATED — INDETERMINATE_SET"
        label = None
    elif n_elevated_v073 >= n_high:
        evaluation_status = "EVALUATED"
        label = "REGIONAL"
    elif n_elevated_v073 > n_low:
        evaluation_status = "EVALUATED"
        label = "ISOLATED"
    else:
        evaluation_status = "EVALUATED"
        label = "NULL"

    # Deterministic result dictionary (NO timestamps, NO file hashes inside result.json per SERIES_TEMPLATE §4)
    result_data = {
        "instance_id": params.get('instance_id', 'entsoe-scarcity-exp-b6'),
        "window": target_window,
        "window_utc_bounds": {
            "start": p_start,
            "end": p_end
        },
        "baseline_utc_bounds": {
            "start": b_start,
            "end": b_end
        },
        "evaluation_status": evaluation_status,
        "label": label,
        "N_total_comparison_zones": len(comp_zones),
        "N_elevated_comparison_zones": n_elevated_v073,
        "s_thresh_pct": round(s_thresh * 100.0, 4),
        "zone_metrics": zone_metrics
    }

    completeness_data = {
        "window": target_window,
        "completeness_floor_pct": floor_pct,
        "zone_completeness": zone_completeness
    }

    # Write run outputs to runs/YYYY-MM/
    run_dir = os.path.join(instance_dir, 'runs', target_window)
    os.makedirs(run_dir, exist_ok=True)

    result_path = os.path.join(run_dir, 'result.json')
    with open(result_path, 'w') as f:
        json.dump(result_data, f, indent=2, sort_keys=True)

    comp_path = os.path.join(run_dir, 'completeness.json')
    with open(comp_path, 'w') as f:
        json.dump(completeness_data, f, indent=2, sort_keys=True)

    result_sha256 = compute_sha256(result_path)

    # Update SERIES_LOG.json
    runs_dir = os.path.join(instance_dir, 'runs')
    log_path = os.path.join(runs_dir, 'SERIES_LOG.json')

    log_entries = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            log_entries = json.load(f)

    # Replace or append record for target_window
    existing_idx = next((i for i, item in enumerate(log_entries) if item.get('window') == target_window), None)
    
    log_record = {
        "window": target_window,
        "evaluation_status": evaluation_status,
        "label": label,
        "result_json_sha256": result_sha256,
        "inputs_manifest_sha256": inputs_manifest_sha256,
        "N_elevated": n_elevated_v073 if evaluation_status == "EVALUATED" else None,
        "evaluated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    if existing_idx is not None:
        log_entries[existing_idx] = log_record
    else:
        log_entries.append(log_record)

    log_entries.sort(key=lambda x: x['window'])

    with open(log_path, 'w') as f:
        json.dump(log_entries, f, indent=2)

    print(f"[{target_window}] Status: {evaluation_status} | Label: {label} | Elevated Zones: {n_elevated_v073}/6 | result.json SHA-256: {result_sha256[:12]}...")

    return result_data, result_sha256

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run 6M Exploratory Window Evaluation")
    parser.add_argument('--window', type=str, required=True, help='Target window in YYYY-MM format')
    parser.add_argument('--instance', type=str, default='/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/entsoe-scarcity-exp-b6', help='Instance directory')
    args = parser.parse_args()

    execute_window_run(args.instance, args.window)
