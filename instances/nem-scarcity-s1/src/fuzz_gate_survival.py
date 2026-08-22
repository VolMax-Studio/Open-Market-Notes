#!/usr/bin/env python3
import copy
import json
import hashlib
import os
import sys
import random
import string
import tempfile
import shutil
import time
from gate_verify import verify_gate, GateVerificationError, canonical_digest

def random_string(n=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def random_hex(n=64):
    return ''.join(random.choices(string.hexdigits.lower(), k=n))

def mutate_candidate(base_v, mutation_type, resign=False):
    d = copy.deepcopy(base_v)
    
    if mutation_type == "delete_key":
        k = random.choice(list(d.keys()))
        del d[k]
        
    elif mutation_type == "type_mutation":
        target = random.choice(["completeness_pct", "nominal_intervals", "s_thresh_pct", "N_elevated", "window"])
        if target == "completeness_pct":
            d["evidence_boundary"]["completeness_pct"] = "98.6671"
        elif target == "nominal_intervals":
            d["evidence_boundary"]["nominal_intervals"] = [8928]
        elif target == "s_thresh_pct":
            d["frozen_rule"]["parameters"]["s_thresh_pct"] = "15.0"
        elif target == "N_elevated":
            d["execution_and_metrics"]["N_elevated"] = "0"
        elif target == "window":
            d["claim"]["window"] = 202607
            
    elif mutation_type == "arithmetic_drift":
        delta = random.choice([-100, -10, -5, -1, 1, 5, 10, 100])
        choice = random.choice(["received", "nominal", "missing", "comp_pct"])
        if choice == "received":
            d["evidence_boundary"]["received_intervals"] += delta
        elif choice == "nominal":
            d["evidence_boundary"]["nominal_intervals"] += delta
        elif choice == "missing":
            d["evidence_boundary"]["missing_intervals_tail"] += delta
        elif choice == "comp_pct":
            d["evidence_boundary"]["completeness_pct"] += float(delta) / 100.0

    elif mutation_type == "temporal_drift":
        delta_day = random.choice([2, 3, 5, 10, 15, 20])
        d["claim"]["window_bounds_utc"]["end"] = f"2026-07-{31-delta_day:02d}T23:59:59Z"

    elif mutation_type == "rule_drift":
        choice = random.choice(["s_thresh", "q_ref", "k_mult", "n_low", "n_high"])
        if choice == "s_thresh":
            d["frozen_rule"]["parameters"]["s_thresh_pct"] = round(random.uniform(1.0, 50.0), 2)
        elif choice == "q_ref":
            d["frozen_rule"]["parameters"]["q_ref"] = round(random.uniform(0.5, 0.99), 2)
        elif choice == "k_mult":
            d["frozen_rule"]["parameters"]["k_mult"] = round(random.uniform(0.5, 3.0), 2)
        elif choice == "n_low":
            d["frozen_rule"]["parameters"]["n_low"] = random.randint(2, 5)
        elif choice == "n_high":
            d["frozen_rule"]["parameters"]["n_high"] = random.randint(4, 10)

    elif mutation_type == "verdict_inversion":
        labels = ["HIGH_ELEVATION", "ELEVATED", "UNRESOLVED", "INVALID"]
        d["verdict"]["label"] = random.choice(labels)
        if random.random() > 0.5:
            d["verdict"]["evaluation_status"] = random.choice(["INCOMPLETE", "REJECTED", "PASSED"])

    elif mutation_type == "metric_fuzz":
        z = random.choice(["NSW1", "QLD1", "SA1", "VIC1", "TAS1"])
        d["execution_and_metrics"]["zone_metrics"][z]["m1_pct"] = round(random.uniform(0.0, 100.0), 4)
        if random.random() > 0.5:
            d["execution_and_metrics"]["zone_metrics"][z]["status"] = random.choice(["ELEVATED", "INCOMPLETE", "INDETERMINATE"])

    elif mutation_type == "admissibility_fuzz":
        d["admissibility"]["source_license"] = random.choice(["PROPRIETARY_NDA", "CLOSED_COMMERCIAL", "UNKNOWN", ""])
        if random.random() > 0.5:
            d["admissibility"]["publication_status"] = random.choice(["RESTRICTED_NDA", "CONFIDENTIAL", "INTERNAL_ONLY"])

    elif mutation_type == "crypto_fuzz":
        choice = random.choice(["integrity", "manifest", "script", "commit"])
        if choice == "integrity":
            d["integrity_digest"] = random_hex(64)
            return d
        elif choice == "manifest":
            d["reproducibility"]["inputs_manifest_sha256"] = random_hex(64)
        elif choice == "script":
            d["frozen_rule"]["rule_script_sha256"] = random_hex(64)
        elif choice == "commit":
            d["frozen_rule"]["code_git_commit"] = random_hex(40)

    elif mutation_type == "recipe_fuzz":
        d["reproducibility"]["reproduce_recipe"] = random.choice(["", "echo 'hello'", "python3 invalid.py", None])

    if resign:
        d["integrity_digest"] = canonical_digest(d)
        
    return d

def run_fuzzing_experiment(N=10000, seed=42, output_corpus=None):
    random.seed(seed)
    v_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/runs/2026-07/VERDICT.json'
    inputs_dir = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/inputs'
    script_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/src/run_window.py'
    params_path = '/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/PARAMS.md'

    with open(v_path) as f:
        base_v = json.load(f)

    mutation_types = [
        "delete_key", "type_mutation", "arithmetic_drift", "temporal_drift",
        "rule_drift", "verdict_inversion", "metric_fuzz", "admissibility_fuzz",
        "crypto_fuzz", "recipe_fuzz"
    ]

    print("================================================================================")
    print(f"P10 ZERO-TRUST GATE: MONTE CARLO MUTATION EXPERIMENT (N = {N:,}, SEED = {seed})")
    print("================================================================================")

    accepted_mutations = []
    rejection_distribution = {
        "GATE_FAIL_A": 0,
        "GATE_FAIL_B": 0,
        "GATE_FAIL_C": 0,
        "UNEXPECTED_ERROR": 0
    }

    start_time = time.time()
    temp_dir = tempfile.mkdtemp(prefix="p10_fuzz_")
    cand_file = os.path.join(temp_dir, "cand_verdict.json")

    try:
        for i in range(1, N + 1):
            m_type = random.choice(mutation_types)
            resign_flag = (random.random() > 0.5) if m_type != "crypto_fuzz" else False
            
            mutated_v = mutate_candidate(base_v, m_type, resign=resign_flag)
            
            with open(cand_file, "w") as f:
                json.dump(mutated_v, f, indent=2)

            try:
                verify_gate(cand_file, inputs_dir, script_path, params_path=params_path, run_cold_reexecution=True)
                accepted_mutations.append({
                    "iteration": i,
                    "mutation_type": m_type,
                    "resigned": resign_flag,
                    "candidate_digest": mutated_v.get("integrity_digest"),
                    "data": mutated_v
                })
            except GateVerificationError as e:
                err_msg = str(e)
                if err_msg.startswith("GATE_FAIL_A"):
                    rejection_distribution["GATE_FAIL_A"] += 1
                elif err_msg.startswith("GATE_FAIL_B"):
                    rejection_distribution["GATE_FAIL_B"] += 1
                elif err_msg.startswith("GATE_FAIL_C"):
                    rejection_distribution["GATE_FAIL_C"] += 1
                else:
                    rejection_distribution["UNEXPECTED_ERROR"] += 1
            except Exception as ex:
                rejection_distribution["UNEXPECTED_ERROR"] += 1

            if i % 2000 == 0 or i == N:
                elapsed = time.time() - start_time
                print(f"[{i:6d}/{N}] Progress: {i/N*100.0:5.1f}% | Caught: A={rejection_distribution['GATE_FAIL_A']} B={rejection_distribution['GATE_FAIL_B']} C={rejection_distribution['GATE_FAIL_C']} | Leaks={len(accepted_mutations)} | Time={elapsed:5.1f}s")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    total_time = time.time() - start_time
    survival_count = len(accepted_mutations)
    survival_rate = (survival_count / N) * 100.0

    print("\n================================================================================")
    print("MONTE CARLO MUTATION EXPERIMENT RESULTS:")
    print("================================================================================")
    print(f"Total Mutations Tested (N): {N:,}")
    print(f"Random Seed               : {seed}")
    print(f"Total Accepted / Survived : {survival_count}")
    print(f"Empirical Survival Rate   : {survival_rate:.4f}%\n")
    print(f"Rejection Breakdown by Verification Tier:")
    print(f"  - Klasa A (Static Envelope & Math Integrity) : {rejection_distribution['GATE_FAIL_A']:6d} ({rejection_distribution['GATE_FAIL_A']/N*100.0:5.2f}%)")
    print(f"  - Klasa B (Evidence Binding & Spec Matching) : {rejection_distribution['GATE_FAIL_B']:6d} ({rejection_distribution['GATE_FAIL_B']/N*100.0:5.2f}%)")
    print(f"  - Klasa C (Cold Re-Execution Output Mismatch): {rejection_distribution['GATE_FAIL_C']:6d} ({rejection_distribution['GATE_FAIL_C']/N*100.0:5.2f}%)")
    print(f"  - Unexpected Exceptions                     : {rejection_distribution['UNEXPECTED_ERROR']:6d}\n")
    print(f"Total Elapsed Time: {total_time:.2f}s ({N/total_time:.1f} iterations/sec)")
    print("================================================================================")

    if output_corpus:
        with open(output_corpus, "w") as f:
            json.dump({
                "seed": seed,
                "N": N,
                "survival_count": survival_count,
                "survival_rate_pct": survival_rate,
                "rejection_distribution": rejection_distribution,
                "leak_samples": accepted_mutations
            }, f, indent=2)
        print(f"Corpus of {survival_count} leak samples saved to: {output_corpus}")

    return survival_count

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    s = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    out = sys.argv[3] if len(sys.argv) > 3 else "/home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/nem-scarcity-s1/runs/2026-07/fuzz_leak_corpus_seed42.json"
    run_fuzzing_experiment(n, seed=s, output_corpus=out)
