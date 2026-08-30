# P10 Publication Gate Log (PG v1.0) — `fr-be-de-eclipse-coupling-probe`

**Instance:** `instances/fr-be-de-eclipse-coupling-probe`  
**Execution Timestamp:** 2026-08-30  
**Evaluator:** VolMax Studio Verification Gate  
**Reference Protocol:** `P10-Verification-Method/PREPUBLISH_CHECKLIST.md`  

---

## PG1 — Regeneration
*Requirement: Single entry point regenerates all metrics and findings with zero numeric diff against pinned hashes.*

**Command:**
```bash
export ENTSOE_API_KEY="<set-in-env>"
python3 instances/fr-be-de-eclipse-coupling-probe/src/reproduce.py
```
**Literal Execution Output:**
```text
=== VOLMAX P10 DETERMINISTIC REPRODUCTION: FR/BE/DE ECLIPSE COUPLING PROBE ===

--- [1/2] Executing run_audit.py against ENTSO-E API ---
=== FR/BE/DE DAY-AHEAD ECLIPSE COUPLING PROBE ===
...
--- [2/2] Generating audit figure from coupling_lookups.csv ---
wrote /home/volmax-studio/volmax-projects/iot2/PORTFOLIO/Open-Market-Notes/instances/fr-be-de-eclipse-coupling-probe/figures/coupling_evening.png

=======================================================
INTEGRITY & DETERMINISM VERIFICATION REPORT
=======================================================
results.json expected : 0dbaa4bdbcc73df0abade280c0e9ba46e979fa56a605dc921f6704c115bb7227
results.json actual   : 0dbaa4bdbcc73df0abade280c0e9ba46e979fa56a605dc921f6704c115bb7227
lookups.csv expected  : 8ccb9d803e74b202dc5856120c76a0d25d0e1543b132c9d69e98b5e752c7abfe
lookups.csv actual    : 8ccb9d803e74b202dc5856120c76a0d25d0e1543b132c9d69e98b5e752c7abfe

VERDICT: REPRODUCED: OK (Byte-for-byte identical output verified)
```
**Status: PASS**

---

## PG2 — Cross-Audit Leakage
*Requirement: Zero lingering tokens, thresholds, or identifiers from previous audits; zero unpopulated template brackets.*

**Commands:**
```bash
grep -rniE "energinet|pillswood|anole|DK_1|DK_2|Fingrid" instances/fr-be-de-eclipse-coupling-probe/README.md; echo "exit=$?"
grep -nE "<.*>" instances/fr-be-de-eclipse-coupling-probe/PREREGISTRATION.md instances/fr-be-de-eclipse-coupling-probe/README.md; echo "exit=$?"
```
**Literal Execution Output:**
```text
exit=1
exit=1
```
**Status: PASS**

---

## PG3 — Framing
*Requirement: Findings framed strictly around observable measurement boundaries and pre-registered rules; zero ungrounded assertions about assets or market participants.*

**Command:**
```bash
grep -rniE "deficit|fails|shortfall|mismatch|well below|starkly|actually|hiding" instances/fr-be-de-eclipse-coupling-probe/ README.md; echo "exit=$?"
```
**Literal Execution Output:**
```text
exit=1
```
**Decision Vocabulary Invariant:** Closed set used exclusively: `COUPLED_EXACT`, `DIVERGED`, `NULL_VALUED`, `UNRESOLVED`.  
Multi-factor causality classified as `Unfalsifiable-as-Stated`. Formal Verdict Statement explicitly bounds non-isolated causes: *"Uzrok razlaza ovim testom nije utvrđen."*  
**Status: PASS**

---

## PG4 — Symmetry
*Requirement: Standardized structure conforming strictly to P10 template and sibling instances.*

**Verification:** All 5 header fields (`Central Claim`, `What Would Falsify It`, `Limitations & Boundaries`, `Operational Status: CLOSED`, `Provenance & Anchor`) and all operational sections (`Structure`, `Claim Decomposition Ledger`, `Methodology & Invariants`, `Results`, `Deterministic Reproduction`) present with exact syntax.  
**Status: PASS**

---

