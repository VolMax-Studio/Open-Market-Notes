import os
import json
import pandas as pd
import numpy as np

def calculate_pure_scarcity_runs(df, price_col='systemSellPrice', threshold=100.0):
    """
    Calculates Pure Continuous Scarcity Runs (strictly >= threshold, zero tolerance for sub-threshold dips).
    Tracks active scarcity hours and exact continuous run lengths.
    """
    prices = df[price_col].values
    timestamps = df.index
    
    mask = prices >= threshold
    total_intervals = int(mask.sum())
    total_hours = float(total_intervals * 0.5)
    
    # Calculate continuous run lengths
    runs = []
    in_run = False
    run_start = 0
    
    for i, is_scarcity in enumerate(mask):
        if is_scarcity:
            if not in_run:
                in_run = True
                run_start = i
        else:
            if in_run:
                run_end = i - 1
                duration_h = (run_end - run_start + 1) * 0.5
                runs.append({
                    'start_time': str(timestamps[run_start]),
                    'end_time': str(timestamps[run_end]),
                    'duration_hours': duration_h,
                    'max_price': float(np.max(prices[run_start:run_end+1]))
                })
                in_run = False
                
    if in_run:
        run_end = len(prices) - 1
        duration_h = (run_end - run_start + 1) * 0.5
        runs.append({
            'start_time': str(timestamps[run_start]),
            'end_time': str(timestamps[run_end]),
            'duration_hours': duration_h,
            'max_price': float(np.max(prices[run_start:run_end+1]))
        })
        
    if not runs:
        return {
            'threshold_gbp': threshold,
            'total_qualifying_intervals': 0,
            'total_active_scarcity_hours': 0.0,
            'total_runs': 0,
            'mean_run_duration_h': 0.0,
            'median_run_duration_h': 0.0,
            'p90_run_duration_h': 0.0,
            'max_run_duration_h': 0.0,
            'max_run_start': None
        }

    durations = [r['duration_hours'] for r in runs]
    max_idx = np.argmax(durations)
    
    return {
        'threshold_gbp': threshold,
        'total_qualifying_intervals': total_intervals,
        'total_active_scarcity_hours': round(total_hours, 2),
        'total_runs': len(runs),
        'mean_run_duration_h': round(float(np.mean(durations)), 2),
        'median_run_duration_h': round(float(np.median(durations)), 2),
        'p90_run_duration_h': round(float(np.percentile(durations, 90)), 2),
        'max_run_duration_h': round(float(np.max(durations)), 2),
        'max_run_start': runs[max_idx]['start_time'],
        'max_run_end': runs[max_idx]['end_time'],
        'max_run_price': runs[max_idx]['max_price']
    }

def calculate_macro_window_spans(df, price_col='systemSellPrice', threshold=100.0, max_bridge_periods=2):
    """
    Calculates Macro Event Window Spans (wall-clock duration of scarcity clusters allowing brief sub-threshold dips < 60 min).
    """
    prices = df[price_col].values
    timestamps = df.index
    
    events = []
    in_event = False
    event_start_idx = 0
    below_count = 0
    
    for i in range(len(prices)):
        p = prices[i]
        curr_time = timestamps[i]
        
        # Time gap check: if consecutive interval is > 35 mins, break event immediately
        if in_event and i > 0:
            time_delta_min = (curr_time - timestamps[i-1]).total_seconds() / 60.0
            if time_delta_min > 35.0:
                event_end_idx = i - 1 - below_count
                if event_end_idx >= event_start_idx:
                    duration_hours = (event_end_idx - event_start_idx + 1) * 0.5
                    events.append({
                        'start_time': str(timestamps[event_start_idx]),
                        'end_time': str(timestamps[event_end_idx]),
                        'wall_clock_span_hours': duration_hours,
                        'max_price': float(np.max(prices[event_start_idx:event_end_idx+1]))
                    })
                in_event = False
                below_count = 0

        if p >= threshold:
            if not in_event:
                in_event = True
                event_start_idx = i
            below_count = 0
        else:
            if in_event:
                below_count += 1
                if below_count >= max_bridge_periods:
                    event_end_idx = i - below_count
                    if event_end_idx >= event_start_idx:
                        duration_hours = (event_end_idx - event_start_idx + 1) * 0.5
                        events.append({
                            'start_time': str(timestamps[event_start_idx]),
                            'end_time': str(timestamps[event_end_idx]),
                            'wall_clock_span_hours': duration_hours,
                            'max_price': float(np.max(prices[event_start_idx:event_end_idx+1]))
                        })
                    in_event = False
                    below_count = 0
                    
    if in_event:
        event_end_idx = len(prices) - 1 - below_count
        if event_end_idx >= event_start_idx:
            duration_hours = (event_end_idx - event_start_idx + 1) * 0.5
            events.append({
                'start_time': str(timestamps[event_start_idx]),
                'end_time': str(timestamps[event_end_idx]),
                'wall_clock_span_hours': duration_hours,
                'max_price': float(np.max(prices[event_start_idx:event_end_idx+1]))
            })

    if not events:
        return {
            'threshold_gbp': threshold,
            'max_bridge_periods': max_bridge_periods,
            'total_macro_windows': 0,
            'mean_window_span_h': 0.0,
            'median_window_span_h': 0.0,
            'p90_window_span_h': 0.0,
            'max_window_span_h': 0.0,
            'max_window_start': None
        }

    durations = [e['wall_clock_span_hours'] for e in events]
    max_idx = np.argmax(durations)
    
    return {
        'threshold_gbp': threshold,
        'max_bridge_periods': max_bridge_periods,
        'total_macro_windows': len(events),
        'mean_window_span_h': round(float(np.mean(durations)), 2),
        'median_window_span_h': round(float(np.median(durations)), 2),
        'p90_window_span_h': round(float(np.percentile(durations, 90)), 2),
        'max_window_span_h': round(float(np.max(durations)), 2),
        'max_window_start': events[max_idx]['start_time'],
        'max_window_end': events[max_idx]['end_time'],
        'max_window_price': events[max_idx]['max_price']
    }

