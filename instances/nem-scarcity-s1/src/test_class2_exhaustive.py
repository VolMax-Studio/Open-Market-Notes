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

    # Scenarios tuple: (name, v_data, expected_outcome, in_d, sc_p, pr_p, do_cold)
    # expected_outcome: "REJECT: <error_prefix>" or "ACCEPT"
    scenarios = []

    # S-1: Zone Metric Tampering (NSW1 M1 4.8360 -> 9.9999, re-signed)
    s1 = copy.deepcopy(base_v)
    s1["execution_and_metrics"]["zone_metrics"]["NSW1"]["m1_pct"] = 9.9999
    resign(s1)
    scenarios.append(("S-1: Zone Metric Tampering", s1, "REJECT: GATE_FAIL_C: OUTPUT_AGREEMENT_MISMATCH", inputs_dir, script_path, params_path, True))

    # S-2: Zone Status Inversion (NSW1 status -> ELEVATED, re-signed)
    s2 = copy.deepcopy(base_v)
    s2["execution_and_metrics"]["zone_metrics"]["NSW1"]["status"] = "ELEVATED"
    resign(s2)
    scenarios.append(("S-2: Zone Status Inversion", s2, "REJECT: GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path, params_path, False))

    # S-3: Deterministic Label Inversion (label -> ELEVATED, re-signed)
    s3 = copy.deepcopy(base_v)
    s3["verdict"]["label"] = "ELEVATED"
    resign(s3)
    scenarios.append(("S-3: Verdict Label Inversion", s3, "REJECT: GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path, params_path, False))

    # S-4: Coordinated Parameter Drift (q_ref 0.80, s_thresh 30.0%, internally consistent, re-signed)
    s4 = copy.deepcopy(base_v)
    s4["frozen_rule"]["parameters"]["q_ref"] = 0.80
    s4["frozen_rule"]["parameters"]["s_thresh_pct"] = 30.0
    resign(s4)
    scenarios.append(("S-4: Coordinated Parameter Drift", s4, "REJECT: GATE_FAIL_B: FROZEN_SPEC_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-5: Interval Arithmetic Forgery (received 8900, missing 28, re-signed)
    s5 = copy.deepcopy(base_v)
    s5["evidence_boundary"]["received_intervals"] = 8900
    s5["evidence_boundary"]["missing_intervals_tail"] = 28
    resign(s5)
    scenarios.append(("S-5: Interval Arithmetic Forgery", s5, "REJECT: GATE_FAIL_A: EVIDENCE_INTEGRITY_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-6: Temporal Window Drift (window -> 2026-08, re-signed)
    s6 = copy.deepcopy(base_v)
    s6["claim"]["window"] = "2026-08"
    resign(s6)
    scenarios.append(("S-6: Temporal Window Drift", s6, "REJECT: GATE_FAIL_A: CLAIM_EVIDENCE_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-7: Telemetry Boundary Overclaim (period_end_utc -> 23:59:59Z, re-signed)
    s7 = copy.deepcopy(base_v)
    s7["evidence_boundary"]["telemetry_period_end_utc"] = "2026-07-31T23:59:59Z"
    resign(s7)
    scenarios.append(("S-7: Telemetry Boundary Overclaim", s7, "REJECT: GATE_FAIL_B: EVIDENCE_BOUNDARY_MISMATCH", inputs_dir, script_path, params_path, False))

    # S-8a: Frozen Rule Code Substitution with UNTOUCHED PARAMS.md
    # Attacker substitutes run_window.py to compute S_thresh=5.0% internally without changing PARAMS.md
    # Expected: REJECT (Klasa A or Klasa B catches discrepancy with PARAMS.md)
    scenarios.append(("S-8a: Frozen Rule Code Substitution (Untouched PARAMS.md)", "DYNAMIC_S8A", "REJECT: GATE_FAIL_A: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, "DYNAMIC_SCRIPT_S8A", params_path, True))

    # S-8b: Frozen Rule Code Substitution with MATCHING MUTATED PARAMS.md (Pre-registered Leak)
    # Attacker substitutes run_window.py AND PARAMS.md together with coherent verdict & hashes
    # Expected: ACCEPT (Proves that without external Git check or signature, code+spec substitution passes package gate)
    scenarios.append(("S-8b: Coherent Code + Spec Substitution (Pre-registered Leak)", "DYNAMIC_S8B", "ACCEPT", inputs_dir, "DYNAMIC_SCRIPT_S8B", "DYNAMIC_PARAMS_S8B", True))

    # S-9: Coherent Telemetry Mutation (Pre-registered Leak)
    # Attacker modifies telemetry data to produce higher prices + coherent verdict + manifest + digest
    # Expected: ACCEPT (Proves Nalaz N-1: package verifier trusts supplied inputs)
    scenarios.append(("S-9: Coherent Telemetry Mutation (Pre-registered Leak)", "DYNAMIC_S9", "ACCEPT", "DYNAMIC_INPUTS_S9", script_path, params_path, True))

    print("================================================================================")
    print("EXHAUSTIVE CLASS II ADVERSARIAL SUITE (4-WAY PREDICTION HARNESS)")
    print("================================================================================")

    results_summary = []
    temp_root = tempfile.mkdtemp(prefix="class2_suite_")

    try:
        for name, v_data, expected_outcome, in_d, sc_p, pr_p, do_cold in scenarios:
            target_v_file = os.path.join(temp_root, "test_verdict.json")
            target_in_d = in_d
            target_sc_p = sc_p
            target_pr_p = pr_p

            if v_data == "DYNAMIC_S8A":
                # S-8a: Substituted script that produces M1=99.9% and ELEVATED, but PARAMS.md expects 15% threshold
                s8a_script = os.path.join(temp_root, "s8a_run_window.py")
                with open(script_path) as f_in:
                    code = f_in.read()
                mod_code = code.replace("m1_pct = (n_elevated_intervals / float(rec)) * 100.0", "m1_pct = 99.9000\n        determinacy = 'ELEVATED'")
                with open(s8a_script, "w") as f_out:
                    f_out.write(mod_code)
                
                s8a_v = copy.deepcopy(base_v)
                s8a_v["frozen_rule"]["rule_script_sha256"] = hashlib.sha256(mod_code.encode('utf-8')).hexdigest()
                for z in s8a_v["execution_and_metrics"]["zone_metrics"]:
                    s8a_v["execution_and_metrics"]["zone_metrics"][z]["m1_pct"] = 99.9000
                    s8a_v["execution_and_metrics"]["zone_metrics"][z]["status"] = "ELEVATED"
                s8a_v["execution_and_metrics"]["N_elevated"] = 4
                s8a_v["verdict"]["evaluation_status"] = "EVALUATED"
                s8a_v["verdict"]["label"] = "HIGH_ELEVATION"
                resign(s8a_v)
                with open(target_v_file, "w") as f:
                    json.dump(s8a_v, f, indent=2)
                target_sc_p = s8a_script

            elif v_data == "DYNAMIC_S8B":
                # S-8b: Substituted script AND matching PARAMS.md
                s8b_script = os.path.join(temp_root, "s8b_run_window.py")
                s8b_params = os.path.join(temp_root, "s8b_PARAMS.md")
                
                # Write matching modified PARAMS.md (q_ref 0.50, k_mult 1.0 -> s_thresh 50.0%, n_low 1, n_high 3)
                with open(params_path) as f_p:
                    p_content = f_p.read()
                mod_params_content = p_content.replace('"q_ref": 0.90', '"q_ref": 0.50').replace('"k_multiplier": 1.50', '"k_multiplier": 1.00')
                with open(s8b_params, "w") as f_out:
                    f_out.write(mod_params_content)
                
                with open(script_path) as f_in:
                    code = f_in.read()
                mod_code = code.replace("q_ref = float(params.get('q_ref', 0.90))", "q_ref = float(params.get('q_ref', 0.50))")
                with open(s8b_script, "w") as f_out:
                    f_out.write(mod_code)

                s8b_v = copy.deepcopy(base_v)
                s8b_v["frozen_rule"]["rule_script_sha256"] = hashlib.sha256(mod_code.encode('utf-8')).hexdigest()
                s8b_v["frozen_rule"]["parameters"]["q_ref"] = 0.50
                s8b_v["frozen_rule"]["parameters"]["k_mult"] = 1.00
                s8b_v["frozen_rule"]["parameters"]["s_thresh_pct"] = 50.0
                resign(s8b_v)
                with open(target_v_file, "w") as f:
                    json.dump(s8b_v, f, indent=2)
                target_sc_p = s8b_script
                target_pr_p = s8b_params

            elif v_data == "DYNAMIC_S9":
                # S-9: Substituted telemetry inputs that generate genuinely different result
                s9_dir = os.path.join(temp_root, "s9_inputs")
                shutil.copytree(inputs_dir, s9_dir)
                
                # Read NSW1, set prices to $15,000 for all intervals
                import pandas as pd
                nsw1_file = os.path.join(s9_dir, "nem_NSW1.feather")
                df = pd.read_feather(nsw1_file)
                df['RRP'] = 15000.0
                df.to_feather(nsw1_file)
                
                new_nsw1_sha = hashlib.sha256(open(nsw1_file, "rb").read()).hexdigest()
                with open(os.path.join(s9_dir, "MANIFEST.json")) as f_m:
                    m_data = json.load(f_m)
                for f_entry in m_data["files"]:
                    if f_entry["filename"] == "nem_NSW1.feather":
                        f_entry["sha256"] = new_nsw1_sha
                with open(os.path.join(s9_dir, "MANIFEST.json"), "w") as f_m:
                    json.dump(m_data, f_m, indent=2)
                new_manifest_sha = hashlib.sha256(open(os.path.join(s9_dir, "MANIFEST.json"), "rb").read()).hexdigest()

                # Build matching verdict for 100% elevation on NSW1
                s9_v = copy.deepcopy(base_v)
                s9_v["reproducibility"]["inputs_manifest_sha256"] = new_manifest_sha
                s9_v["execution_and_metrics"]["zone_metrics"]["NSW1"]["m1_pct"] = 100.0000
                s9_v["execution_and_metrics"]["zone_metrics"]["NSW1"]["status"] = "ELEVATED"
                s9_v["execution_and_metrics"]["zone_metrics"]["NSW1"]["exposure_lower_pct"] = 98.6671
                s9_v["execution_and_metrics"]["zone_metrics"]["NSW1"]["exposure_upper_pct"] = 100.0000
                s9_v["execution_and_metrics"]["N_elevated"] = 1
                s9_v["verdict"]["evaluation_status"] = "EVALUATED"
                s9_v["verdict"]["label"] = "ELEVATED"
                s9_v["verdict"]["rationale"] = "Completeness >= 98.0% and N_elevated (1) >= n_low (1)"
                resign(s9_v)
                with open(target_v_file, "w") as f:
                    json.dump(s9_v, f, indent=2)
                target_in_d = s9_dir

            else:
                with open(target_v_file, "w") as f:
                    json.dump(v_data, f, indent=2)

            print(f"\n--- Testing [{name}] ---")
            actual_status = "UNKNOWN"
            diagnostic = "NONE"

            try:
                verify_gate(target_v_file, target_in_d, target_sc_p, params_path=target_pr_p, run_cold_reexecution=do_cold)
                actual_status = "ACCEPT"
                diagnostic = "VERIFIED_VERDICT"
            except GateVerificationError as e:
                actual_status = "REJECT"
                diagnostic = str(e)

            # 4-Way Prediction Evaluation
            is_expected_reject = expected_outcome.startswith("REJECT")
            is_expected_accept = (expected_outcome == "ACCEPT")

            if is_expected_reject and actual_status == "REJECT":
                eval_result = "PASS: INTERCEPTED (CORRECT PREDICTION)"
                print(f"RESULT: {eval_result}\n  Diagnostic: {diagnostic}")
            elif is_expected_accept and actual_status == "ACCEPT":
                eval_result = "PASS: STRUCTURAL LIMITATION CONFIRMED (CORRECT PREDICTION)"
                print(f"RESULT: {eval_result}\n  Diagnostic: {diagnostic}")
            elif is_expected_reject and actual_status == "ACCEPT":
                eval_result = "FAILED PREDICTION: UNEXPECTED LEAK!"
                print(f"RESULT: {eval_result}\n  Candidate was ACCEPTED when REJECT was expected!")
            elif is_expected_accept and actual_status == "REJECT":
                eval_result = "FAILED PREDICTION: UNEXPECTED REJECTION!"
                print(f"RESULT: {eval_result}\n  Candidate was REJECTED ({diagnostic}) when ACCEPT was expected!")

            results_summary.append({
                "name": name,
                "expected": expected_outcome,
                "actual": actual_status,
                "diagnostic": diagnostic,
                "evaluation": eval_result
            })

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("\n================================================================================")
    print("CLASS II EXHAUSTIVE SUITE 4-WAY EVALUATION SUMMARY:")
    print("================================================================================")
    for r in results_summary:
        print(f"[{r['name']}]\n  Expected: {r['expected']}\n  Actual  : {r['actual']} ({r['diagnostic']})\n  Eval    : {r['evaluation']}\n")

if __name__ == "__main__":
    run_exhaustive_class2_suite()
