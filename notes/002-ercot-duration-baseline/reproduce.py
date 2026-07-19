#!/usr/bin/env python3
import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for rich aesthetics (dark grid with premium look)
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16,
    "font.family": "sans-serif"
})

HUBS = ["HB_WEST", "HB_NORTH", "HB_SOUTH", "HB_HOUSTON"]
START_DATE = "2025-06-01"
END_DATE = "2026-06-30"

def main():
    print("======================================================================")
    print("STARTING REPRODUCTION OF VOLMAX NOTE #2: ERCOT DURATION BASELINE")
    print("======================================================================")

    # 1. Load processed price data
    proc_path = './data/processed/ercot_spp_202506_202606.csv'
    if not os.path.exists(proc_path):
        proc_path = '../../data/processed/ercot_spp_202506_202606.csv'
        
    if not os.path.exists(proc_path):
        raise FileNotFoundError(f"Processed price data not found at {proc_path}")

    print(f"Loading SPP data from {proc_path}...")
    df = pd.read_csv(proc_path)
    df['timestamp'] = pd.to_datetime(df['interval_start_utc'])
    
    # Localize to Chicago timezone (Central Time) for operating day classification
    df['local_time'] = df['timestamp'].dt.tz_convert('America/Chicago')
    df['operating_day'] = df['local_time'].dt.date
    
    print(f"Loaded {len(df)} price intervals.")

    # Reference date range (395 days)
    ref_dates = pd.date_range(start=START_DATE, end=END_DATE).date
    total_days = len(ref_dates)
    print(f"Analysis window contains {total_days} calendar days.")

    results = {
        "Metric_1_Scarcity_Pricing_Duration": {
            "Threshold_100": {},
            "Threshold_250": {}
        },
        "Metric_2_Charging_Window_Availability": {}
    }

    # ==========================================================================
    # METRIC 1: SCARCITY PRICING DURATION
    # ==========================================================================
    print("\nCalculating Metric 1 (Scarcity Pricing Duration)...")
    
    thresholds = [100.0, 250.0]
    for th in thresholds:
        th_key = f"Threshold_{int(th)}"
        print(f"\n--- Threshold >= ${int(th)}/MWh ---")
        
        for hub in HUBS:
            hub_df = df[df['location'] == hub].copy().sort_values('timestamp')
            hub_df['is_spike'] = (hub_df['spp'] >= th).astype(int)
            
            # Group contiguous intervals meeting the threshold
            hub_df['event_id'] = (hub_df['is_spike'] != hub_df['is_spike'].shift()).cumsum()
            events = hub_df[hub_df['is_spike'] == 1].groupby('event_id')
            
            durations = []
            event_details = []
            
            for name, group in events:
                dur_mins = len(group) * 15 # 15-minute intervals
                start_time = group['interval_start_utc'].min()
                max_price = float(group['spp'].max())
                durations.append(dur_mins)
                event_details.append({
                    "start_time": start_time,
                    "duration_minutes": dur_mins,
                    "max_price": max_price
                })
                
            if durations:
                mean_dur = float(np.mean(durations))
                median_dur = float(np.median(durations))
                p90_dur = float(np.percentile(durations, 90))
                max_idx = np.argmax(durations)
                max_dur = int(durations[max_idx])
                max_date = event_details[max_idx]["start_time"]
            else:
                mean_dur = median_dur = p90_dur = max_dur = 0.0
                max_date = "N/A"
                
            results["Metric_1_Scarcity_Pricing_Duration"][th_key][hub] = {
                "Total_Events": len(durations),
                "Mean_Duration_Minutes": round(mean_dur, 2),
                "Median_Duration_Minutes": round(median_dur, 2),
                "P90_Duration_Minutes": round(p90_dur, 2),
                "Max_Duration_Minutes": max_dur,
                "Max_Duration_Timestamp": max_date,
                "Event_List": event_details
            }
            print(f"  {hub}: {len(durations)} events | Mean: {mean_dur:.1f}m | Max: {max_dur}m ({max_date})")

    # ==========================================================================
    # METRIC 2: CHARGING WINDOW AVAILABILITY
    # ==========================================================================
    print("\nCalculating Metric 2 (Charging Window Availability)...")
    
    for hub in HUBS:
        hub_df = df[df['location'] == hub].copy()
        
        # Calculate daily cheap energy (SPP <= 25) hours
        hub_df['is_cheap'] = (hub_df['spp'] <= 25.0).astype(int)
        daily_cheap = hub_df.groupby('operating_day')['is_cheap'].sum() * 0.25 # 15 mins = 0.25 hours
        
        # Align with the full reference window
        daily_cheap = daily_cheap.reindex(ref_dates, fill_value=0.0)
        
        # Check thresholds
        days_met_8h = (daily_cheap >= 9.4).sum()
        days_met_4h = (daily_cheap >= 4.7).sum()
        
        pct_8h = (days_met_8h / total_days) * 100.0
        pct_4h = (days_met_4h / total_days) * 100.0
        
        results["Metric_2_Charging_Window_Availability"][hub] = {
            "Total_Days": total_days,
            "Days_Met_8h_BESS": int(days_met_8h),
            "Pct_Days_Met_8h_BESS": round(float(pct_8h), 2),
            "Days_Met_4h_BESS": int(days_met_4h),
            "Pct_Days_Met_4h_BESS": round(float(pct_4h), 2)
        }
        print(f"  {hub}: 4h BESS window (>=4.7h) met on {pct_4h:.1f}% of days | 8h BESS window (>=9.4h) met on {pct_8h:.1f}% of days")

    # ==========================================================================
    # SAVE OUTPUTS AND GENERATE PLOTS
    # ==========================================================================
    # Path resolution relative to this script
    script_dir = Path(__file__).resolve().parent
    plot_dir = script_dir / "results"
    plot_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = script_dir / "results.json"
    
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\nSaved results to {json_path}")

    # Generate Plots
    # Plot 1: Charging Window Availability
    plt.figure(figsize=(10, 6))
    x = np.arange(len(HUBS))
    width = 0.35
    
    pcts_4h = [results["Metric_2_Charging_Window_Availability"][hub]["Pct_Days_Met_4h_BESS"] for hub in HUBS]
    pcts_8h = [results["Metric_2_Charging_Window_Availability"][hub]["Pct_Days_Met_8h_BESS"] for hub in HUBS]
    
    plt.bar(x - width/2, pcts_4h, width, label='4h BESS (>=4.7h/day)', color='#10b981')
    plt.bar(x + width/2, pcts_8h, width, label='8h BESS (>=9.4h/day)', color='#06b6d4')
    
    plt.title("ERCOT Charging Window Availability by Hub (1 Jun 2025 - 30 Jun 2026)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("ERCOT Zonal Hub")
    plt.ylabel("% of Days Meeting Cumulative Charging Window")
    plt.xticks(x, HUBS)
    plt.ylim(0, 105)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plot1_path = plot_dir / "plot1_charging_window_availability.png"
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    print(f"Saved plot: {plot1_path}")

    # Plot 2: Scarcity Pricing Duration
    plt.figure(figsize=(12, 6))
    
    means_100 = [results["Metric_1_Scarcity_Pricing_Duration"]["Threshold_100"][hub]["Mean_Duration_Minutes"] for hub in HUBS]
    medians_100 = [results["Metric_1_Scarcity_Pricing_Duration"]["Threshold_100"][hub]["Median_Duration_Minutes"] for hub in HUBS]
    p90s_100 = [results["Metric_1_Scarcity_Pricing_Duration"]["Threshold_100"][hub]["P90_Duration_Minutes"] for hub in HUBS]
    
    plt.bar(x - width, medians_100, width/2, label='Median Duration', color='#f59e0b')
    plt.bar(x, means_100, width/2, label='Mean Duration', color='#ef4444')
    plt.bar(x + width, p90s_100, width/2, label='P90 Duration', color='#3b82f6')
    
    plt.title("ERCOT Scarcity Event Durations (>= $100/MWh) by Hub", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("ERCOT Zonal Hub")
    plt.ylabel("Event Duration (Minutes)")
    plt.xticks(x, HUBS)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plot2_path = plot_dir / "plot2_scarcity_duration_100.png"
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    print(f"Saved plot: {plot2_path}")

    print("\n--- GENERATED MARKDOWN TABLES ---")
    print("### Metric 1: Scarcity Pricing Duration (Threshold >= $100/MWh)")
    print("| Hub | Total Events | Median Duration | Mean Duration | P90 Duration | Max Duration | Max Timestamp |")
    print("|:---|:---:|:---:|:---:|:---:|:---:|:---|")
    for hub in HUBS:
        m1 = results["Metric_1_Scarcity_Pricing_Duration"]["Threshold_100"][hub]
        print(f"| **{hub}** | {m1['Total_Events']} | {m1['Median_Duration_Minutes']:.1f} min | {m1['Mean_Duration_Minutes']:.2f} min | {m1['P90_Duration_Minutes']:.1f} min | {m1['Max_Duration_Minutes']} min ({m1['Max_Duration_Minutes']/60:.1f}h) | {m1['Max_Duration_Timestamp']} |")
    
    print("\n### Metric 1: Scarcity Pricing Duration (Threshold >= $250/MWh)")
    print("| Hub | Total Events | Median Duration | Mean Duration | P90 Duration | Max Duration | Max Timestamp |")
    print("|:---|:---:|:---:|:---:|:---:|:---:|:---|")
    for hub in HUBS:
        m1 = results["Metric_1_Scarcity_Pricing_Duration"]["Threshold_250"][hub]
        print(f"| **{hub}** | {m1['Total_Events']} | {m1['Median_Duration_Minutes']:.1f} min | {m1['Mean_Duration_Minutes']:.2f} min | {m1['P90_Duration_Minutes']:.1f} min | {m1['Max_Duration_Minutes']} min ({m1['Max_Duration_Minutes']/60:.1f}h) | {m1['Max_Duration_Timestamp']} |")

    print("\n### Metric 2: Charging Window Availability")
    print("| Hub | 4-Hour BESS Charging Window (\\ge 4.7h) | 8-Hour BESS Charging Window (\\ge 9.4h) |")
    print("|:---|:---:|:---:|")
    for hub in HUBS:
        m2 = results["Metric_2_Charging_Window_Availability"][hub]
        print(f"| **{hub}** | {m2['Pct_Days_Met_4h_BESS']:.2f}% | {m2['Pct_Days_Met_8h_BESS']:.2f}% |")
    print("---------------------------------\n")

    print("======================================================================")
    print("SUCCESS: Note #2 reproduction calculations completed.")
    print("======================================================================")

if __name__ == '__main__':
    main()
