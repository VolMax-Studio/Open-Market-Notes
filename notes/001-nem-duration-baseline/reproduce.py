#!/usr/bin/env python3
import os
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for rich aesthetics (dark mode/premium look)
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

# Public registered energy capacity mapping for the 16 accepted BESS units
BESS_ENERGY_CAPACITY = {
    'HPR1': 193.5,      # Hornsdale Power Reserve
    'VBB1': 450.0,      # Victorian Big Battery
    'WANDB1': 150.0,    # Wandoan South BESS
    'WDBESS1': 540.0,   # Western Downs BESS
    'TIB1': 250.0,      # Torrens Island BESS
    'HBESS1': 150.0,    # Hazelwood BESS
    'RANGEB1': 400.0,   # Rangebank BESS
    'CHBESS1': 200.0,   # Chinchilla BESS
    'BLYTHB1': 477.0,   # Blyth BESS
    'BHB1': 50.0,       # Broken Hill Battery
    'BBATTERY1': 100.0, # Bouldercombe BESS
    'ULPBESS1': 298.0,  # Ulinda Park BESS
    'WALGRV1': 75.0,    # Wallgrove Grid Battery
    'RESS1': 120.0,     # Riverina BESS 1
    'RIVNB2': 130.0,    # Riverina BESS 2
    'CAPBES1': 200.0,   # Capital BESS
}

