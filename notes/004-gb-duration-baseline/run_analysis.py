import os
import json
import pandas as pd
import numpy as np

proc_path = './data/processed/gb_system_prices.feather'

def calculate_m1_scarcity(df, price_col='systemSellPrice', threshold=100.0, separation_periods=2):
    """
    Calculates M1: Scarcity Pricing Duration with explicit Time Continuity Checks.
    - separation_periods: number of periods below threshold to break an event (1 period = strict, 2 periods = 60 min bridge).
    - Time continuity: Any gap in timestamps (>30 min between consecutive intervals) immediately breaks the event.
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
        
        # Time gap check: if consecutive interval is > 30 mins, break event immediately
        if in_event and i > 0:
            time_delta_min = (curr_time - timestamps[i-1]).total_seconds() / 60.0
            if time_delta_min > 35.0: # allow small jitter for DST transitions
                event_end_idx = i - 1 - below_count
                if event_end_idx >= event_start_idx:
                    duration_hours = (event_end_idx - event_start_idx + 1) * 0.5
                    events.append({
                        'start_time': str(timestamps[event_start_idx]),
                        'end_time': str(timestamps[event_end_idx]),
                        'duration_hours': duration_hours,
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
                if below_count >= separation_periods:
                    event_end_idx = i - below_count
                    if event_end_idx >= event_start_idx:
                        duration_hours = (event_end_idx - event_start_idx + 1) * 0.5
                        events.append({
                            'start_time': str(timestamps[event_start_idx]),
                            'end_time': str(timestamps[event_end_idx]),
                            'duration_hours': duration_hours,
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
                'duration_hours': duration_hours,
                'max_price': float(np.max(prices[event_start_idx:event_end_idx+1]))
            })

    if not events:
        return {
            'threshold_gbp': threshold,
            'separation_periods': separation_periods,
            'total_events': 0,
            'mean_duration_h': 0.0,
            'median_duration_h': 0.0,
            'p90_duration_h': 0.0,
            'max_duration_h': 0.0,
            'max_event_start': None
        }

    durations = [e['duration_hours'] for e in events]
    max_idx = np.argmax(durations)
    
    return {
        'threshold_gbp': threshold,
        'separation_periods': separation_periods,
        'total_events': len(events),
        'mean_duration_h': round(float(np.mean(durations)), 2),
        'median_duration_h': round(float(np.median(durations)), 2),
        'p90_duration_h': round(float(np.percentile(durations, 90)), 2),
        'max_duration_h': round(float(np.max(durations)), 2),
        'max_event_start': events[max_idx]['start_time'],
        'max_event_end': events[max_idx]['end_time'],
        'max_event_price': events[max_idx]['max_price']
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

def run_full_analysis():
    df = pd.read_feather(proc_path)
    df['startTime'] = pd.to_datetime(df['startTime'])
    df = df.set_index('startTime')
    
    print("==========================================")
    print("RUNNING METRIC CALCULATIONS FOR GB BASELINE")
    print("==========================================")
    
    m1_100_strict = calculate_m1_scarcity(df, threshold=100.0, separation_periods=1)
    m1_100_bridged = calculate_m1_scarcity(df, threshold=100.0, separation_periods=2)
    m1_250_strict = calculate_m1_scarcity(df, threshold=250.0, separation_periods=1)
    m1_250_bridged = calculate_m1_scarcity(df, threshold=250.0, separation_periods=2)
    
    m2 = calculate_m2_charging_windows(df, cheap_threshold=25.0)
    
    results = {
        'market': 'GB (Great Britain)',
        'data_source': 'Elexon Insights API (System Prices)',
        'time_range': f"{df.index.min()} to {df.index.max()}",
        'total_intervals': len(df),
        'm1_scarcity_100_strict': m1_100_strict,
        'm1_scarcity_100_bridged': m1_100_bridged,
        'm1_scarcity_250_strict': m1_250_strict,
        'm1_scarcity_250_bridged': m1_250_bridged,
        'm2_charging_windows': m2
    }
    
    out_json = './data/processed/gb_baseline_results.json'
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\n--- METRIC 1: SCARCITY DURATION (STRICT 1-PERIOD SEPARATION, GBP >= 100/MWh) ---")
    print(json.dumps(m1_100_strict, indent=2))

    print("\n--- METRIC 1: SCARCITY DURATION (BRIDGED 2-PERIOD SEPARATION, GBP >= 100/MWh) ---")
    print(json.dumps(m1_100_bridged, indent=2))
    
    print("\n--- METRIC 1: EXTREME SCARCITY DURATION (GBP >= 250/MWh) ---")
    print(json.dumps(m1_250_strict, indent=2))
    
    print("\n--- METRIC 2: CHARGING WINDOW AVAILABILITY (GBP <= 25/MWh) ---")
    print(json.dumps(m2, indent=2))
    
    return results

if __name__ == '__main__':
    run_full_analysis()
