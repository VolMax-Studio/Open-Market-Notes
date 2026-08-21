#!/usr/bin/env python3
import sys
import os
import json
import hashlib
import calendar

class VerdictVerificationError(Exception):
    pass

def verify_verdict_dict(v_dict, inputs_dir=None, script_path=None):
    # 1. Structural Completeness & Integrity Digest
    required_sections = [
        "verdict_version", "claim", "evidence_boundary", "frozen_rule",
        "execution_and_metrics", "verdict", "admissibility", "reproducibility", "integrity_digest"
    ]
    for sec in required_sections:
        if sec not in v_dict:
            raise VerdictVerificationError(f"REJECT: MISSING_SECTION_{sec.upper()}")

    claimed_digest = v_dict["integrity_digest"]
    copy_dict = {k: v for k, v in v_dict.items() if k != "integrity_digest"}
    canonical_str = json.dumps(copy_dict, sort_keys=True, indent=2)
    computed_digest = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
    
    if computed_digest != claimed_digest:
        raise VerdictVerificationError(f"REJECT: INTEGRITY_DIGEST_MISMATCH (expected {claimed_digest}, got {computed_digest})")

    claim = v_dict["claim"]
    eb = v_dict["evidence_boundary"]
    fr = v_dict["frozen_rule"]
    em = v_dict["execution_and_metrics"]
    vd = v_dict["verdict"]
    adm = v_dict["admissibility"]
    rep = v_dict["reproducibility"]

    # 2. Claim & Temporal Evidence Boundary Alignment (NC-1)
    window = claim.get("window", "")
    try:
        year, month = map(int, window.split('-'))
        days_in_month = calendar.monthrange(year, month)[1]
    except Exception:
        raise VerdictVerificationError("REJECT: CLAIM_EVIDENCE_MISMATCH (invalid window format)")

    expected_p_start = f"{year:04d}-{month:02d}-01T00:00:00Z"
    expected_p_end = f"{year:04d}-{month:02d}-{days_in_month:02d}T23:59:59Z"

    if eb.get("period_start_utc") != expected_p_start or eb.get("period_end_utc") != expected_p_end:
        raise VerdictVerificationError("REJECT: CLAIM_EVIDENCE_MISMATCH (period bounds mismatch claim window)")

    # 3. Evidence Boundary Internal Arithmetic (NC-2)
    expected_nominal = days_in_month * 288
    if eb.get("nominal_intervals") != expected_nominal:
        raise VerdictVerificationError("REJECT: EVIDENCE_INTEGRITY_MISMATCH (nominal_intervals mismatch)")

    rec = eb.get("received_intervals", 0)
    if rec > expected_nominal:
        raise VerdictVerificationError("REJECT: EVIDENCE_INTEGRITY_MISMATCH (received exceeds nominal)")

    expected_missing = expected_nominal - rec
    if eb.get("missing_intervals_tail") != expected_missing:
        raise VerdictVerificationError("REJECT: EVIDENCE_INTEGRITY_MISMATCH (missing_intervals_tail arithmetic mismatch)")

    expected_comp = round((rec / expected_nominal) * 100.0, 4)
    if round(float(eb.get("completeness_pct", 0.0)), 4) != expected_comp:
        raise VerdictVerificationError("REJECT: EVIDENCE_INTEGRITY_MISMATCH (completeness_pct arithmetic mismatch)")

    # 4. Frozen Rule Hash & Parameter Verification (NC-3)
    params = fr.get("parameters", {})
    s_thresh_pct = float(params.get("s_thresh_pct", 0.0))
    q_ref = float(params.get("q_ref", 0.0))
    k_mult = float(params.get("k_mult", 0.0))
    if round(k_mult * (1.0 - q_ref) * 100.0, 4) != round(s_thresh_pct, 4):
        raise VerdictVerificationError("REJECT: FROZEN_RULE_HASH_MISMATCH (s_thresh_pct != k_mult * (1 - q_ref))")

    if script_path and os.path.exists(script_path):
        with open(script_path, "rb") as f:
            actual_script_sha = hashlib.sha256(f.read()).hexdigest()
        if actual_script_sha != fr.get("rule_script_sha256"):
            raise VerdictVerificationError(f"REJECT: FROZEN_RULE_HASH_MISMATCH (rule_script_sha256 expected {fr.get('rule_script_sha256')}, got {actual_script_sha})")

    # 5. Deterministic Logic and Metric Verification (NC-4)
    zone_metrics = em.get("zone_metrics", {})
    comp_floor = float(eb.get("completeness_floor_pct", 98.0))
    actual_comp = float(eb.get("completeness_pct", 0.0))
    
    n_elevated_counted = 0
    comparison_zones = [z for z, zm in zone_metrics.items() if z != "TAS1"] # TAS1 is companion

    for z, zm in zone_metrics.items():
        is_comp = (z in comparison_zones)
        st = zm.get("status")
        exp_lower = float(zm.get("exposure_lower_pct", 0.0))
        exp_upper = float(zm.get("exposure_upper_pct", 100.0))
        
        if actual_comp < comp_floor:
            expected_status = "INCOMPLETE"
        elif exp_lower >= s_thresh_pct:
            expected_status = "ELEVATED"
            if is_comp:
                n_elevated_counted += 1
        elif exp_upper < s_thresh_pct:
            expected_status = "NOT_ELEVATED"
        else:
            expected_status = "INDETERMINATE"
            
        if st != expected_status:
            raise VerdictVerificationError(f"REJECT: DETERMINISTIC_LOGIC_VIOLATION (zone {z} status {st} != expected {expected_status})")

    if em.get("N_elevated") != n_elevated_counted:
        raise VerdictVerificationError("REJECT: DETERMINISTIC_LOGIC_VIOLATION (N_elevated count mismatch)")

    n_low = int(params.get("n_low", 1))
    n_high = int(params.get("n_high", 3))

    if actual_comp < comp_floor:
        expected_eval_status = "INCOMPLETE"
        expected_label = "UNRESOLVED"
    else:
        expected_eval_status = "EVALUATED"
        if n_elevated_counted >= n_high:
            expected_label = "HIGH_ELEVATION"
        elif n_elevated_counted >= n_low:
            expected_label = "ELEVATED"
        else:
            expected_label = "NULL"

    if vd.get("evaluation_status") != expected_eval_status or vd.get("label") != expected_label:
        raise VerdictVerificationError(f"REJECT: DETERMINISTIC_LOGIC_VIOLATION (verdict label {vd.get('label')} != expected {expected_label})")

    # 6. Admissibility Policy Verification (NC-5)
    pub_status = adm.get("publication_status")
    src_lic = adm.get("source_license", "")
    if pub_status not in ["PUBLIC_PERMITTED", "RESTRICTED_NDA", "TRUSTED_PARTY_ONLY"]:
        raise VerdictVerificationError("REJECT: ADMISSIBILITY_POLICY_VIOLATION (invalid publication_status)")
    if pub_status == "PUBLIC_PERMITTED" and not ("CC BY" in src_lic or "Open" in src_lic or "Public" in src_lic):
        raise VerdictVerificationError("REJECT: ADMISSIBILITY_POLICY_VIOLATION (public status without compatible license)")

    # 7. Input Manifest Hash Verification (NC-6)
    if inputs_dir and os.path.exists(inputs_dir):
        manifest_path = os.path.join(inputs_dir, "MANIFEST.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "rb") as f:
                actual_man_sha = hashlib.sha256(f.read()).hexdigest()
            if actual_man_sha != rep.get("inputs_manifest_sha256"):
                raise VerdictVerificationError(f"REJECT: INPUT_MANIFEST_HASH_MISMATCH (manifest expected {rep.get('inputs_manifest_sha256')}, got {actual_man_sha})")

    # 8. Reproducibility Recipe Presence (NC-7)
    recipe = rep.get("reproduce_recipe", "")
    if not recipe or len(recipe.strip()) == 0 or "run_window.py" not in recipe:
        raise VerdictVerificationError("REJECT: REPRODUCTION_FAILED (reproduce_recipe missing or broken)")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: verify_verdict.py <path_to_VERDICT.json> [inputs_dir] [script_path]")
        sys.exit(1)
        
    v_path = sys.argv[1]
    in_dir = sys.argv[2] if len(sys.argv) > 2 else None
    sc_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(v_path) as f:
        data = json.load(f)
        
    try:
        verify_verdict_dict(data, inputs_dir=in_dir, script_path=sc_path)
        print(f"VERDICT VALIDATION: PASSED (Integrity Digest: {data.get('integrity_digest')[:16]}...)")
        sys.exit(0)
    except VerdictVerificationError as e:
        print(f"VERDICT VALIDATION: {e}")
        sys.exit(1)
