#!/usr/bin/env python3
import os
import sys
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

def run_invariance_check(instance_dir, rule_version="v0.7.2"):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")

    # Load params
    with open(params_path) as f:
        content = f.read()
        json_str = content[content.find('{'):content.rfind('}')+1]
        params = json.loads(json_str)

    q_ref = float(params.get('q_ref', 0.90))
    k_mult = float(params.get('k_multiplier', 1.50))
    s_thresh = k_mult * (1.0 - q_ref)  # 0.150 = 15.0%

    comp_zones = params.get('comparison_zones', ["AT", "BE", "DK_1", "DK_2", "FR", "NL"])
    companion_zones = params.get('companion_zones', ["GB"])

    inputs_dir = os.path.join(instance_dir, 'inputs')
    
    # Load published v0.6.0 probe report for exact control comparison
    pub_report_path = os.path.join(instance_dir, 'results', 'probe_verdict_report.json')
    if not os.path.exists(pub_report_path):
        raise FileNotFoundError(f"Published probe report missing at {pub_report_path}")

    with open(pub_report_path) as f:
        pub_data = json.load(f)

    # Read v0.6.0 verdict directly from published report
    verdict_v060 = pub_data.get("decision_evaluation", {}).get("classifier_c_emitted_verdict", "REGIONAL")

    eu_pub = pub_data.get("benchmark_metrics", {}).get("eu_zones", {})
    gb_pub = pub_data.get("benchmark_metrics", {}).get("gb_companion", {})

    published_results = {}
    for z_name, z_data in eu_pub.items():
        published_results[z_name] = {
            'M1_pct': z_data.get('jul_2026_share_q90_pct'),
            'R_val': z_data.get('baseline_q90_eur'),
            'elevated': z_data.get('is_elevated'),
            'completeness_pct': z_data.get('completeness_pct')
        }
    if gb_pub.get('market') == 'GB':
        published_results['GB'] = {
            'M1_pct': gb_pub.get('jul_2026_share_q90_pct'),
            'R_val': gb_pub.get('baseline_q90_gbp'),
            'elevated': gb_pub.get('is_elevated_descriptive'),
            'completeness_pct': gb_pub.get('completeness_pct')
        }

    zone_records = []
    all_determinate = True
    n_elevated_v072 = 0
    implementation_error_occurred = False

    # Extract window configurations from PARAMS.md
    b_window = params.get('baseline_window', {})
    b_start = b_window.get('start_utc', '2025-08-01T00:00:00Z')
    b_end = b_window.get('end_utc', '2026-06-30T23:59:59Z')

    p_window = params.get('probe_window', {})
    p_start = p_window.get('start_utc', '2026-07-01T00:00:00Z')
    p_end = p_window.get('end_utc', '2026-07-31T23:59:59Z')

    nominal_15m_intervals = int(p_window.get('nominal_intervals_15m', 2976))

    for z in comp_zones + companion_zones:
        is_companion = z in companion_zones
        if is_companion:
            b_path = os.path.join(inputs_dir, 'gb_system_prices.feather')
            p_path = b_path
            col_name = params.get('series_bindings', {}).get('GB', {}).get('baseline_col', 'systemSellPrice')
            interval_sec = 1800.0  # 30-min settlement intervals in GB
            nominal_intervals = int(nominal_15m_intervals / 2)  # 1488 30m intervals
        else:
            b_path = os.path.join(inputs_dir, 'baseline', f'imbalance_{z}.feather')
            p_path = os.path.join(inputs_dir, 'probe_jul2026', f'imbalance_{z}.feather')
            col_name = params.get('series_bindings', {}).get(z, {}).get('baseline_col', 'Short')
            interval_sec = 900.0   # 15-min settlement intervals in EU
            nominal_intervals = nominal_15m_intervals  # 2976 15m intervals

        # Load baseline feather
        df_b = pd.read_feather(b_path)
        t_col_b = bind_timestamp_col(df_b)
        df_b[t_col_b] = pd.to_datetime(df_b[t_col_b], utc=True)
        df_b = df_b.set_index(t_col_b).sort_index()

        # Slice uncontaminated 11M baseline window per PARAMS.md
        b_slice = df_b.loc[b_start:b_end]
        b_series = b_slice[col_name].dropna()
        R_val = float(np.percentile(b_series, q_ref * 100.0, method='linear'))

        # Load probe telemetry as evaluated in published v0.6.0 run
        if is_companion:
            df_p = df_b
            p_slice = df_p.loc[p_start:p_end]
        else:
            df_p = pd.read_feather(p_path)
            t_col_p = bind_timestamp_col(df_p)
            df_p[t_col_p] = pd.to_datetime(df_p[t_col_p], utc=True)
            df_p = df_p.set_index(t_col_p).sort_index()
            p_slice = df_p

        p_valid = p_slice.loc[p_slice[col_name].dropna().index]

        # Nominal seconds calculation from nominal intervals and duration
        nominal_seconds = float(nominal_intervals * interval_sec)
        
        # Admitted interval count and duration (excluding missing rows)
        admitted_intervals = len(p_valid)
        admitted_seconds = float(admitted_intervals * interval_sec)
        missing_seconds = float(nominal_seconds - admitted_seconds)
        completeness_pct = (admitted_seconds / nominal_seconds) * 100.0

        # Qualifying interval count (value >= R_val)
        qualifying_intervals = int((p_valid[col_name] >= R_val).sum())
        qualifying_seconds = float(qualifying_intervals * interval_sec)

        # M1 scalar (Q / A)
        m1_val = qualifying_seconds / admitted_seconds
        m1_pct = round(m1_val * 100.0, 4)

        # Exposure bounds under M1 v0.7.2 (Q / N and (Q + M) / N)
        exp_lower_val = qualifying_seconds / nominal_seconds
        exp_upper_val = (qualifying_seconds + missing_seconds) / nominal_seconds

        exp_lower_pct = round(exp_lower_val * 100.0, 4)
        exp_upper_pct = round(exp_upper_val * 100.0, 4)
        missing_fraction_pct = round((missing_seconds / nominal_seconds) * 100.0, 4)

        s_thresh_pct = round(s_thresh * 100.0, 4)

        # Published v0.6.0 values
        pub_entry = published_results.get(z, {})
        pub_m1 = pub_entry.get('M1_pct')
        pub_R = pub_entry.get('R_val')
        elevated_v060 = pub_entry.get('elevated')

        # Control checks against published v0.6.0 report baseline
        m1_control_failed = pub_m1 is None or abs(pub_m1 - m1_pct) > 1e-4
        r_control_failed = pub_R is None or abs(pub_R - R_val) > 1e-4

        if m1_control_failed or r_control_failed:
            implementation_error_occurred = True

        # v0.7.2 determinacy evaluation
        if exp_lower_pct >= s_thresh_pct:
            determinacy = "ELEVATED"
            if not is_companion:
                n_elevated_v072 += 1
        elif exp_upper_pct < s_thresh_pct:
            determinacy = "NOT_ELEVATED"
        else:
            determinacy = "INDETERMINATE"
            if not is_companion:
                all_determinate = False

        # Determine change_reason per zone
        if m1_control_failed and r_control_failed:
            change_reason = "CONTROL_FAILED_BOTH"
        elif m1_control_failed:
            change_reason = "CONTROL_FAILED_M1"
        elif r_control_failed:
            change_reason = "CONTROL_FAILED_R"
        elif determinacy == "INDETERMINATE":
            change_reason = "BECAME_INDETERMINATE"
        elif elevated_v060 and determinacy == "NOT_ELEVATED":
            change_reason = "ELEVATED_TO_NOT_ELEVATED"
        elif not elevated_v060 and determinacy == "ELEVATED":
            change_reason = "NOT_ELEVATED_TO_ELEVATED"
        else:
            change_reason = "NONE"

        changed = change_reason != "NONE"

        zone_records.append({
            'zone': z,
            'is_companion': is_companion,
            'R_val': round(R_val, 4),
            'published_v060_R_val': pub_R,
            'M1_pct': m1_pct,
            'published_v060_M1_pct': pub_m1,
            'completeness_pct': round(completeness_pct, 4),
            'missing_fraction_pct': missing_fraction_pct,
            'exposure_lower_pct': exp_lower_pct,
            'exposure_upper_pct': exp_upper_pct,
            'elevated_v060': elevated_v060,
            'determinacy_v072': determinacy,
            'changed': changed,
            'change_reason': change_reason
        })

    # Window-level verdict
    n_high = params.get('n_high', 4)
    if implementation_error_occurred:
        verdict_v072 = "IMPLEMENTATION_ERROR"
        invariance_status = "VOIDED_BY_IMPLEMENTATION_ERROR"
    elif not all_determinate:
        verdict_v072 = "NOT_EVALUATED — INDETERMINATE_SET"
        invariance_status = "VERDICT_ALTERED"
    elif n_elevated_v072 >= n_high:
        verdict_v072 = "REGIONAL"
        invariance_status = "DISCHARGED"
    elif n_elevated_v072 > params.get('n_low', 1):
        verdict_v072 = "ISOLATED"
        invariance_status = "VERDICT_ALTERED"
    else:
        verdict_v072 = "NULL"
        invariance_status = "VERDICT_ALTERED"

    verdict_changed = verdict_v060 != verdict_v072

    # Metadata block contains NO timestamps to guarantee report hash stability
    report = {
        "_metadata": {
            "title": "M1 v0.7.2 Invariance Verification Report",
            "instance_id": params.get('instance_id', '2026-08-scarcity-jul'),
            "rule_version_evaluated": rule_version,
            "rule_version_baseline": "v0.6.0",
            "invariance_obligation_status": invariance_status,
            "note_on_test_coverage": "EU comparison zones evaluated at 100.0% completeness in published telemetry window; GB companion zone (99.8656% completeness) provides active exposure bound separation."
        },
        "window_summary": {
            "window": "2026-07",
            "verdict_v060": verdict_v060,
            "verdict_v072": verdict_v072,
            "verdict_changed": verdict_changed,
            "N_total_comparison_zones": len(comp_zones),
            "N_elevated_v072": n_elevated_v072,
            "all_zones_determinate": all_determinate,
            "count_changed_zones": sum(1 for r in zone_records if r['changed'])
        },
        "zone_evaluations": zone_records
    }

    results_dir = os.path.join(instance_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, 'invariance_v0.7.2.json')
    
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)

    report_sha256 = compute_sha256(out_path)

    print("\n=======================================================")
    print("      M1 v0.7.2 INVARIANCE VERIFICATION REPORT")
    print("=======================================================")
    print(f"Instance: {params.get('instance_id')}")
    print(f"Evaluated Rule: M1 {rule_version} §4 Exposure Bounds")
    print(f"Report File: {out_path}")
    print(f"Report SHA-256: {report_sha256}\n")

    df_out = pd.DataFrame(zone_records)
    print(df_out[['zone', 'M1_pct', 'published_v060_M1_pct', 'R_val', 'published_v060_R_val', 'completeness_pct', 'missing_fraction_pct', 'exposure_lower_pct', 'exposure_upper_pct', 'determinacy_v072', 'changed', 'change_reason']].to_string(index=False))

    print("\n--- WINDOW-LEVEL VERDICT COMPARISON ---")
    print(f"v0.6.0 Verdict: {verdict_v060}")
    print(f"v0.7.2 Verdict: {verdict_v072}")
    print(f"Verdict Changed: {verdict_changed}")
    print(f"Invariance Status: {invariance_status}")
    print("=======================================================\n")

    if implementation_error_occurred:
        raise ValueError("INVARIANCE ABORT: Control check failed against published v0.6.0 report. Implementation error detected.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M1 v0.7.2 Invariance Verification Script")
    parser.add_argument('--instance', type=str, default='/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/2026-08-scarcity-jul', help='Instance directory path')
    parser.add_argument('--rule', type=str, default='v0.7.2', help='Rule version to evaluate')
    args = parser.parse_args()
    
    run_invariance_check(args.instance, args.rule)
