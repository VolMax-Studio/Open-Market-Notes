#!/usr/bin/env python3
"""
VolMax Isolated Instance 2026-08-scarcity-jul Evaluator
Strict Manifest-Bound Evaluation of July 2026 Imbalance Scarcity Elevation
Conforming to INSTRUMENT_SPEC (v0.3.0), M1 (v0.6.0), C (v1.2.0), and INSTANCE_ISOLATION (v0.1.0)
"""

import os
import json
import pandas as pd
import numpy as np

def bind_entsoe_timestamp_col(df, filename):
    if 'index' in df.columns:
        return 'index'
    elif 'startTime' in df.columns:
        return 'startTime'
    raise ValueError(f"DATAFRAME ABORT: Missing bound timestamp column ('index' or 'startTime') in {filename}. Columns: {list(df.columns)}")

def load_params_from_file(params_path):
    if not os.path.exists(params_path):
        raise ValueError(f"PARAMS ABORT: PARAMS.md missing at {params_path}")
    with open(params_path, 'r') as f:
        text = f.read()
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"PARAMS ABORT: Unable to parse JSON configuration block from {params_path}")
    return json.loads(text[start_idx:end_idx+1])

def evaluate_instance(instance_dir='.'):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    params_config = load_params_from_file(params_path)

    # Dynamic coupling per C §4.3 & PARAMS
    q_ref = float(params_config["q_ref"])
    e_m1_ref = 1.0 - q_ref  # 0.100 for q=0.90
    k_multiplier = float(params_config["k_multiplier"])
    s_thresh_pct = k_multiplier * e_m1_ref * 100.0  # Dynamic coupling: 15.0%

    n_low = int(params_config["n_low"])
    n_high = int(params_config["n_high"])
    completeness_floor_pct = float(params_config["completeness_floor_pct"])
    max_gap_seconds_limit = float(params_config["max_allowed_gap_seconds"])
    series_bindings = params_config["series_bindings"]

    eu_results = {}
    elevated_count = 0
    actual_intervals_dict = {}
    zone_completeness_dict = {}
    zone_no_gaps_dict = {}

    expected_intervals_per_zone = params_config["probe_window"]["nominal_intervals_15m"]
    nominal_baseline_intervals = params_config["baseline_window"]["nominal_intervals_15m"]

    print("=== EXECUTING ISOLATED INSTANCE 2026-08-scarcity-jul EVALUATOR (M1 v0.6.0 & C v1.2.0) ===")

    zones = params_config["comparison_zones"]
    for zone in zones:
        if zone not in series_bindings:
            raise ValueError(f"PARAMS ABORT: Missing series_bindings entry for comparison zone {zone}")

        base_col = series_bindings[zone]["baseline_col"]
        probe_col = series_bindings[zone]["probe_col"]

        base_feather = os.path.join(instance_dir, 'inputs', 'baseline', f"imbalance_{zone}.feather")
        if not os.path.exists(base_feather):
            raise ValueError(f"INPUT ABORT: Baseline feather file missing for {zone} at {base_feather}")

        base_df = pd.read_feather(base_feather)
        time_col = bind_entsoe_timestamp_col(base_df, f"imbalance_{zone}.feather (baseline)")

        # Enforce UTC timestamp index and sort ascending (M1 §5)
        base_df[time_col] = pd.to_datetime(base_df[time_col], utc=True)
        base_df = base_df.set_index(time_col).sort_index()

        if base_col not in base_df.columns:
            raise ValueError(f"PARAMS BINDING ABORT: Bound baseline shortage column '{base_col}' missing in {zone} baseline columns: {list(base_df.columns)}")

        # Uncontaminated baseline window (2025-08-01 to 2026-06-30 UTC)
        uncontam_df = base_df.loc['2025-08-01 00:00:00+00:00':'2026-06-30 23:59:59+00:00']
        admitted_base_obs = len(uncontam_df[base_col].dropna())
        base_completeness_pct = round((admitted_base_obs / nominal_baseline_intervals) * 100.0, 4)

        if base_completeness_pct < completeness_floor_pct:
            raise ValueError(f"BASELINE ABORT: Baseline completeness for {zone} ({base_completeness_pct:.2f}%) below floor ({completeness_floor_pct:.2f}%)")

        q90 = float(np.percentile(uncontam_df[base_col].dropna(), q_ref * 100.0, method='linear'))

        # Load Probe July 2026 feather
        probe_feather = os.path.join(instance_dir, 'inputs', 'probe_jul2026', f"imbalance_{zone}.feather")
        if not os.path.exists(probe_feather):
            raise ValueError(f"PROBE ABORT: Probe feather file missing for {zone} at {probe_feather}.")

        probe_df = pd.read_feather(probe_feather)
        p_time_col = bind_entsoe_timestamp_col(probe_df, f"imbalance_{zone}.feather (probe)")
        probe_df[p_time_col] = pd.to_datetime(probe_df[p_time_col], utc=True)
        probe_df = probe_df.set_index(p_time_col).sort_index()

        if probe_col not in probe_df.columns:
            raise ValueError(f"PARAMS BINDING ABORT: Bound probe shortage column '{probe_col}' missing in {zone} probe columns: {list(probe_df.columns)}")

        # Strict NaN Exclusion from numerator, denominator, and completeness (M1 §4.2)
        clean_probe_series = probe_df[probe_col].dropna()
        clean_probe_df = probe_df.loc[clean_probe_series.index]

        actual_intervals = len(clean_probe_df)
        actual_intervals_dict[zone] = actual_intervals
        zone_completeness = round((actual_intervals / expected_intervals_per_zone) * 100.0, 4)
        zone_completeness_dict[zone] = zone_completeness

        time_diffs = pd.Series(clean_probe_df.index).diff()
        if len(time_diffs) <= 1:
            raise ValueError(f"PROBE ABORT: Insufficient telemetry timestamp records for {zone}.")

        max_gap_seconds = float(time_diffs.max().total_seconds())
        no_gaps_gt_15m = bool(max_gap_seconds <= max_gap_seconds_limit)
        zone_no_gaps_dict[zone] = no_gaps_gt_15m

        if zone_completeness < completeness_floor_pct:
            raise ValueError(f"MANDATE 8 ABORT: {zone} probe telemetry incomplete: {actual_intervals}/{expected_intervals_per_zone} ({zone_completeness:.2f}%).")

        if not no_gaps_gt_15m:
            raise ValueError(f"MANDATE 8 ABORT: {zone} probe telemetry contains gap exceeding limits (Max gap = {max_gap_seconds/60.0:.1f} min).")

        # M1 §5 Time-Weighted Duration Ratio in seconds with boundary interval median duration
        time_diffs_sec = pd.Series(clean_probe_df.index).diff().dt.total_seconds().values
        if len(time_diffs_sec) > 1:
            time_diffs_sec[0] = float(np.median(time_diffs_sec[1:]))
        else:
            time_diffs_sec[0] = 900.0

        qualifying_mask = (clean_probe_df[probe_col] >= q90).values
        qualifying_seconds = float(np.sum(time_diffs_sec[qualifying_mask]))
        total_admitted_seconds = float(np.sum(time_diffs_sec))

        share_q90 = float((qualifying_seconds / total_admitted_seconds) * 100.0)
        is_elevated = share_q90 >= s_thresh_pct

        if is_elevated:
            elevated_count += 1

        eu_results[zone] = {
            "baseline_q90_eur": round(q90, 4),
            "baseline_admitted_obs": admitted_base_obs,
            "baseline_nominal_obs": nominal_baseline_intervals,
            "baseline_completeness_pct": base_completeness_pct,
            "jul_2026_share_q90_pct": round(share_q90, 4),
            "is_elevated": is_elevated,
            "probe_intervals": actual_intervals,
            "completeness_pct": zone_completeness,
            "no_gaps_exceeding_15min": no_gaps_gt_15m,
            "manifest_bound_baseline_col": base_col,
            "manifest_bound_probe_col": probe_col
        }

        print(f"Zone {zone:4s}: Q90 = €{q90:7.4f}/MWh | Base Comp = {base_completeness_pct:6.2f}% ({admitted_base_obs}/{nominal_baseline_intervals}) | S(z) = {share_q90:6.4f}% | Elevated: {is_elevated}")

    # GB Matched Pair Companion Metric
    companion_zones = params_config.get("companion_zones", [])
    if "GB" in companion_zones:
        gb_feather = os.path.join(instance_dir, 'inputs', 'gb_system_prices.feather')
        if not os.path.exists(gb_feather):
            raise ValueError(f"GB COMPARATOR ABORT: GB dataset missing at {gb_feather}")

        gb_base_col = series_bindings["GB"]["baseline_col"]
        gb_probe_col = series_bindings["GB"]["probe_col"]
        gb_max_gap = series_bindings["GB"].get("max_allowed_gap_seconds", 1800.0)

        gb_df = pd.read_feather(gb_feather)
        gb_time_col = bind_entsoe_timestamp_col(gb_df, "gb_system_prices.feather")

        gb_df[gb_time_col] = pd.to_datetime(gb_df[gb_time_col], utc=True)
        gb_df = gb_df.set_index(gb_time_col).sort_index()

        if gb_base_col not in gb_df.columns:
            raise ValueError(f"PARAMS BINDING ABORT: Bound GB baseline column '{gb_base_col}' missing in dataset columns: {list(gb_df.columns)}")
        if gb_probe_col not in gb_df.columns:
            raise ValueError(f"PARAMS BINDING ABORT: Bound GB probe column '{gb_probe_col}' missing in dataset columns: {list(gb_df.columns)}")

        gb_base = gb_df.loc['2025-08-01 00:00:00+00:00':'2026-06-30 23:59:59+00:00']
        gb_q90 = float(np.percentile(gb_base[gb_base_col].dropna(), q_ref * 100.0, method='linear'))

        gb_jul26 = gb_df.loc['2026-07-01 00:00:00+00:00':'2026-07-31 23:59:59+00:00']
        gb_clean_jul26 = gb_jul26[gb_jul26[gb_probe_col].notna()]

        gb_diffs_jul26 = pd.Series(gb_clean_jul26.index).diff().dt.total_seconds().values
        if len(gb_diffs_jul26) > 1:
            gb_diffs_jul26[0] = float(np.median(gb_diffs_jul26[1:]))
        else:
            gb_diffs_jul26[0] = gb_max_gap

        gb_qual_jul26 = (gb_clean_jul26[gb_probe_col] >= gb_q90).values
        gb_share_jul26 = float((np.sum(gb_diffs_jul26[gb_qual_jul26]) / np.sum(gb_diffs_jul26)) * 100.0)
        gb_is_elevated = gb_share_jul26 >= s_thresh_pct

        print(f"\nGB Companion Metric: Q90 = £{gb_q90:.4f}/MWh | Jul26 S(GB) = {gb_share_jul26:.4f}% | Elevated (Descriptive): {gb_is_elevated}")
    else:
        gb_q90, gb_share_jul26, gb_is_elevated = None, None, None

    # Emission Rules of Classifier C v1.2.0
    if elevated_count <= n_low:
        verdict = "NULL"
    elif elevated_count < n_high:
        verdict = "ISOLATED"
    else:
        verdict = "REGIONAL"

    print(f"\n=== CLASSIFIER C v1.2.0 EMITTED VERDICT: {verdict} (N_elevated = {elevated_count} of 6 EU zones) ===")

    overall_completeness_pct = round(sum(actual_intervals_dict.values()) / (len(zones) * expected_intervals_per_zone) * 100.0, 4)
    overall_no_gaps = all(zone_no_gaps_dict.values())

    report = {
        "metadata": {
            "instance_id": "2026-08-scarcity-jul",
            "overall_completeness_pct": overall_completeness_pct,
            "mandate_8_status": "PASSED" if (overall_completeness_pct >= completeness_floor_pct and overall_no_gaps) else "FAILED"
        },
        "provenance": {
            "evaluator_script": "src/evaluate_probe.py",
            "params_file": "PARAMS.md",
            "data_license_attribution": "Primary ENTSO-E Transparency Platform Telemetry (Imbalance Prices [17.1.g / 17.2.f]), formally listed under CC BY 4.0 free re-use (Item #27). All raw files anchored with SHA-256 hashes in inputs/MANIFEST.json.",
            "pre_registered_ratifier": "Nestorov, Ivan / VolMax Studio Lab"
        },
        "benchmark_metrics": {
            "gb_companion": {
                "market": "GB",
                "baseline_q90_gbp": round(gb_q90, 4) if gb_q90 is not None else None,
                "jul_2026_share_q90_pct": round(gb_share_jul26, 4) if gb_share_jul26 is not None else None,
                "is_elevated_descriptive": gb_is_elevated
            },
            "eu_zones": eu_results
        },
        "decision_evaluation": {
            "q_ref": q_ref,
            "e_m1_ref": e_m1_ref,
            "k_multiplier": k_multiplier,
            "dynamically_coupled_s_thresh_pct": s_thresh_pct,
            "frozen_n_high_threshold": n_high,
            "frozen_n_low_threshold": n_low,
            "total_eu_zones_elevated": elevated_count,
            "elevated_eu_zones_list": [z for z, r in eu_results.items() if r["is_elevated"]],
            "non_elevated_eu_zones_list": [z for z, r in eu_results.items() if not r["is_elevated"]],
            "classifier_c_emitted_verdict": verdict
        }
    }

    results_dir = os.path.join(instance_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    out_report_path = os.path.join(results_dir, 'probe_verdict_report.json')
    with open(out_report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Saved reproducible probe verdict report to {out_report_path}")
    return report

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inst_dir = os.path.abspath(os.path.join(script_dir, '..'))
    evaluate_instance(instance_dir=inst_dir)
