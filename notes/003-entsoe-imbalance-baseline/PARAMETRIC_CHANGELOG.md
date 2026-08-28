# Open Market Note #003 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Transition & Code Alignment (2026-07-31)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`PARAMS.md`)
- **Audit Findings:**
  1. **Parameter Lineage:** Draft commit `99f87bb` (24 July 2026 22:19Z) proposed v3.0.0 rules featuring heuristic gap-bridging.
  2. **Transition to Strict Contiguous Rule:** On 27 July 2026 (commit `a2c0b3a`), `PARAMS.md` was updated to v3.1.0, replacing heuristic gap-bridging with Strict Contiguous Block Evaluation.
  3. **Empirical Zero Output Under Draft Rule:** Un-filtered git history inspection (all `.json` files) confirms zero output files were ever produced under the draft v3.0.0 bridging rule. No post-hoc tuning occurred; the rule was revised before any result existed.
  4. **Freeze Precedence Distinction:** For Note #003, no separate pre-execution freeze commit exists; `PARAMS.md` v3.1.0 and the first output landed in the same commit (`a2c0b3a`). The absence of any output under the earlier draft rule is verified, so no post-hoc tuning occurred—but the freeze-then-execute separation visible in Notes #001, #002, #004, and #005 is not present here.
- **Rule of Precedence:** *`PARAMS.md` v3.1.0 matches the executed analytical code in the published Zenodo package. `params_commit_hash` records commit `a2c0b3a`.*
- **Status:** Ratified (Merged to main)

---

