#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import pandas as pd
import numpy as np

OVERLAP_START_UTC = "2025-05-31 22:00:00+00:00"
OVERLAP_END_UTC = "2026-07-31 21:45:00+00:00"
FLOAT_TOLERANCE = 1e-4

VOTING_ZONES = ["AT", "BE", "DK_1", "DK_2", "FR", "NL"]
COMPANION_ZONES = ["GB"]

def get_git_commit(cwd):
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"

def evaluate_column_pair(df_base, df_fresh, zone, col_name, is_duplicate=False):
    if is_duplicate:
        return {
            "status": "DUPLICATE_SERIES (Long == Short)",
            "N_price_revisions_archive": 0,
            "pct_price_revisions_archive": 0.0,
            "N_coverage_changes_archive": 0,
            "pct_coverage_changes_archive": 0.0,
            "N_price_revisions_july": 0,
            "pct_price_revisions_july": 0.0,
            "N_coverage_changes_july": 0,
            "pct_coverage_changes_july": 0.0,
            "max_abs_drift_eur_mwh": 0.0,
            "monthly_price_revisions": {},
            "monthly_coverage_changes": {}
        }

    # Slice overlapping window
    base_slice = df_base.loc[OVERLAP_START_UTC:OVERLAP_END_UTC, col_name]
    fresh_slice = df_fresh.loc[OVERLAP_START_UTC:OVERLAP_END_UTC, col_name]

    # Align indexes
    all_indices = base_slice.index.union(fresh_slice.index)
    base_aligned = base_slice.reindex(all_indices)
    fresh_aligned = fresh_slice.reindex(all_indices)

    # Separate monthly tracking
    monthly_price_rev = {}
    monthly_cov_change = {}
    
    n_price_rev_archive = 0
    n_cov_change_archive = 0
    n_price_rev_july = 0
    n_cov_change_july = 0
    max_drift = 0.0

    july_start = pd.Timestamp("2026-07-01 00:00:00", tz="UTC")
    july_end = pd.Timestamp("2026-07-31 21:45:00", tz="UTC")

    for idx, p1 in base_aligned.items():
        p2 = fresh_aligned.get(idx, np.nan)
        p1_nan = pd.isna(p1)
        p2_nan = pd.isna(p2)

        m_str = idx.strftime("%Y-%m")
        is_july = (july_start <= idx <= july_end)

        if p1_nan and p2_nan:
            pass  # STABLE
        elif p1_nan != p2_nan:
            # Explicit coverage change (one side is missing)
            monthly_cov_change[m_str] = monthly_cov_change.get(m_str, 0) + 1
            n_cov_change_archive += 1
            if is_july:
                n_cov_change_july += 1
        else:
            diff = abs(float(p2) - float(p1))
            if diff > FLOAT_TOLERANCE:
                # Explicit price revision
                monthly_price_rev[m_str] = monthly_price_rev.get(m_str, 0) + 1
                n_price_rev_archive += 1
                if is_july:
                    n_price_rev_july += 1
                if diff > max_drift:
                    max_drift = diff

    total_archive = len(all_indices)
    july_indices = [idx for idx in all_indices if july_start <= idx <= july_end]
    total_july = len(july_indices)

    pct_rev_archive = (n_price_rev_archive / total_archive * 100.0) if total_archive > 0 else 0.0
    pct_cov_archive = (n_cov_change_archive / total_archive * 100.0) if total_archive > 0 else 0.0

    pct_rev_july = (n_price_rev_july / total_july * 100.0) if total_july > 0 else 0.0
    pct_cov_july = (n_cov_change_july / total_july * 100.0) if total_july > 0 else 0.0

    has_price_revision = (n_price_rev_archive > 0)
    has_coverage_change = (n_cov_change_archive > 0)

    if has_price_revision and has_coverage_change:
        status = "PRICE_REVISION + COVERAGE_CHANGE"
    elif has_price_revision:
        status = "PRICE_REVISION"
    elif has_coverage_change:
        status = "COVERAGE_CHANGE"
    else:
        status = "STABLE"

    return {
        "status": status,
        "N_price_revisions_archive": n_price_rev_archive,
        "pct_price_revisions_archive": round(pct_rev_archive, 4),
        "N_coverage_changes_archive": n_cov_change_archive,
        "pct_coverage_changes_archive": round(pct_cov_archive, 4),
        "total_archive_intervals": total_archive,
        "N_price_revisions_july": n_price_rev_july,
        "pct_price_revisions_july": round(pct_rev_july, 4),
        "N_coverage_changes_july": n_cov_change_july,
        "pct_coverage_changes_july": round(pct_cov_july, 4),
        "total_july_intervals": total_july,
        "max_abs_drift_eur_mwh": round(max_drift, 4),
        "monthly_price_revisions": monthly_price_rev,
        "monthly_coverage_changes": monthly_cov_change
    }

