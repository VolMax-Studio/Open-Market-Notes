#!/usr/bin/env python3
import copy
import json
import hashlib
import os
import sys
import tempfile
import shutil
import subprocess
import pandas as pd
from gate_verify import verify_gate, GateVerificationError, canonical_digest, parse_params_file

def build_coherent_telemetry_forgery():
    """
    Constructs a 100% coherent telemetry forgery (Coherent S-9):
    1. Modifies raw telemetry feather files (injecting extreme scarcity prices).
    2. Executes the frozen run_window.py script over the modified telemetry to derive true metrics.
    3. Populates VERDICT.json with the exact derived metrics and rationale.
    4. Recomputes MANIFEST.json hashes and inputs_manifest_sha256.
    5. Re-signs the envelope canonical integrity_digest.
    """
    base_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1'
    v_path = os.path.join(base_dir, 'runs/2026-07/VERDICT.json')
    inputs_dir = os.path.join(base_dir, 'inputs')
    script_path = os.path.join(base_dir, 'src/run_window.py')
    params_path = os.path.join(base_dir, 'PARAMS.md')

    temp_root = tempfile.mkdtemp(prefix="coherent_forgery_")
    
    try:
        # Step 1: Copy clean instance structure to temp workspace
        forge_inputs = os.path.join(temp_root, "inputs")
        forge_src = os.path.join(temp_root, "src")
        os.makedirs(forge_inputs, exist_ok=True)
        os.makedirs(forge_src, exist_ok=True)
        
        shutil.copy(script_path, os.path.join(forge_src, "run_window.py"))
        shutil.copy(params_path, os.path.join(temp_root, "PARAMS.md"))
        for f in os.listdir(inputs_dir):
            shutil.copy(os.path.join(inputs_dir, f), os.path.join(forge_inputs, f))

        # Step 2: Inject simulated market scarcity into NSW1 for July 2026 window
        nsw1_path = os.path.join(forge_inputs, "nem_NSW1.feather")
        df = pd.read_feather(nsw1_path)
        # Set prices above threshold for July intervals
        mask_jul = (df['SETTLEMENTDATE'] >= '2026-07-01') & (df['SETTLEMENTDATE'] <= '2026-07-31 14:00:00')
        df.loc[mask_jul, 'RRP'] = 14500.00
        df.to_feather(nsw1_path)

        # Step 3: Run execution over the modified inputs to generate ground-truth output
        cmd = [sys.executable, os.path.join(forge_src, "run_window.py"), "--window", "2026-07", "--instance", temp_root]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Run window failed: {res.stderr}")

        with open(os.path.join(temp_root, "runs/2026-07/result.json")) as f:
            true_run_result = json.load(f)
        with open(os.path.join(temp_root, "runs/2026-07/completeness.json")) as f:
            true_comp_result = json.load(f)

        # Step 4: Recompute MANIFEST.json
        manifest_data = {"files": []}
        for fn in sorted(os.listdir(forge_inputs)):
            if fn.endswith('.feather'):
                sha = hashlib.sha256(open(os.path.join(forge_inputs, fn), 'rb').read()).hexdigest()
                manifest_data["files"].append({"filename": fn, "sha256": sha})
        
        manifest_path = os.path.join(forge_inputs, "MANIFEST.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=2)
        manifest_sha = hashlib.sha256(open(manifest_path, 'rb').read()).hexdigest()

        # Step 5: Construct 100% Coherent VERDICT.json
        with open(v_path) as f:
            forged_v = json.load(f)

        forged_v["reproducibility"]["inputs_manifest_sha256"] = manifest_sha
        nsw1_comp = true_comp_result["zone_completeness"]["NSW1"]
        forged_v["evidence_boundary"]["received_intervals"] = nsw1_comp["admitted_intervals"]
        forged_v["evidence_boundary"]["completeness_pct"] = nsw1_comp["completeness_pct"]
        forged_v["evidence_boundary"]["missing_intervals_tail"] = nsw1_comp["missing_intervals"]
        
        # Populate execution & metrics exactly as produced by cold runner
        forged_v["execution_and_metrics"]["N_elevated"] = true_run_result["N_elevated_comparison_zones"]
        forged_v["execution_and_metrics"]["zone_metrics"] = {}
        for z, zm in true_run_result["zone_metrics"].items():
            forged_v["execution_and_metrics"]["zone_metrics"][z] = {
                "m1_pct": zm["M1_pct"],
                "status": zm["determinacy"],
                "exposure_lower_pct": zm["exposure_lower_pct"],
                "exposure_upper_pct": zm["exposure_upper_pct"]
            }

        forged_v["verdict"]["evaluation_status"] = true_run_result["evaluation_status"]
        forged_v["verdict"]["label"] = true_run_result["label"]
        forged_v["verdict"]["rationale"] = f"Completeness >= 98.0% and N_elevated ({true_run_result['N_elevated_comparison_zones']}) >= n_low (1)"

        # Re-sign digest
        copy_v = {k: val for k, val in forged_v.items() if k != 'integrity_digest'}
        canonical_str = json.dumps(copy_v, sort_keys=True, indent=2)
        forged_v["integrity_digest"] = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

        forged_v_file = os.path.join(temp_root, "COHERENT_FORGED_VERDICT.json")
        with open(forged_v_file, "w") as f:
            json.dump(forged_v, f, indent=2)

        print("=== RUNNING ZERO-TRUST GATE OVER COHERENT TELEMETRY FORGERY (COHERENT S-9) ===")
        print(f"Candidate Verdict: {forged_v_file}")
        print(f"Forged Verdict Label: {forged_v['verdict']['label']} (N_elevated: {forged_v['execution_and_metrics']['N_elevated']})")
        print(f"NSW1 M1 Pct: {forged_v['execution_and_metrics']['zone_metrics']['NSW1']['m1_pct']:.4f}%")
        print(f"Integrity Digest: {forged_v['integrity_digest']}\n")

        # Execute gate_verify over the coherent forgery
        verify_gate(forged_v_file, forge_inputs, os.path.join(forge_src, "run_window.py"), params_path=os.path.join(temp_root, "PARAMS.md"))

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

if __name__ == "__main__":
    build_coherent_telemetry_forgery()
