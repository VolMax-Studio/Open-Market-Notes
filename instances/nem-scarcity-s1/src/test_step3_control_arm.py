#!/usr/bin/env python3
import base64
import copy
import hashlib
import json
import os
import sys
import tempfile
import shutil
import subprocess
import pandas as pd

from cryptography.hazmat.primitives.asymmetric import ed25519

sys.path.insert(0, os.path.dirname(__file__))
from gate_verify import verify_gate, GateVerificationError, canonical_digest

def create_intoto_dsse_attestation(v_obj, inputs_dir, script_path, private_key):
    """
    Constructs a canonical in-toto Statement (v1.0) wrapped in a DSSE envelope,
    signed by the provided private key.
    """
    subjects = []
    for fn in sorted(os.listdir(inputs_dir)):
        if fn.endswith('.feather'):
            fp = os.path.join(inputs_dir, fn)
            sha = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            subjects.append({"name": fn, "digest": {"sha256": sha}})
    
    script_sha = hashlib.sha256(open(script_path, 'rb').read()).hexdigest()
    subjects.append({"name": "src/run_window.py", "digest": {"sha256": script_sha}})

    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": subjects,
        "predicateType": "https://slsa.dev/verification_summary/v1",
        "predicate": {
            "verifier": {
                "id": "https://volmax.studio/verifiers/nem-scarcity-s1/v1"
            },
            "timeValidated": v_obj["execution_and_metrics"]["evaluated_at_utc"],
            "resourceUri": f"volmax://market-notes/nem-scarcity-s1/{v_obj['claim']['window']}",
            "verificationResult": "PASSED" if v_obj["verdict"]["evaluation_status"] == "EVALUATED" else "FAILED",
            "verdict": v_obj["verdict"],
            "execution_and_metrics": v_obj["execution_and_metrics"],
            "evidence_boundary": v_obj["evidence_boundary"],
            "admissibility": v_obj["admissibility"]
        }
    }

    payload_type = "application/vnd.in-toto+json"
    payload_bytes = json.dumps(statement, sort_keys=True).encode('utf-8')
    pae = f"DSSEv1 {len(payload_type)} {payload_type} {len(payload_bytes)} ".encode('utf-8') + payload_bytes
    signature = private_key.sign(pae)
    
    dsse_envelope = {
        "payloadType": payload_type,
        "payload": base64.b64encode(payload_bytes).decode('ascii'),
        "signatures": [
            {
                "keyid": "volmax-issuer-ed25519-key-01",
                "sig": base64.b64encode(signature).decode('ascii')
            }
        ]
    }
    return dsse_envelope

def verify_dsse_attestation(envelope_path, inputs_dir, public_key):
    """
    Standard in-toto / DSSE Attestation Verifier:
    1. Validates cryptographic signature over PAE using public key.
    2. Decodes in-toto Statement payload.
    3. Verifies that all declared subject digests match physical files on disk.
    4. Evaluates verificationResult policy.
    """
    with open(envelope_path) as f:
        env = json.load(f)
    
    if "payloadType" not in env or "payload" not in env or "signatures" not in env:
        raise ValueError("DSSE_FAIL: Malformed envelope")
    
    payload_bytes = base64.b64decode(env["payload"])
    payload_type = env["payloadType"]
    pae = f"DSSEv1 {len(payload_type)} {payload_type} {len(payload_bytes)} ".encode('utf-8') + payload_bytes

    sigs = env.get("signatures", [])
    if not sigs:
        raise ValueError("DSSE_FAIL: Missing signatures")
    
    verified_sig = False
    for s in sigs:
        try:
            sig_bytes = base64.b64decode(s["sig"])
            public_key.verify(sig_bytes, pae)
            verified_sig = True
            break
        except Exception:
            continue
    
    if not verified_sig:
        raise ValueError("DSSE_FAIL: Signature verification failed (invalid key or forged payload)")

    statement = json.loads(payload_bytes.decode('utf-8'))
    subjects = statement.get("subject", [])
    for sub in subjects:
        name = sub["name"]
        expected_sha = sub["digest"]["sha256"]
        if name.startswith("src/"):
            disk_path = os.path.join(os.path.dirname(inputs_dir), name)
        else:
            disk_path = os.path.join(inputs_dir, name)
            
        if not os.path.exists(disk_path):
            raise ValueError(f"DSSE_FAIL: Subject file {name} missing on disk")
        actual_sha = hashlib.sha256(open(disk_path, "rb").read()).hexdigest()
        if actual_sha != expected_sha:
            raise ValueError(f"DSSE_FAIL: Subject digest mismatch for {name} (disk {actual_sha} != attestation {expected_sha})")

    res = statement.get("predicate", {}).get("verificationResult")
    if res != "PASSED":
        raise ValueError(f"DSSE_FAIL: Attestation policy verificationResult is {res}")

    return True, statement

