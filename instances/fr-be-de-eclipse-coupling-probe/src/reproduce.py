#!/usr/bin/env python3
"""
reproduce.py — Single entry-point reproduction runner for fr-be-de-eclipse-coupling-probe.
Executes audit acquisition, verifies machine-readable results against pinned SHA-256,
and regenerates the audit figure.
"""

import os
import sys
import hashlib
import subprocess

EXPECTED_RESULTS_SHA256 = "4e4c3b06b8116fd8d72f5a019f118c01a23d2eb8e3d1de6f0133bd5604040e63"
EXPECTED_LOOKUPS_SHA256 = "8ccb9d803e74b202dc5856120c76a0d25d0e1543b132c9d69e98b5e752c7abfe"

INSTANCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(INSTANCE_DIR, "results.json")
LOOKUPS_PATH = os.path.join(INSTANCE_DIR, "data", "coupling_lookups.csv")
AUDIT_SCRIPT = os.path.join(INSTANCE_DIR, "src", "run_audit.py")
FIGURE_SCRIPT = os.path.join(INSTANCE_DIR, "src", "make_figure.py")

print("=== VOLMAX P10 DETERMINISTIC REPRODUCTION: FR/BE/DE ECLIPSE COUPLING PROBE ===\n")

# Check API Token
if not os.environ.get("ENTSOE_API_KEY"):
    key_path = os.path.expanduser("~/Documents/Kljucevi/apientso.txt")
    if not os.path.exists(key_path):
        print("[ERROR] ENTSOE_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please export your API key before running reproduction:\n  export ENTSOE_API_KEY=\"<your-token>\"\n", file=sys.stderr)
        sys.exit(1)

# 1. Run Audit
print("--- [1/2] Executing run_audit.py against ENTSO-E API ---")
res_audit = subprocess.run([sys.executable, AUDIT_SCRIPT], cwd=INSTANCE_DIR)
if res_audit.returncode != 0:
    print(f"\n[FAILURE] run_audit.py exited with error code {res_audit.returncode}", file=sys.stderr)
    sys.exit(1)

# 2. Run Figure Generation
print("\n--- [2/2] Generating audit figure from coupling_lookups.csv ---")
res_fig = subprocess.run([sys.executable, FIGURE_SCRIPT], cwd=INSTANCE_DIR)
if res_fig.returncode != 0:
    print(f"\n[FAILURE] make_figure.py exited with error code {res_fig.returncode}", file=sys.stderr)
    sys.exit(1)

# 3. Verify Hashes
actual_results_hash = hashlib.sha256(open(RESULTS_PATH, "rb").read()).hexdigest()
actual_lookups_hash = hashlib.sha256(open(LOOKUPS_PATH, "rb").read()).hexdigest()

print("\n=======================================================")
print("INTEGRITY & DETERMINISM VERIFICATION REPORT")
print("=======================================================")
print(f"results.json expected : {EXPECTED_RESULTS_SHA256}")
print(f"results.json actual   : {actual_results_hash}")
print(f"lookups.csv expected  : {EXPECTED_LOOKUPS_SHA256}")
print(f"lookups.csv actual    : {actual_lookups_hash}")

mismatch = False
if actual_results_hash != EXPECTED_RESULTS_SHA256:
    print("[FAIL] results.json hash mismatch!", file=sys.stderr)
    mismatch = True

if actual_lookups_hash != EXPECTED_LOOKUPS_SHA256:
    print("[FAIL] coupling_lookups.csv hash mismatch!", file=sys.stderr)
    mismatch = True

if mismatch:
    print("\nVERDICT: MISMATCH (Audit output diverged from frozen baseline)", file=sys.stderr)
    sys.exit(1)
else:
    print("\nVERDICT: REPRODUCED: OK (Byte-for-byte identical output verified)")
    sys.exit(0)
