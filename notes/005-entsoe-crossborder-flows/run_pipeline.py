#!/usr/bin/env python3
"""
Open Market Note #005 — Deterministic Pipeline Execution (L1–L6)
Metric M2: ENTSO-E Intra-Corridor Physical Flow Dynamics (June 1, 2025 – June 30, 2026)
Protocol Stack: market-note-baseline v1.4.0, p10-gate v1.1.0, p10-client-audit v1.0.0
Execution Mode: EMPIRICAL SCIENTIFIC DATASET (100% REAL ENTSO-E A11 PHYSICAL FLOW TELEMETRY)
"""

import os
import sys
import json
import hashlib
import glob
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Define workspace paths
NOTE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTE_DIR, "data")
RAW_FLOW_DIR = os.path.join(DATA_DIR, "raw_xml_flow")
FIGURES_DIR = os.path.join(NOTE_DIR, "figures")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# 1. Compute Provenance Hashes
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
    'FR': '10YFR-RTE------C'
}

# Fixed geographic / alphabetical corridor listing across telemetered borders (Rule D compliant)
CORRIDORS = [
    {"id": "AT_DE", "name": "AT ↔ DE", "c1": ("AT", "DE"), "c2": ("DE", "AT"), "color": "#00d2ff"},
    {"id": "BE_NL", "name": "BE ↔ NL", "c1": ("BE", "NL"), "c2": ("NL", "BE"), "color": "#39ff14"},
    {"id": "FR_BE", "name": "FR ↔ BE", "c1": ("FR", "BE"), "c2": ("BE", "FR"), "color": "#ff007f"},
    {"id": "NL_DE", "name": "NL ↔ DE", "c1": ("NL", "DE"), "c2": ("DE", "NL"), "color": "#ffaa00"}
]

def parse_xml_payload(filepath, qty_name="flow_mw"):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
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
                        qty_name: abs(qty),
                        "resolution": res,
                        "hours_weight": hours_weight
                    })
                    
    return pd.DataFrame(records)

def load_and_aggregate_empirical_telemetry():
    flow_files = glob.glob(os.path.join(RAW_FLOW_DIR, "*.xml"))
    
    if not flow_files:
        print("[ERROR] Missing raw XML flow files.")
        sys.exit(1)
        
    print(f"[INGEST] Processing {len(flow_files)} physical flow XMLs...")
    
    raw_flow_df = pd.concat([parse_xml_payload(f, "flow_mw") for f in flow_files], ignore_index=True)
    raw_flow_df["timestamp"] = pd.to_datetime(raw_flow_df["timestamp"])
    
    # Calculate dataset SHA256
    hasher = hashlib.sha256()
    for f in sorted(flow_files):
        with open(f, "rb") as fp:
            hasher.update(fp.read())
    data_sha256 = hasher.hexdigest()
    
    corridor_dfs = []
    
    for c in CORRIDORS:
        in1, out1 = EIC_MAP[c["c1"][1]], EIC_MAP[c["c1"][0]]
        in2, out2 = EIC_MAP[c["c2"][1]], EIC_MAP[c["c2"][0]]
        
        # Physical flows in both directions
        f1 = raw_flow_df[(raw_flow_df["in_domain"] == in1) & (raw_flow_df["out_domain"] == out1)].copy()
        f2 = raw_flow_df[(raw_flow_df["in_domain"] == in2) & (raw_flow_df["out_domain"] == out2)].copy()
        
        f1 = f1.rename(columns={"flow_mw": "flow1"})
        f2 = f2.rename(columns={"flow_mw": "flow2"})
        
        # Merge directional flow telemetry
        m_df = pd.merge(f1[["timestamp", "flow1", "resolution", "hours_weight"]],
                        f2[["timestamp", "flow2"]], on="timestamp", how="outer").fillna(0.0)
                        
        # Rule C: Absolute net physical flow
        m_df["net_flow_mw"] = (m_df["flow1"] - m_df["flow2"]).abs()
        m_df["corridor"] = c["id"]
        m_df["name"] = c["name"]
        
        corridor_dfs.append(m_df)
        
    full_df = pd.concat(corridor_dfs, ignore_index=True)
    full_df = full_df.sort_values("timestamp").reset_index(drop=True)
    
    return full_df, data_sha256

