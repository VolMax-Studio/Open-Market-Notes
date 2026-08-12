#!/usr/bin/env python3
import os
import json
import argparse
import hashlib
import pandas as pd
import numpy as np

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
    for col in ['DateTime', 'timestamp', 'startTime', 'MTU', 'Position', 'index']:
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
    q_method = params.get('quantile_method', 'linear')

    comp_zones = params.get('comparison_zones', ["ES", "PT", "FR", "DE_LU", "NL"])
    series_bindings = params.get('series_bindings', {})
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
    print(f"Event Window   : {event_win.get('start')} to {event_win.get('end')} (Half-Open [start, end), {event_win.get('duration_minutes')} min)")
    print(f"Control Days   : {len(control_wins)} baseline control windows (2026-08-05 to 2026-08-11)")
    print(f"Target Zones   : {', '.join(comp_zones)}")
    print(f"Threshold      : q = {q_ref:.2f} | S_thresh = {s_thresh_pct:.1f}% ({params.get('s_thresh_discrete_intervals')})")
    print(f"========================================================================\n")

    zone_results = {}
    zone_completeness = {}
    zone_determinacies = []
    n_elevated_by_event = 0

    for z in comp_zones:
        filepath = os.path.join(inputs_dir, f'imbalance_{z}.feather')
        if not os.path.exists(filepath):
            print(f"Zone {z:6s} | Status: DATA_PENDING (File not yet fetched: {os.path.basename(filepath)})")
            zone_results[z] = {"status": "DATA_PENDING"}
            zone_completeness[z] = {"completeness_pct": 0.0, "status": "DATA_PENDING"}
            zone_determinacies.append("DATA_PENDING")
            continue

        df = pd.read_feather(filepath)
        t_col = bind_timestamp_col(df)
        df[t_col] = pd.to_datetime(df[t_col], utc=True)
        df = df.set_index(t_col).sort_index()

        z_bind = series_bindings.get(z, {})
        val_col = z_bind.get('imbalance_col', 'imbalance_price_eur_mwh')

        # Fix B26: Require target column explicitly, NO silent fallback!
        if val_col not in df.columns:
            raise KeyError(f"Target column '{val_col}' specified in series_bindings not found in telemetry file for zone {z}. Available columns: {list(df.columns)}")

        # 1. Baseline R_z calculation (12M rolling P90, method='linear') using half-open slicing
        b_start = pd.Timestamp(b_bounds['start'])
        b_end = pd.Timestamp(b_bounds['end'])
        b_slice = df.loc[(df.index >= b_start) & (df.index < b_end)][val_col].dropna()
        if len(b_slice) == 0:
            raise ValueError(f"Baseline empty for zone {z}")
        r_val = float(np.percentile(b_slice, q_ref * 100.0, method=q_method))

        # 2. Event window measurement (Fix B20: Half-Open Interval Slicing [start, end))
        ev_start = pd.Timestamp(event_win['start'])
        ev_end = pd.Timestamp(event_win['end'])
        e_slice = df.loc[(df.index >= ev_start) & (df.index < ev_end)][val_col]
        e_valid = e_slice.dropna()

        nominal_mtus = z_bind.get('nominal_mtus', event_win.get('nominal_15min_mtus', 10))
        admitted_mtus = len(e_valid)
        missing_mtus = nominal_mtus - admitted_mtus
        comp_pct = (admitted_mtus / nominal_mtus) * 100.0 if nominal_mtus > 0 else 0.0

        q_count = (e_valid >= r_val).sum() if admitted_mtus > 0 else 0
        exp_lower = (q_count) / nominal_mtus if nominal_mtus > 0 else 0.0
        exp_upper = (q_count + missing_mtus) / nominal_mtus if nominal_mtus > 0 else 0.0

        # Determinacy evaluation under M1 v0.7.4
        if comp_pct < floor_pct:
            event_determinacy = "INCOMPLETE"
        elif exp_lower >= s_thresh_frac:
            event_determinacy = "ELEVATED"
        elif exp_upper < s_thresh_frac:
            event_determinacy = "NOT_ELEVATED"
        else:
            event_determinacy = "INDETERMINATE"

        # 3. Control days measurements (Fix B23: Symmetric M1 v0.7.4 bounded exposure)
        control_crossings = 0
        incomplete_control_days = 0
        control_details = []

        for c_win in control_wins:
            c_start = pd.Timestamp(c_win['start'])
            c_end = pd.Timestamp(c_win['end'])
            c_slice = df.loc[(df.index >= c_start) & (df.index < c_end)][val_col].dropna()

            c_admitted = len(c_slice)
            c_missing = nominal_mtus - c_admitted
            c_comp_pct = (c_admitted / nominal_mtus) * 100.0 if nominal_mtus > 0 else 0.0

            c_q_count = (c_slice >= r_val).sum() if c_admitted > 0 else 0
            c_exp_lower = (c_q_count) / nominal_mtus if nominal_mtus > 0 else 0.0
            c_exp_upper = (c_q_count + c_missing) / nominal_mtus if nominal_mtus > 0 else 0.0

            if c_comp_pct < floor_pct:
                c_status = "INCOMPLETE"
                incomplete_control_days += 1
                c_crossed = False
            elif c_exp_lower >= s_thresh_frac:
                c_status = "ELEVATED"
                c_crossed = True
            elif c_exp_upper < s_thresh_frac:
                c_status = "NOT_ELEVATED"
                c_crossed = False
            else:
                c_status = "INDETERMINATE"
                c_crossed = True  # Conservative inclusion against false event elevation claim

            if c_crossed:
                control_crossings += 1

            control_details.append({
                "date": c_win['date'],
                "status": c_status,
                "completeness_pct": round(c_comp_pct, 2),
                "exp_lower_pct": round(c_exp_lower * 100.0, 2),
                "exp_upper_pct": round(c_exp_upper * 100.0, 2),
                "crossed_thresh": c_crossed
            })

        # Per-zone elevation rule
        if incomplete_control_days >= 2:
            zone_determinacy = "INCOMPLETE"
            is_elevated_by_event = False
        else:
            is_elevated_by_event = (event_determinacy == "ELEVATED") and (control_crossings <= max_control_crossings)
            if is_elevated_by_event:
                zone_determinacy = "ELEVATED_BY_EVENT"
                n_elevated_by_event += 1
            else:
                zone_determinacy = event_determinacy

        zone_determinacies.append(zone_determinacy)

        m1_admitted_pct = (q_count / admitted_mtus) * 100.0 if admitted_mtus > 0 else 0.0

        zone_results[z] = {
            "status": "EVALUATED",
            "target_column": val_col,
            "R_val": round(r_val, 2),
            "admitted_mtus": admitted_mtus,
            "nominal_mtus": nominal_mtus,
            "M1_admitted_pct": round(m1_admitted_pct, 2),
            "exposure_lower_pct": round(exp_lower * 100.0, 2),
            "exposure_upper_pct": round(exp_upper * 100.0, 2),
            "completeness_pct": round(comp_pct, 2),
            "event_determinacy": event_determinacy,
            "zone_determinacy": zone_determinacy,
            "control_crossings": control_crossings,
            "max_control_crossings_allowed": max_control_crossings,
            "is_elevated_by_event": is_elevated_by_event,
            "control_details": control_details
        }

        zone_completeness[z] = {
            "completeness_pct": round(comp_pct, 2),
            "admitted_mtus": admitted_mtus,
            "nominal_mtus": nominal_mtus,
            "status": "PASS" if comp_pct >= floor_pct else "FAIL"
        }

        print(f"Zone {z:6s} | R_z = {r_val:7.2f} | Admitted: {admitted_mtus}/{nominal_mtus} | Exp Lower: {exp_lower*100:5.1f}% | Exp Upper: {exp_upper*100:5.1f}% | Control Crossings: {control_crossings}/7 | Verdict: {zone_determinacy}")

    all_pending = all(d == 'DATA_PENDING' for d in zone_determinacies)
    if all_pending:
        print("\nProbe evaluation state: SPREMNO ZA EVALUACIJU (Specification Frozen, Awaiting Telemetry Download).")
        return {"status": "SPREMNO ZA EVALUACIJU", "inputs_manifest_sha256": inputs_manifest_sha256}

    # Fix B22: Enum final verdict distinction
    if any(d == "ELEVATED_BY_EVENT" for d in zone_determinacies):
        final_verdict = "ELEVATED_BY_EVENT"
    elif any(d == "INDETERMINATE" for d in zone_determinacies):
        final_verdict = "INDETERMINATE"
    elif any(d == "INCOMPLETE" for d in zone_determinacies):
        final_verdict = "INCOMPLETE"
    else:
        final_verdict = "NULL"

    print(f"\nFinal Global Probe Verdict: {final_verdict} (Elevated zones: {n_elevated_by_event}/{len(comp_zones)})")

    # Fix B19, B28, B29: Output artifact generation & deterministic hash
    runs_dir = os.path.join(instance_dir, 'runs')
    event_date_str = event_win.get('date', '2026-08-12')
    run_date_dir = os.path.join(runs_dir, event_date_str)
    os.makedirs(run_date_dir, exist_ok=True)

    result_json_path = os.path.join(run_date_dir, 'result.json')
    result_meta_path = os.path.join(run_date_dir, 'result_metadata.json')
    completeness_json_path = os.path.join(run_date_dir, 'completeness.json')
    series_log_path = os.path.join(runs_dir, 'SERIES_LOG.json')

    # Deterministic result payload (NO volatile timestamps!)
    deterministic_run_output = {
        "instance_id": params.get('instance_id'),
        "selection_mode": params.get('selection_mode'),
        "final_verdict": final_verdict,
        "n_elevated_by_event": n_elevated_by_event,
        "inputs_manifest_sha256": inputs_manifest_sha256,
        "zone_results": zone_results
    }

    with open(result_json_path, 'w') as f:
        json.dump(deterministic_run_output, f, indent=2)

    # Volatile execution metadata stored separately
    volatile_meta = {
        "evaluation_timestamp_utc": pd.Timestamp.now(tz='UTC').isoformat(),
        "evaluator_script": "evaluate_eclipse_probe.py",
        "result_sha256": compute_sha256(result_json_path)
    }

    with open(result_meta_path, 'w') as f:
        json.dump(volatile_meta, f, indent=2)

    with open(completeness_json_path, 'w') as f:
        json.dump({"zone_completeness": zone_completeness, "floor_pct": floor_pct}, f, indent=2)

    # Fix B28: Append-only SERIES_LOG.json
    existing_log = []
    if os.path.exists(series_log_path):
        try:
            with open(series_log_path, 'r') as f:
                existing_log = json.load(f)
        except Exception:
            existing_log = []

    series_log_entry = {
        "window": event_date_str,
        "evaluated_at": pd.Timestamp.now(tz='UTC').isoformat(),
        "verdict": final_verdict,
        "n_elevated_by_event": n_elevated_by_event,
        "result_sha256": compute_sha256(result_json_path)
    }

    # Append if not duplicate timestamp window
    existing_log = [e for e in existing_log if e.get('window') != event_date_str]
    existing_log.append(series_log_entry)

    with open(series_log_path, 'w') as f:
        json.dump(existing_log, f, indent=2)

    return {"status": "EVALUATED", "verdict": final_verdict, "zone_results": zone_results}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate Pre-Registered Eclipse Probe")
    parser.add_argument('--instance', type=str, default=None, help='Instance directory')
    args = parser.parse_args()

    evaluate_eclipse_probe(args.instance)
