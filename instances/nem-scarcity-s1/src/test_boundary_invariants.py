#!/usr/bin/env python3
"""
Deterministic Boundary Regression Fixture & Window-Level Defect Classification
for NEM July 2026 Artifact (nem_NSW1.feather).

Locks and verifies the regression fixtures for the empirical evidence chain:
1. Total row count across 14-month rolling baseline (122,688 rows).
2. Zero internal timestamp gaps (non-5min delta == 0).
3. Production slice replication: locks historical 8,809 admitted count from closed .loc slice.
4. Declared evaluation grid: 8,928 nominal intervals (2026-07-01 00:05:00Z -> 2026-08-01 00:00:00Z).
5. Strict set partition:
   - Admitted on-grid intervals: 8,808 (98.66% strict coverage)
   - Missing on-grid intervals: 120 (Right-boundary truncation)
   - Left-boundary off-grid over-inclusion: 1 (2026-07-01 00:00:00Z captured by production p_start '2026-07-01T00:00:00Z')
   - Historical reconciliation: 8,808 (on-grid) + 1 (off-grid) == 8,809 (production slice count)
   - Denominator closes: admitted (8,808) + missing (120) == grid (8,928).
6. Non-tautological window-level defect classification (IEC 61850-7-3 / SDMX / EARL).
"""

import os
import sys
import pandas as pd
import numpy as np