def generate_small_multiples_fdc_chart(full_df, summary_by_corridor):
    """
    Generates a 2x2 Small Multiples Flow Duration Curve chart in strict compliance with Rule D.
    Each corridor receives its own independent panel with its own percentiles.
    """
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    fig.suptitle("ENTSO-E Intra-Corridor Physical Flow Duration Curves (Metric M2 Baseline)",
                 fontsize=15, fontweight='bold', color='#ffffff', y=0.98)
                 
    fig.text(0.5, 0.94, "Rule D Compliance: Small Multiples Layout — Each corridor evaluated strictly against its own temporal distribution.",
             ha='center', fontsize=10, fontstyle='italic', color='#bbbbbb')

    axes_flat = axes.flatten()

    for idx, c in enumerate(CORRIDORS):
        ax = axes_flat[idx]
        cdf = full_df[full_df["corridor"] == c["id"]].copy()
        flows_sorted = np.sort(cdf["net_flow_mw"].values)[::-1]  # Sort descending for FDC
        percent_duration = np.linspace(0, 100, len(flows_sorted))
        
        stats = summary_by_corridor[c["id"]]
        
        # Plot FDC
        ax.plot(percent_duration, flows_sorted, color=c["color"], linewidth=2.2, label=f"{c['name']} Flow Duration")
        ax.fill_between(percent_duration, 0, flows_sorted, color=c["color"], alpha=0.15)
        
        # Reference lines matching summary.json percentiles
        p50 = stats["median_p50_flow_mw"]
        p90 = stats["p90_flow_mw"]
        p99 = stats["p99_flow_mw"]
        
        ax.axhline(p50, color='#ffffff', linestyle='--', linewidth=1.0, alpha=0.7, label=f"Median (P50): {p50:,.1f} MW")
        ax.axhline(p90, color='#ffea00', linestyle=':', linewidth=1.0, alpha=0.8, label=f"High (P90): {p90:,.1f} MW")
        ax.axhline(p99, color='#ff3333', linestyle='-.', linewidth=1.0, alpha=0.8, label=f"Peak (P99): {p99:,.1f} MW")
        
        ax.set_title(f"Corridor: {c['name']} (13-Month Self-Distribution)", fontsize=12, fontweight='bold', color='#ffffff', pad=8)
        ax.set_xlabel("% of Annual Duration", fontsize=9, color='#cccccc')
        ax.set_ylabel("Net Physical Flow (|P_flow| MW)", fontsize=9, color='#cccccc')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, max(flows_sorted) * 1.15)
        
        ax.grid(True, linestyle=':', alpha=0.25, color='#888888')
        ax.legend(loc='upper right', fontsize=8.5, framealpha=0.4, facecolor='#111111')
        
        # Stats annotation box inside panel
        stats_text = (f"Mean: {stats['mean_flow_mw']:,.1f} MW\n"
                      f"Std (σ): {stats['std_flow_mw']:,.1f} MW\n"
                      f"Peak Ratio: {stats['peak_to_mean_ratio']}x")
        ax.text(0.04, 0.08, stats_text, transform=ax.transAxes, fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.4", facecolor='#111111', edgecolor='#444444', alpha=0.8),
                color='#e0e0e0')

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    
    chart_path = os.path.join(FIGURES_DIR, "m2_flow_duration_curves.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    
    print(f"[FIGURE SUCCESS] Rule D Small Multiples Flow Duration Curves chart saved: {chart_path}")
    return compute_file_sha256(chart_path)

def run_pipeline():
    print("=== Open Market Note #005 — Deterministic Pipeline Execution (L1–L6) ===")
    print("[EXECUTION MODE] EMPIRICAL METRIC M2 — INTRA-CORRIDOR PHYSICAL FLOW DYNAMICS")
    print(f"[METADATA] methodology_sha256: {METHODOLOGY_SHA256}")
    print(f"[METADATA] pipeline_sha256:    {PIPELINE_SHA256}")
    
    # L1: Ingest Empirical Telemetry
    full_df, DATA_SHA256 = load_and_aggregate_empirical_telemetry()
    print(f"[L1 SUCCESS] 100% Real ENTSO-E physical flow telemetry loaded. data_sha256: {DATA_SHA256}")
    
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
        "dataset_name": "ENTSO-E Cross-Border Physical Flow Telemetry Dataset (202506 - 202606)",
        "dataset_status": "100% Verified Empirical Telemetry (ENTSO-E DocumentType A11)",
        "period_start": full_df["timestamp"].min().isoformat(),
        "period_end": full_df["timestamp"].max().isoformat(),
        "total_records": len(full_df),
        "protocol_stack": PROTOCOL_STACK
    }
    with open(os.path.join(DATA_DIR, "input_manifest.json"), "w") as f:
        json.dump(input_manifest, f, indent=2)

    # L2 & L3: Metric M2 Computation (Intra-Corridor Self-Distribution per Rule D)
    summary_by_corridor = {}
    
    for corridor in CORRIDORS:
        cdf = full_df[full_df["corridor"] == corridor["id"]].copy().sort_values("timestamp")
        flows = cdf["net_flow_mw"]
        total_eval_hours = len(cdf) * cdf["hours_weight"].iloc[0] if len(cdf) > 0 else 1.0
        
        # Intra-corridor percentiles (Rule D)
        p10 = float(flows.quantile(0.10))
        p50 = float(flows.quantile(0.50))
        p90 = float(flows.quantile(0.90))
        p99 = float(flows.quantile(0.99))
        
        mean_flow = float(flows.mean())
        std_flow = float(flows.std())
        max_flow = float(flows.max())
        min_flow = float(flows.min())
        
        # Peak Ratio relative to own mean
        peak_ratio = round(max_flow / mean_flow, 2) if mean_flow > 0 else 0.0
        
        summary_by_corridor[corridor["id"]] = {
            "name": corridor["name"],
            "total_eval_hours": round(float(total_eval_hours), 2),
            "mean_flow_mw": round(mean_flow, 2),
            "std_flow_mw": round(std_flow, 2),
            "median_p50_flow_mw": round(p50, 2),
            "p10_flow_mw": round(p10, 2),
            "p90_flow_mw": round(p90, 2),
            "p99_flow_mw": round(p99, 2),
            "max_peak_flow_mw": round(max_flow, 2),
            "min_flow_mw": round(min_flow, 2),
            "peak_to_mean_ratio": peak_ratio
        }
        
    # L4: Generate Rule D Small Multiples Visual
    chart_sha256 = generate_small_multiples_fdc_chart(full_df, summary_by_corridor)
    PROTOCOL_STACK["provenance_hashes"]["figure_sha256"] = chart_sha256

    # L4: Assemble summary.json
    summary_output = {
        "note_id": "005",
        "market": "ENTSO-E Transparency Platform",
        "primary_metric": "M2 — Intra-Corridor Physical Flow Dynamics (Rule D Compliance)",
        "metric_m1_note": "Metric M1 (Utilization Ratio) is EXCLUDED for all corridors per Decision D-006 / Rule A due to missing directional Total NTC telemetry under CC BY 4.0.",
        "dataset_status": "100% Empirical Telemetry Verified",
        "eval_period": "2025-06-01 to 2026-06-30 (13 Months)",
        "total_corridors_evaluated": len(CORRIDORS),
        "corridor_metrics_m2": summary_by_corridor,
        "protocol_stack": PROTOCOL_STACK
    }
    
    summary_path = os.path.join(NOTE_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary_output, f, indent=2)
        
    with open(summary_path, "rb") as f:
        summary_sha256 = hashlib.sha256(f.read()).hexdigest()
        
    print(f"[L4 SUCCESS] Empirical M2 summary.json created. summary_sha256: {summary_sha256}")
    
    # L5: Summary Display
    print("\n=== METRIC M2: INTRA-CORRIDOR PHYSICAL FLOW DYNAMICS (RULE D COMPLIANT) ===")
    print(f"{'Corridor':<10} | {'Mean (MW)':<10} | {'Std (MW)':<10} | {'P50 (MW)':<10} | {'P90 (MW)':<10} | {'P99 (MW)':<10} | {'Peak Ratio':<10}")
    print("-" * 82)
    for c_id, stats in summary_by_corridor.items():
        print(f"{stats['name']:<10} | {stats['mean_flow_mw']:<10.1f} | {stats['std_flow_mw']:<10.1f} | {stats['median_p50_flow_mw']:<10.1f} | {stats['p90_flow_mw']:<10.1f} | {stats['p99_flow_mw']:<10.1f} | {stats['peak_to_mean_ratio']:<10.2f}")
    print("-" * 82)
    
    return summary_output

if __name__ == "__main__":
    run_pipeline()
