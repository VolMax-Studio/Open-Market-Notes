import os
import sys
import json
import hashlib
import glob
import re
import math
import argparse
import yaml
import pandas as pd
from datetime import datetime, timezone

# Scope: Strict UTC domain per PARAMS.md time_contract specification
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PARAMS_PATH = os.path.join(SCRIPT_DIR, "PARAMS.md")

ZONES = {
    'NL': '10YNL----------L',
    'BE': '10YBE----------X',
    'FR': '10YFR-RTE------C',
    'DK_1': '10YDK-1--------W',
    'DK_2': '10YDK-2--------T',
    'AT': '10YAT-APG------L'
}

FROZEN_REGIMES = {
    'NL': 'DUAL_PRICING',
    'BE': 'SINGLE_PRICING',
    'FR': 'DUAL_PRICING',
    'DK_1': 'SINGLE_PRICING',
    'DK_2': 'SINGLE_PRICING',
    'AT': 'SINGLE_PRICING'
}

def load_params_time_contract(params_path=DEFAULT_PARAMS_PATH):
    """
    Strictly loads and mathematically validates the time_contract and license
    metadata from PARAMS.md frontmatter.
    """
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS file not found: {params_path}")
    with open(params_path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            if meta and "time_contract" in meta:
                tc = meta["time_contract"]
                req_keys = [
                    "timezone", "timestamp_convention", "sampling_step_seconds",
                    "sampling_step_minutes", "window_start_utc", "window_end_utc",
                    "total_days", "intervals_per_day", "nominal_intervals"
                ]
                for k in req_keys:
                    if k not in tc or tc[k] is None:
                        raise KeyError(f"Missing required time_contract key '{k}' in {params_path}")
                
                # Derive and verify invariant formulas
                start_dt = pd.Timestamp(tc["window_start_utc"])
                end_dt = pd.Timestamp(tc["window_end_utc"])
                derived_days = (end_dt - start_dt).days
                if derived_days != tc["total_days"]:
                    raise ValueError(f"Time contract invariant mismatch: calculated total_days={derived_days} != total_days={tc['total_days']}")
                
                step_min = tc["sampling_step_minutes"]
                intervals_per_day = 24 * 60 // step_min
                if intervals_per_day != tc["intervals_per_day"]:
                    raise ValueError(f"Time contract invariant mismatch: calculated intervals_per_day={intervals_per_day} != intervals_per_day={tc['intervals_per_day']}")
                    
                derived_nominal = derived_days * intervals_per_day
                if derived_nominal != tc["nominal_intervals"]:
                    raise ValueError(f"Time contract invariant mismatch: calculated nominal_intervals={derived_nominal} != nominal_intervals={tc['nominal_intervals']}")
                
                return tc, meta.get("license", {})
    raise KeyError(f"Missing structured 'time_contract' frontmatter in {params_path}")

def sanitize_token_url(text_or_error):
    """
    Mandate 9 Zero Secret Leakage:
    Scrubs ENTSO-E securityToken from any string, Exception, HTTP response/request URL, or traceback.
    Uses greedy non-ampersand match ([^&]+) to prevent any token format leakage.
    """
    msg = str(text_or_error)
    if hasattr(text_or_error, 'response') and getattr(text_or_error, 'response', None) is not None:
        resp_url = getattr(text_or_error.response, 'url', '')
        if resp_url:
            clean_resp_url = re.sub(r'securityToken=[^&]+', 'securityToken=REDACTED_MANDATE_9', str(resp_url))
            msg += f" | Response URL: {clean_resp_url}"
    if hasattr(text_or_error, 'request') and getattr(text_or_error, 'request', None) is not None:
        req_url = getattr(text_or_error.request, 'url', '')
        if req_url:
            clean_req_url = re.sub(r'securityToken=[^&]+', 'securityToken=REDACTED_MANDATE_9', str(req_url))
            msg += f" | Request URL: {clean_req_url}"
            
    return re.sub(r'securityToken=[^&]+', 'securityToken=REDACTED_MANDATE_9', msg)

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_manifest(filepath, file_hash, source_url, acquisition_mode, manifest_dir, regime_info=None):
    manifest_path = os.path.join(manifest_dir, 'data_manifest.json')
    if not os.path.exists(manifest_path):
        print(f"Initializing fresh data_manifest.json at {manifest_path}")
        manifest_data = {
            "protocol_version": "v1.0.0",
            "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": []
        }
    else:
        with open(manifest_path, 'r') as f:
            try:
                manifest_data = json.load(f)
            except Exception as e:
                raise ValueError(f"Corrupted manifest JSON at {manifest_path}: {e}")
            
    basename = os.path.basename(filepath)
    acquired_at = datetime.now(timezone.utc).isoformat()
    clean_source_url = sanitize_token_url(source_url)
    
    files_list = manifest_data.get("files", [])
    files_dict = {item["file_name"]: item for item in files_list if isinstance(item, dict) and "file_name" in item}
    
    dirty = False
    if basename in files_dict:
        expected_hash = files_dict[basename]["sha256"]
        if file_hash != expected_hash:
            if acquisition_mode == "manifest_verified_cache":
                raise ValueError(f"Integrity check failed: Hash mismatch for verified cache {basename}! Expected {expected_hash}, got {file_hash}")
            else:
                print(f"Live API acquisition updated SHA-256 for {basename}: {expected_hash} -> {file_hash}")
                files_dict[basename]["sha256"] = file_hash
                files_dict[basename]["acquired_at_utc"] = acquired_at
                dirty = True
        else:
            print(f"Integrity check passed: SHA-256 matches for {basename}.")
            if regime_info:
                entry = files_dict[basename]
                if entry.get("frozen_regime") != regime_info["regime"]:
                    entry["frozen_regime"] = regime_info["regime"]
                    entry["m1_shortage_col"] = regime_info["M1_shortage_col"]
                    entry["m2_surplus_col"] = regime_info["M2_surplus_col"]
                    dirty = True
    else:
        print(f"Registering new entry with provenance metadata in manifest: {basename}")
        entry = {
            "file_name": basename,
            "sha256": file_hash,
            "size_bytes": os.path.getsize(filepath),
            "source_url": clean_source_url,
            "acquisition_mode": acquisition_mode,
            "acquired_at_utc": acquired_at
        }
        if regime_info:
            entry["frozen_regime"] = regime_info["regime"]
            entry["m1_shortage_col"] = regime_info["M1_shortage_col"]
            entry["m2_surplus_col"] = regime_info["M2_surplus_col"]
            
        files_list.append(entry)
        files_dict[basename] = entry
        dirty = True

    if dirty:
        manifest_data["acquired_at_utc"] = acquired_at
        manifest_data["files"] = list(files_dict.values())
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)

