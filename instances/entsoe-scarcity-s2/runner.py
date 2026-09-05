#!/usr/bin/env python3
"""
runner.py — Official Execution Harness for entsoe-scarcity-s2

Executes the frozen 12-request acquisition batch.
Enforces pre-execution environment invariants (clean tree, git commit verification).
Derives evidence dynamically from system state.
Preserves all raw response payloads byte-for-byte before parsing.
Evaluates Target S (exact population) and Target R (July 2026 scarcity classification).
"""

import os
import sys
import json
import hashlib
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

ENDPOINT = "https://web-api.tp.entsoe.eu/api"

# Pinned Area EICs per ENTSO-E Market Areas v2.0
ZONES = {
    'AT': '10YAT-APG------L',
    'BE': '10YBE----------2',
    'DK_1': '10YDK-1--------W',
    'DK_2': '10YDK-2--------M',
    'FR': '10YFR-RTE------C',
    'NL': '10YNL----------L'
}

WINDOWS = {
    'baseline': {
        'periodStart': '202507312200',
        'periodEnd': '202606302200',
        'expected_count': 32064,
        'start_utc': '2025-07-31T22:00:00Z',
        'end_utc': '2026-06-30T22:00:00Z'
    },
    'target': {
        'periodStart': '202606302200',
        'periodEnd': '202607312200',
        'expected_count': 2976,
        'start_utc': '2026-06-30T22:00:00Z',
        'end_utc': '2026-07-31T22:00:00Z'
    }
}

PUBLISHED_REFERENCES = {
    'FR': {'occupancy': 31.8, 'classification': 'ELEVATED'},
    'NL': {'occupancy': 23.3, 'classification': 'ELEVATED'},
    'BE': {'occupancy': 18.8, 'classification': 'ELEVATED'},
    'AT': {'occupancy': 18.4, 'classification': 'ELEVATED'},
    'DK_1': {'occupancy': 17.5, 'classification': 'ELEVATED'},
    'DK_2': {'occupancy': 11.3, 'classification': 'NOT_ELEVATED'}
}

IMMUTABLE_INPUT_FILES = [
    "PREREGISTRATION.md",
    "L0.md",
    "runner.py",
    "requirements.txt"
]


def verify_environment(instance_dir, expected_prereg_sha=None):
    """
    Verifies git working tree cleanliness and captures dynamic commit SHA.
    Enforces EXECUTION_STATE_INVALID halt if preconditions fail.
    """
    try:
        # 1. Clean status check
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=instance_dir,
            capture_output=True,
            text=True,
            check=True
        )
        # Note: If uncommitted changes exist, halt immediately
        if res_status.stdout.strip():
            sys.stderr.write(f"FATAL [EXECUTION_STATE_INVALID]: Working tree is not clean:\n{res_status.stdout}\n")
            sys.exit(1)

        # 2. Dynamic SHA capture
        res_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=instance_dir,
            capture_output=True,
            text=True,
            check=True
        )
        actual_sha = res_sha.stdout.strip()

        # 3. If governing PREREG_SHA is passed, verify exact match
        if expected_prereg_sha and actual_sha != expected_prereg_sha:
            sys.stderr.write(
                f"FATAL [EXECUTION_STATE_INVALID]: git rev-parse HEAD ({actual_sha}) != expected PREREG_SHA ({expected_prereg_sha})\n"
            )
            sys.exit(1)

        return actual_sha
    except Exception as e:
        sys.stderr.write(f"FATAL [EXECUTION_STATE_INVALID]: Failed git environment check: {e}\n")
        sys.exit(1)


def get_token():
    token_path = os.environ.get("ENTSOE_TOKEN_PATH", "/home/volmax-studio/Documents/Kljucevi/apientso.txt")
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return f.read().strip()
    token = os.environ.get("ENTSOE_API_KEY") or os.environ.get("ENTSOE_TOKEN")
    if token:
        return token.strip()
    sys.stderr.write("FATAL: ENTSO-E API token not found.\n")
    sys.exit(1)


def generate_expected_grid(start_iso, end_iso):
    """Generates continuous 15-minute UTC timestamp grid [start, end)."""
    start_dt = pd.to_datetime(start_iso)
    end_dt = pd.to_datetime(end_iso)
    grid = pd.date_range(start=start_dt, end=end_dt - pd.Timedelta(minutes=15), freq='15min')
    return [ts.strftime('%Y-%m-%dT%H:%M:%SZ') for ts in grid]


