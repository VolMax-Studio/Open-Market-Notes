#!/usr/bin/env python3
"""
VolMax Open Market Notes — Automated Recurrence Script
Governed by Recurrence Specification

This script executes the rolling 13-month recurrent measurement pipeline,
verifies telemetry completeness and PARAMS/pipeline immutability, appends to the
versioned measurement log with full Quad-Hash provenance, and generates a dynamic PR summary.
"""

import os
import sys
import json
import hashlib
import datetime
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "notes_registry.json")
SPEC_PATH = os.path.join(BASE_DIR, "RECURRENCE_SPEC.md")

NOTE_PIPELINE_MAP = {
    "001": {
        "folder": "notes/001-nem-duration-baseline",
        "download_script": "download_aemo_data.py",
        "analysis_script": "reproduce.py",
        "parameterized": True
    },
    "002": {
        "folder": "notes/002-ercot-duration-baseline",
        "download_script": "download_ercot_data.py",
        "analysis_script": "reproduce.py",
        "parameterized": False
    },
    "003": {
        "folder": "notes/003-entsoe-imbalance-baseline",
        "download_script": "download_entsoe_data.py",
        "analysis_script": "run_imbalance_analysis.py",
        "parameterized": False
    },
    "004": {
        "folder": "notes/004-gb-duration-baseline",
        "download_script": "download_elexon_data.py",
        "analysis_script": "run_analysis.py",
        "parameterized": False
    },
    "005": {
        "folder": "notes/005-entsoe-crossborder-flows",
        "download_script": "download_all_corridors.py",
        "analysis_script": "run_pipeline.py",
        "parameterized": False
    }
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_spec_version():
    if os.path.exists(SPEC_PATH):
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("**Version:**"):
                    return line.split("**Version:**")[1].strip()
    return "v1.0.6"

def get_git_commit_sha():
    if "GITHUB_SHA" in os.environ and os.environ["GITHUB_SHA"].strip():
        return os.environ["GITHUB_SHA"].strip()
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        sha = res.stdout.strip()
        if len(sha) == 40:
            return sha
        raise ValueError(f"Invalid Git SHA length: {sha}")
    except Exception as e:
        print(f"FATAL ERROR (Mandate 4 Abort): Unable to resolve pipeline_commit_sha! Details: {e}")
        sys.exit(1)

def calculate_rolling_window(reference_date=None):
    if reference_date is None:
        reference_date = datetime.date.today()
    
    # 1. Last fully completed calendar month end
    first_of_curr = reference_date.replace(day=1)
    last_completed_month_end = first_of_curr - datetime.timedelta(days=1)
    
    end_year = last_completed_month_end.year
    end_month = last_completed_month_end.month
    
    # 2. 13 full calendar months back (start_month == end_month, start_year == end_year - 1)
    start_year = end_year - 1
    start_month = end_month
    
    start_date_str = f"{start_year:04d}-{start_month:02d}-01"
    end_date_str = f"{end_year:04d}-{end_month:02d}-{last_completed_month_end.day:02d}"
    return start_date_str, end_date_str

def generate_expected_months(start_date_str, end_date_str):
    start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    
    months = []
    curr = datetime.datetime(start_dt.year, start_dt.month, 1)
    end_month_dt = datetime.datetime(end_dt.year, end_dt.month, 1)
    
    while curr <= end_month_dt:
        months.append(f"{curr.year:04d}{curr.month:02d}")
        if curr.month == 12:
            curr = datetime.datetime(curr.year + 1, 1, 1)
        else:
            curr = datetime.datetime(curr.year, curr.month + 1, 1)
    return months

def main():
    parser = argparse.ArgumentParser(description="Execute VolMax Recurrent Measurement Pipeline")
    parser.add_argument("--note-id", default="001", help="Note number (e.g. 001)")
    parser.add_argument("--start-date", default=None, help="Override start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="Override end date (YYYY-MM-DD)")
    args = parser.parse_args()

    spec_ver = get_spec_version()

    note_num = args.note_id.zfill(3)
    if note_num not in NOTE_PIPELINE_MAP:
        print(f"FATAL ERROR: Note #{note_num} not recognized in NOTE_PIPELINE_MAP!")
        sys.exit(1)
        
    config = NOTE_PIPELINE_MAP[note_num]
    if not config["parameterized"]:
        print(f"FATAL ERROR: Note #{note_num} pipeline is not yet date-parameterized!")
        print("Parametric changelog and date parameterization PR required before recurrent execution.")
        sys.exit(1)

    # 1. Read Frozen Registry Entry
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    registry_entry = next((e for e in registry if e["note_number"] == note_num), None)
    if not registry_entry:
        print(f"FATAL ERROR (Registry Missing): Note #{note_num} not found in notes_registry.json!")
        sys.exit(1)

    note_dir = os.path.join(BASE_DIR, config["folder"])
    folder_name = os.path.basename(note_dir)
    print(f"=== RECURRENT MEASUREMENT RUNNER — NOTE #{note_num} ({folder_name}) ===")
    print(f"Governed by Recurrence Specification {spec_ver}")
    
    # 2. Mandate 3: PARAMS.md & Pipeline Script Immutability Verification against Frozen Registry Reference
    params_file = os.path.join(note_dir, "PARAMS.md")
    if not os.path.exists(params_file):
        print(f"FATAL ERROR (Mandate 3 Abort): PARAMS.md missing at {params_file}")
        sys.exit(1)
        
    expected_params_sha256 = registry_entry.get("params_sha256")
    if expected_params_sha256 is None:
        print(f"FATAL ERROR (Mandate 3 Abort): Frozen registry missing params_sha256 for Note #{note_num}!")
        sys.exit(1)

    actual_params_sha256 = compute_sha256(params_file)
    if actual_params_sha256 != expected_params_sha256:
        print(f"FATAL ERROR (Mandate 3 Abort): PARAMS.md hash mismatch!")
        print(f"  Expected (Frozen Baseline): {expected_params_sha256}")
        print(f"  Actual:                    {actual_params_sha256}")
        print("ABORTING WORKFLOW — PARAMS.MD WAS MODIFIED. NO PULL REQUEST WILL BE OPENED.")
        sys.exit(1)

    reproduce_script = os.path.join(note_dir, config["analysis_script"])
    expected_reproduce_sha256 = registry_entry.get("reproduce_sha256")
    if expected_reproduce_sha256 is None:
        print(f"FATAL ERROR (Mandate 3 Abort): Frozen registry missing reproduce_sha256 for Note #{note_num}!")
        sys.exit(1)

    actual_reproduce_sha256 = compute_sha256(reproduce_script)
    if actual_reproduce_sha256 != expected_reproduce_sha256:
        print(f"FATAL ERROR (Mandate 3 Abort): Analytical script ({config['analysis_script']}) hash mismatch!")
        print(f"  Expected (Frozen Baseline): {expected_reproduce_sha256}")
        print(f"  Actual:                    {actual_reproduce_sha256}")
        print("ABORTING WORKFLOW — PIPELINE SCRIPT WAS MODIFIED. NO PULL REQUEST WILL BE OPENED.")
        sys.exit(1)
            
    print(f"Mandate 3 Check PASSED: PARAMS.md ({actual_params_sha256[:12]}...) and pipeline script ({actual_reproduce_sha256[:12]}...) immutability verified.")

    # 3. Determine target rolling window dynamically if not provided
    if args.start_date and args.end_date:
        start_date, end_date = args.start_date, args.end_date
    else:
        start_date, end_date = calculate_rolling_window()
        
    print(f"Calculated 13-Month Rolling Window: {start_date} to {end_date}")
    
    # 4. Step 3: Execute Telemetry Download if download script exists
    download_script_name = config["download_script"]
    if download_script_name:
        download_script = os.path.join(note_dir, download_script_name)
        if os.path.exists(download_script):
            print("\n--- Executing Telemetry Download ---")
            cmd = [sys.executable, download_script, "--start-date", start_date, "--end-date", end_date]
            res = subprocess.run(cmd, cwd=note_dir, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"FATAL ERROR (Download Failed):\n{res.stderr[:500]}")
                sys.exit(1)
            print("Telemetry download completed successfully.")
            
    # 5. Mandate 8: Telemetry Completeness & Boundary Verification (STRICT NO-BYPASS)
    # Check root telemetry dir if present, else note-level dir
    root_proc_dir = os.path.join(BASE_DIR, "data", "processed")
    proc_dir = root_proc_dir if (os.path.exists(root_proc_dir) and len(os.listdir(root_proc_dir)) > 0) else os.path.abspath(os.path.join(note_dir, "data", "processed"))
    
    expected_months = generate_expected_months(start_date, end_date)
    print(f"\n--- Mandate 8 Check: Verifying {len(expected_months)} Expected Monthly Telemetry Files in {proc_dir} ---")
    
    if not os.path.exists(proc_dir):
        print(f"FATAL ERROR (Mandate 8 Abort): Processed telemetry directory missing: {proc_dir}")
        print("ABORTING WORKFLOW — NO PULL REQUEST WILL BE OPENED.")
        sys.exit(1)
        
    missing_files = []
    for ym in expected_months:
        price_file = os.path.join(proc_dir, f"price_{ym}.feather")
        scada_file = os.path.join(proc_dir, f"scada_{ym}.feather")
        for filepath, label in [(price_file, f"price_{ym}.feather"), (scada_file, f"scada_{ym}.feather")]:
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                missing_files.append(label)
            else:
                try:
                    df = pd.read_feather(filepath)
                    if len(df) == 0:
                        missing_files.append(f"{label} (0 rows)")
                except Exception:
                    missing_files.append(f"{label} (corrupt/unreadable)")
            
    if missing_files:
        print(f"FATAL ERROR (Mandate 8 Abort): Missing or empty monthly telemetry files for: {missing_files}")
        print("ABORTING WORKFLOW — NO PULL REQUEST WILL BE OPENED.")
        sys.exit(1)
        
    print(f"Mandate 8 Check PASSED: All {len(expected_months)*2} monthly telemetry files (price + scada) verified in {proc_dir}.")

    # 6. Execute Analytical Pipeline with cwd=note_dir and explicit --data-dir
    print(f"\n--- Executing Analytical Pipeline ({os.path.basename(reproduce_script)}) ---")
    cmd = [sys.executable, reproduce_script, "--start-date", start_date, "--end-date", end_date, "--data-dir", proc_dir]
    res = subprocess.run(cmd, cwd=note_dir, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FATAL ERROR (Pipeline Failed):\n{res.stderr[:500]}")
        sys.exit(1)
    print("Pipeline execution completed successfully.")
    
    # 7. Compute SHA-256 Hashes & Pipeline Commit SHA
    results_json_path = os.path.join(note_dir, "results.json")
    manifest_json_path = os.path.join(note_dir, "data_manifest.json")
    
    if not os.path.exists(results_json_path) or not os.path.exists(manifest_json_path):
        print("FATAL ERROR: Missing results.json or data_manifest.json outputs!")
        sys.exit(1)
        
    calc_results_sha256 = compute_sha256(results_json_path)
    calc_manifest_sha256 = compute_sha256(manifest_json_path)
    pipeline_commit_sha = get_git_commit_sha()
    
    print(f"\nResults Output Hash (`results_sha256`): {calc_results_sha256}")
    print(f"Input Manifest Hash (`input_manifest_sha256`): {calc_manifest_sha256}")
    print(f"PARAMS Parameters Hash (`params_sha256`): {actual_params_sha256}")
    print(f"Script Pipeline Hash (`reproduce_sha256`): {actual_reproduce_sha256}")
    print(f"Pipeline Commit SHA (`pipeline_commit_sha`): {pipeline_commit_sha}")

    # 8. Mandate 4, 5 & 6: Appending to history/measurement_log.json
    history_dir = os.path.join(note_dir, "history")
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, "measurement_log.json")
    
    history_log = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_log = json.load(f)
        except Exception:
            history_log = []
            
    # Calculate next version dynamically
    if not history_log:
        next_version = "v1.1.0"
    else:
        last_ver = history_log[-1].get("version", "v1.0.0")
        parts = last_ver.lstrip("v").split(".")
        if len(parts) == 3:
            minor = int(parts[1]) + 1
            next_version = f"v{parts[0]}.{minor}.0"
        else:
            next_version = "v1.1.0"
            
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_entry = {
        "version": next_version,
        "measurement_window": f"{start_date} to {end_date}",
        "results_sha256": calc_results_sha256,
        "input_manifest_sha256": calc_manifest_sha256,
        "params_sha256": actual_params_sha256,
        "reproduce_sha256": actual_reproduce_sha256,
        "pipeline_commit_sha": pipeline_commit_sha,
        "executed_at": now_utc
    }
    history_log.append(new_entry)
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_log, f, indent=2)
    print(f"Appended entry ({next_version}) to history/measurement_log.json.")

    # 9. Generate Dynamic PR Body outside git repository tree
    runner_temp = os.environ.get("RUNNER_TEMP", os.environ.get("TMPDIR", "/tmp"))
    pr_body_path = os.path.join(runner_temp, "pr_body.md")
    
    pr_body = f"""## VolMax Recurrent Measurement PR — OMN-{note_num} ({next_version})

This automated Pull Request presents a recurrent measurement baseline refresh executed per **Recurrence Specification {spec_ver}**.

### Verification Summary:
- **Target Note:** Open Market Note #{note_num} (`OMN-{note_num}`)
- **Version:** `{next_version}`
- **Calculated Rolling Window:** `{start_date} to {end_date}`
- **Mandate 3 PARAMS Check:** PASSED (`{actual_params_sha256[:12]}...` verified against frozen registry reference).
- **Mandate 3 Script Check:** PASSED (`{actual_reproduce_sha256[:12]}...` verified against frozen registry reference).
- **Mandate 8 Abort Check:** PASSED ({len(expected_months)} expected monthly telemetry files verified).

### Quad-Hash Provenance Stack:
1. **`results_sha256` (Analytical Output):** `{calc_results_sha256}`
2. **`input_manifest_sha256` (Telemetry Input):** `{calc_manifest_sha256}`
3. **`params_sha256` (PARAMS Parameters):** `{actual_params_sha256}`
4. **`reproduce_sha256` (Analytical Script):** `{actual_reproduce_sha256}`
5. **`pipeline_commit_sha` (Pipeline Code):** `{pipeline_commit_sha}`
- **`executed_at`:** `{now_utc}`

### Included Payload Files:
- `notes/{folder_name}/results.json`
- `notes/{folder_name}/data_manifest.json`
- `notes/{folder_name}/history/measurement_log.json`
- `notes/{folder_name}/results/*.png`

---
*Review the diff carefully. Click **Merge pull request** to ratify this measurement into main.*
"""
    with open(pr_body_path, "w", encoding="utf-8") as f:
        f.write(pr_body)
    print(f"Generated dynamic PR body at {pr_body_path}.")

if __name__ == "__main__":
    main()
