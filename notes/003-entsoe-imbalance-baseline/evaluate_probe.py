#!/usr/bin/env python3
"""
VolMax Open Market Note #003 Probe: Pre-Registered Decision Verdict Evaluator
Strict Manifest-Bound Evaluation of July 2026 Imbalance Scarcity Elevation (C1-C5)
"""

import os
import sys
import json
import hashlib
import subprocess
import pandas as pd
import numpy as np

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def get_active_git_commit(note_dir='.'):
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=note_dir, stderr=subprocess.DEVNULL).decode().strip()
        if commit and len(commit) >= 7:
            return commit
    except Exception as e:
        raise ValueError(f"GIT PROVENANCE ABORT: Unable to resolve active git commit HEAD: {e}")
    raise ValueError("GIT PROVENANCE ABORT: Resolved empty git commit HEAD.")

def resolve_datetime_col(df, filename):
    if 'index' in df.columns:
        return 'index'
    for col in df.columns:
        if 'time' in col.lower() or 'date' in col.lower() or pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    raise ValueError(f"DATAFRAME ABORT: Unable to resolve datetime column for {filename}. Available columns: {list(df.columns)}")

def evaluate_probe(note_dir='.', probe_dir='probe_jul2026'):
    target_probe_path = os.path.join(note_dir, probe_dir)
    if not os.path.exists(target_probe_path):
        raise ValueError(f"PROBE ABORT: Target probe directory missing at {target_probe_path}")

    manifest_path = os.path.join(note_dir, 'data_manifest.json')
    if not os.path.exists(manifest_path):
        raise ValueError(f"MANIFEST ABORT: data_manifest.json missing at {manifest_path}")

    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)

    files_list = manifest_data.get("files", [])
    manifest_dict = {item["file_name"]: item for item in files_list if isinstance(item, dict) and "file_name" in item}

    zones = ['AT', 'BE', 'DK_1', 'DK_2', 'FR', 'NL']
    eu_results = {}
    elevated_count = 0
    actual_intervals_dict = {}
    zone_no_gaps_dict = {}
    zone_completeness_dict = {}

    # Target July 2026 window: 31 days * 96 15-min MTUs = 2,976 expected MTU intervals
    expected_intervals_per_zone = 31 * 96

    print("=== EXECUTING VOLMAX NOTE #3 PROBE EVALUATOR (STRICT MANIFEST BINDING) ===")

    for zone in zones:
        # Load baseline feather to compute uncontaminated Q90 (1 Aug 2025 - 30 Jun 2026)
        base_feather = os.path.join(note_dir, 'data', 'processed', f"imbalance_{zone}.feather")
        if not os.path.exists(base_feather):
            raise ValueError(f"BASELINE ABORT: Baseline feather file missing for {zone} at {base_feather}")

        base_df = pd.read_feather(base_feather)
        time_col = resolve_datetime_col(base_df, f"imbalance_{zone}.feather (baseline)")
        base_df[time_col] = pd.to_datetime(base_df[time_col])
        base_df = base_df.set_index(time_col)

        # Enforce manifest-bound shortage column selection
        manifest_csv_key = f"imbalance_{zone}_202506_202606.csv"
        if manifest_csv_key not in manifest_dict:
            raise ValueError(f"MANIFEST ABORT: Missing baseline manifest entry for {manifest_csv_key}")

        regime_info = manifest_dict[manifest_csv_key]
        if "m1_shortage_col" not in regime_info:
            raise ValueError(f"MANIFEST ABORT: 'm1_shortage_col' missing in manifest entry for {manifest_csv_key}")

        shortage_col = regime_info["m1_shortage_col"]
        if shortage_col not in base_df.columns:
            raise ValueError(f"MANIFEST ABORT: Shortage column '{shortage_col}' bound in manifest for {zone} missing in baseline columns: {list(base_df.columns)}")

        # Uncontaminated baseline window (11 calendar months)
        uncontam_df = base_df['2025-08-01':'2026-06-30']
        q90 = float(uncontam_df[shortage_col].quantile(0.90))

        # Load Probe July 2026 feather
        probe_feather = os.path.join(target_probe_path, 'processed', f"imbalance_{zone}.feather")
        if not os.path.exists(probe_feather):
            raise ValueError(f"PROBE ABORT: Probe feather file missing for {zone} at {probe_feather}")

        probe_df = pd.read_feather(probe_feather)
        p_time_col = resolve_datetime_col(probe_df, f"imbalance_{zone}.feather (probe)")
        probe_df[p_time_col] = pd.to_datetime(probe_df[p_time_col])
        probe_df = probe_df.set_index(p_time_col)

        # Enforce manifest-bound shortage column on probe dataset
        if shortage_col not in probe_df.columns:
            raise ValueError(f"MANIFEST ABORT: Shortage column '{shortage_col}' bound in manifest for {zone} missing in probe columns: {list(probe_df.columns)}")

        p_shortage_col = shortage_col
        actual_intervals = len(probe_df)
        actual_intervals_dict[zone] = actual_intervals
        zone_completeness = round((actual_intervals / expected_intervals_per_zone) * 100.0, 4)
        zone_completeness_dict[zone] = zone_completeness

        # Measured telemetry gap audit
        time_diffs = pd.Series(probe_df.index).diff()
        max_gap_seconds = float(time_diffs.max().total_seconds()) if len(time_diffs) > 1 else 900.0
        no_gaps_gt_15m = bool(max_gap_seconds <= 900.0)
        zone_no_gaps_dict[zone] = no_gaps_gt_15m

        # Mandate 8 Completeness Check (>= 98.0% threshold)
        if zone_completeness < 98.0:
            raise ValueError(f"MANDATE 8 ABORT: {zone} probe telemetry incomplete: {actual_intervals}/{expected_intervals_per_zone} ({zone_completeness:.2f}%).")

        if not no_gaps_gt_15m:
            raise ValueError(f"MANDATE 8 ABORT: {zone} probe telemetry contains gap exceeding 15 minutes (Max gap = {max_gap_seconds/60.0:.1f} min).")

        # Compute S(z) share >= Q90
        share_q90 = float((probe_df[p_shortage_col] >= q90).mean() * 100.0)
        is_elevated = share_q90 >= 15.0

        if is_elevated:
            elevated_count += 1

        eu_results[zone] = {
            "baseline_q90_eur": round(q90, 2),
            "jul_2026_share_q90_pct": round(share_q90, 2),
            "is_elevated": is_elevated,
            "manifest_bound_column": p_shortage_col,
            "probe_intervals": actual_intervals,
            "completeness_pct": zone_completeness,
            "no_gaps_exceeding_15min": no_gaps_gt_15m
        }

        print(f"Zone {zone:4s}: Q90 = €{q90:6.2f}/MWh | S(z) = {share_q90:5.2f}% | Elevated: {is_elevated}")

    # GB Matched Pair Comparator Evaluation
    gb_feather = os.path.join(note_dir, '..', '004-gb-duration-baseline', 'data', 'processed', 'gb_system_prices.feather')
    if not os.path.exists(gb_feather):
        raise ValueError(f"GB COMPARATOR ABORT: GB dataset missing at {gb_feather}")

    gb_df = pd.read_feather(gb_feather)
    gb_time_col = resolve_datetime_col(gb_df, "gb_system_prices.feather")
    gb_df[gb_time_col] = pd.to_datetime(gb_df[gb_time_col])
    gb_df = gb_df.set_index(gb_time_col).tz_convert('Europe/London')

    gb_base = gb_df['2025-08-01':'2026-06-30']
    gb_q90 = float(gb_base['systemSellPrice'].quantile(0.90))

    gb_jul26 = gb_df['2026-07-01':'2026-07-31']
    gb_jul25 = gb_df['2025-07-01':'2025-07-31']

    gb_share_jul26 = float((gb_jul26['systemSellPrice'] >= gb_q90).mean() * 100.0)
    gb_share_jul25 = float((gb_jul25['systemSellPrice'] >= gb_q90).mean() * 100.0)
    gb_is_elevated = gb_share_jul26 >= 15.0

    print(f"\nGB Comparator: Q90 = £{gb_q90:.2f}/MWh | Jul26 S(GB) = {gb_share_jul26:.2f}% | Elevated: {gb_is_elevated}")

    # Pre-Registered Decision Rule (C4)
    if gb_is_elevated and elevated_count >= 4:
        verdict = "REGIONAL"
    elif gb_is_elevated and elevated_count <= 1:
        verdict = "GB-SPECIFIC"
    else:
        verdict = "INCONCLUSIVE"

    print(f"\n=== PRE-REGISTERED VERDICT: {verdict} (N_elevated = {elevated_count} of 6 EU zones) ===")

    total_actual_intervals = sum(actual_intervals_dict.values())
    total_expected_intervals = len(zones) * expected_intervals_per_zone
    overall_completeness_pct = round((total_actual_intervals / total_expected_intervals) * 100.0, 4)
    overall_no_gaps = all(zone_no_gaps_dict.values())

    active_commit = get_active_git_commit(note_dir)

    report = {
        "probe_name": "OMN-003 July 2026 Recurrence & European Imbalance Scarcity Probe",
        "execution_timestamp_utc": pd.Timestamp.now(tz='UTC').isoformat(),
        "provenance": {
            "git_commit": active_commit,
            "evaluator_script": "notes/003-entsoe-imbalance-baseline/evaluate_probe.py",
            "evaluator_sha256": compute_sha256(os.path.join(note_dir, 'evaluate_probe.py')),
            "params_hash": "acc7111a0119f835540689fcffbe7f3333cef9d2b580bc81e8174c2add2c9e58",
            "pre_registered_ratifier": "Ivan Nestorov (2026-08-08)"
        },
        "mandate_8_telemetry_audit": {
            "expected_intervals_per_zone": expected_intervals_per_zone,
            "actual_intervals_per_zone": actual_intervals_dict,
            "measured_completeness_pct": overall_completeness_pct,
            "measured_no_gaps_exceeding_15min": overall_no_gaps,
            "mandate_8_status": "PASSED" if (overall_completeness_pct >= 98.0 and overall_no_gaps) else "FAILED"
        },
        "benchmark_metrics": {
            "gb_comparator": {
                "market": "GB",
                "baseline_q90_gbp": round(gb_q90, 2),
                "jul_2026_share_q90_pct": round(gb_share_jul26, 2),
                "jul_2025_share_q90_pct": round(gb_share_jul25, 2),
                "is_elevated": gb_is_elevated
            },
            "eu_zones": eu_results
        },
        "decision_evaluation": {
            "frozen_elevation_threshold_pct": 15.0,
            "frozen_n_high_threshold": 4,
            "frozen_n_low_threshold": 1,
            "total_eu_zones_elevated": elevated_count,
            "elevated_eu_zones_list": [z for z, r in eu_results.items() if r["is_elevated"]],
            "non_elevated_eu_zones_list": [z for z, r in eu_results.items() if not r["is_elevated"]],
            "pre_registered_verdict": verdict
        }
    }

    out_report_path = os.path.join(target_probe_path, 'probe_verdict_report.json')
    with open(out_report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Saved reproducible probe verdict report to {out_report_path}")
    return report

if __name__ == '__main__':
    evaluate_probe()