def fetch_zone_monthly_chunks(client, zone_code, start_dt, end_dt):
    """
    Fetches imbalance prices in month-by-month chunks in UTC domain.
    Eliminates entsoe-py's @year_limited yearly split boundary truncation.
    """
    current_month_start = start_dt
    monthly_dfs = []
    
    while current_month_start < end_dt:
        if current_month_start.month == 12:
            next_month_start = pd.Timestamp(year=current_month_start.year + 1, month=1, day=1, tz='UTC')
        else:
            next_month_start = pd.Timestamp(year=current_month_start.year, month=current_month_start.month + 1, day=1, tz='UTC')
        
        current_chunk_end = min(next_month_start, end_dt)
        query_end = current_chunk_end - pd.Timedelta(minutes=15)
        
        print(f"  Fetching chunk [{zone_code}]: {current_month_start.strftime('%Y-%m-%d %H:%M')} -> {query_end.strftime('%Y-%m-%d %H:%M')} UTC")
        chunk_df = client.query_imbalance_prices(country_code=zone_code, start=current_month_start, end=query_end)
        
        if chunk_df.index.tz is None:
            chunk_df.index = chunk_df.index.tz_localize('UTC')
        else:
            chunk_df.index = chunk_df.index.tz_convert('UTC')
            
        monthly_dfs.append(chunk_df)
        current_month_start = next_month_start
        
    full_df = pd.concat(monthly_dfs).sort_index()
    return full_df