## Entry #002: Timestamp Continuity Rule Enforcement (Δt > 15 min Termination) (2026-08-08)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`run_imbalance_analysis.py`)
- **Motivation:** In published Zenodo v1.0.0 (`results_sha256: b1c713379887...`), event continuity was computed via row-adjacency (`compute_m1`). While row-adjacency evaluates strictly contiguous rows, missing telemetry timestamp intervals across row boundaries could silently bridge events separated by missing clock time.
- **Remediated Rule:** Enforce strict timestamp gap termination ($\Delta t > 15\text{ min}$ terminates an active block and starts a new event).
- **Verbatim Empirical Audit Findings (59 Total Gaps Across 6 Zones):**
  1. **Rule Refinement:** Enforcing strict timestamp gap termination across row boundaries.
  2. **Telemetry Gap & Scarcity Breach Breakdown:**
     - **Dataset Totals:** Across all 6 bidding zones in the 13-month baseline, there are **59 total telemetry gaps** ($\Delta t > 15\text{ min}$): 55 gaps in Denmark (27 in DK_1, 28 in DK_2, episodic with 24 of 27 DK_1 gaps and 22 of 28 DK_2 gaps occurring on 10 August 2025) and 4 gaps in non-Danish zones (1 gap each in AT, BE, FR, NL).
     - **Missing 22:00 UTC MTU Gap (6 gaps total: 5 scarcity breaches, 1 non-scarcity gap):** All 6 zones (AT, BE, DK_1, DK_2, FR, NL) possess an identical 30-minute timestamp gap at `2026-05-31 21:45 UTC` $\rightarrow$ `22:15 UTC` (missing 22:00 UTC Market Time Unit), accounting for 6 total gaps. Cause not established; single-call window acquisition in `download_entsoe_data.py` excludes monthly stitching in analysis code. In FR, price drops to €96.3/MWh after the gap (1 non-scarcity gap); in AT, BE, DK_1, DK_2, and NL, prices remain $\ge €100/\text{MWh}$ across the gap, generating 5 gap breaches across 5 zones.
     - **Danish Telemetry Gap Scarcity Breaches (3 breaches across 2 zones):** Out of 55 total Danish gaps, exactly 3 fall within $\ge €100/\text{MWh}$ scarcity events: 1 breach in DK_1 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC`) and 2 separate breaches in DK_2 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC` and `19:45 UTC` $\rightarrow$ `20:15 UTC`). In DK_2, both 10 August 2025 gaps occurred within a single ongoing extended scarcity event (Bridged Event #1), while the 31 May 2026 gap occurred in a separate event 10 months later (Bridged Event #2), totaling 3 gap breaches across 2 bridged events in DK_2.
     - **DK_2 Extreme Price Boundary Note (10 Aug 2025):** Imbalance shortage prices in DK_2 reached €803.80/MWh at 16:30 UTC (`curr_p` following the 16:00 $\rightarrow$ 16:30 30m gap) and €4,689.50/MWh at 16:45 UTC (`prev_p` preceding the 16:45 $\rightarrow$ 17:30 45m gap). These prices sit directly on gap boundaries of the 10 August 2025 telemetry gap cluster in Denmark. Prices adjacent to telemetry gaps carry potential boundary artifacts and should be interpreted with operational caution.
     - **Diagnostic vs Analyzer Definition:** The diagnostic script evaluates static price thresholds (`prev_p >= 100 and curr_p >= 100`) across timestamp gaps $\Delta t > 15\text{ min}$, whereas `run_imbalance_analysis.py` (`compute_m1`) evaluates active event block state transitions during timeline iteration. In this 13-month baseline, both methods yield identical counts (8 gap breaches across 7 bridged events).
     - **Scarcity vs Non-Scarcity Totals:** Exactly **8 gaps** fall inside active scarcity events ($\ge €100/\text{MWh}$) across 7 bridged events. The remaining **51 gaps** fall outside scarcity events, distributed as: 25 in DK_1 (27 total - 2 scarcity breaches), 25 in DK_2 (28 total - 3 scarcity breaches), 1 in FR (1 total - 0 scarcity breaches), and 0 in AT, BE, NL (1 total - 1 scarcity breach each).
  3. **Empirical Impact:** Across 19,219 total M1 moderate scarcity events ($\ge €100/\text{MWh}$ across 13 calendar months, 6 zones), 19,212 events ($99.964\%$) contained ZERO internal timestamp gaps. Enforcing strict timestamp gap termination split exactly **7 bridged events** (8 total gap breaches).
  4. €250 extreme scarcity metrics and daily BESS M2 metrics are 100% unaffected. €100 mean durations shifted by $-0.1\text{ min}$ in BE (76.0m $\rightarrow$ 75.9m) and NL (67.4m $\rightarrow$ 67.3m). Maximum event duration in BE remained exactly 1,545 minutes ($25.75\text{ hours}$).
  5. Remediated baseline result hash under strict timestamp gap termination: `a10c0aae107b52147e98bb269c44a3fac6d9656c7b70af5b398352545a03635c`.
- **Status:** Pending Ratification (Pre-Merge on `feature/omn-003-preregistration-draft`)

---

## Entry #003: Normative UTC Time Contract, Interval Beginning Invariant, and License Register Alignment (2026-08-27)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`PARAMS.md`, `download_entsoe_data.py`)
- **Version Bump:** `v3.1.0` $\rightarrow$ `v3.2.0`
- **Audit Findings:**
  1. **Omission of Normative Time Contract in Prior Versions:** Prior versions (`v3.0.0`, `v3.1.0`) stated the calendar range as "1 June 2025 – 30 June 2026" without normatively defining the timezone domain, sampling step, or timestamp boundary invariants.
  2. **Ratified Time Invariants:**
     - **Timezone Domain:** Strict **`UTC`** (`timestamp_tz: UTC`).
     - **Timestamp Convention:** **`interval_beginning`** (timestamps index the beginning of each 15-minute MTU: `00:00:00` through `23:45:00`).
     - **Derived Invariant Formula:**
       $$\text{Nominal Intervals} = N_{\text{days}} \times 96 = 395 \times 96 = \mathbf{37,920 \text{ MTUs}}$$
       guaranteeing zero DST discontinuities ($96\text{ MTUs/day}$ identically for all 395 days).
  3. **Licensing Register Pin:** Formally bound licensing metadata to `L-04` (Terms of Use 29/03/2023 Article 2.5) and `L-08` (List of Data 18/10/2023 Item #27 [Article 17.1.g / 17.2.f], CC BY 4.0), pinned against commit `9eac856` of `VolMax-Studio/P10-Verification-Method`.
  4. **Epistemic Disclosure on July 2026 Run:** The July 2026 probe run executed on 2026-08-09 was performed under a draft contract that lacked a normative timezone and timestamp convention. This contract amendment does not retroactively pre-register that run; historical July results retain exploratory status until re-executed under this ratified specification.
  5. **Archival of Pre-Existing Untracked Fetch Artefacts:** Untracked legacy data files (`instances/entsoe-scarcity-s1/test_fresh_fetch/`, dated 15 August 2026, containing `imbalance_*_202506_202607.csv`) were moved out of the working tree to external escrow (`sources_raw_escrow/untracked_legacy_test_fresh_fetch_20260815/`) to guarantee that all specification rules and chunking mechanics are written and verified without un-ratified data artifacts in the working tree.
- **Status:** Pending Ratification (Pre-Merge on `fix/entsoe-note003-contract-boundary`)

---

## Entry #004: Quality Contract Parametrization, Post-Hoc Calibration Disclosure, and Gap Resolution (2026-08-28)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`PARAMS.md`, `PARAMETRIC_CHANGELOG.md`, `download_entsoe_data.py`)
- **Audit & Governance Findings:**
  1. **Post-Hoc Empirical Calibration Disclosure for 90-Minute Gap Limit:**
     - The parameter `max_telemetry_gap_minutes: 90` is **formally recorded as a post-hoc empirical baseline calibration**, fitted directly to the maximum observed telemetry outage in historical Danish TSO data (`DK_1` and `DK_2` on 10 August 2025: 6 consecutive 15-minute intervals = 90 minutes).
     - **Negative Epistemic Finding:** No external regulatory rule, standard, or ENTSO-E market code has been established for a 90-minute threshold. It is recorded strictly as an empirical baseline parameter representing historical telemetry dropouts in DK bidding zones.
     - **Verification Operator:** Evaluated as strict greater-than (`diffs.max() > max_telemetry_gap_minutes`). Observed 90-minute historical gaps satisfy $\le 90\text{ min}$ and pass; any future gap $> 90\text{ min}$ triggers an immediate Mandate 8 violation.
  2. **Three-Axis Taxonomy Verification:**
     - `QUERY_WINDOW_MISALIGNMENT`: Formally enforced at every monthly chunk junction across all zones during live and offline ingestion. Any non-contiguous step at a month boundary causes an immediate abort.
     - `TELEMETRY_GAP`: All interior steps $> 15\text{ min}$ within monthly chunks are logged with timestamp and duration, subject to Mandate 8 quality limits ($\ge 98.0\%$ completeness, $\le 90\text{ min}$ max gap).
  3. **Empirical Resolution of Danish Gap Count (55 $\rightarrow$ 53):**
     - Verification of the full 13-month dataset confirms that `2026-05-31 22:00:00 UTC` is present in both `DK_1` (108.32 €/MWh) and `DK_2` (151.02 €/MWh).
     - The resolution of the month-boundary acquisition artifact reduced the total Danish gap count from 55 (27 in `DK_1`, 28 in `DK_2`) to **53** (26 in `DK_1`, 27 in `DK_2`), proving that the two missing intervals were acquisition defects rather than grid events.
- **Status:** Pending Ratification (Pre-Merge on `fix/entsoe-note003-contract-boundary`)
