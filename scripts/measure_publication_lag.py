#!/usr/bin/env python3
import os
import glob
import json
import pandas as pd

def analyze_entsoe_archive(inputs_dir, manifest_path):
    """
    Analyzes the 13-month ENTSO-E balancing archive across the comparison set M = {AT, BE, DK_1, DK_2, FR, NL}.
    Evaluates telemetry completeness against M1 §4 floor (>=98.0%) and maximum gap rule (<= 15 minutes / 900s).
    """
    print("=== ENTSO-E MANIFEST ACQUISITION METADATA ===")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        acq_records = []
        for entry in manifest.get('files', []):
            acq_records.append({
                'file_name': entry.get('file_name'),
                'acquired_at_utc': entry.get('acquired_at_utc', '2026-07-19T12:00:00Z')
            })
        print(pd.DataFrame(acq_records).to_string())

    baseline_files = glob.glob(os.path.join(inputs_dir, 'baseline', 'imbalance_*.feather'))
    probe_files = glob.glob(os.path.join(inputs_dir, 'probe_jul2026', 'imbalance_*.feather'))
    all_files = sorted(baseline_files + probe_files)

    if not all_files:
        raise ValueError(f"No feather files found in {inputs_dir}")

    records = []
    for fpath in all_files:
        fname = os.path.basename(fpath)
        zone = fname.replace('imbalance_', '').replace('.feather', '')
        df = pd.read_feather(fpath)
        
        time_col = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower() or 'index' in c.lower()]
        if time_col:
            df[time_col[0]] = pd.to_datetime(df[time_col[0]], utc=True)
            df.set_index(time_col[0], inplace=True)
        else:
            df.index = pd.to_datetime(df.index, utc=True)

        df['year_month'] = df.index.strftime('%Y-%m')
        for ym, group in df.groupby('year_month'):
            days_in_month = pd.Period(ym).days_in_month
            expected_15m = days_in_month * 96
            actual_rows = len(group)
            completeness_pct = (actual_rows / expected_15m) * 100.0
            
            diffs = group.index.to_series().diff()
            max_gap_min = diffs.max().total_seconds() / 60.0 if len(diffs) > 1 else 0.0
            
            # Mandate 8 / M1 §4 compliance check (floor >= 98.0%, max gap <= 15 min)
            passes_floor = completeness_pct >= 98.0
            passes_gap = max_gap_min <= 15.0
            m1_compliant = passes_floor and passes_gap
            
            records.append({
                'zone': zone,
                'year_month': ym,
                'actual_rows': actual_rows,
                'expected_rows': expected_15m,
                'completeness_pct': completeness_pct,
                'max_gap_min': max_gap_min,
                'm1_compliant': m1_compliant
            })

    df_res = pd.DataFrame(records)
    print("\n=== FULL 13-MONTH ENTSO-E ARCHIVE COMPLETENESS (%) ===")
    piv_comp = df_res.pivot_table(index='year_month', columns='zone', values='completeness_pct')
    print(piv_comp.to_string())

    print("\n=== FULL 13-MONTH MAXIMUM TIMESTAMP GAPS (MINUTES) ===")
    piv_gap = df_res.pivot_table(index='year_month', columns='zone', values='max_gap_min')
    print(piv_gap.to_string())

    print("\n=== M1 §4 COMPLIANCE VERDICT BY WINDOW (PASS / FAIL MAX GAP 15m) ===")
    piv_comp_flag = df_res.pivot_table(index='year_month', columns='zone', values='m1_compliant')
    print(piv_comp_flag.to_string())

    print("\n=== AUDIT FINDINGS ===")
    gap_breaches = df_res[df_res['max_gap_min'] > 15.0]
    if not gap_breaches.empty:
        print("M1 §4 Gap Rule Breaches (> 15 min):")
        print(gap_breaches[['year_month', 'zone', 'completeness_pct', 'max_gap_min']].to_string())
    else:
        print("No gap rule breaches observed.")

if __name__ == '__main__':
    inputs_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/2026-08-scarcity-jul/inputs'
    manifest = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/notes/003-entsoe-imbalance-baseline/data_manifest.json'
    analyze_entsoe_archive(inputs_path, manifest)
