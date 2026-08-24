#!/usr/bin/env python3
"""
Deterministic Boundary Regression Fixture & Window-Level Defect Classification
for NEM July 2026 Artifact (nem_NSW1.feather).

Proves the exact empirical evidence chain:
1. Total row count across 14-month rolling baseline (122,688 rows).
2. Zero internal timestamp gaps (non-5min delta == 0).
3. Declared evaluation grid: 8,928 nominal intervals (2026-07-01 00:05:00Z -> 2026-08-01 00:00:00Z).
4. Strict set partition:
   - Admitted on-grid intervals: 8,808 (98.66% coverage)
   - Missing on-grid intervals: 120 (Right-boundary truncation)
   - Left-boundary over-inclusion: 1 (2026-07-01 00:00:00Z off-grid interval captured by closed .loc slice)
   - Denominator closes: admitted (8,808) + missing (120) == grid (8,928).
5. Dynamically derived window-level defect classification (IEC 61850-7-3 / SDMX / EARL).
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

    # 3. Declared Evaluation Grid (Single Source of Truth for Denominator)
    GRID_START = pd.Timestamp("2026-07-01 00:05:00Z")
    GRID_END   = pd.Timestamp("2026-08-01 00:00:00Z")
    grid = pd.date_range(GRID_START, GRID_END, freq="5min")
    assert len(grid) == 8928, f"Expected 8928 grid intervals, got {len(grid)}"

    observed = pd.DatetimeIndex(ts_utc.unique())
    admitted = grid.intersection(observed)
    missing  = grid.difference(observed)
    
    # Off-grid observations within the closed slice [2026-07-01 00:00:00Z, 2026-08-01 00:00:00Z]
    slice_observed = observed[(observed >= GRID_START - pd.Timedelta("5min")) & (observed <= GRID_END)]
    off_grid = slice_observed.difference(grid)

    # 4. Strict Set Partition Invariants
    assert len(admitted) == 8808, f"Expected 8808 admitted intervals, got {len(admitted)}"
    assert len(missing) == 120, f"Expected 120 missing intervals, got {len(missing)}"
    assert len(off_grid) == 1, f"Expected 1 off-grid left-boundary interval, got {len(off_grid)}"
    assert off_grid[0] == pd.Timestamp("2026-07-01 00:00:00Z"), f"Unexpected off-grid timestamp: {off_grid[0]}"
    
    # Denominator closes strictly
    assert len(admitted) + len(missing) == len(grid), "Denominator partition does not close!"

    # 5. Exact Coverage Calculation
    coverage_ratio = len(admitted) / len(grid)
    coverage_pct = round(coverage_ratio * 100.0, 2)
    assert coverage_pct == 98.66, f"Expected 98.66% coverage, got {coverage_pct}%"

    # 6. Dynamically Derived Defect Classifications
    # Right Boundary Truncation Check
    is_missing_contiguous = bool((pd.Series(missing).diff().dropna() == pd.Timedelta("5min")).all())
    acq_right_class = (
        "RIGHT_BOUNDARY_TRUNCATION"
        if len(missing) > 0 and missing[-1] == GRID_END and is_missing_contiguous
        else "UNCLASSIFIED_RIGHT_DEFECT"
    )
    assert acq_right_class == "RIGHT_BOUNDARY_TRUNCATION", f"Failed right defect classification: {acq_right_class}"

    # Left Boundary Over-Inclusion Check
    acq_left_class = (
        "LEFT_BOUNDARY_OVER_INCLUSION"
        if len(off_grid) == 1 and off_grid[0] == (GRID_START - pd.Timedelta("5min"))
        else "UNCLASSIFIED_LEFT_DEFECT"
    )
    assert acq_left_class == "LEFT_BOUNDARY_OVER_INCLUSION", f"Failed left defect classification: {acq_left_class}"

    # 7. Window-Level Diagnostic Record (Single Structured Acquisition Record)
    window_acquisition_record = {
        "evaluation_grid_intervals": len(grid),
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
                "axis_3_instrument": "CLOSED_SLICE_OVER_INCLUSION (00:00:00Z precedes 00:05:00Z grid start)",
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
    print(f"Declared Evaluation Grid     : {len(grid):,} intervals ({GRID_START} -> {GRID_END})")
    print(f"Admitted On-Grid             : {len(admitted):,} intervals")
    print(f"Missing On-Grid              : {len(missing)} intervals")
    print(f"Off-Grid Left Over-Inclusion : {len(off_grid)} interval ({off_grid[0]})")
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
