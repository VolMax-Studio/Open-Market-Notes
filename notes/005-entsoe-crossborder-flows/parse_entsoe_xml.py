#!/usr/bin/env python3
"""
Open Market Note #005 — Real ENTSO-E Telemetry & Capacity Parser
Parses A11 (Physical Flow) and A09 (Final Transfer Capacity) XML files into DataFrames.
"""

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

NOTE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTE_DIR, "data")
RAW_FLOW_DIR = os.path.join(DATA_DIR, "raw_xml_flow")
RAW_CAP_DIR = os.path.join(DATA_DIR, "raw_xml_capacity")

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

def parse_all_data():
    flow_files = glob.glob(os.path.join(RAW_FLOW_DIR, "*.xml"))
    cap_files = glob.glob(os.path.join(RAW_CAP_DIR, "*.xml"))
    
    print(f"[PARSER] Found {len(flow_files)} flow XMLs and {len(cap_files)} capacity XMLs.")
    
    # Parse Flows
    f_list = [parse_xml_payload(f, "flow_mw") for f in flow_files]
    flow_df = pd.concat([df for df in f_list if not df.empty], ignore_index=True) if f_list else pd.DataFrame()
    
    # Parse Capacities
    c_list = [parse_xml_payload(f, "capacity_mw") for f in cap_files]
    cap_df = pd.concat([df for df in c_list if not df.empty], ignore_index=True) if c_list else pd.DataFrame()
    
    return flow_df, cap_df

if __name__ == "__main__":
    fdf, cdf = parse_all_data()
    print(f"Flows parsed: {len(fdf)} rows | Capacities parsed: {len(cdf)} rows")