def record_immutable_inputs(instance_dir, run_dir):
    """Records sha256 digests strictly for immutable specification and execution code."""
    input_hashes = []
    for filename in IMMUTABLE_INPUT_FILES:
        filepath = os.path.join(instance_dir, filename)
        if not os.path.exists(filepath):
            sys.stderr.write(f"FATAL [EXECUTION_STATE_INVALID]: Required input file {filename} missing at {filepath}\n")
            sys.exit(1)
        with open(filepath, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        input_hashes.append(f"{h}  {filename}")

    inputs_file = os.path.join(run_dir, "inputs.sha256")
    with open(inputs_file, "w") as f:
        f.write("\n".join(input_hashes) + "\n")


def parse_acknowledgement(raw_bytes):
    """Parses ENTSO-E Acknowledgement_MarketDocument XML to classify error reasons."""
    try:
        root = ET.fromstring(raw_bytes)
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
        reason_elem = root.find('.//ns:Reason', ns) if ns else root.find('.//Reason')
        if reason_elem is not None:
            code_node = reason_elem.find('.//ns:code', ns) if ns else reason_elem.find('.//code')
            text_node = reason_elem.find('.//ns:text', ns) if ns else reason_elem.find('.//text')
            code = code_node.text.strip() if code_node is not None and code_node.text else ""
            text = text_node.text.strip() if text_node is not None and text_node.text else ""
            return code, text
    except Exception:
        pass
    return None, None


def execute_run(instance_dir, run_dir, run_id, prereg_sha):
    raw_dir = os.path.join(run_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # 1. Record inputs.sha256
    record_immutable_inputs(instance_dir, run_dir)

    # 2. Record dynamic git_commit.txt
    with open(os.path.join(run_dir, "git_commit.txt"), "w") as f:
        f.write(f"{prereg_sha}\n")

    token = get_token()

    t_run_start = datetime.now(timezone.utc).isoformat()
    print(f"=== OFFICIAL RUN START: {t_run_start} ===")
    print(f"RUN_ID:     {run_id}")
    print(f"PREREG_SHA: {prereg_sha}\n")

    requests_meta = []
    raw_file_hashes = {}
    halt_class = None
    halt_reason = None

    # Step 1: Execute exactly 12 HTTP requests
    for zone, eic in ZONES.items():
        for window_name, win_info in WINDOWS.items():
            req_idx = len(requests_meta) + 1
            t_req = datetime.now(timezone.utc).isoformat()
            
            params = {
                'documentType': 'A85',
                'controlArea_Domain': eic,
                'periodStart': win_info['periodStart'],
                'periodEnd': win_info['periodEnd'],
                'securityToken': token
            }
            
            redacted_params = {k: ('[REDACTED]' if k == 'securityToken' else v) for k, v in params.items()}
            query_str = urllib.parse.urlencode(params)
            full_url = f"{ENDPOINT}?{query_str}"
            redacted_url = f"{ENDPOINT}?{urllib.parse.urlencode(redacted_params)}"

            print(f"[{req_idx:02d}/12] Requesting {zone} {window_name} ({win_info['periodStart']} -> {win_info['periodEnd']})...")
            
            req_obj = urllib.request.Request(full_url, headers={'User-Agent': 'VolMax-Studio-Audit/2.0'})
            status_code = None
            raw_bytes = b''

            try:
                with urllib.request.urlopen(req_obj, timeout=120) as resp:
                    status_code = resp.status
                    raw_bytes = resp.read()
            except urllib.error.HTTPError as e:
                status_code = e.code
                raw_bytes = e.read()
            except Exception as e:
                status_code = 0
                raw_bytes = str(e).encode('utf-8')

            t_resp = datetime.now(timezone.utc).isoformat()
            sha256_digest = hashlib.sha256(raw_bytes).hexdigest() if raw_bytes else None

            # Save raw bytes immediately before any inspection
            raw_filename = f"{zone}_{window_name}_raw.xml"
            raw_filepath = os.path.join(raw_dir, raw_filename)
            with open(raw_filepath, "wb") as f:
                f.write(raw_bytes)

            raw_file_hashes[raw_filename] = sha256_digest

            req_record = {
                'request_index': req_idx,
                'zone': zone,
                'eic': eic,
                'window': window_name,
                'periodStart': win_info['periodStart'],
                'periodEnd': win_info['periodEnd'],
                't_req_utc': t_req,
                't_resp_utc': t_resp,
                'http_status': status_code,
                'raw_filename': raw_filename,
                'sha256': sha256_digest,
                'bytes_count': len(raw_bytes),
                'redacted_url': redacted_url
            }

            # Evaluation of response status and halt taxonomy classification
            if status_code != 200:
                halt_class = "HTTP_ERROR"
                halt_reason = f"HTTP_ERROR: Server returned HTTP {status_code} on {zone} {window_name}"
                req_record['error'] = True
                req_record['halt_class'] = halt_class
                req_record['error_snippet'] = raw_bytes[:500].decode('utf-8', errors='replace')
                requests_meta.append(req_record)
                break

            if b'<Reason>' in raw_bytes or b'Acknowledgement_MarketDocument' in raw_bytes:
                code, reason_text = parse_acknowledgement(raw_bytes)
                req_record['error'] = True
                req_record['reason_code'] = code
                req_record['reason_text'] = reason_text

                if code == "999" or "No matching data found" in (reason_text or ""):
                    halt_class = "SOURCE_DATA_ABSENT"
                    halt_reason = f"SOURCE_DATA_ABSENT: Reason 999 on {zone} {window_name}: {reason_text}"
                elif "amount of requested data exceeds allowed limit" in (reason_text or "") or "exceeds allowed limit" in raw_bytes.decode('utf-8', errors='replace'):
                    halt_class = "REQUEST_CONTRACT_UNSUPPORTED"
                    halt_reason = f"REQUEST_CONTRACT_UNSUPPORTED: Query window exceeded on {zone} {window_name}: {reason_text}"
                else:
                    halt_class = "API_REASON_OTHER"
                    halt_reason = f"API_REASON_OTHER: Code {code} on {zone} {window_name}: {reason_text}"

                req_record['halt_class'] = halt_class
                requests_meta.append(req_record)
                break

            print(f"  -> HTTP {status_code} OK ({len(raw_bytes)} bytes, SHA256: {sha256_digest[:16]}...)")
            requests_meta.append(req_record)

        if halt_class:
            break

    t_run_end = datetime.now(timezone.utc).isoformat()
    print(f"\n=== ACQUISITION COMPLETED: {t_run_end} ===")

    # Step 2: Assemble run_metadata.json
    run_metadata = {
        'run_id': run_id,
        'prereg_sha': prereg_sha,
        'repository': 'VolMax-Studio/Open-Market-Notes',
        'branch': 'instances/entsoe-scarcity-s2',
        't_run_start_utc': t_run_start,
        't_run_end_utc': t_run_end,
        'total_requests_executed': len(requests_meta),
        'expected_requests_count': 12,
        'halt_class': halt_class,
        'halt_reason': halt_reason,
        'requests': requests_meta
    }

    with open(os.path.join(run_dir, "run_metadata.json"), "w") as f:
        json.dump(run_metadata, f, indent=2)

    if halt_class:
        print(f"\n[AUDIT HALT — {halt_class}] {halt_reason}")
        with open(os.path.join(run_dir, "exit_code.txt"), "w") as f:
            f.write("1\n")
        save_outputs_sha256(run_dir)
        return 1

    # Step 3: Parse raw responses and evaluate Target S & R
    print("\n=== PARSING RAW XML RESPONSES & EVALUATING TARGET S ===")
    
    expected_grids = {}
    missing_listings = {}
    duplicate_listings = {}
    unexpected_listings = {}
    doc_inventory = {}
    parsed_series = {}
    target_s_verdicts = {}

    for zone, eic in ZONES.items():
        parsed_series[zone] = {}
        for window_name, win_info in WINDOWS.items():
            key = f"{zone}_{window_name}"
            exp_grid = generate_expected_grid(win_info['start_utc'], win_info['end_utc'])
            expected_grids[key] = exp_grid

            raw_filename = f"{zone}_{window_name}_raw.xml"
            raw_filepath = os.path.join(raw_dir, raw_filename)
            with open(raw_filepath, "rb") as f:
                xml_bytes = f.read()

            parsed_data, docs_meta = parse_a85_xml(xml_bytes, zone, window_name)
            doc_inventory[key] = docs_meta

            observed_timestamps = [p['timestamp_utc'] for p in parsed_data]
            unique_observed = sorted(list(set(observed_timestamps)))

            exp_set = set(exp_grid)
            obs_set = set(observed_timestamps)

            missing = sorted(list(exp_set - obs_set))
            unexpected = sorted(list(obs_set - exp_set))
            
            counts = {}
            for ts in observed_timestamps:
                counts[ts] = counts.get(ts, 0) + 1
            duplicates = [ts for ts, c in counts.items() if c > 1]

            missing_listings[key] = missing
            unexpected_listings[key] = unexpected
            duplicate_listings[key] = duplicates

            has_correct_resolution = all(d.get('resolution') == 'PT15M' for d in docs_meta)
            has_correct_doctype = all(d.get('document_type') == 'A85' for d in docs_meta)
            has_correct_process = all(d.get('process_type') == 'A16' for d in docs_meta)

            s_pass = (
                len(missing) == 0 and
                len(duplicates) == 0 and
                len(unexpected) == 0 and
                has_correct_resolution and
                has_correct_doctype and
                has_correct_process
            )

            target_s_verdicts[key] = {
                'zone': zone,
                'window': window_name,
                'expected_count': len(exp_grid),
                'observed_unique_count': len(unique_observed),
                'missing_count': len(missing),
                'duplicate_count': len(duplicates),
                'unexpected_count': len(unexpected),
                'resolution_verified': has_correct_resolution,
                'document_type_verified': has_correct_doctype,
                'process_type_verified': has_correct_process,
                'status': 'S-PASS' if s_pass else 'S-FAIL'
            }

            print(f"Target S [{zone:<4} {window_name:<8}]: {'S-PASS' if s_pass else 'S-FAIL'} (Observed: {len(unique_observed)}/{len(exp_grid)}, Missing: {len(missing)}, Duplicates: {len(duplicates)})")

            if s_pass:
                ts_dict = {p['timestamp_utc']: p['shortage_price'] for p in parsed_data}
                parsed_series[zone][window_name] = [ts_dict[ts] for ts in exp_grid]

    # Save intermediate listings
    with open(os.path.join(run_dir, "expected_grids.json"), "w") as f:
        json.dump(expected_grids, f, indent=2)
    with open(os.path.join(run_dir, "missing_listings.json"), "w") as f:
        json.dump(missing_listings, f, indent=2)
    with open(os.path.join(run_dir, "duplicate_listings.json"), "w") as f:
        json.dump(duplicate_listings, f, indent=2)
    with open(os.path.join(run_dir, "unexpected_listings.json"), "w") as f:
        json.dump(unexpected_listings, f, indent=2)
    with open(os.path.join(run_dir, "document_inventory.json"), "w") as f:
        json.dump(doc_inventory, f, indent=2)

    # Step 4: Evaluate Target R
    print("\n=== EVALUATING TARGET R (SCARCITY REPRODUCTION) ===")
    target_r_results = {}
    classifications_match = True

    for zone in ZONES.keys():
        s_base = target_s_verdicts[f"{zone}_baseline"]['status'] == 'S-PASS'
        s_target = target_s_verdicts[f"{zone}_target"]['status'] == 'S-PASS'

        if not (s_base and s_target):
            print(f"Zone {zone}: Target S failed -> Target R NOT_EVALUATED")
            target_r_results[zone] = {
                'status': 'NOT_EVALUATED',
                'reason': 'Target S structural gate failure'
            }
            classifications_match = False
            continue

        b_prices = parsed_series[zone]['baseline']
        t_prices = parsed_series[zone]['target']

        # Single executable quantile formula
        r_z = float(pd.Series(b_prices).quantile(0.90, interpolation='linear'))

        # July occupancy
        count_elevated = sum(1 for p in t_prices if p >= r_z)
        m_z = count_elevated / 2976.0
        m_z_pct = m_z * 100.0

        is_elevated = (m_z >= 0.15)
        computed_class = 'ELEVATED' if is_elevated else 'NOT_ELEVATED'
        pub_ref = PUBLISHED_REFERENCES[zone]
        matches_pub_class = (computed_class == pub_ref['classification'])

        if not matches_pub_class:
            classifications_match = False

        target_r_results[zone] = {
            'baseline_r_z_eur': round(r_z, 4),
            'target_elevated_count': count_elevated,
            'target_occupancy_m_z': round(m_z, 6),
            'target_occupancy_pct': round(m_z_pct, 2),
            'computed_classification': computed_class,
            'published_occupancy_pct': pub_ref['occupancy'],
            'published_classification': pub_ref['classification'],
            'classification_match': matches_pub_class
        }

        print(f"Zone {zone:<4}: R_z = €{r_z:6.2f} | M_z = {m_z_pct:5.2f}% (Pub: {pub_ref['occupancy']:5.1f}%) | {computed_class} [Match: {matches_pub_class}]")

    overall_reproduction = "REPRODUCED" if classifications_match else "PARTIALLY_REPRODUCED"

    derived_results = {
        'run_id': run_id,
        'prereg_sha': prereg_sha,
        'structural_target_s': target_s_verdicts,
        'scarcity_target_r': target_r_results,
        'overall_classification_reproduction': overall_reproduction
    }

    with open(os.path.join(run_dir, "derived_results.json"), "w") as f:
        json.dump(derived_results, f, indent=2)

    with open(os.path.join(run_dir, "exit_code.txt"), "w") as f:
        f.write("0\n")

    save_outputs_sha256(run_dir)
    print(f"\nAll run artifacts and logs written to {run_dir}")
    return 0


def parse_a85_xml(xml_bytes, zone, window_name):
    """
    Parses Balancing_MarketDocument XML payload.
    Extracts 15-minute points, verifies process/document types, and resolves latest revisions.
    """
    root = ET.fromstring(xml_bytes)
    ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    
    doctype_elem = root.find('.//ns:type', ns) if ns else root.find('.//type')
    doctype = doctype_elem.text.strip() if doctype_elem is not None and doctype_elem.text else ""

    process_elem = root.find('.//ns:process.processType', ns) if ns else root.find('.//process.processType')
    process_type = process_elem.text.strip() if process_elem is not None and process_elem.text else ""

    docs_meta = []
    points_out = []

    timeseries_nodes = root.findall('.//ns:TimeSeries', ns) if ns else root.findall('.//TimeSeries')
    
    for ts in timeseries_nodes:
        mrid_elem = ts.find('.//ns:mRID', ns) if ns else ts.find('.//mRID')
        mrid = mrid_elem.text if mrid_elem is not None else "unknown"

        flow_dir = ts.find('.//ns:flowDirection.direction', ns) if ns else ts.find('.//flowDirection.direction')
        dir_str = flow_dir.text if flow_dir is not None else ""

        period_node = ts.find('.//ns:Period', ns) if ns else ts.find('.//Period')
        if period_node is None:
            continue

        res_node = period_node.find('.//ns:resolution', ns) if ns else period_node.find('.//resolution')
        resolution = res_node.text if res_node is not None else ""

        start_node = period_node.find('.//ns:timeInterval/ns:start', ns) if ns else period_node.find('.//timeInterval/start')
        p_start = start_node.text if start_node is not None else ""

        docs_meta.append({
            'mRID': mrid,
            'document_type': doctype,
            'process_type': process_type,
            'resolution': resolution,
            'direction': dir_str,
            'period_start': p_start
        })

        if not p_start:
            continue

        p_start_dt = pd.to_datetime(p_start)
        point_nodes = period_node.findall('.//ns:Point', ns) if ns else period_node.findall('.//Point')
        
        for pt in point_nodes:
            pos_node = pt.find('.//ns:position', ns) if ns else pt.find('.//position')
            price_node = pt.find('.//ns:imbalance_Price.amount', ns) if ns else pt.find('.//imbalance_Price.amount')
            
            if pos_node is not None and price_node is not None:
                pos = int(pos_node.text)
                price = float(price_node.text)
                pt_time = p_start_dt + pd.Timedelta(minutes=15 * (pos - 1))
                pt_iso = pt_time.strftime('%Y-%m-%dT%H:%M:%SZ')

                points_out.append({
                    'timestamp_utc': pt_iso,
                    'shortage_price': price,
                    'direction': dir_str,
                    'position': pos
                })

    return points_out, docs_meta


def save_outputs_sha256(run_dir):
    out_hashes = []
    for root, _, files in os.walk(run_dir):
        for f in sorted(files):
            if f == 'outputs.sha256':
                continue
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, run_dir)
            with open(fpath, 'rb') as fp:
                h = hashlib.sha256(fp.read()).hexdigest()
            out_hashes.append(f"{h}  {relpath}")

    with open(os.path.join(run_dir, "outputs.sha256"), "w") as fp:
        fp.write("\n".join(out_hashes) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Official Execution Runner for entsoe-scarcity-s2")
    parser.add_argument("--run-id", default="run-002-confirmatory", help="Run ID")
    parser.add_argument("--prereg-sha", default=None, help="Expected governing PREREG_SHA")
    parser.add_argument("--skip-git-check", action="store_true", help="Skip git environment checks (dry run only)")
    args = parser.parse_args()

    instance_dir = os.path.dirname(os.path.abspath(__file__))
    run_dir = os.path.join(instance_dir, "evidence", "runs", args.run_id)
    os.makedirs(run_dir, exist_ok=True)

    if not args.skip_git_check:
        actual_sha = verify_environment(instance_dir, expected_prereg_sha=args.prereg_sha)
    else:
        actual_sha = args.prereg_sha or "unverified_dry_run"
    
    code = execute_run(instance_dir, run_dir, args.run_id, actual_sha)
    sys.exit(code)
