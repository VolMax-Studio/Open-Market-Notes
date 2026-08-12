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
    print(f"Event Window   : {event_win.get('start')} to {event_win.get('end')} ({event_win.get('duration_minutes')} min)")
    print(f"Control Days   : {len(control_wins)} baseline control windows (2026-08-05 to 2026-08-11)")
    print(f"Target Zones   : {', '.join(comp_zones)}")
    print(f"Threshold      : q = {q_ref:.2f} | S_thresh = {s_thresh_pct:.1f}% ({params.get('s_thresh_discrete_intervals')})")
    print(f"========================================================================\n")

    zone_results = {}
    zone_completeness = {}
    n_elevated_by_event = 0

    for z in comp_zones:
        filepath = os.path.join(inputs_dir, f'imbalance_{z}.feather')
        if not os.path.exists(filepath):
            print(f"Zone {z:6s} | Status: DATA_PENDING (File not yet fetched: {os.path.basename(filepath)})")
            zone_results[z] = {"status": "DATA_PENDING"}
            zone_completeness[z] = {"completeness_pct": 0.0, "status": "DATA_PENDING"}
            continue

        df = pd.read_feather(filepath)
        t_col = bind_timestamp_col(df)
        df[t_col] = pd.to_datetime(df[t_col], utc=True)
        df = df.set_index(t_col).sort_index()

        z_bind = series_bindings.get(z, {})
        val_col = z_bind.get('imbalance_col', 'imbalance_price_eur_mwh')
        if val_col not in df.columns:
            val_col = [c for c in df.columns if 'price' in c.lower() or 'imbalance' in c.lower() or 'val' in c.lower()][0]

        # 1. Baseline R_z calculation (12M rolling P90, method='linear')
        b_slice = df.loc[b_bounds['start']:b_bounds['end']][val_col].dropna()
        if len(b_slice) == 0:
            raise ValueError(f"Baseline empty for zone {z}")
        r_val = float(np.percentile(b_slice, q_ref * 100.0, method=q_method))

        # 2. Event window measurement (M1 v0.7.4 bounded exposure)
        e_slice = df.loc[event_win['start']:event_win['end']][val_col]
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

        # 3. Control days measurements (Symmetric M1 v0.7.4 bounded exposure)
        control_crossings = 0
        control_details = []

        for c_win in control_wins:
            c_slice = df.loc[c_win['start']:c_win['end']][val_col].dropna()
            c_admitted = len(c_slice)
            c_missing = nominal_mtus - c_admitted
            c_comp_pct = (c_admitted / nominal_mtus) * 100.0 if nominal_mtus > 0 else 0.0

            c_q_count = (c_slice >= r_val).sum() if c_admitted > 0 else 0
            c_exp_lower = (c_q_count) / nominal_mtus if nominal_mtus > 0 else 0.0

            c_crossed = (c_exp_lower >= s_thresh_frac)
            if c_crossed:
                control_crossings += 1

            control_details.append({
                "date": c_win['date'],
                "completeness_pct": round(c_comp_pct, 2),
                "exp_lower_pct": round(c_exp_lower * 100.0, 2),
                "crossed_thresh": c_crossed
            })

        # Per-zone elevation rule
        is_elevated_by_event = (event_determinacy == "ELEVATED") and (control_crossings <= max_control_crossings)
        if is_elevated_by_event:
            n_elevated_by_event += 1

        m1_admitted_pct = (q_count / admitted_mtus) * 100.0 if admitted_mtus > 0 else 0.0

        zone_results[z] = {
            "status": "EVALUATED",
            "target_column": val_col,
            "R_val": round(r_val, 2),
            "M1_admitted_pct": round(m1_admitted_pct, 2),
            "exposure_lower_pct": round(exp_lower * 100.0, 2),
            "exposure_upper_pct": round(exp_upper * 100.0, 2),
            "completeness_pct": round(comp_pct, 2),
            "event_determinacy": event_determinacy,
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

        print(f"Zone {z:6s} | R_z = {r_val:7.2f} | Exp Lower = {exp_lower*100:5.1f}% | Exp Upper = {exp_upper*100:5.1f}% | Control Crossings: {control_crossings}/7 | Verdict: {'ELEVATED_BY_EVENT' if is_elevated_by_event else event_determinacy}")

    all_pending = all(v.get('status') == 'DATA_PENDING' for v in zone_results.values())
    if all_pending:
        print("\nProbe evaluation state: SPREMNO ZA EVALUACIJU (Specification Frozen, Awaiting Telemetry Download).")
        return {"status": "SPREMNO ZA EVALUACIJU", "inputs_manifest_sha256": inputs_manifest_sha256}

    final_verdict = "ELEVATED_BY_EVENT" if n_elevated_by_event > 0 else "NULL"
    print(f"\nFinal Global Probe Verdict: {final_verdict} (Elevated zones: {n_elevated_by_event}/{len(comp_zones)})")

    # Output artifact generation (Fix B19)
    runs_dir = os.path.join(instance_dir, 'runs')
    run_date_dir = os.path.join(runs_dir, '2026-08-12')
    os.makedirs(run_date_dir, exist_ok=True)

    result_json_path = os.path.join(run_date_dir, 'result.json')
    completeness_json_path = os.path.join(run_date_dir, 'completeness.json')
    series_log_path = os.path.join(runs_dir, 'SERIES_LOG.json')

    run_output = {
        "instance_id": params.get('instance_id'),
        "selection_mode": params.get('selection_mode'),
        "evaluation_timestamp_utc": pd.Timestamp.now(tz='UTC').isoformat(),
        "final_verdict": final_verdict,
        "n_elevated_by_event": n_elevated_by_event,
        "inputs_manifest_sha256": inputs_manifest_sha256,
        "zone_results": zone_results
    }

    with open(result_json_path, 'w') as f:
        json.dump(run_output, f, indent=2)

    with open(completeness_json_path, 'w') as f:
        json.dump({"zone_completeness": zone_completeness, "floor_pct": floor_pct}, f, indent=2)

    series_log_entry = [{
        "window": "2026-08-12",
        "evaluated_at": pd.Timestamp.now(tz='UTC').isoformat(),
        "verdict": final_verdict,
        "n_elevated_by_event": n_elevated_by_event,
        "result_sha256": compute_sha256(result_json_path)
    }]

    with open(series_log_path, 'w') as f:
        json.dump(series_log_entry, f, indent=2)

    return {"status": "EVALUATED", "verdict": final_verdict, "zone_results": zone_results}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate Pre-Registered Eclipse Probe")
    parser.add_argument('--instance', type=str, default=None, help='Instance directory')
    args = parser.parse_args()

    evaluate_eclipse_probe(args.instance)
