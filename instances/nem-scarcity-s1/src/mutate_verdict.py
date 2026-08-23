#!/usr/bin/env python3
import copy
import json
import hashlib
import os
import sys
import tempfile
import shutil
import pandas as pd
from gate_verify import verify_gate, GateVerificationError, canonical_digest

def run_multiclass_falsification_suite():
    v_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/runs/2026-07/VERDICT.json'
    inputs_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/inputs'
    script_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/src/run_window.py'
    params_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/PARAMS.md'

    with open(v_path) as f:
        base_v = json.load(f)

    def resign(d):
        d["integrity_digest"] = canonical_digest(d)
        return d

    test_cases = []

    # =========================================================================
    # KLASA A TESTS: Envelope & Self-Consistency
    # =========================================================================
    # A0: Raw Envelope Digest Bit-Flip
    t_a0 = copy.deepcopy(base_v)
    t_a0["integrity_digest"] = "ffff" + t_a0["integrity_digest"][4:]
    test_cases.append(("A0: Envelope Digest Tampering", t_a0, "GATE_FAIL_A: INTEGRITY_DIGEST_MISMATCH", inputs_dir, script_path, params_path, False))

    # A1: Claim Window Mutation
    t_a1 = copy.deepcopy(base_v)
    t_a1["claim"]["window"] = "2026-08"
    resign(t_a1)
    test_cases.append(("A1: Claim Window Mutation", t_a1, "GATE_FAIL_A: CLAIM_EVIDENCE_MISMATCH", inputs_dir, script_path, params_path, False))

    # A2: Evidence Boundary Interval Tampering
    t_a2 = copy.deepcopy(base_v)
    t_a2["evidence_boundary"]["received_intervals"] = 8900
    resign(t_a2)
    test_cases.append(("A2: Evidence Boundary Forgery", t_a2, "GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH", inputs_dir, script_path, params_path, False))

    # A3: Internal Parameter Math Discrepancy
    t_a3 = copy.deepcopy(base_v)
    t_a3["frozen_rule"]["parameters"]["s_thresh_pct"] = 5.0
    resign(t_a3)
    test_cases.append(("A3: Internal Parameter Incoherence", t_a3, "GATE_FAIL_A: FROZEN_RULE_HASH_MISMATCH", inputs_dir, script_path, params_path, False))

    # A4: Verdict Inversion
    t_a4 = copy.deepcopy(base_v)
    t_a4["verdict"]["label"] = "ELEVATED"
    resign(t_a4)
    test_cases.append(("A4: Verdict Inversion Bias", t_a4, "GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path, params_path, False))

    # A5: Admissibility Policy Spoofing
    t_a5 = copy.deepcopy(base_v)
    t_a5["admissibility"]["source_license"] = "PROPRIETARY_NDA_CLOSED"
    resign(t_a5)
    test_cases.append(("A5: Admissibility License Spoof", t_a5, "GATE_FAIL_A: ADMISSIBILITY_POLICY_VIOLATION", inputs_dir, script_path, params_path, False))

    # =========================================================================
    # KLASA B TESTS: Evidence Binding & Telemetry Corruption
    # =========================================================================
    # B1: Physical Telemetry Bit-Flip on Disk
    test_cases.append(("B1: Telemetry Data Corruption on Disk", "DYNAMIC_B1", "GATE_FAIL_B: TELEMETRY_CORRUPTION", "DYNAMIC_STORE", script_path, params_path, False))

    # B2: Manifest Hash Forgery in Verdict
    t_b2 = copy.deepcopy(base_v)
    t_b2["reproducibility"]["inputs_manifest_sha256"] = "11223344" + t_b2["reproducibility"]["inputs_manifest_sha256"][8:]
    resign(t_b2)
    test_cases.append(("B2: Manifest Hash Forgery", t_b2, "GATE_FAIL_B: INPUT_MANIFEST_HASH_MISMATCH", inputs_dir, script_path, params_path, False))

    # B3: Frozen Script Code Tampering
    t_b3 = copy.deepcopy(base_v)
    t_b3["frozen_rule"]["rule_script_sha256"] = "deadbeef" + t_b3["frozen_rule"]["rule_script_sha256"][8:]
    resign(t_b3)
    test_cases.append(("B3: Frozen Script Hash Mismatch", t_b3, "GATE_FAIL_B: FROZEN_RULE_HASH_MISMATCH", inputs_dir, script_path, params_path, False))

    # B4: Coordinated Parameter Tampering (q_ref AND s_thresh altered together, self-consistent in JSON, but fails against external PARAMS.md!)
    t_b4 = copy.deepcopy(base_v)
    t_b4["frozen_rule"]["parameters"]["q_ref"] = 0.80
    t_b4["frozen_rule"]["parameters"]["s_thresh_pct"] = 30.0 # 1.5 * (1 - 0.80) * 100 = 30.0 (internally coherent!)
    resign(t_b4)
    test_cases.append(("B4: Coordinated Parameter Drift (Caught by External Spec Binding)", t_b4, "GATE_FAIL_B: FROZEN_SPEC_MISMATCH", inputs_dir, script_path, params_path, False))

    # B5: Telemetry Boundary Tampering (period_end_utc claims coverage beyond actual feather cutoff)
    t_b5 = copy.deepcopy(base_v)
    t_b5["evidence_boundary"]["telemetry_period_end_utc"] = "2026-07-31T23:59:59Z"
    resign(t_b5)
    test_cases.append(("B5: Telemetry Boundary Overclaim", t_b5, "GATE_FAIL_B: EVIDENCE_BOUNDARY_MISMATCH", inputs_dir, script_path, params_path, False))

    # =========================================================================
    # KLASA C TESTS: Cold Re-Execution & Output Agreement
    # =========================================================================
    # C1: Broken Reproducibility Recipe
    t_c1 = copy.deepcopy(base_v)
    t_c1["reproducibility"]["reproduce_recipe"] = ""
    resign(t_c1)
    test_cases.append(("C1: Broken Reproduce Recipe", t_c1, "GATE_FAIL_C: REPRODUCTION_FAILED", inputs_dir, script_path, params_path, True))

    # C2: Output Agreement Discrepancy (Declared metric changed from 4.8360 to 9.9999, passes A and B, fails C!)
    t_c2 = copy.deepcopy(base_v)
    t_c2["execution_and_metrics"]["zone_metrics"]["NSW1"]["m1_pct"] = 9.9999
    resign(t_c2)
    test_cases.append(("C2: Output Agreement Discrepancy (Fails Cold Re-Execution)", t_c2, "GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH", inputs_dir, script_path, params_path, True))

    print("================================================================================")
    print("ZERO-TRUST GATE: 3-TIER FALSIFICATION & ADVERSARIAL SUITE (KLASA A, B, C)")
    print("================================================================================")

    passed_count = 0
    total_tests = len(test_cases)

    temp_root = tempfile.mkdtemp(prefix="gate_falsification_suite_")
    try:
        for name, v_data, expected_err, in_d, sc_p, pr_p, do_cold in test_cases:
            target_v_file = os.path.join(temp_root, "test_verdict.json")
            target_in_d = in_d

            if v_data == "DYNAMIC_B1":
                b1_dir = os.path.join(temp_root, "corrupted_inputs")
                shutil.copytree(inputs_dir, b1_dir)
                corrupt_file = os.path.join(b1_dir, "nem_NSW1.feather")
                with open(corrupt_file, "r+b") as f:
                    f.seek(100)
                    f.write(b'\xFF\xFF')
                with open(target_v_file, "w") as f:
                    json.dump(base_v, f, indent=2)
                target_in_d = b1_dir
            else:
                with open(target_v_file, "w") as f:
                    json.dump(v_data, f, indent=2)

            try:
                verify_gate(target_v_file, target_in_d, sc_p, params_path=pr_p, run_cold_reexecution=do_cold)
                print(f"FAILED: {name} was unexpectedly ACCEPTED by the Gate!")
            except GateVerificationError as e:
                err_msg = str(e)
                if err_msg.startswith(expected_err):
                    print(f"PASSED: [{name}]\n        -> Correctly Rejected: {err_msg}")
                    passed_count += 1
                else:
                    print(f"FAILED: [{name}]\n        -> Expected '{expected_err}', but got:\n        {err_msg}")
            except Exception as ex:
                print(f"FAILED: [{name}]\n        -> Unexpected Exception: {ex}")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("================================================================================")
    print(f"GATE SUMMARY: {passed_count}/{total_tests} Multi-Class Adversarial Attacks Successfully Intercepted.")
    print("================================================================================")

    if passed_count == total_tests:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_multiclass_falsification_suite()