def run_boundary_invariant_test():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.abspath(os.path.join(script_dir, '..'))
    feather_path = os.path.join(instance_dir, 'inputs', 'nem_NSW1.feather')

    if not os.path.exists(feather_path):
        raise FileNotFoundError(f"Missing test fixture: {feather_path}")

    df = pd.read_feather(feather_path)
    t_col = 'SETTLEMENTDATE' if 'SETTLEMENTDATE' in df.columns else 'index'
    
    # 1. Total Rows Invariant
    assert len(df) == 122688, f"Expected 122688 rows, got {len(df)}"
    
    # 2. Internal Continuity Invariant (Zero internal non-5min gaps)
    ts_utc = pd.to_datetime(df[t_col], utc=True).sort_values()
    diffs = ts_utc.diff().dropna()
    non_5min_gaps = diffs[diffs != pd.Timedelta(minutes=5)]
    assert len(non_5min_gaps) == 0, f"Expected 0 internal gaps, got {len(non_5min_gaps)}"

    # 3. Replicate Actual Production Slicing from run_window.py
    # Production slice uses p_start '2026-07-01T00:00:00Z' and p_end '2026-07-31T23:59:59Z'
    p_start_prod = '2026-07-01T00:00:00Z'
    p_end_prod   = '2026-07-31T23:59:59Z'
    df_indexed = df.set_index(pd.to_datetime(df[t_col], utc=True)).sort_index()
    prod_slice = df_indexed.loc[p_start_prod:p_end_prod]
    prod_admitted_count = len(prod_slice)
    
    # Lock historical published 8,809 count as a regression invariant
    assert prod_admitted_count == 8809, (
        f"Regression failure: Expected historical production slice to yield exactly 8,809 rows, got {prod_admitted_count}"
    )

    # 4. Declared Evaluation Grid (Single Source of Truth for Denominator)
    GRID_START = pd.Timestamp("2026-07-01 00:05:00Z")
    GRID_END   = pd.Timestamp("2026-08-01 00:00:00Z")
    grid = pd.date_range(GRID_START, GRID_END, freq="5min")
    assert len(grid) == 8928, f"Expected 8928 grid intervals, got {len(grid)}"

    # Partition actual production slice against declared grid
    prod_observed = prod_slice.index
    admitted = grid.intersection(prod_observed)
    missing  = grid.difference(prod_observed)
    off_grid = prod_observed.difference(grid)

    # 5. Strict Set Partition Invariants
    assert len(admitted) == 8808, f"Expected 8808 on-grid admitted intervals, got {len(admitted)}"
    assert len(missing) == 120, f"Expected 120 missing intervals, got {len(missing)}"
    assert len(off_grid) == 1, f"Expected 1 off-grid left-boundary interval, got {len(off_grid)}"
    assert off_grid[0] == pd.Timestamp("2026-07-01 00:00:00Z"), f"Unexpected off-grid timestamp: {off_grid[0]}"
    
    # Historical reconciliation invariant: 8808 (on-grid) + 1 (off-grid) == 8809 (production slice)
    assert len(admitted) + len(off_grid) == prod_admitted_count, (
        f"Reconciliation failure: {len(admitted)} + {len(off_grid)} != {prod_admitted_count}"
    )

    # Denominator closes strictly against declared grid: 8808 + 120 == 8928
    assert len(admitted) + len(missing) == len(grid), "Denominator partition does not close!"

    # 6. Exact Coverage Calculation
    coverage_ratio = len(admitted) / len(grid)
    coverage_pct = round(coverage_ratio * 100.0, 2)
    assert coverage_pct == 98.66, f"Expected 98.66% coverage, got {coverage_pct}%"

    # 7. Non-Tautological, Falsifiable Defect Classifications
    # Right Boundary Truncation Check: derived from actual grid missing set
    is_missing_contiguous = bool((pd.Series(missing).diff().dropna() == pd.Timedelta("5min")).all())
    acq_right_class = (
        "RIGHT_BOUNDARY_TRUNCATION"
        if len(missing) > 0 and missing[-1] == GRID_END and is_missing_contiguous
        else "UNCLASSIFIED_RIGHT_DEFECT"
    )
    assert acq_right_class == "RIGHT_BOUNDARY_TRUNCATION", f"Failed right defect classification: {acq_right_class}"

    # Left Boundary Over-Inclusion Check: derived from actual production slice difference
    acq_left_class = (
        "LEFT_BOUNDARY_OVER_INCLUSION"
        if len(off_grid) == 1 and off_grid[0] == pd.Timestamp("2026-07-01 00:00:00Z")
        else ("CLEAN_LEFT_BOUNDARY" if len(off_grid) == 0 else "UNCLASSIFIED_LEFT_DEFECT")
    )
    assert acq_left_class == "LEFT_BOUNDARY_OVER_INCLUSION", f"Failed left defect classification: {acq_left_class}"

    # 8. Window-Level Diagnostic Record (Single Structured Acquisition Record)
    window_acquisition_record = {
        "evaluation_grid_intervals": len(grid),
        "production_slice_count": prod_admitted_count,
        "admitted_on_grid": len(admitted),
        "missing_on_grid": len(missing),
        "off_grid_captured": len(off_grid),
        "coverage_pct": coverage_pct,
        "defects": [
            {
                "defect_class": acq_right_class,
                "intervals_affected": len(missing),
                "start_utc": str(missing[0]),
                "end_utc": str(missing[-1]),
                "axis_3_instrument": "QUERY_WINDOW_MISALIGNMENT (AEST month acquisition vs UTC evaluation grid)",
                "axis_2_observation": "SDMX: M (Missing value)",
                "axis_1_subject_outcome": "earl:untested (evaluation not performed due to instrument truncation)"
            },
            {
                "defect_class": acq_left_class,
                "intervals_affected": len(off_grid),
                "timestamp_utc": str(off_grid[0]),
                "axis_3_instrument": "CLOSED_SLICE_OVER_INCLUSION (production p_start 00:00:00Z captures preceding interval)",
                "axis_2_observation": "SDMX: A (Normal observed value outside evaluation grid)",
                "axis_1_subject_outcome": "earl:inapplicable (outside declared evaluation grid)"
            }
        ]
    }

    print("================================================================================")
    print("DETERMINISTIC BOUNDARY REGRESSION FIXTURE PASSED")
    print("================================================================================")
    print(f"Total Rows in Fixture        : {len(df):,}")
    print(f"Internal Gaps Count          : {len(non_5min_gaps)} (100% continuous)")
    print(f"Production Slice Output      : {prod_admitted_count:,} rows (locked historical count)")
    print(f"Declared Evaluation Grid     : {len(grid):,} intervals ({GRID_START} -> {GRID_END})")
    print(f"Admitted On-Grid             : {len(admitted):,} intervals")
    print(f"Missing On-Grid              : {len(missing)} intervals")
    print(f"Off-Grid Left Over-Inclusion : {len(off_grid)} interval ({off_grid[0]})")
    print(f"Historical Reconciliation    : {len(admitted)} (on-grid) + {len(off_grid)} (off-grid) == {prod_admitted_count} (True)")
    print(f"Denominator Closes           : {len(admitted)} + {len(missing)} == {len(grid)} (True)")
    print(f"Strict Coverage Percentage   : {coverage_pct}% (8,808 / 8,928)")
    print("--------------------------------------------------------------------------------")
    print(f"Derived Defect #1 Class      : {acq_right_class} ({len(missing)} intervals)")
    print(f"  Missing Span               : {missing[0]} -> {missing[-1]}")
    print(f"  Axis 3 Instrument          : {window_acquisition_record['defects'][0]['axis_3_instrument']}")
    print(f"  Axis 2 Observation         : {window_acquisition_record['defects'][0]['axis_2_observation']}")
    print(f"  Axis 1 Subject Outcome     : {window_acquisition_record['defects'][0]['axis_1_subject_outcome']}")
    print("--------------------------------------------------------------------------------")
    print(f"Derived Defect #2 Class      : {acq_left_class} ({len(off_grid)} interval)")
    print(f"  Timestamp                  : {off_grid[0]}")
    print(f"  Axis 3 Instrument          : {window_acquisition_record['defects'][1]['axis_3_instrument']}")
    print(f"  Axis 2 Observation         : {window_acquisition_record['defects'][1]['axis_2_observation']}")
    print(f"  Axis 1 Subject Outcome     : {window_acquisition_record['defects'][1]['axis_1_subject_outcome']}")
    print("================================================================================")

if __name__ == '__main__':
    run_boundary_invariant_test()
