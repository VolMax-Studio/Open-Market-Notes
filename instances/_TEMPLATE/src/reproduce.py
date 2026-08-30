#!/usr/bin/env python3
"""
Canonical reproduction entry point for template instance.
Runs the audit, regenerates results.json, and verifies against expected sha256.
"""

import os
import sys
import hashlib
import subprocess

EXPECTED_RESULTS_SHA256 = "<sha256-placeholder>"

INSTANCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(INSTANCE_DIR, "results.json")
RUNNER_PATH = os.path.join(INSTANCE_DIR, "src", "run_audit.py")

print("=== VOLMAX P10 DETERMINISTIC REPRODUCTION RUNNER ===\n")

# 1. Check Execution
cmd = [sys.executable, RUNNER_PATH]
res = subprocess.run(cmd, cwd=INSTANCE_DIR)
if res.returncode != 0:
    print(f"\n[FAILURE] Execution failed with exit code {res.returncode}", file=sys.stderr)
    sys.exit(1)

# 2. Check Results Hash
if not os.path.exists(RESULTS_PATH):
    print(f"\n[FAILURE] results.json not found at {RESULTS_PATH}", file=sys.stderr)
    sys.exit(1)

actual_hash = hashlib.sha256(open(RESULTS_PATH, "rb").read()).hexdigest()

print("\n=== INTEGRITY & DETERMINISM VERIFICATION ===")
print(f"Expected results.json SHA-256 : {EXPECTED_RESULTS_SHA256}")
print(f"Actual results.json SHA-256   : {actual_hash}")

if actual_hash == EXPECTED_RESULTS_SHA256:
    print("\nVERDICT: REPRODUCED: OK (byte-identical match)")
    sys.exit(0)
else:
    print("\nVERDICT: MISMATCH (hash divergence)", file=sys.stderr)
    sys.exit(1)
