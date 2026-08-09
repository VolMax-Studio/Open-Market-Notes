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

def run_invariance_check(instance_dir, rule_version="v0.7.2"):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")

    # Load params
    with open(params_path) as f:
        content = f.read()
        json_str = content[content.find('{'):content.rfind('}')+1]
        params = json.loads(json_str)

    q_ref = params.get('q_ref', 0.90)
    k_mult = params.get('k_multiplier', 1.50)
    s_thresh = k_mult * (1.0 - q_ref)  # 0.150 = 15.0%

    comp_zones = params.get('comparison_zones', ["AT", "BE", "DK_1", "DK_2", "FR", "NL"])
    companion_zones = params.get('companion_zones', ["GB"])

    inputs_dir = os.path.join(instance_dir, 'inputs')
    
    # Load published v0.6.0 probe report if available for byte-for-byte baseline comparison
    pub_report_path = os.path.join(instance_dir, 'results', 'probe_verdict_report.json')
    published_results = {}
    if os.path.exists(pub_report_path):
        with open(pub_report_path) as f:
            pub_data = json.load(f)
            for z_item in pub_data.get('comparison_zones', []):
                published_results[z_item['zone']] = z_item
            for c_item in pub_data.get('companion_markets', []):
                published_results[c_item['market']] = c_item

    zone_records = []
    all_determinate = True
    n_elevated_v072 = 0

    for z in comp_zones + companion_zones:
        is_companion = z in companion_zones
        if is_companion:
            b_path = os.path.join(inputs_dir, 'gb_system_prices.feather')
            p_path = b_path
            col_name = 'systemSellPrice'
        else:
            b_path = os.path.join(inputs_dir, 'baseline', f'imbalance_{z}.feather')
            p_path = os.path.join(inputs_dir, 'probe_jul2026', f'imbalance_{z}.feather')
            col_name = 'Short'

        df_b = pd.read_feather(b_path)
        t_col_b = [c for c in df_b.columns if 'time' in c.lower() or 'date' in c.lower() or 'index' in c.lower()][0]
        df_b[t_col_b] = pd.to_datetime(df_b[t_col_b], utc=True)
        df_b.set_index(t_col_b, inplace=True)
        df_b.sort_index(inplace=True)

        if is_companion:
            b_slice = df_b.loc['2025-08-01 00:00:00+00:00':'2026-06-30 23:59:59+00:00']
            p_slice = df_b.loc['2026-07-01 00:00:00+00:00':'2026-07-31 23:59:59+00:00']
        else:
            b_slice = df_b
            df_p = pd.read_feather(p_path)
            t_col_p = [c for c in df_p.columns if 'time' in c.lower() or 'date' in c.lower() or 'index' in c.lower()][0]
            df_p[t_col_p] = pd.to_datetime(df_p[t_col_p], utc=True)
            df_p.set_index(t_col_p, inplace=True)
            df_p.sort_index(inplace=True)
            p_slice = df_p

        # Reference Quantile calculation (64-bit float linear interpolation)
        b_series = b_slice[col_name].dropna()
        R_val = float(b_series.quantile(q_ref, interpolation='linear'))

        # Probe window slicing & interval durations
        p_series = p_slice[col_name]
        
        # Nominal seconds calculation (July 2026 = 31 days * 86400s)
        nominal_seconds = 31 * 86400.0
        
        # Admitted timestamps and diffs
        p_valid = p_series.dropna()
        p_times = p_valid.index.to_series()
        diffs_list = p_times.diff().dt.total_seconds().tolist()
        if len(diffs_list) > 1:
            median_dt = float(pd.Series(diffs_list[1:]).median())
            diffs_list[0] = median_dt
        else:
            diffs_list[0] = 900.0
        diffs = pd.Series(diffs_list, index=p_times.index)

        admitted_seconds = float(diffs.sum())
        missing_seconds = float(nominal_seconds - admitted_seconds)
        completeness_pct = (admitted_seconds / nominal_seconds) * 100.0

        # Qualifying intervals (value >= R_val)
        qualifying_mask = p_valid >= R_val
        qualifying_seconds = float(diffs[qualifying_mask].sum())

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

        # v0.6.0 published state
        pub_entry = published_results.get(z, {})
        elevated_v060 = pub_entry.get('elevated', m1_pct >= s_thresh_pct)

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

        # Check numerical identity with v0.6.0
        pub_m1 = pub_entry.get('M1_pct', None)
        implementation_error = False
        if pub_m1 is not None:
            if abs(pub_m1 - m1_pct) > 1e-4:
                implementation_error = True

        # Determine change_reason
        if implementation_error:
            change_reason = "IMPLEMENTATION_ERROR"
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
            'M1_pct': m1_pct,
            'published_v060_M1_pct': pub_m1,
            'completeness_pct': completeness_pct,
            'exposure_lower_pct': exp_lower_pct,
            'exposure_upper_pct': exp_upper_pct,
            'missing_fraction_pct': missing_fraction_pct,
            'elevated_v060': elevated_v060,
            'determinacy_v072': determinacy,
            'changed': changed,
            'change_reason': change_reason
        })

    # Window-level verdict
    n_high = params.get('n_high', 4)
    verdict_v060 = "REGIONAL"
    if not all_determinate:
        verdict_v072 = "NOT_EVALUATED — INDETERMINATE_SET"
    elif n_elevated_v072 >= n_high:
        verdict_v072 = "REGIONAL"
    elif n_elevated_v072 > params.get('n_low', 1):
        verdict_v072 = "ISOLATED"
    else:
        verdict_v072 = "NULL"

    verdict_changed = verdict_v060 != verdict_v072

    report = {
        "_metadata": {
            "title": "M1 v0.7.2 Invariance Verification Report",
            "instance_id": params.get('instance_id', '2026-08-scarcity-jul'),
            "rule_version_evaluated": rule_version,
            "rule_version_baseline": "v0.6.0",
            "executed_at_utc": pd.Timestamp.now(tz='UTC').isoformat(),
            "invariance_obligation_status": "DISCHARGED" if not verdict_changed else "VERDICT_ALTERED"
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
    report['_metadata']['report_sha256'] = report_sha256

    print("\n=======================================================")
    print("      M1 v0.7.2 INVARIANCE VERIFICATION REPORT")
    print("=======================================================")
    print(f"Instance: {params.get('instance_id')}")
    print(f"Evaluated Rule: M1 {rule_version} §4 Exposure Bounds")
    print(f"Report File: {out_path}")
    print(f"Report SHA-256: {report_sha256}\n")

    df_out = pd.DataFrame(zone_records)
    print(df_out[['zone', 'M1_pct', 'completeness_pct', 'exposure_lower_pct', 'exposure_upper_pct', 'elevated_v060', 'determinacy_v072', 'changed', 'change_reason']].to_string(index=False))

    print("\n--- WINDOW-LEVEL VERDICT COMPARISON ---")
    print(f"v0.6.0 Verdict: {verdict_v060}")
    print(f"v0.7.2 Verdict: {verdict_v072}")
    print(f"Verdict Changed: {verdict_changed}")
    print(f"Invariance Status: {report['_metadata']['invariance_obligation_status']}")
    print("=======================================================\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M1 v0.7.2 Invariance Verification Script")
    parser.add_argument('--instance', type=str, default='/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/2026-08-scarcity-jul', help='Instance directory path')
    parser.add_argument('--rule', type=str, default='v0.7.2', help='Rule version to evaluate')
    args = parser.parse_args()
    
    run_invariance_check(args.instance, args.rule)