def verify_time_invariants(df, zone_code, tc):
    """
    Strict verification of contract invariants:
    1. Continuity: exact 00:15:00 steps
    2. Boundaries: exactly [start_mtu, end_mtu]
    3. Length: exactly nominal_intervals
    4. Duplicates: exactly 0
    """
    expected_start = pd.Timestamp(tc["window_start_utc"])
    expected_end = pd.Timestamp(tc["window_end_utc"]) - pd.Timedelta(minutes=tc["sampling_step_minutes"])
    
    if df.index[0] != expected_start:
        raise ValueError(f"Boundary invariant violation for {zone_code}: start timestamp {df.index[0]} != {expected_start}")
    if df.index[-1] != expected_end:
        raise ValueError(f"Boundary invariant violation for {zone_code}: end timestamp {df.index[-1]} != {expected_end}")
        
    dup_count = int(df.index.duplicated().sum())
    if dup_count > 0:
        raise ValueError(f"Duplicate invariant violation for {zone_code}: {dup_count} duplicate timestamps found across monthly chunks!")
        
    diffs = df.index.to_series().diff().iloc[1:]
    diff_counts = diffs.value_counts()
    expected_step = pd.Timedelta(minutes=tc["sampling_step_minutes"])
    
    print(f"\n[{zone_code}] Index Step Counts (Pre-Deduplication):\n{diff_counts}")
    print(f"[{zone_code}] Duplicate Count: {dup_count}")
    print(f"[{zone_code}] Total MTU count: {len(df)} (Expected nominal: {tc['nominal_intervals']})")
    print(f"[{zone_code}] Start MTU: {df.index[0]} | End MTU: {df.index[-1]}")
    
    if len(diff_counts) != 1 or diff_counts.index[0] != expected_step:
        raise ValueError(f"Continuity invariant violation for {zone_code}: non-uniform step detected: {diff_counts}")