def main():
    print("======================================================================")
    print("STARTING REPRODUCTION OF VOLMAX NOTE #1: NEM DURATION BASELINE")
    print("======================================================================")

    proc_dir = '../../data/processed'
    if not os.path.exists(proc_dir):
        # Try local path if run from repo root
        proc_dir = './data/processed'
    
    if not os.path.exists(proc_dir):
        raise FileNotFoundError(f"Processed data directory not found at {proc_dir}")

    # 1. Stitch and load 13 months of price data
    price_files = sorted(glob.glob(os.path.join(proc_dir, "price_*.feather")))
    print(f"Loading {len(price_files)} price files...")
    price_list = []
    for f in price_files:
        df = pd.read_feather(f)
        price_list.append(df)
    price_df = pd.concat(price_list, ignore_index=True)
    price_df['SETTLEMENTDATE'] = pd.to_datetime(price_df['SETTLEMENTDATE'])
    
    # Filter strictly to the 13-month trading window
    price_df = price_df[(price_df['SETTLEMENTDATE'] >= '2025-06-01 04:05:00') & 
                        (price_df['SETTLEMENTDATE'] <= '2026-07-01 04:00:00')].copy()
    print(f"Stitched and filtered price data shape: {price_df.shape}")

    # 2. Stitch and load 13 months of SCADA data
    scada_files = sorted(glob.glob(os.path.join(proc_dir, "scada_*.feather")))
    print(f"Loading {len(scada_files)} SCADA files...")
    scada_list = []
    for f in scada_files:
        df = pd.read_feather(f)
        # Filter for the 16 accepted DUIDs
        df = df[df['DUID'].isin(BESS_ENERGY_CAPACITY.keys())]
        scada_list.append(df)
    scada_df = pd.concat(scada_list, ignore_index=True)
    scada_df['SETTLEMENTDATE'] = pd.to_datetime(scada_df['SETTLEMENTDATE'])
    
    # Filter strictly to the 13-month trading window
    scada_df = scada_df[(scada_df['SETTLEMENTDATE'] >= '2025-06-01 04:05:00') & 
                        (scada_df['SETTLEMENTDATE'] <= '2026-07-01 04:00:00')].copy()
    print(f"Stitched and filtered BESS SCADA data shape: {scada_df.shape}")

    regions = ['NSW1', 'QLD1', 'SA1', 'VIC1']
    results = {
        "Metric_1_Scarcity_Pricing_Duration": {},
        "Metric_2_Charging_Window_Availability": {},
        "Metric_3_Fleet_Cycling_Feedback_Loop": {}
    }

    # ==========================================================================
    # METRIC 1: SCARCITY PRICING DURATION
    # ==========================================================================
    print("\nCalculating Metric 1 (Scarcity Pricing Duration)...")
    for r in regions:
        r_df = price_df[price_df['REGIONID'] == r].copy().sort_values('SETTLEMENTDATE')
        r_df['is_spike'] = (r_df['RRP'] >= 300.0).astype(int)
        
        # Consecutive group detection
        r_df['event_id'] = (r_df['is_spike'] != r_df['is_spike'].shift()).cumsum()
        events = r_df[r_df['is_spike'] == 1].groupby('event_id')
        
        durations = []
        event_details = []
        
        for name, group in events:
            dur_mins = len(group) * 5
            start_time = group['SETTLEMENTDATE'].min().strftime('%Y-%m-%d %H:%M:%S')
            max_price = float(group['RRP'].max())
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
            
        results["Metric_1_Scarcity_Pricing_Duration"][r] = {
            "Total_Events": len(durations),
            "Mean_Duration_Minutes": round(mean_dur, 2),
            "Median_Duration_Minutes": round(median_dur, 2),
            "P90_Duration_Minutes": round(p90_dur, 2),
            "Max_Duration_Minutes": max_dur,
            "Max_Duration_Timestamp": max_date,
            "Event_List": event_details
        }
        print(f"  {r}: {len(durations)} events | Mean: {mean_dur:.1f}m | Max: {max_dur}m ({max_date})")

    # ==========================================================================
    # METRIC 2: CHARGING WINDOW AVAILABILITY
    # ==========================================================================
    print("\nCalculating Metric 2 (Charging Window Availability)...")
    # Define AEMO trading days (04:00 to 04:00) by shifting date back 245 minutes
    price_df['Trading_Date'] = (price_df['SETTLEMENTDATE'] - pd.Timedelta(minutes=245)).dt.date
    
    # Generate reference list of 395 days (1 Jun 2025 to 30 Jun 2026)
    ref_dates = pd.date_range(start='2025-06-01', end='2026-06-30').date
    total_days = len(ref_dates)
    print(f"  Analysis window contains {total_days} trading days.")

    for r in regions:
        r_df = price_df[price_df['REGIONID'] == r].copy()
        
        # Calculate daily cheap energy (RRP <= 50) hours
        r_df['is_cheap'] = (r_df['RRP'] <= 50.0).astype(int)
        daily_cheap = r_df.groupby('Trading_Date')['is_cheap'].sum() * (5.0 / 60.0)
        
        # Align with the full reference window
        daily_cheap = daily_cheap.reindex(ref_dates, fill_value=0.0)
        
        # Check thresholds
        days_met_8h = (daily_cheap >= 9.4).sum()
        days_met_4h = (daily_cheap >= 4.7).sum()
        
        pct_8h = (days_met_8h / total_days) * 100.0
        pct_4h = (days_met_4h / total_days) * 100.0
        
        results["Metric_2_Charging_Window_Availability"][r] = {
            "Total_Days": total_days,
            "Days_Met_8h_BESS": int(days_met_8h),
            "Pct_Days_Met_8h_BESS": round(float(pct_8h), 2),
            "Days_Met_4h_BESS": int(days_met_4h),
            "Pct_Days_Met_4h_BESS": round(float(pct_4h), 2)
        }
        print(f"  {r}: 4h BESS window (>=4.7h) met on {pct_4h:.1f}% of days | 8h BESS window (>=9.4h) met on {pct_8h:.1f}% of days")

    # ==========================================================================
    # METRIC 3: FLEET CYCLING FEEDBACK LOOP
    # ==========================================================================
    print("\nCalculating Metric 3 (Fleet Cycling Feedback Loop)...")
    
    # Map SCADA timestamps to trading dates and then to YearMonth
    scada_df['Trading_Date'] = (scada_df['SETTLEMENTDATE'] - pd.Timedelta(minutes=245)).dt.date
    scada_df['YearMonth'] = scada_df['Trading_Date'].apply(lambda x: x.strftime('%Y-%m'))
    
    # Calculate EFC per asset per month
    monthly_efc_list = []
    
    for duid, energy_cap in BESS_ENERGY_CAPACITY.items():
        sub = scada_df[scada_df['DUID'] == duid].copy()
        if sub.empty:
            continue
            
        # Group by YearMonth and compute throughput
        monthly_throughput = sub.groupby('YearMonth')['SCADAVALUE'].apply(lambda x: x.abs().sum() * (5.0 / 60.0))
        
        for ym, throughput in monthly_throughput.items():
            efc = throughput / (2.0 * energy_cap)
            monthly_efc_list.append({
                "DUID": duid,
                "YearMonth": ym,
                "Throughput_MWh": float(throughput),
                "EFC": float(efc)
            })
            
    m_df = pd.DataFrame(monthly_efc_list)
    
    # Group results into Short-to-Medium (all units are in this group)
    short_medium_duids = list(BESS_ENERGY_CAPACITY.keys())
    
    short_medium_monthly = m_df[m_df['DUID'].isin(short_medium_duids)].groupby('YearMonth')['EFC'].mean()
    
    results["Metric_3_Fleet_Cycling_Feedback_Loop"] = {
        "Short_Medium_Duration_Group_Monthly_Average": {ym: round(float(val), 4) for ym, val in short_medium_monthly.items()},
        "Long_Duration_Group_Monthly_Average": {}, # Empty as no operational 4h+ units exist
        "Per_Asset_Monthly_EFC": {}
    }
    
    for ym, group in m_df.groupby('YearMonth'):
        results["Metric_3_Fleet_Cycling_Feedback_Loop"]["Per_Asset_Monthly_EFC"][ym] = {
            row['DUID']: round(row['EFC'], 4) for _, row in group.iterrows()
        }
        
    print("  Monthly average EFC (Short-to-Medium Duration Group):")
    for ym, val in short_medium_monthly.items():
        print(f"    {ym}: {val:.3f} EFC/month")

    # ==========================================================================
    # SAVE OUTPUTS AND GENERATE PLOTS
    # ==========================================================================
    # Write JSON results
    out_dir = './results' if os.path.exists('./results') else './notes/nem-duration-baseline/results'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    json_path = os.path.join(out_dir, '../results.json') if 'notes' in os.getcwd() else './notes/nem-duration-baseline/results.json'
    # Ensure folder containing results.json exists
    os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
    
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\nSaved results to {json_path}")

    # Generate Plots
    plot_dir = os.path.join(os.path.dirname(json_path), 'results')
    os.makedirs(plot_dir, exist_ok=True)

    # Plot 1: Charging Window Availability
    plt.figure(figsize=(10, 6))
    x = np.arange(len(regions))
    width = 0.35
    
    pcts_4h = [results["Metric_2_Charging_Window_Availability"][r]["Pct_Days_Met_4h_BESS"] for r in regions]
    pcts_8h = [results["Metric_2_Charging_Window_Availability"][r]["Pct_Days_Met_8h_BESS"] for r in regions]
    
    plt.bar(x - width/2, pcts_4h, width, label='4h BESS (>=4.7h/day)', color='#10b981')
    plt.bar(x + width/2, pcts_8h, width, label='8h BESS (>=9.4h/day)', color='#06b6d4')
    
    plt.title("NEM Charging Window Availability by Region (1 Jun 2025 - 30 Jun 2026)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("NEM Region")
    plt.ylabel("% of Days Meeting Cumulative Charging Window")
    plt.xticks(x, regions)
    plt.ylim(0, 105)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plot1_path = os.path.join(plot_dir, "plot1_charging_window_availability.png")
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    print(f"Saved plot: {plot1_path}")

    # Plot 2: Fleet Monthly EFC Trends
    plt.figure(figsize=(12, 6))
    months_list = sorted(short_medium_monthly.index)
    plt.plot(months_list, [short_medium_monthly[ym] for ym in months_list], marker='o', linewidth=2.5, color='#047857', label='Short-to-Medium Fleet Avg')
    
    # Plot individual assets in background
    for duid in BESS_ENERGY_CAPACITY.keys():
        asset_data = m_df[m_df['DUID'] == duid].sort_values('YearMonth')
        if not asset_data.empty:
            plt.plot(asset_data['YearMonth'], asset_data['EFC'], alpha=0.15, color='#9ca3af', linewidth=1)
            
    plt.title("NEM BESS Fleet: Monthly Equivalent Full Cycles (EFC)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Month")
    plt.ylabel("Equivalent Full Cycles (EFC)")
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plot2_path = os.path.join(plot_dir, "plot2_fleet_monthly_efc.png")
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    print(f"Saved plot: {plot2_path}")

    print("\n--- GENERATED MARKDOWN TABLES ---")
    print("### Metric 1: Scarcity Pricing Duration")
    print("| Region | Total Events | Median Duration | Mean Duration | P90 Duration | Max Duration | Max Timestamp |")
    print("|:---|:---:|:---:|:---:|:---:|:---:|:---|")
    for r in regions:
        m1 = results["Metric_1_Scarcity_Pricing_Duration"][r]
        print(f"| **{r}** | {m1['Total_Events']} | {m1['Median_Duration_Minutes']:.1f} min | {m1['Mean_Duration_Minutes']:.2f} min | {m1['P90_Duration_Minutes']:.1f} min | {m1['Max_Duration_Minutes']} min ({m1['Max_Duration_Minutes']/60:.1f}h) | {m1['Max_Duration_Timestamp']} |")
    
    print("\n### Metric 2: Charging Window Availability")
    print("| Region | 4-Hour BESS Charging Window (\\ge 4.7h) | 8-Hour BESS Charging Window (\\ge 9.4h) |")
    print("|:---|:---:|:---:|")
    for r in regions:
        m2 = results["Metric_2_Charging_Window_Availability"][r]
        print(f"| **{r}** | {m2['Pct_Days_Met_4h_BESS']:.2f}% | {m2['Pct_Days_Met_8h_BESS']:.2f}% |")
    print("---------------------------------\n")

    print("\n======================================================================")
    print("SUCCESS: Note #1 reproduction calculations completed.")
    print("======================================================================")

if __name__ == '__main__':
    main()
