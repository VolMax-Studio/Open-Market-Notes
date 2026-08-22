#!/usr/bin/env python3
import copy
import json
import hashlib
import os
import sys
import tempfile
import shutil
from gate_verify import verify_gate, GateVerificationError, canonical_digest

def run_exhaustive_class2_suite():
    v_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/runs/2026-07/VERDICT.json'
    inputs_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/inputs'
    script_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/src/run_window.py'
    params_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/PARAMS.md'

    with open(v_path) as f:
        base_v = json.load(f)

    def resign(d):
        d["integrity_digest"] = canonical_digest(d)
        return d

    scenarios = []

    # S-1: Zone Metric Tampering (NSW1 M1 4.8360 -> 9.9999, re-signed)
    s1 = copy.deepcopy(base_v)
    s1["execution_and_metrics"]["zone_metrics"]["NSW1"]["m1_pct"] = 9.9999
    resign(s1)
    scenarios.append(("S-1: Zone Metric Tampering", s1, "GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH", inputs_dir, script_path, params_path, True))

    # S-2: Zone Status Inversion (NSW1 status -> ELEVATED, re-signed)
    s2 = copy.deepcopy(base_v)
    s2["execution_and_metrics"]["zone_metrics"]["NSW1"]["status"] = "ELEVATED"
    resign(s2)
    scenarios.append(("S-2: Zone Status Inversion", s2, "GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path, params_path, False))

    # S-3: Deterministic Label Inversion (label -> ELEVATED, re-signed)
    s3 = copy.deepcopy(base_v)
    s3["verdict"]["label"] = "ELEVATED"
    resign(s3)
    scenarios.append(("S-3: Verdict Label Inversion", s3, "GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path, params_path, False))

    # S-4: Coordinated Parameter Drift (q_ref 0.80, s_thresh 30.0%, internally consistent, re-signed)
    s4 = copy.deepcopy(base_v)
    s4["frozen_rule"]["parameters"]["q_ref"] = 0.80
    s4["frozen_rule"]["parameters"]["s_thresh_pct"] = 30.0
    resign(s4)
    scenarios.append(("S-4: Coordinated Parameter Drift", s4, "GATE_FAIL_B: FROZEN_SPEC_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-5: Interval Arithmetic Forgery (received 8900, missing 28, re-signed)
    s5 = copy.deepcopy(base_v)
    s5["evidence_boundary"]["received_intervals"] = 8900
    s5["evidence_boundary"]["missing_intervals_tail"] = 28
    resign(s5)
    scenarios.append(("S-5: Interval Arithmetic Forgery", s5, "GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-6: Temporal Window Drift (window -> 2026-08, re-signed)
    s6 = copy.deepcopy(base_v)
    s6["claim"]["window"] = "2026-08"
    resign(s6)
    scenarios.append(("S-6: Temporal Window Drift", s6, "GATE_FAIL_A: CLAIM_EVIDENCE_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-7: Telemetry Boundary Overclaim (period_end_utc -> 23:59:59Z, re-signed)
    s7 = copy.deepcopy(base_v)
    s7["evidence_boundary"]["telemetry_period_end_utc"] = "2026-07-31T23:59:59Z"
    resign(s7)
    scenarios.append(("S-7: Telemetry Boundary Overclaim", s7, "GATE_FAIL_B: EVIDENCE_BOUNDARY_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-8: Frozen Rule Substitution (Attacker modifies script on disk & in verdict, re-signed)
    # This is a pre-registered structural property test (Demonstrates lack of asymmetric signature)
    scenarios.append(("S-8: Frozen Rule Code Substitution (Pre-registered Leak)", "DYNAMIC_S8", "ACCEPTED_AS_PREDICTED", inputs_dir, "DYNAMIC_SCRIPT", params_path, True))

    # S-9: Closed-Loop Telemetry Mutation (Attacker modifies feather file on disk & manifest & verdict, re-signed)
    # This is a pre-registered structural property test (Demonstrates Nalaz N-1)
    scenarios.append(("S-9: Closed-Loop Telemetry Mutation (Pre-registered Leak)", "DYNAMIC_S9", "ACCEPTED_AS_PREDICTED", "DYNAMIC_INPUTS", script_path, params_path, True))

    print("================================================================================")
    print("EXHAUSTIVE CLASS II ADVERSARIAL SUITE (SCHEMA-AWARE WITH RE-SIGNED DIGESTS)")
    print("================================================================================")

    temp_root = tempfile.mkdtemp(prefix="class2_suite_")
    try:
        for name, v_data, expected_outcome, in_d, sc_p, pr_p, do_cold in scenarios:
            target_v_file = os.path.join(temp_root, "test_verdict.json")
            target_in_d = in_d
            target_sc_p = sc_p

            if v_data == "DYNAMIC_S8":
                # Create a modified run_window.py that forces result
                s8_script = os.path.join(temp_root, "substituted_run_window.py")
                with open(script_path) as f_in:
                    code = f_in.read()
                # Substitute code to produce M1 = 99.9%
                mod_code = code.replace("m1_pct = (n_elevated_intervals / float(rec)) * 100.0", "m1_pct = 99.9000\n        determinacy = 'ELEVATED'")
                with open(s8_script, "w") as f_out:
                    f_out.write(mod_code)
                
                # Recompute rule_script_sha256 and verdict for S8
                s8_v = copy.deepcopy(base_v)
                s8_v["frozen_rule"]["rule_script_sha256"] = hashlib.sha256(mod_code.encode('utf-8')).hexdigest()
                for z in s8_v["execution_and_metrics"]["zone_metrics"]:
                    s8_v["execution_and_metrics"]["zone_metrics"][z]["m1_pct"] = 99.9000
                    s8_v["execution_and_metrics"]["zone_metrics"][z]["status"] = "ELEVATED"
                s8_v["execution_and_metrics"]["N_elevated"] = 4
                s8_v["verdict"]["evaluation_status"] = "EVALUATED"
                s8_v["verdict"]["label"] = "HIGH_ELEVATION"
                resign(s8_v)
                with open(target_v_file, "w") as f:
                    json.dump(s8_v, f, indent=2)
                target_sc_p = s8_script

            elif v_data == "DYNAMIC_S9":
                # Create modified telemetry files & manifest
                s9_dir = os.path.join(temp_root, "substituted_inputs")
                shutil.copytree(inputs_dir, s9_dir)
                # Modify NSW1
                corrupt_file = os.path.join(s9_dir, "nem_NSW1.feather")
                with open(corrupt_file, "r+b") as f:
                    f.seek(100)
                    f.write(b'\xFF\xFF')
                new_nsw1_sha = hashlib.sha256(open(corrupt_file, "rb").read()).hexdigest()
                
                # Recompute MANIFEST.json
                with open(os.path.join(s9_dir, "MANIFEST.json")) as f_m:
                    m_data = json.load(f_m)
                for f_entry in m_data["files"]:
                    if f_entry["filename"] == "nem_NSW1.feather":
                        f_entry["sha256"] = new_nsw1_sha
                with open(os.path.join(s9_dir, "MANIFEST.json"), "w") as f_m:
                    json.dump(m_data, f_m, indent=2)
                new_manifest_sha = hashlib.sha256(open(os.path.join(s9_dir, "MANIFEST.json"), "rb").read()).hexdigest()

                # Recompute VERDICT.json
                s9_v = copy.deepcopy(base_v)
                s9_v["reproducibility"]["inputs_manifest_sha256"] = new_manifest_sha
                resign(s9_v)
                with open(target_v_file, "w") as f:
                    json.dump(s9_v, f, indent=2)
                target_in_d = s9_dir

            else:
                with open(target_v_file, "w") as f:
                    json.dump(v_data, f, indent=2)

            print(f"\n--- Testing [{name}] ---")
            try:
                verify_gate(target_v_file, target_in_d, target_sc_p, params_path=pr_p, run_cold_reexecution=do_cold)
                if expected_outcome == "ACCEPTED_AS_PREDICTED":
                    print(f"CONFIRMED STRUCTURAL LIMITATION: {name} was ACCEPTED by the Gate (as predicted by N-1/N-3).")
                else:
                    print(f"FAILED: {name} was unexpectedly ACCEPTED by the Gate!")
            except GateVerificationError as e:
                err_msg = str(e)
                print(f"REJECTED by Gate: {err_msg}")
                if expected_outcome != "ACCEPTED_AS_PREDICTED" and err_msg.startswith(expected_outcome):
                    print("  ✓ Correctly Intercepted at expected verification tier.")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("\n================================================================================")
    print("CLASS II EXHAUSTIVE SUITE COMPLETE.")
    print("================================================================================")

if __name__ == "__main__":
    run_exhaustive_class2_suite()