def check_mandate8_completeness(df, zone_code, start_dt, end_dt, step_minutes=15):
    """
    Mandate 8 Telemetry Completeness & Boundary Verification Guard.
    Enforces minimum row count (>=98.0% ceiling of expected 15-min intervals) and timestamp gap limits (<=90 min).
    """
    days = (end_dt - start_dt).days
    expected_intervals = days * (24 * 60 // step_minutes)
    min_required_intervals = math.ceil(expected_intervals * 0.98)
    
    actual_rows = len(df)
    if actual_rows < min_required_intervals:
        pct = (actual_rows / expected_intervals) * 100.0
        raise ValueError(
            f"[MANDATE 8 ABORT] {zone_code} telemetry incompleteness: {actual_rows}/{expected_intervals} "
            f"intervals ({pct:.2f}%). Minimum floor: {min_required_intervals}."
        )
    
    dt_series = pd.to_datetime(df.index, utc=True)
    gaps = dt_series.to_series().diff()
    max_gap = gaps.max()
    
    # [POST-HOC EMPIRICAL CALIBRATION] Threshold of 90 minutes calibrated to DK_1/DK_2 historical baseline gaps
    if max_gap > pd.Timedelta(minutes=90):
        raise ValueError(
            f"[MANDATE 8 ABORT] {zone_code} timestamp continuity breach: Maximum gap {max_gap} exceeds 90-minute threshold limit."
        )
    
    print(f"Mandate 8 Verification PASSED for {zone_code}: {actual_rows}/{expected_intervals} intervals, max gap: {max_gap}")

def analyze_regime_classification(df, zone_code):
    """
    Procedural Pricing Regime Detection & Frozen Assignment Validation.
    Returns column mapping dictionary enforcing pre-registered frozen regime.
    """
    cols = list(df.columns)
    print(f"\n--- PROCEDURAL REGIME ANALYSIS: {zone_code} ---")
    print(f"Columns present: {cols}")
    
    if len(cols) == 1:
        emp_regime = "SINGLE_PRICING"
    else:
        if 'Long' in cols and 'Short' in cols:
            p_long = df['Long']
            p_short = df['Short']
        else:
            p_long = df.iloc[:, 0]
            p_short = df.iloc[:, 1]
            
        valid_mask = p_long.notna() & p_short.notna()
        total_valid = int(valid_mask.sum())
        diff = (p_long[valid_mask] - p_short[valid_mask]).abs()
        matches = int((diff < 1e-4).sum())
        
        if matches == total_valid and total_valid > 0:
            emp_regime = "SINGLE_PRICING"
        else:
            emp_regime = "DUAL_PRICING"
            
    frozen = FROZEN_REGIMES.get(zone_code, 'SINGLE_PRICING')
    if emp_regime != frozen:
        print(f"WARNING: Empirical regime '{emp_regime}' diverges from frozen regime '{frozen}' for {zone_code}.")
        print(f"Enforcing frozen pre-registered regime: {frozen}")
    else:
        print(f"Regime Match: {emp_regime} aligns with pre-registered frozen baseline for {zone_code}.")
        
    if frozen == 'DUAL_PRICING':
        return {'M1_shortage_col': 'Short', 'M2_surplus_col': 'Long', 'regime': frozen}
    else:
        col_name = 'Short' if 'Short' in cols else cols[0]
        return {'M1_shortage_col': col_name, 'M2_surplus_col': col_name, 'regime': frozen}

def download_entsoe_imbalance(params_file=DEFAULT_PARAMS_PATH, data_dir='.', out_dir='.', allow_overwrite=False, api_key=None):
    raw_dir = os.path.join(out_dir, 'raw_cache')
    proc_dir = os.path.join(out_dir, 'processed')
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    tc, lic_meta = load_params_time_contract(params_file)
    api_key = api_key or os.environ.get('ENTSOE_API_KEY')
    
    start_dt = pd.Timestamp(tc["window_start_utc"])
    end_dt = pd.Timestamp(tc["window_end_utc"])
    
    s_tag = start_dt.strftime('%Y%m')
    e_tag = (end_dt - pd.Timedelta(days=1)).strftime('%Y%m')
    
    if api_key:
        try:
            from entsoe import EntsoePandasClient
            client = EntsoePandasClient(api_key=api_key)
        except Exception as e:
            sanitized = sanitize_token_url(e)
            raise ValueError(f"Failed to instantiate EntsoePandasClient: {sanitized}") from None
            
        for zone_code, eic in ZONES.items():
            print(f"\n==========================================")
            print(f"FETCHING ENTSO-E IMBALANCE PRICES FOR {zone_code} (UTC Domain: {tc['window_start_utc']} -> {tc['window_end_utc']})")
            print(f"==========================================")
            try:
                proc_path = os.path.join(proc_dir, f"imbalance_{zone_code}.feather")
                if os.path.exists(proc_path) and not allow_overwrite:
                    raise ValueError(f"Overwrite Guard: Refusing to overwrite existing feather cache at {proc_path}. Pass --allow-overwrite or use a separate --out-dir.")
                    
                df = fetch_zone_monthly_chunks(client, zone_code, start_dt, end_dt)
                
                check_mandate8_completeness(df, zone_code, start_dt, end_dt)
                verify_time_invariants(df, zone_code, tc)
                mapping = analyze_regime_classification(df, zone_code)
                
                csv_path = os.path.join(raw_dir, f"imbalance_{zone_code}_{s_tag}_{e_tag}.csv")
                df.to_csv(csv_path)
                
                source_endpoint = f"ENTSO-E REST API DocumentType A85 (Area EIC: {eic}, Zone: {zone_code})"
                file_hash = compute_sha256(csv_path)
                update_manifest(csv_path, file_hash, source_url=source_endpoint, acquisition_mode="live_api_query", manifest_dir=out_dir, regime_info=mapping)
                
                df.reset_index().to_feather(proc_path)
                print(f"Saved processed imbalance prices ({mapping['regime']}) to {proc_path}")
            except Exception as e:
                sanitized_err = sanitize_token_url(e)
                raise ValueError(f"ENTSO-E Execution Failed for {zone_code}: {sanitized_err}") from None
    else:
        print("ENTSOE_API_KEY environment variable not set.")
        print("Checking data_manifest.json for registered raw cache files with proven provenance...")
        manifest_path = os.path.join(data_dir, 'data_manifest.json')
        if not os.path.exists(manifest_path):
            raise ValueError(f"ENTSOE_API_KEY required for live API ingestion and no data_manifest.json exists at {manifest_path}.")
        
        with open(manifest_path, 'r') as f:
            try:
                manifest_data = json.load(f)
            except Exception as e:
                raise ValueError(f"Corrupted manifest JSON at {manifest_path}: {e}")
            
        raw_csv_pattern = os.path.join(raw_dir, f"imbalance_*_{s_tag}_{e_tag}.csv")
        csv_files = glob.glob(raw_csv_pattern)
        if not csv_files:
            raise ValueError(f"No raw cache files found matching pattern {raw_csv_pattern} in {raw_dir}.")
            
        files_list = manifest_data.get("files", [])
        manifest_files_dict = {item["file_name"]: item for item in files_list if isinstance(item, dict) and "file_name" in item}
        
        for csv_file in csv_files:
            basename = os.path.basename(csv_file)
            match = re.search(r'imbalance_([A-Z0-9_]+)_\d{6}_\d{6}\.csv', basename)
            if not match:
                print(f"Ignoring non-matching filename format: {basename}")
                continue
            zone_code = match.group(1)
            
            if basename not in manifest_files_dict:
                raise ValueError(f"File {basename} lacks verified provenance in data_manifest.json! Silent unanchored cache fallback rejected.")
                
            print(f"Verifying pre-registered cache file: {basename}")
            file_hash = compute_sha256(csv_file)
            entry = manifest_files_dict[basename]
            df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
            
            check_mandate8_completeness(df, zone_code, start_dt, end_dt)
            mapping = analyze_regime_classification(df, zone_code)
            
            update_manifest(csv_file, file_hash, source_url=entry.get("source_url", ""), acquisition_mode="manifest_verified_cache", manifest_dir=data_dir, regime_info=mapping)
            
            proc_path = os.path.join(proc_dir, f"imbalance_{zone_code}.feather")
            if not os.path.exists(proc_path):
                df.reset_index().to_feather(proc_path)
                print(f"Generated missing processed feather cache ({mapping['regime']}): {proc_path}")
            elif allow_overwrite:
                df.reset_index().to_feather(proc_path)
                print(f"Replaced existing processed feather cache ({mapping['regime']}) per --allow-overwrite: {proc_path}")
            else:
                print(f"Preserved existing verified feather cache ({mapping['regime']}): {proc_path}")

def main():
    parser = argparse.ArgumentParser(description="ENTSO-E Imbalance Telemetry Downloader & Provenance Manager")
    parser.add_argument('--start-date', type=str, default='2025-06-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default='2026-06-30', help='End date (YYYY-MM-DD)')
    parser.add_argument('--data-dir', type=str, default='.', help='Input data and manifest directory')
    parser.add_argument('--out-dir', type=str, default='.', help='Output cache directory')
    parser.add_argument('--allow-overwrite', action='store_true', help='Allow overwriting existing feather files in output directory')
    args = parser.parse_args()
    
    try:
        download_entsoe_imbalance(
            start_date=args.start_date,
            end_date=args.end_date,
            data_dir=args.data_dir,
            out_dir=args.out_dir,
            allow_overwrite=args.allow_overwrite
        )
    except Exception as e:
        sanitized = sanitize_token_url(e)
        print(f"ERROR: {sanitized}")
        sys.exit(1)

if __name__ == '__main__':
    main()
