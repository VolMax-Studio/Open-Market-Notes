#!/usr/bin/env python3
"""
Open Market Note #005 — Real ENTSO-E Physical Flow XML Parser
Parses DocumentType A11 XML payloads into cleaned DataFrames following Rules A, B, and C.
"""

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

NOTE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_xml")

def parse_xml_file(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Extract namespace if present
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
                
            # Parse start ISO timestamp
            clean_start = start_str.replace("Z", "+00:00")
            base_dt = datetime.fromisoformat(clean_start)
            
            points = period.findall('ns:Point', ns) if ns else period.findall('Point')
            for pt in points:
                pos_elem = pt.find('ns:position', ns) if ns else pt.find('position')
                qty_elem = pt.find('ns:quantity', ns) if ns else pt.find('quantity')
                
                if pos_elem is not None and qty_elem is not None:
                    pos = int(pos_elem.text)
                    qty = float(qty_elem.text)
                    
                    # Position is 1-indexed
                    pt_dt = base_dt + (pos - 1) * step
                    records.append({
                        "timestamp": pt_dt.isoformat(),
                        "in_domain": in_domain,
                        "out_domain": out_domain,
                        "flow_mw": abs(qty),  # Rule C: Directional Neutrality |Pflow|
                        "resolution": res,
                        "hours_weight": hours_weight
                    })
                    
    return pd.DataFrame(records)

def parse_all_raw_data():
    xml_files = glob.glob(os.path.join(RAW_DIR, "*.xml"))
    print(f"[PARSER] Found {len(xml_files)} raw XML files in {RAW_DIR}")
    
    all_df_list = []
    for f in xml_files:
        df = parse_xml_file(f)
        if not df.empty:
            all_df_list.append(df)
            
    if not all_df_list:
        print("[WARN] No valid XML telemetry parsed.")
        return pd.DataFrame()
        
    full_df = pd.concat(all_df_list, ignore_index=True)
    full_df["timestamp"] = pd.to_datetime(full_df["timestamp"])
    full_df = full_df.sort_values("timestamp").reset_index(drop=True)
    print(f"[PARSER SUCCESS] Parsed {len(full_df)} telemetry interval records.")
    return full_df

if __name__ == "__main__":
    df = parse_all_raw_data()
    if not df.empty:
        print(df.head())
