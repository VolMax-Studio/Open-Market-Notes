#!/usr/bin/env python3
"""
Open Market Note #005 — Real ENTSO-E Deterministic Execution Pipeline (L1–L6)
Metric M1: ENTSO-E High Utilization Duration Baseline (June 1, 2025 – June 30, 2026)
Protocol Stack: market-note-baseline v1.4.0, p10-gate v1.1.0, p10-client-audit v1.0.0
Execution Mode: EMPIRICAL SCIENTIFIC DATASET (REAL ENTSO-E TELEMETRY)
"""

import os
import sys
import json
import hashlib
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Define workspace paths
NOTE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_xml")
FIGURES_DIR = os.path.join(NOTE_DIR, "figures")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# 1. Compute Hashes
def compute_file_sha256(filepath):
    hasher = hashlib.sha256()
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            hasher.update(f.read())
    return hasher.hexdigest()

def compute_methodology_hash():
    params_path = os.path.join(NOTE_DIR, "PARAMS.md")
    decisions_path = os.path.join(NOTE_DIR, "DECISIONS.md")
    
    hasher = hashlib.sha256()
    for filepath in [params_path, decisions_path]:
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                hasher.update(f.read())
    return hasher.hexdigest()

METHODOLOGY_SHA256 = compute_methodology_hash()
PIPELINE_SHA256 = compute_file_sha256(os.path.abspath(__file__))

EIC_MAP = {
    'NL': '10YNL----------L',
    'DE': '10Y1001A1001A83F',
    'BE': '10YBE----------2',
    'AT': '10YAT-APG------L',
    'DK1': '10YDK-1--------W',
    'FR': '10YFR-RTE------C'
}

CORRIDORS = [
    {"id": "NL_DE", "name": "NL ↔ DE", "c1": ("NL", "DE"), "c2": ("DE", "NL"), "pmax_mw": 5200.0},
    {"id": "BE_NL", "name": "BE ↔ NL", "c1": ("BE", "NL"), "c2": ("NL", "BE"), "pmax_mw": 3400.0},
    {"id": "AT_DE", "name": "AT ↔ DE", "c1": ("AT", "DE"), "c2": ("DE", "AT"), "pmax_mw": 4800.0},
    {"id": "FR_BE", "name": "FR ↔ BE", "c1": ("FR", "BE"), "c2": ("BE", "FR"), "pmax_mw": 3200.0}
]

def parse_xml_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        return pd.DataFrame()
        
    ns = {}
    if root.tag.startswith('{'):
        ns_url = root.tag.split('}')[0].strip('{')
        ns = {'ns': ns_url}
        
    timeseries_list = root.findall('.//ns:TimeSeries', ns) if ns else root.findall('.//TimeSeries')
    records = []
    
    for ts in timeseries_list:
        in_domain_elem = ts.find('ns:in_Domain.mRID', ns) if ns else ts.find('in_Domain.mRID')
        out_domain_elem = ts.find('ns:out_Domain.mRID', ns) if ns else ts.find('out_Domain.mRID')
        
        in_domain = in_domain_elem.text if in_domain_elem is not None else ""
        out_domain = out_domain_elem.text if out_domain_elem is not None else ""
        
        period_elems = ts.findall('ns:Period', ns) if ns else ts.findall('Period')
        for period in period_elems:
            time_interval = period.find('ns:timeInterval', ns) if ns else period.find('timeInterval')
            start_str = time_interval.find('ns:start', ns).text if ns else time_interval.find('start').text
            
            resolution_elem = period.find('ns:resolution', ns) if ns else period.find('resolution')
            res = resolution_elem.text if resolution_elem is not None else "PT60M"
            
            if res == "PT15M":
                step = timedelta(minutes=15)
                hours_weight = 0.25
            elif res == "PT30M":
                step = timedelta(minutes=30)
                hours_weight = 0.50
            else:
                step = timedelta(hours=1)
                hours_weight = 1.00
                
            clean_start = start_str.replace("Z", "+00:00")
            base_dt = datetime.fromisoformat(clean_start)
            
            points = period.findall('ns:Point', ns) if ns else period.findall('Point')
            for pt in points:
                pos_elem = pt.find('ns:position', ns) if ns else pt.find('position')
                qty_elem = pt.find('ns:quantity', ns) if ns else pt.find('quantity')
                
                if pos_elem is not None and qty_elem is not None:
                    pos = int(pos_elem.text)
                    qty = float(qty_elem.text)
                    pt_dt = base_dt + (pos - 1) * step
                    
                    records.append({
                        "timestamp": pt_dt.isoformat(),
                        "in_domain": in_domain,
                        "out_domain": out_domain,
                        "flow_mw": abs(qty),
                        "resolution": res,
                        "hours_weight": hours_weight
                    })
                    
    return pd.DataFrame(records)

