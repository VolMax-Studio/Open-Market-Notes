#!/usr/bin/env python3
import copy
import json
import hashlib
import os
import sys
from verify_verdict import verify_verdict_dict, VerdictVerificationError

def compute_digest(d):
    copy_d = {k: v for k, v in d.items() if k != "integrity_digest"}
    canonical_str = json.dumps(copy_d, sort_keys=True, indent=2)
    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()

def re_sign(d):
    d["integrity_digest"] = compute_digest(d)
    return d

def run_suite():
    v_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/runs/2026-07/VERDICT.json'
    inputs_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/inputs'
    script_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/src/run_window.py'
    
    with open(v_path) as f:
        base_verdict = json.load(f)

    tests = []

    # NC-0: Direct Bit-flip in Envelope Digest
    d0 = copy.deepcopy(base_verdict)
    d0["integrity_digest"] = "0000" + d0["integrity_digest"][4:]
    tests.append(("NC-0 (Envelope Digest Bit-Flip)", d0, "REJECT: INTEGRITY_DIGEST_MISMATCH", inputs_dir, script_path))

    # NC-1: Claim Mutation (window changed to 2026-08 without changing period bounds)
    d1 = copy.deepcopy(base_verdict)
    d1["claim"]["window"] = "2026-08"
    re_sign(d1)
    tests.append(("NC-1 (Claim Mutation / Window Drift)", d1, "REJECT: CLAIM_EVIDENCE_MISMATCH", inputs_dir, script_path))

    # NC-2: Evidence Boundary Forgery (received_intervals set to 8900 without changing nominal/missing)
    d2 = copy.deepcopy(base_verdict)
    d2["evidence_boundary"]["received_intervals"] = 8900
    re_sign(d2)
    tests.append(("NC-2 (Evidence Boundary Forgery)", d2, "REJECT: EVIDENCE_INTEGRITY_MISMATCH", inputs_dir, script_path))

    # NC-3: Post-Hoc Rule Tampering (s_thresh_pct tampered to 4.0% without changing q_ref/k_mult)
    d3 = copy.deepcopy(base_verdict)
    d3["frozen_rule"]["parameters"]["s_thresh_pct"] = 4.0
    re_sign(d3)
    tests.append(("NC-3 (Post-Hoc Rule Tampering)", d3, "REJECT: FROZEN_RULE_HASH_MISMATCH", inputs_dir, script_path))

    # NC-4: Verdict Inversion (label changed from NULL to ELEVATED despite metrics)
    d4 = copy.deepcopy(base_verdict)
    d4["verdict"]["label"] = "ELEVATED"
    re_sign(d4)
    tests.append(("NC-4 (Verdict Inversion / Bias Injection)", d4, "REJECT: DETERMINISTIC_LOGIC_VIOLATION", inputs_dir, script_path))

    # NC-5: Admissibility Spoofing (publication_status set to PUBLIC_PERMITTED but license corrupted to PROPRIETARY_NDA)
    d5 = copy.deepcopy(base_verdict)
    d5["admissibility"]["source_license"] = "PROPRIETARY_CLOSED_NDA"
    re_sign(d5)
    tests.append(("NC-5 (Admissibility Spoofing)", d5, "REJECT: ADMISSIBILITY_POLICY_VIOLATION", inputs_dir, script_path))

    # NC-6: Input Manifest Hash Tampering (manifest hash mutated)
    d6 = copy.deepcopy(base_verdict)
    d6["reproducibility"]["inputs_manifest_sha256"] = "deadbeef" + d6["reproducibility"]["inputs_manifest_sha256"][8:]
    re_sign(d6)
    tests.append(("NC-6 (Input Manifest Telemetry Tampering)", d6, "REJECT: INPUT_MANIFEST_HASH_MISMATCH", inputs_dir, script_path))

    # NC-7: Broken Reproducibility Recipe (recipe cleared)
    d7 = copy.deepcopy(base_verdict)
    d7["reproducibility"]["reproduce_recipe"] = ""
    re_sign(d7)
    tests.append(("NC-7 (Broken Reproducibility Recipe)", d7, "REJECT: REPRODUCTION_FAILED", inputs_dir, script_path))

    print("================================================================================")
    print("ROUND 6 NEGATIVE CONTROL TEST SUITE: ADVERSARIAL MUTATION OF VERDICT.json")
    print("================================================================================")
    
    passed_count = 0
    for name, v_data, expected_prefix, in_d, sc_p in tests:
        try:
            verify_verdict_dict(v_data, inputs_dir=in_d, script_path=sc_p)
            print(f"FAILED: {name} was unexpectedly ACCEPTED!")
        except VerdictVerificationError as e:
            err_msg = str(e)
            if err_msg.startswith(expected_prefix):
                print(f"PASSED: {name} -> Caught with exact diagnostic:\n        {err_msg}")
                passed_count += 1
            else:
                print(f"FAILED: {name} -> Expected prefix '{expected_prefix}', but got:\n        {err_msg}")
        except Exception as ex:
            print(f"FAILED: {name} -> Unexpected non-verdict exception: {ex}")

    print("================================================================================")
    print(f"SUMMARY: {passed_count}/{len(tests)} Negative Controls Successfully Caught and Rejected.")
    print("================================================================================")
    
    if passed_count == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