def calculate_m2_charging_windows(df, price_col='systemSellPrice', cheap_threshold=25.0):
    df_cheap = df[df[price_col] <= cheap_threshold].copy()
    daily_hours = df_cheap.groupby(df_cheap.index.date).size() * 0.5
    
    all_dates = pd.date_range(start=df.index.min().date(), end=df.index.max().date(), freq='D').date
    daily_hours = daily_hours.reindex(all_dates, fill_value=0.0)
    
    total_days = len(daily_hours)
    
    days_8h = (daily_hours >= 9.5).sum()
    days_4h = (daily_hours >= 4.8).sum()
    days_2h = (daily_hours >= 2.4).sum()
    
    return {
        'cheap_threshold_gbp': cheap_threshold,
        'total_days': total_days,
        'bess_8h_target_hours': 9.5,
        'bess_8h_qualifying_days': int(days_8h),
        'bess_8h_qualifying_pct': round(float(days_8h / total_days * 100.0), 2),
        'bess_4h_target_hours': 4.8,
        'bess_4h_qualifying_days': int(days_4h),
        'bess_4h_qualifying_pct': round(float(days_4h / total_days * 100.0), 2),
        'bess_2h_target_hours': 2.4,
        'bess_2h_qualifying_days': int(days_2h),
        'bess_2h_qualifying_pct': round(float(days_2h / total_days * 100.0), 2),
        'mean_daily_cheap_hours': round(float(daily_hours.mean()), 2),
        'max_daily_cheap_hours': round(float(daily_hours.max()), 2)
    }

import argparse

def run_full_analysis(start_date=None, end_date=None, data_dir=None, out_dir=None):
    if start_date is None:
        start_date = "2025-06-01"
    if end_date is None:
        end_date = "2026-06-30"
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data_dir is None:
        if (start_date, end_date) == ("2025-06-01", "2026-06-30"):
            baseline_file = os.path.join(base_dir, 'data', 'baseline', 'gb_system_prices_202506_202606.feather')
            if os.path.exists(baseline_file):
                feather_file = baseline_file
            else:
                feather_file = os.path.join(base_dir, 'data', 'processed', 'gb_system_prices.feather')
        else:
            import sys
            sys.exit("FATAL ERROR: Non-baseline measurement window requires explicit --data-dir argument")
    else:
        feather_file = os.path.join(data_dir, 'gb_system_prices.feather')

    if out_dir is None:
        out_dir = '.'
        
    df = pd.read_feather(feather_file)
    df['startTime'] = pd.to_datetime(df['startTime'])
    df = df.set_index('startTime')
    
    if start_date and end_date:
        start_dt = pd.Timestamp(start_date, tz=df.index.tz)
        end_dt = pd.Timestamp(end_date, tz=df.index.tz) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
    
    print("==========================================")
    print("RUNNING METRIC CALCULATIONS FOR GB BASELINE")
    print("==========================================")
    
    m1_100_pure = calculate_pure_scarcity_runs(df, threshold=100.0)
    m1_100_window = calculate_macro_window_spans(df, threshold=100.0, max_bridge_periods=2)
    
    m1_250_pure = calculate_pure_scarcity_runs(df, threshold=250.0)
    m1_250_window = calculate_macro_window_spans(df, threshold=250.0, max_bridge_periods=2)
    
    m2 = calculate_m2_charging_windows(df, cheap_threshold=25.0)
    
    results = {
        'market': 'GB (Great Britain)',
        'data_source': 'Elexon Insights API (System Prices)',
        'time_range': f"{df.index.min()} to {df.index.max()}",
        'total_intervals': len(df),
        'm1_scarcity_100_pure_runs': m1_100_pure,
        'm1_scarcity_100_macro_windows': m1_100_window,
        'm1_extreme_250_pure_runs': m1_250_pure,
        'm1_extreme_250_macro_windows': m1_250_window,
        'm2_charging_windows': m2
    }
    
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, 'results.json')
    
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\n--- METRIC 1: PURE CONTINUOUS SCARCITY RUNS (GBP >= 100/MWh) ---")
    print(json.dumps(m1_100_pure, indent=2))

    print("\n--- METRIC 1: MACRO EVENT WINDOW SPANS (GBP >= 100/MWh, BRIDGED) ---")
    print(json.dumps(m1_100_window, indent=2))
    
    print("\n--- METRIC 1: PURE EXTREME SCARCITY RUNS (GBP >= 250/MWh) ---")
    print(json.dumps(m1_250_pure, indent=2))
    
    print("\n--- METRIC 2: CHARGING WINDOW AVAILABILITY (GBP <= 25/MWh) ---")
    print(json.dumps(m2, indent=2))
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run GB BESS Duration Baseline Analysis")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--data-dir", help="Directory containing gb_system_prices.feather")
    parser.add_argument("--out-dir", help="Directory to write results.json")
    args = parser.parse_args()
    
    run_full_analysis(start_date=args.start_date, end_date=args.end_date, data_dir=args.data_dir, out_dir=args.out_dir)
