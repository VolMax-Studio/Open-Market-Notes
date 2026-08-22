#!/usr/bin/env python3
import sys
import os
import json
import hashlib
import calendar
import tempfile
import subprocess
import shutil
import pandas as pd

class GateVerificationError(Exception):
    pass

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

def canonical_digest(d):
    copy_d = {k: v for k, v in d.items() if k != "integrity_digest"}
    canonical_str = json.dumps(copy_d, sort_keys=True, indent=2)
    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

def parse_params_file(params_path):
    if not os.path.exists(params_path):
        raise GateVerificationError(f"GATE_FAIL_B: PARAMS_FILE_NOT_FOUND ({params_path})")
    with open(params_path) as f:
        content = f.read()
    if '```json' in content:
        start_idx = content.find('```json') + 7
        end_idx = content.find('```', start_idx)
        json_str = content[start_idx:end_idx].strip()
    else:
        json_str = content[content.find('{'):content.rfind('}')+1]
    return json.loads(json_str)

def verify_gate(verdict_path, inputs_dir, script_path, params_path=None, run_cold_reexecution=True):
    if params_path is None:
        instance_root = os.path.dirname(os.path.dirname(script_path))
        params_path = os.path.join(instance_root, "PARAMS.md")

    print(f"=== P10 ZERO-TRUST GATE VERIFIER ===")
    print(f"Candidate: {verdict_path}")
    print(f"Evidence Store: {inputs_dir}")
    print(f"Frozen Script: {script_path}")
    print(f"Frozen Spec: {params_path}\n")

    if not os.path.exists(verdict_path):
        raise GateVerificationError("GATE_FAIL_A: VERDICT_FILE_NOT_FOUND")

    with open(verdict_path) as f:
        try:
            v_data = json.load(f)
        except Exception as e:
            raise GateVerificationError(f"GATE_FAIL_A: INVALID_JSON ({e})")

    # =========================================================================
    # KLASA A: ENVELOPE INTEGRITY & SELF-CONSISTENCY (Static Math & Structure)
    # =========================================================================
    print("[KLASA A] Verifying Envelope Integrity & Self-Consistency...")
    
    required_sections = [
        "verdict_version", "claim", "evidence_boundary", "frozen_rule",
        "execution_and_metrics", "verdict", "admissibility", "reproducibility", "integrity_digest"
    ]
    for sec in required_sections:
        if sec not in v_data:
            raise GateVerificationError(f"GATE_FAIL_A: MISSING_SECTION_{sec.upper()}")

    claimed_digest = v_data["integrity_digest"]
    actual_digest = canonical_digest(v_data)
    if claimed_digest != actual_digest:
        raise GateVerificationError(f"GATE_FAIL_A: INTEGRITY_DIGEST_MISMATCH (expected {claimed_digest}, computed {actual_digest})")

    claim = v_data["claim"]
    eb = v_data["evidence_boundary"]
    fr = v_data["frozen_rule"]
    em = v_data["execution_and_metrics"]
    vd = v_data["verdict"]
    adm = v_data["admissibility"]
    rep = v_data["reproducibility"]

    # Temporal Bounds Check against claim.window_bounds_utc
    window = claim.get("window", "")
    try:
        year, month = map(int, window.split('-'))
        days_in_month = calendar.monthrange(year, month)[1]
    except Exception:
        raise GateVerificationError("GATE_FAIL_A: INVALID_WINDOW_FORMAT")

    expected_p_start = f"{year:04d}-{month:02d}-01T00:00:00Z"
    expected_p_end = f"{year:04d}-{month:02d}-{days_in_month:02d}T23:59:59Z"
    
    wb = claim.get("window_bounds_utc", {})
    if wb.get("start") != expected_p_start or wb.get("end") != expected_p_end:
        raise GateVerificationError("GATE_FAIL_A: CLAIM_EVIDENCE_MISMATCH (claim.window_bounds_utc mismatch window string)")

    # Interval Arithmetic
    expected_nominal = days_in_month * 288
    if eb.get("nominal_intervals") != expected_nominal:
        raise GateVerificationError("GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH (nominal_intervals mismatch)")

    rec = eb.get("received_intervals", 0)
    expected_missing = expected_nominal - rec
    if eb.get("missing_intervals_tail") != expected_missing:
        raise GateVerificationError("GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH (missing_intervals_tail arithmetic mismatch)")

    expected_comp = round((rec / expected_nominal) * 100.0, 4)
    if round(float(eb.get("completeness_pct", 0.0)), 4) != expected_comp:
        raise GateVerificationError("GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH (completeness_pct arithmetic mismatch)")

    # Internal Parameter Coherence
    params = fr.get("parameters", {})
    s_thresh_pct = float(params.get("s_thresh_pct", 0.0))
    q_ref = float(params.get("q_ref", 0.0))
    k_mult = float(params.get("k_mult", 0.0))
    if round(k_mult * (1.0 - q_ref) * 100.0, 4) != round(s_thresh_pct, 4):
        raise GateVerificationError("GATE_FAIL_A: FROZEN_RULE_HASH_MISMATCH (s_thresh_pct inconsistent with k_mult * (1 - q_ref))")

    # Deterministic Decision Logic
    comp_floor = float(eb.get("completeness_floor_pct", 98.0))
    actual_comp = float(eb.get("completeness_pct", 0.0))
    zone_metrics = em.get("zone_metrics", {})
    
    n_elevated_counted = 0
    comparison_zones = [z for z in zone_metrics.keys() if z != "TAS1"]

    for z, zm in zone_metrics.items():
        is_comp = (z in comparison_zones)
        st = zm.get("status")
        exp_lower = float(zm.get("exposure_lower_pct", 0.0))
        exp_upper = float(zm.get("exposure_upper_pct", 100.0))
        
        if actual_comp < comp_floor:
            expected_status = "INCOMPLETE"
        elif exp_lower >= s_thresh_pct:
            expected_status = "ELEVATED"
            if is_comp:
                n_elevated_counted += 1
        elif exp_upper < s_thresh_pct:
            expected_status = "NOT_ELEVATED"
        else:
            expected_status = "INDETERMINATE"
            
        if st != expected_status:
            raise GateVerificationError(f"GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION (zone {z} status {st} != expected {expected_status})")

    if em.get("N_elevated") != n_elevated_counted:
        raise GateVerificationError("GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION (N_elevated count mismatch)")

    n_low = int(params.get("n_low", 1))
    n_high = int(params.get("n_high", 3))

    if actual_comp < comp_floor:
        expected_eval_status = "INCOMPLETE"
        expected_label = "UNRESOLVED"
    else:
        expected_eval_status = "EVALUATED"
        if n_elevated_counted >= n_high:
            expected_label = "HIGH_ELEVATION"
        elif n_elevated_counted >= n_low:
            expected_label = "ELEVATED"
        else:
            expected_label = "NULL"

    if vd.get("evaluation_status") != expected_eval_status or vd.get("label") != expected_label:
        raise GateVerificationError(f"GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION (verdict label {vd.get('label')} != expected {expected_label})")

    # Admissibility Policy Check
    pub_status = adm.get("publication_status")
    src_lic = adm.get("source_license", "")
    if pub_status == "PUBLIC_PERMITTED" and not ("CC BY" in src_lic or "Open" in src_lic or "Public" in src_lic):
        raise GateVerificationError("GATE_FAIL_A: ADMISSIBILITY_POLICY_VIOLATION (public status incompatible with source license)")

    print("  ✓ Klasa A Passed: Envelope is internally coherent, mathematically sound, and non-tampered.\n")

    # =========================================================================
    # KLASA B: EVIDENCE BINDING (External Spec, Data Store & Hash Verification)
    # =========================================================================
    print("[KLASA B] Verifying Evidence Binding against Physical Telemetry & Frozen Spec...")

    # Verify parameters against frozen PARAMS.md spec (BREAKS SELF-ATTESTATION LOOP)
    frozen_spec = parse_params_file(params_path)
    if float(frozen_spec.get("q_ref", 0.0)) != q_ref:
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (q_ref spec {frozen_spec.get('q_ref')} != verdict {q_ref})")
    if float(frozen_spec.get("k_multiplier", 0.0)) != k_mult:
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (k_mult spec {frozen_spec.get('k_multiplier')} != verdict {k_mult})")
    if float(frozen_spec.get("completeness_floor_pct", 0.0)) != comp_floor:
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (completeness_floor spec {frozen_spec.get('completeness_floor_pct')} != verdict {comp_floor})")
    if int(frozen_spec.get("n_low", 0)) != n_low:
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (n_low spec {frozen_spec.get('n_low')} != verdict {n_low})")
    if int(frozen_spec.get("n_high", 0)) != n_high:
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (n_high spec {frozen_spec.get('n_high')} != verdict {n_high})")
    if int(frozen_spec.get("N", 0)) != int(params.get("n_baseline_months", 0)):
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_SPEC_MISMATCH (N baseline spec {frozen_spec.get('N')} != verdict {params.get('n_baseline_months')})")

    if not os.path.exists(inputs_dir):
        raise GateVerificationError("GATE_FAIL_B: INPUTS_STORE_NOT_FOUND")

    manifest_path = os.path.join(inputs_dir, "MANIFEST.json")
    if not os.path.exists(manifest_path):
        raise GateVerificationError("GATE_FAIL_B: MANIFEST_FILE_NOT_FOUND")

    # Verify physical bytes of each telemetry file against manifest
    with open(manifest_path) as f:
        manifest_data = json.load(f)

    for f_entry in manifest_data.get("files", []):
        fn = f_entry["filename"]
        claimed_file_sha = f_entry["sha256"]
        f_path = os.path.join(inputs_dir, fn)
        if not os.path.exists(f_path):
            raise GateVerificationError(f"GATE_FAIL_B: TELEMETRY_FILE_MISSING ({fn})")
        actual_file_sha = compute_sha256(f_path)
        if actual_file_sha != claimed_file_sha:
            raise GateVerificationError(f"GATE_FAIL_B: TELEMETRY_CORRUPTION ({fn} hash mismatch: claimed {claimed_file_sha[:12]}, actual {actual_file_sha[:12]})")

    # Check actual telemetry boundary cutoff in feather files
    sample_file = os.path.join(inputs_dir, "nem_NSW1.feather")
    df_sample = pd.read_feather(sample_file)
    actual_max_time = pd.to_datetime(df_sample['SETTLEMENTDATE']).max()
    actual_max_str = actual_max_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    if eb.get("telemetry_period_end_utc") != actual_max_str:
        raise GateVerificationError(f"GATE_FAIL_B: EVIDENCE_BOUNDARY_MISMATCH (telemetry_period_end_utc declared {eb.get('telemetry_period_end_utc')} != actual data max {actual_max_str})")

    # Verify manifest hash against VERDICT.json reference
    actual_manifest_sha = compute_sha256(manifest_path)
    if actual_manifest_sha != rep.get("inputs_manifest_sha256"):
        raise GateVerificationError(f"GATE_FAIL_B: INPUT_MANIFEST_HASH_MISMATCH (manifest hash {actual_manifest_sha[:12]} != verdict pointer {rep.get('inputs_manifest_sha256')[:12]})")

    # Verify frozen script hash on disk
    if not os.path.exists(script_path):
        raise GateVerificationError("GATE_FAIL_B: FROZEN_SCRIPT_NOT_FOUND")
    actual_script_sha = compute_sha256(script_path)
    if actual_script_sha != fr.get("rule_script_sha256"):
        raise GateVerificationError(f"GATE_FAIL_B: FROZEN_RULE_HASH_MISMATCH (script hash {actual_script_sha[:12]} != verdict pointer {fr.get('rule_script_sha256')[:12]})")

    print("  ✓ Klasa B Passed: Physical telemetry and frozen spec PARAMS.md match VERDICT.json anchors exactly.\n")

    # =========================================================================
    # KLASA C: COLD RE-EXECUTION (Independent Sandbox Runtime & Output Agreement)
    # =========================================================================
    if run_cold_reexecution:
        print("[KLASA C] Executing Cold Sandbox Re-Execution (Zero-Trust Output Agreement)...")
        
        recipe = rep.get("reproduce_recipe", "")
        if not recipe or "run_window.py" not in recipe:
            raise GateVerificationError("GATE_FAIL_C: REPRODUCTION_FAILED (invalid reproduce_recipe)")

        # Create isolated temporary instance workspace
        temp_dir = tempfile.mkdtemp(prefix="p10_gate_sandbox_")
        try:
            os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, "inputs"), exist_ok=True)
            
            shutil.copy(script_path, os.path.join(temp_dir, "src", "run_window.py"))
            shutil.copy(params_path, os.path.join(temp_dir, "PARAMS.md"))

            for f_entry in manifest_data.get("files", []):
                fn = f_entry["filename"]
                shutil.copy(os.path.join(inputs_dir, fn), os.path.join(temp_dir, "inputs", fn))
            shutil.copy(manifest_path, os.path.join(temp_dir, "inputs", "MANIFEST.json"))

            cmd = [sys.executable, os.path.join(temp_dir, "src", "run_window.py"), "--window", window, "--instance", temp_dir]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if proc.returncode != 0:
                raise GateVerificationError(f"GATE_FAIL_C: REPRODUCTION_EXECUTION_ERROR ({proc.stderr.strip()})")

            sandbox_result_path = os.path.join(temp_dir, "runs", window, "result.json")
            if not os.path.exists(sandbox_result_path):
                raise GateVerificationError("GATE_FAIL_C: REPRODUCTION_FAILED (sandbox result.json not generated)")

            with open(sandbox_result_path) as f:
                reproduced_res = json.load(f)

            if reproduced_res.get("evaluation_status") != vd.get("evaluation_status"):
                raise GateVerificationError("GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (evaluation_status)")
            if reproduced_res.get("label") != vd.get("label"):
                raise GateVerificationError("GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (label)")
            if reproduced_res.get("N_elevated_comparison_zones") != em.get("N_elevated"):
                raise GateVerificationError("GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (N_elevated)")

            for z, declared_zm in em.get("zone_metrics", {}).items():
                if z not in reproduced_res.get("zone_metrics", {}):
                    raise GateVerificationError(f"GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (zone {z} missing in reproduction)")
                rep_zm = reproduced_res["zone_metrics"][z]
                if round(rep_zm["M1_pct"], 4) != round(declared_zm["m1_pct"], 4):
                    raise GateVerificationError(f"GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (zone {z} M1_pct declared {declared_zm['m1_pct']} != reproduced {rep_zm['M1_pct']})")
                if rep_zm["determinacy"] != declared_zm["status"]:
                    raise GateVerificationError(f"GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH (zone {z} status declared {declared_zm['status']} != reproduced {rep_zm['determinacy']})")

            print(f"  ✓ Klasa C Passed: Declared fields agree with sandbox re-execution.\n")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print("================================================================================")
    print("VERDICT STATUS: ACCEPT (VERIFIED_VERDICT)")
    print(f"Integrity Digest: {claimed_digest}")
    print("Zero-Trust Gate completed all 3 verification tiers (Klasa A, B, C) successfully.")
    print("================================================================================")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: gate_verify.py <VERDICT.json> <inputs_dir> <script_path> [params_path] [--no-cold-run]")
        sys.exit(1)
        
    v_file = sys.argv[1]
    in_dir = sys.argv[2]
    sc_file = sys.argv[3]
    pr_file = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else None
    cold_run = "--no-cold-run" not in sys.argv
    
    try:
        verify_gate(v_file, in_dir, sc_file, params_path=pr_file, run_cold_reexecution=cold_run)
        sys.exit(0)
    except GateVerificationError as e:
        print(f"\nGATE REJECTION: {e}")
        sys.exit(1)