def load_and_aggregate_empirical_telemetry():
    xml_files = glob.glob(os.path.join(RAW_DIR, "*.xml"))
    if not xml_files:
        print("[ERROR] No XML raw files found in raw_xml/")
        sys.exit(1)
        
    df_list = []
    for f in xml_files:
        df = parse_xml_file(f)
        if not df.empty:
            df_list.append(df)
            
    raw_df = pd.concat(df_list, ignore_index=True)
    raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp"])
    
    # Calculate dataset SHA256
    hasher = hashlib.sha256()
    for f in sorted(xml_files):
        with open(f, "rb") as fp:
            hasher.update(fp.read())
    data_sha256 = hasher.hexdigest()
    
    corridor_dfs = []
    
    for c in CORRIDORS:
        in1, out1 = EIC_MAP[c["c1"][1]], EIC_MAP[c["c1"][0]]
        in2, out2 = EIC_MAP[c["c2"][1]], EIC_MAP[c["c2"][0]]
        
        # Subset flows in both directions
        f1 = raw_df[(raw_df["in_domain"] == in1) & (raw_df["out_domain"] == out1)].copy()
        f2 = raw_df[(raw_df["in_domain"] == in2) & (raw_df["out_domain"] == out2)].copy()
        
        f1 = f1.rename(columns={"flow_mw": "flow1"})
        f2 = f2.rename(columns={"flow_mw": "flow2"})
        
        # Merge on timestamp
        m_df = pd.merge(f1[["timestamp", "flow1", "resolution", "hours_weight"]],
                        f2[["timestamp", "flow2"]], on="timestamp", how="outer").fillna(0.0)
                        
        m_df["net_flow_mw"] = (m_df["flow1"] - m_df["flow2"]).abs()  # Rule C: Absolute net flow
        m_df["corridor"] = c["id"]
        m_df["name"] = c["name"]
        m_df["capacity_mw"] = c["pmax_mw"]
        m_df["utilization_ratio"] = m_df["net_flow_mw"] / c["pmax_mw"]
        
        corridor_dfs.append(m_df)
        
    full_df = pd.concat(corridor_dfs, ignore_index=True)
    full_df = full_df.sort_values("timestamp").reset_index(drop=True)
    
    return full_df, data_sha256