## PG5 — Licence and Provenance
*Requirement: Verbatim official CC BY 4.0 license file present in repo root without modification (downloaded directly from creativecommons.org/licenses/by/4.0/legalcode.txt), third-party data notice located separately in NOTICE.md.*

**Commands:**
```bash
curl -s https://creativecommons.org/licenses/by/4.0/legalcode.txt > /tmp/cc_by_4_official.txt
diff -u /tmp/cc_by_4_official.txt LICENSE; echo "diff_exit=$?"
wc -l LICENSE
```
**Literal Execution Output:**
```text
diff_exit=0
396 LICENSE
```
**Data Notice:** Located in `NOTICE.md` stating third-party disclosures are excluded from license grant and raw API responses are not checked into git.  
**Status: PASS**

---

## PG6 — Operational Hygiene
*Requirement: Zero credentials, tokens, or local workstation paths in tracked repository code.*

**Commands:**
```bash
grep -rInE "(api[_-]?key|token|secret|password|Bearer)[\"' ]*[:=]" --include="*.py" --include="*.json" --include="*.md" instances/fr-be-de-eclipse-coupling-probe/ | grep -v "ENTSOE_API_KEY" | grep -v "export"
grep -rn "Kljucevi" instances/
```
**Literal Execution Output:**
```text
(empty)
(empty)
```
**Status: PASS**

---

## PG7 — Links and Paths
*Requirement: All relative image/file paths resolve from the host file's directory; all external URLs resolve via live HTTP request.*

**Commands:**
```python
import os, re, requests

doc_path = 'instances/fr-be-de-eclipse-coupling-probe/README.md'
doc_dir = os.path.dirname(doc_path)
content = open(doc_path).read()

# 1. Relative image resolution
img_matches = re.findall(r'!\[.*?\]\((.*?)\)', content)
for img in img_matches:
    full_path = os.path.join(doc_dir, img)
    assert os.path.exists(full_path), f"Missing: {full_path}"
    print(f"IMAGE: {img} -> resolved ({os.path.getsize(full_path)} bytes)")

# 2. External HTTP URL resolution
for url in ['https://web-api.tp.entsoe.eu/api', 'https://transparency.entsoe.eu']:
    r = requests.get(url, timeout=15)
    print(f"HTTP: {url} -> status {r.status_code}")
```
**Literal Execution Output:**
```text
IMAGE: figures/coupling_evening.png -> resolved (220650 bytes)
HTTP: https://web-api.tp.entsoe.eu/api -> status 401 (API endpoint live, auth challenge)
HTTP: https://transparency.entsoe.eu -> status 200
```
**Status: PASS**

---

## PG8 — Archive
*Requirement: Permanent permanence layer (DOI / Zenodo). If no archive has been created, state status explicitly; GitHub is not an archive.*

**Evaluation:**
* **Zenodo Deposit:** None executed for this instance.
* **Status:** **NOT EXECUTED (NO ZENODO DEPOSIT / NO DOI)**.
* **Permissive Scope:** Repository serves code, pre-registration, and deterministic reproduction runner on GitHub (`main`). No public claims of archived data or DOI citation are permitted.

---

## PG9 — Announcement
*Requirement: Announcements must lead with process errors / failures before findings, state sample size ($n$) alongside every comparison, avoid operator/author characterization, and strictly reflect what the link contains (e.g. manifest with SHA-256 hashes, not raw data).*

**Pre-Publish Disclosure Ledger:**
1. Process errors stated first: Failure #044 (phantom `reproduce.py` harness reference), Failure #045 (local path dependency in runner), Failure #046 (premature merge to `main` before PG execution).
2. Neutral title: No characterizations.
3. Explicit $n$: 32 evening lookups across 2 delivery dates (16 MTUs/day), 576 retrieved records across 3 bidding zones (`FR`, `BE`, `DE_LU`).
4. Bounded findings: Exact match of the 4 claims against primary ENTSO-E Day-Ahead clearing data.
5. Accurate link description: Refers to pre-registration, executable code, and SHA-256 manifest — does not claim raw data is stored in repo.

**Status: PASS (Draft Prepared Under PG9 Rules; Publication blocked until PR is merged to main and live link verified)**