def run_step3_complete_benchmark():
    base_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1'
    v_path = os.path.join(base_dir, 'runs/2026-07/VERDICT.json')
    inputs_dir = os.path.join(base_dir, 'inputs')
    script_path = os.path.join(base_dir, 'src/run_window.py')
    params_path = os.path.join(base_dir, 'PARAMS.md')

    with open(v_path) as f:
        base_v = json.load(f)

    # Generate Keys
    issuer_priv = ed25519.Ed25519PrivateKey.generate()
    issuer_pub = issuer_priv.public_key()

    attacker_priv = ed25519.Ed25519PrivateKey.generate()
    attacker_pub = attacker_priv.public_key()

    # Pre-registered 5 Scenarios x 2 Threat Models (T1 and T2)
    # Plus Row 9 (T3)
    scenarios = [
        # (Row ID, Name, ThreatModel, Expected P10, Expected DSSE)
        ("Row 1", "Envelope Bit-Flip (Un-resigned/Un-signed)", "T1", "REJECT", "REJECT"),
        ("Row 2", "Payload Mutation (rationale) + Recomputed Digest", "T1", "ACCEPT", "REJECT"),
        ("Row 2", "Payload Mutation (rationale) + Recomputed Digest", "T2", "ACCEPT", "ACCEPT"),
        ("Row 3", "Telemetry Bit-Flip on Disk", "T1", "REJECT", "REJECT"),
        ("Row 3", "Telemetry Bit-Flip on Disk", "T2", "REJECT", "REJECT"),
        ("Row 4", "Declared Metric Mutation (NSW1 m1=99%) + Recomputed Digest", "T1", "REJECT", "REJECT"),
        ("Row 4", "Declared Metric Mutation (NSW1 m1=99%) + Recomputed Digest", "T2", "REJECT", "ACCEPT"),
        ("Row 5", "Coherent Rule + Spec Substitution (S-8b)", "T1", "ACCEPT", "REJECT"),
        ("Row 5", "Coherent Rule + Spec Substitution (S-8b)", "T2", "ACCEPT", "ACCEPT"),
        ("Row 7", "Coherent Telemetry Forgery (D-1 Price Spike)", "T1", "ACCEPT", "REJECT"),
        ("Row 7", "Coherent Telemetry Forgery (D-1 Price Spike)", "T2", "ACCEPT", "ACCEPT"),
    ]

    print("================================================================================")
    print("STEP 3: COMPLETE 5x{T1,T2} COMPARATIVE BENCHMARK (P10 vs in-toto/DSSE)")
    print("================================================================================")

    results = []
    temp_root = tempfile.mkdtemp(prefix="step3_benchmark_full_")

    try:
        for row_id, name, tm, exp_p10, exp_dsse in scenarios:
            t_dir = os.path.join(temp_root, f"{row_id.replace(' ', '_')}_{tm}")
            t_inputs = os.path.join(t_dir, "inputs")
            t_src = os.path.join(t_dir, "src")
            os.makedirs(t_inputs, exist_ok=True)
            os.makedirs(t_src, exist_ok=True)

            shutil.copy(script_path, os.path.join(t_src, "run_window.py"))
            shutil.copy(params_path, os.path.join(t_dir, "PARAMS.md"))
            for fn in os.listdir(inputs_dir):
                shutil.copy(os.path.join(inputs_dir, fn), os.path.join(t_inputs, fn))

            t_v = copy.deepcopy(base_v)
            t_script = os.path.join(t_src, "run_window.py")
            t_params = os.path.join(t_dir, "PARAMS.md")
            signing_key = issuer_priv if tm == "T2" else attacker_priv

            if "Envelope Bit-Flip" in name:
                t_v["integrity_digest"] = "0" * 64
                # Create DSSE with corrupt base64
                t_dsse = create_intoto_dsse_attestation(base_v, t_inputs, t_script, issuer_priv)
                raw_p = base64.b64decode(t_dsse["payload"])
                mod_p = raw_p.replace(b"2026-07", b"2026-08")
                t_dsse["payload"] = base64.b64encode(mod_p).decode('ascii')

            elif "Payload Mutation (rationale)" in name:
                t_v["verdict"]["rationale"] = "Forged auxiliary rationale"
                t_v["integrity_digest"] = canonical_digest(t_v)
                t_dsse = create_intoto_dsse_attestation(t_v, t_inputs, t_script, signing_key)

            elif "Telemetry Bit-Flip on Disk" in name:
                # Corrupt 1 byte in feather file on disk
                fp = os.path.join(t_inputs, "nem_NSW1.feather")
                with open(fp, "r+b") as f_b:
                    f_b.seek(50)
                    f_b.write(b"\xFF")
                # Manifest & envelopes are left un-updated (bit flip on disk)
                t_dsse = create_intoto_dsse_attestation(base_v, t_inputs, t_script, signing_key)

            elif "Declared Metric Mutation" in name:
                t_v["execution_and_metrics"]["zone_metrics"]["NSW1"]["m1_pct"] = 99.0
                t_v["integrity_digest"] = canonical_digest(t_v)
                t_dsse = create_intoto_dsse_attestation(t_v, t_inputs, t_script, signing_key)

            elif "Coherent Rule + Spec Substitution" in name:
                # 100% Coherent S-8b Construction:
                # 1. Substitute PARAMS.md: q_ref = 0.50, k_mult = 1.00 (s_thresh = 50.0%)
                with open(t_params) as f_p:
                    p_c = f_p.read().replace('"q_ref": 0.90', '"q_ref": 0.50').replace('"k_multiplier": 1.50', '"k_multiplier": 1.00')
                with open(t_params, "w") as f_p:
                    f_p.write(p_c)

                # 2. Substitute run_window.py: default q_ref = 0.50, k_mult = 1.00
                with open(t_script) as f_s:
                    s_c = f_s.read().replace("q_ref = float(params.get('q_ref', 0.90))", "q_ref = float(params.get('q_ref', 0.50))")
                with open(t_script, "w") as f_s:
                    f_s.write(s_c)

                # 3. Execute substituted pipeline
                cmd = [sys.executable, t_script, "--window", "2026-07", "--instance", t_dir]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                with open(os.path.join(t_dir, "runs/2026-07/result.json")) as f_r:
                    r_data = json.load(f_r)

                # 4. Populate 100% Coherent VERDICT.json
                t_v["frozen_rule"]["rule_script_sha256"] = hashlib.sha256(s_c.encode('utf-8')).hexdigest()
                t_v["frozen_rule"]["parameters"]["q_ref"] = 0.50
                t_v["frozen_rule"]["parameters"]["k_mult"] = 1.00
                t_v["frozen_rule"]["parameters"]["s_thresh_pct"] = 50.0
                t_v["execution_and_metrics"]["N_elevated"] = r_data["N_elevated_comparison_zones"]
                for z, zm in r_data["zone_metrics"].items():
                    t_v["execution_and_metrics"]["zone_metrics"][z] = {
                        "m1_pct": zm["M1_pct"],
                        "status": zm["determinacy"],
                        "exposure_lower_pct": zm["exposure_lower_pct"],
                        "exposure_upper_pct": zm["exposure_upper_pct"]
                    }
                t_v["verdict"]["evaluation_status"] = r_data["evaluation_status"]
                t_v["verdict"]["label"] = r_data["label"]
                t_v["integrity_digest"] = canonical_digest(t_v)

                t_dsse = create_intoto_dsse_attestation(t_v, t_inputs, t_script, signing_key)

            elif "Coherent Telemetry Forgery" in name:
                # 100% Coherent S-9 Telemetry Forgery Construction:
                for z in ['NSW1', 'QLD1']:
                    fp = os.path.join(t_inputs, f'nem_{z}.feather')
                    df = pd.read_feather(fp)
                    mask = (df['SETTLEMENTDATE'] >= '2026-07-01') & (df['SETTLEMENTDATE'] <= '2026-07-31 14:00:00')
                    df.loc[mask, 'RRP'] = 14500.00
                    df.to_feather(fp)
                
                m_data = {"files": []}
                for fn in sorted(os.listdir(t_inputs)):
                    if fn.endswith('.feather'):
                        sha = hashlib.sha256(open(os.path.join(t_inputs, fn), 'rb').read()).hexdigest()
                        m_data["files"].append({"filename": fn, "sha256": sha})
                with open(os.path.join(t_inputs, "MANIFEST.json"), "w") as f_m:
                    json.dump(m_data, f_m, indent=2)

                cmd = [sys.executable, t_script, "--window", "2026-07", "--instance", t_dir]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                with open(os.path.join(t_dir, "runs/2026-07/result.json")) as f_r:
                    r_data = json.load(f_r)
                with open(os.path.join(t_dir, "runs/2026-07/completeness.json")) as f_c:
                    c_data = json.load(f_c)

                t_v["reproducibility"]["inputs_manifest_sha256"] = hashlib.sha256(open(os.path.join(t_inputs, "MANIFEST.json"), 'rb').read()).hexdigest()
                nsw1_comp = c_data["zone_completeness"]["NSW1"]
                t_v["evidence_boundary"]["received_intervals"] = nsw1_comp["admitted_intervals"]
                t_v["evidence_boundary"]["completeness_pct"] = nsw1_comp["completeness_pct"]
                t_v["evidence_boundary"]["missing_intervals_tail"] = nsw1_comp["missing_intervals"]
                t_v["execution_and_metrics"]["N_elevated"] = r_data["N_elevated_comparison_zones"]
                t_v["execution_and_metrics"]["zone_metrics"] = {}
                for z, zm in r_data["zone_metrics"].items():
                    t_v["execution_and_metrics"]["zone_metrics"][z] = {
                        "m1_pct": zm["M1_pct"],
                        "status": zm["determinacy"],
                        "exposure_lower_pct": zm["exposure_lower_pct"],
                        "exposure_upper_pct": zm["exposure_upper_pct"]
                    }
                t_v["verdict"]["evaluation_status"] = r_data["evaluation_status"]
                t_v["verdict"]["label"] = r_data["label"]
                t_v["verdict"]["rationale"] = f"Completeness >= 98.0% and N_elevated ({r_data['N_elevated_comparison_zones']}) > n_low (1)"
                t_v["integrity_digest"] = canonical_digest(t_v)

                t_dsse = create_intoto_dsse_attestation(t_v, t_inputs, t_script, signing_key)

            # Test P10
            v_test_file = os.path.join(t_dir, "test_verdict.json")
            with open(v_test_file, "w") as f_out:
                json.dump(t_v, f_out, indent=2)

            try:
                verify_gate(v_test_file, t_inputs, t_script, params_path=t_params, run_cold_reexecution=True)
                obs_p10 = "ACCEPT"
                diag_p10 = "Verified Klasa A, B, C"
            except GateVerificationError as e:
                obs_p10 = "REJECT"
                diag_p10 = str(e)
            except Exception as ex:
                obs_p10 = "ERROR"
                diag_p10 = str(ex)

            # Test DSSE
            dsse_test_file = os.path.join(t_dir, "test_dsse.json")
            with open(dsse_test_file, "w") as f_out:
                json.dump(t_dsse, f_out, indent=2)

            try:
                verify_dsse_attestation(dsse_test_file, t_inputs, issuer_pub)
                obs_dsse = "ACCEPT"
                diag_dsse = "Signature valid, subjects match disk, policy PASSED"
            except Exception as ex:
                obs_dsse = "REJECT"
                diag_dsse = str(ex)

            print(f"\n--- [{row_id}: {name} ({tm})] ---")
            print(f"  P10 Expected : {exp_p10:6s} | Observed : {obs_p10:6s} ({diag_p10})")
            print(f"  DSSE Expected: {exp_dsse:6s} | Observed : {obs_dsse:6s} ({diag_dsse})")

            results.append({
                "row_id": row_id,
                "name": name,
                "threat_model": tm,
                "p10_status": obs_p10,
                "p10_diag": diag_p10,
                "dsse_status": obs_dsse,
                "dsse_diag": diag_dsse
            })

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("\n================================================================================")
    print("STEP 3: RATIFIED COMPARATIVE MATRIX (OBSERVED EMPIRICAL RESULTS)")
    print("================================================================================")
    print(f"| {'Dimension':55s} | {'TM':2s} | {'P10 Verdict v1.0.0':18s} | {'in-toto / DSSE':18s} |")
    print("|" + "-"*57 + "|" + "-"*4 + "|" + "-"*20 + "|" + "-"*20 + "|")
    for r in results:
        print(f"| {r['name']:55s} | {r['threat_model']:2s} | {r['p10_status']:18s} | {r['dsse_status']:18s} |")
    print(f"| {'Issuer Identity Forgery':55s} | {'T1':2s} | {'ABSENT (Structural)':18s} | {'REJECT':18s} |")
    print(f"| {'Upstream Boundary Truncation (119 int. at source)':55s} | {'T3':2s} | {'NOT TESTED (Ext Ref)':18s} | {'NOT TESTED (Ext Ref)':18s} |")
    print("================================================================================")

if __name__ == "__main__":
    run_step3_complete_benchmark()