def run_l10_evaluation(baseline_dir, fresh_dir, report_out_path=None):
    # Strict validation check 1: Enforce pre-registered fresh directory path
    norm_fresh = os.path.normpath(fresh_dir)
    if "test_fresh_fetch" not in norm_fresh:
        print(f"FATAL ERROR: fresh_dir '{fresh_dir}' violates pre-registered path requirement (must contain 'test_fresh_fetch'). Aborting.", file=sys.stderr)
        sys.exit(1)

    # Strict validation check 2: Temporal monotonicity (fresh snapshot mtime > baseline mtime)
    base_sample = os.path.join(baseline_dir, "imbalance_AT.feather")
    fresh_sample = os.path.join(fresh_dir, "imbalance_AT.feather")
    if os.path.exists(base_sample) and os.path.exists(fresh_sample):
        base_mtime = os.path.getmtime(base_sample)
        fresh_mtime = os.path.getmtime(fresh_sample)
        if fresh_mtime <= base_mtime:
            print(f"FATAL ERROR: Fresh fetch timestamp ({fresh_mtime}) is older or equal to baseline snapshot timestamp ({base_mtime}). Temporal monotonicity violated. Aborting.", file=sys.stderr)
            sys.exit(1)

    results = {}
    overall_l10_sufficient = True

    for z in VOTING_ZONES:
        base_f = os.path.join(baseline_dir, f"imbalance_{z}.feather")
        fresh_f = os.path.join(fresh_dir, f"imbalance_{z}.feather")

        if not os.path.exists(fresh_f):
            raise FileNotFoundError(f"Fresh fetch file missing for zone {z}: {fresh_f}")

        df_b = pd.read_feather(base_f).set_index('index').sort_index()
        df_f = pd.read_feather(fresh_f).set_index('index').sort_index()

        df_b.index = pd.to_datetime(df_b.index, utc=True)
        df_f.index = pd.to_datetime(df_f.index, utc=True)

        # Enforce duplicate check across BOTH baseline AND fresh snapshots
        is_single_pricing = (df_b['Long'] == df_b['Short']).all() and (df_f['Long'] == df_f['Short']).all()

        res_short = evaluate_column_pair(df_b, df_f, z, 'Short')
        res_long = evaluate_column_pair(df_b, df_f, z, 'Long', is_duplicate=is_single_pricing)

        # Apply primary condition to ALL non-duplicate columns
        if "PRICE_REVISION" in res_short['status'] or ("PRICE_REVISION" in res_long['status'] and not is_single_pricing):
            overall_l10_sufficient = False

        results[z] = {
            "is_single_pricing_both_snapshots": bool(is_single_pricing),
            "columns": {
                "Short": res_short,
                "Long": res_long
            }
        }

    # Companion zone GB
    gb_base_f = os.path.join(baseline_dir, "gb_system_prices.feather")
    gb_fresh_f = os.path.join(fresh_dir, "gb_system_prices.feather")

    if os.path.exists(gb_fresh_f):
        df_gb_b = pd.read_feather(gb_base_f).set_index('startTime').sort_index()
        df_gb_f = pd.read_feather(gb_fresh_f).set_index('startTime').sort_index()

        df_gb_b.index = pd.to_datetime(df_gb_b.index, utc=True)
        df_gb_f.index = pd.to_datetime(df_gb_f.index, utc=True)

        res_gb_sell = evaluate_column_pair(df_gb_b, df_gb_f, "GB", 'systemSellPrice')
        res_gb_buy = evaluate_column_pair(df_gb_b, df_gb_f, "GB", 'systemBuyPrice')

        if "PRICE_REVISION" in res_gb_sell['status'] or "PRICE_REVISION" in res_gb_buy['status']:
            overall_l10_sufficient = False

        results["GB"] = {
            "columns": {
                "systemSellPrice": res_gb_sell,
                "systemBuyPrice": res_gb_buy
            }
        }

    script_cwd = os.path.dirname(os.path.abspath(__file__))
    current_commit = get_git_commit(script_cwd)

    summary = {
        "protocol_version": "v1.0.0",
        "preregistration_commit": "3057a72",
        "evaluator_commit": current_commit,
        "overall_l10_sufficient": overall_l10_sufficient,
        "scope_limitation_note": (
            "n=1 empirical snapshot comparison over the July 2026 window between 2026-08-09 and 2026-08-15. "
            "A STABLE verdict demonstrates that L=10 publication lag was not breached for this specific window; "
            "multi-window stability across future runs is required before L=10 can transition from PROVISIONAL."
        ),
        "zone_results": results
    }

    if report_out_path:
        with open(report_out_path, 'w') as f:
            json.dump(summary, f, indent=2)

    return summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate L10 Lag Verification Fresh Fetch")
    parser.add_argument('--baseline-dir', type=str, default='/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/entsoe-scarcity-s1/inputs')
    parser.add_argument('--fresh-dir', type=str, required=True, help='Fresh fetch processed directory')
    parser.add_argument('--out-report', type=str, help='JSON summary output path')
    args = parser.parse_args()

    run_l10_evaluation(args.baseline_dir, args.fresh_dir, args.out_report)

