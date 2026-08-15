#!/usr/bin/env python3
import os
import sys
import json
import argparse
import pandas as pd
import numpy as np

OVERLAP_START_UTC = "2025-05-31 22:00:00+00:00"
OVERLAP_END_UTC = "2026-07-31 21:45:00+00:00"
FLOAT_TOLERANCE = 1e-4

VOTING_ZONES = ["AT", "BE", "DK_1", "DK_2", "FR", "NL"]
COMPANION_ZONES = ["GB"]

def evaluate_column_pair(df_base, df_fresh, zone, col_name, is_duplicate=False):
    if is_duplicate:
        return {
            "status": "DUPLICATE_SERIES (Long == Short)",
            "N_revised_archive": 0,
            "pct_revised_archive": 0.0,
            "N_revised_july": 0,
            "pct_revised_july": 0.0,
            "max_abs_drift": 0.0,
            "monthly_distribution": {}
        }

    # Slice overlapping window
    base_slice = df_base.loc[OVERLAP_START_UTC:OVERLAP_END_UTC, col_name]
    fresh_slice = df_fresh.loc[OVERLAP_START_UTC:OVERLAP_END_UTC, col_name]

    # Align indexes
    all_indices = base_slice.index.union(fresh_slice.index)
    base_aligned = base_slice.reindex(all_indices)
    fresh_aligned = fresh_slice.reindex(all_indices)

    # Monthly breakdown tracking
    monthly_rev = {}
    
    n_revised_archive = 0
    n_revised_july = 0
    max_drift = 0.0
    has_coverage_change = False
    has_price_revision = False

    july_start = pd.Timestamp("2026-07-01 00:00:00", tz="UTC")
    july_end = pd.Timestamp("2026-07-31 21:45:00", tz="UTC")

    for idx, p1 in base_aligned.items():
        p2 = fresh_aligned.get(idx, np.nan)
        p1_nan = pd.isna(p1)
        p2_nan = pd.isna(p2)

        is_revised = False
        is_coverage = False
        drift = 0.0

        if p1_nan and p2_nan:
            pass  # STABLE
        elif p1_nan != p2_nan:
            is_coverage = True
            has_coverage_change = True
        else:
            diff = abs(float(p2) - float(p1))
            if diff > FLOAT_TOLERANCE:
                is_revised = True
                has_price_revision = True
                drift = diff
                if diff > max_drift:
                    max_drift = diff

        if is_revised or is_coverage:
            m_str = idx.strftime("%Y-%m")
            monthly_rev[m_str] = monthly_rev.get(m_str, 0) + 1
            n_revised_archive += 1
            if july_start <= idx <= july_end:
                n_revised_july += 1

    total_archive = len(all_indices)
    july_indices = [idx for idx in all_indices if july_start <= idx <= july_end]
    total_july = len(july_indices)

    pct_archive = (n_revised_archive / total_archive * 100.0) if total_archive > 0 else 0.0
    pct_july = (n_revised_july / total_july * 100.0) if total_july > 0 else 0.0

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
        "N_revised_archive": n_revised_archive,
        "total_archive_intervals": total_archive,
        "pct_revised_archive": round(pct_archive, 4),
        "N_revised_july": n_revised_july,
        "total_july_intervals": total_july,
        "pct_revised_july": round(pct_july, 4),
        "max_abs_drift_eur_mwh": round(max_drift, 4),
        "monthly_distribution": monthly_rev
    }

def run_l10_evaluation(baseline_dir, fresh_dir, report_out_path=None):
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

        is_single_pricing = (df_b['Long'] == df_b['Short']).all()

        res_short = evaluate_column_pair(df_b, df_f, z, 'Short')
        res_long = evaluate_column_pair(df_b, df_f, z, 'Long', is_duplicate=is_single_pricing)

        if "PRICE_REVISION" in res_short['status']:
            overall_l10_sufficient = False

        results[z] = {
            "is_single_pricing": bool(is_single_pricing),
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

        if "PRICE_REVISION" in res_gb_sell['status']:
            overall_l10_sufficient = False

        results["GB"] = {
            "columns": {
                "systemSellPrice": res_gb_sell,
                "systemBuyPrice": res_gb_buy
            }
        }

    summary = {
        "protocol_version": "v1.0.0",
        "preregistration_commit": "3057a72",
        "overall_l10_sufficient": overall_l10_sufficient,
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