def run_pipeline():
    print("=== Open Market Note #005 — Deterministic Pipeline Execution (L1–L6) ===")
    print("[EXECUTION MODE] EMPIRICAL SCIENTIFIC DATASET (REAL ENTSO-E TELEMETRY)")
    print(f"[METADATA] methodology_sha256: {METHODOLOGY_SHA256}")
    print(f"[METADATA] pipeline_sha256:    {PIPELINE_SHA256}")
    
    # L1: Load Empirical Telemetry
    full_df, DATA_SHA256 = load_and_aggregate_empirical_telemetry()
    print(f"[L1 SUCCESS] Real ENTSO-E telemetry loaded. data_sha256: {DATA_SHA256}")
    
    PROTOCOL_STACK = {
        "market-note-baseline": "1.4.0",
        "p10-gate": "1.1.0",
        "p10-client-audit": "1.0.0",
        "provenance_hashes": {
            "methodology_sha256": METHODOLOGY_SHA256,
            "pipeline_sha256": PIPELINE_SHA256,
            "data_sha256": DATA_SHA256
        }
    }
    
    input_manifest = {
        "dataset_name": "ENTSO-E Cross-Border Physical Flows Empirical Dataset (202506 - 202606)",
        "dataset_status": "Empirical Scientific Dataset (Real ENTSO-E Telemetry)",
        "period_start": full_df["timestamp"].min().isoformat(),
        "period_end": full_df["timestamp"].max().isoformat(),
        "total_records": len(full_df),
        "protocol_stack": PROTOCOL_STACK
    }
    with open(os.path.join(DATA_DIR, "input_manifest.json"), "w") as f:
        json.dump(input_manifest, f, indent=2)

    # L2 & L3: Metric Computation (M1 High Utilization Duration >= 90%)
    full_df["high_util_flag"] = full_df["utilization_ratio"] >= 0.90
    full_df["hours_contrib"] = full_df["high_util_flag"].astype(float) * full_df["hours_weight"]
    
    summary_by_corridor = {}
    total_hours_system = 0.0
    total_events_system = 0
    
    for corridor in CORRIDORS:
        cdf = full_df[full_df["corridor"] == corridor["id"]].copy().sort_values("timestamp")
        high_util_df = cdf[cdf["high_util_flag"]]
        m1_hours = high_util_df["hours_contrib"].sum()
        
        cdf["event_change"] = (cdf["high_util_flag"] != cdf["high_util_flag"].shift()).cumsum()
        events = cdf[cdf["high_util_flag"]].groupby("event_change")
        event_count = len(events)
        
        if event_count > 0:
            durations = events["hours_weight"].sum()
            max_event_hours = durations.max()
            mean_event_hours = durations.mean()
        else:
            max_event_hours = 0.0
            mean_event_hours = 0.0
            
        summary_by_corridor[corridor["id"]] = {
            "name": corridor["name"],
            "capacity_mw": corridor["pmax_mw"],
            "m1_high_utilization_hours": round(float(m1_hours), 2),
            "pct_of_year": round(float(m1_hours / 9480.0 * 100), 2),
            "event_count": int(event_count),
            "max_event_duration_hours": round(float(max_event_hours), 2),
            "mean_event_duration_hours": round(float(mean_event_hours), 2)
        }
        total_hours_system += m1_hours
        total_events_system += event_count
        
    # L4: Assemble summary.json
    summary_output = {
        "note_id": "005",
        "market": "ENTSO-E",
        "metric": "M1 — High Utilization Duration (>= 90% Capacity)",
        "dataset_status": "Empirical Scientific Dataset (Real ENTSO-E Telemetry)",
        "eval_period": "2025-06-01 to 2026-06-30 (13 Months)",
        "total_corridors_evaluated": len(CORRIDORS),
        "system_total_high_utilization_hours": round(total_hours_system, 2),
        "system_total_events": total_events_system,
        "corridor_breakdown": summary_by_corridor,
        "protocol_stack": PROTOCOL_STACK
    }
    
    summary_path = os.path.join(NOTE_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary_output, f, indent=2)
        
    with open(summary_path, "rb") as f:
        summary_sha256 = hashlib.sha256(f.read()).hexdigest()
        
    print(f"[L4 SUCCESS] Empirical summary.json created. summary_sha256: {summary_sha256}")
    
    # L5: Summary Display
    print("\n=== M1 High Utilization Duration Summary Table (REAL ENTSO-E TELEMETRY) ===")
    print(f"{'Corridor':<12} | {'Cap (MW)':<10} | {'M1 Hours':<10} | {'Events':<8} | {'Max Event (h)':<13}")
    print("-" * 65)
    for c_id, stats in summary_by_corridor.items():
        print(f"{stats['name']:<12} | {stats['capacity_mw']:<10.0f} | {stats['m1_high_utilization_hours']:<10.2f} | {stats['event_count']:<8d} | {stats['max_event_duration_hours']:<13.2f}")
    print("-" * 65)
    
    return summary_output

if __name__ == "__main__":
    run_pipeline()
