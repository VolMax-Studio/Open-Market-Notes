#!/usr/bin/env python3
import os
import sys
import json
import argparse
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime, timezone

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def evaluate_eclipse_probe(instance_dir):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")

    with open(params_path) as f:
        content = f.read()
        json_str = content[content.find('{'):content.rfind('}')+1]
        params = json.loads(json_str)

    q_ref = float(params.get('q_ref', 0.90))
    s_thresh_pct = float(params.get('s_thresh_pct', 15.0))
    comp_zones = params.get('comparison_zones', ["ES", "PT", "FR", "DE_LU", "NL"])

    event_win = params.get('event_utc_window', {})
    control_wins = params.get('control_utc_windows', [])

    print(f"========================================================================")
    print(f"  PRE-REGISTERED SOLAR ECLIPSE PROBE EVALUATOR ({params.get('instance_id')})")
    print(f"========================================================================")
    print(f"Event Window   : {event_win.get('start')} to {event_win.get('end')} ({event_win.get('duration_minutes')} min)")
    print(f"Control Days   : {len(control_wins)} baseline control windows (2026-08-05 to 2026-08-11)")
    print(f"Target Zones   : {', '.join(comp_zones)}")
    print(f"Quantile / S   : q = {q_ref:.2f} | S_thresh = {s_thresh_pct:.1f}%")
    print(f"========================================================================\n")

    # Script structure ready for telemetry execution following data fetch
    print("Instance parameters successfully loaded and verified.")
    print("Ready for data fetch execution.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate Pre-Registered Eclipse Probe")
    parser.add_argument('--instance', type=str, default='/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/entsoe-eclipse-exp-20260812', help='Instance directory')
    args = parser.parse_args()

    evaluate_eclipse_probe(args.instance)
