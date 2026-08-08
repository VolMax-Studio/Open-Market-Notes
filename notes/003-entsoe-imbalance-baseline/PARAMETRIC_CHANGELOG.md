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
- **Dual Cause & Empirical Audit Findings:**
  1. **Rule Refinement:** Enforcing strict timestamp gap termination across row boundaries.
  2. **Dual Cause Breakdown:**
     - **Data Acquisition Artifact (5 breaches):** 5 of 8 total gap breaches occurred simultaneously across AT, BE, DK_1, DK_2, and NL at `2026-05-31 21:45 UTC` $\rightarrow$ `2026-05-31 22:15 UTC` at the boundary of monthly ENTSO-E CSV chunk stitching in `download_entsoe_data.py`.
     - **Raw TSO Telemetry Gaps (3 breaches):** 3 gap breaches occurred in Denmark (1 breach in DK_1, 2 breaches in DK_2) at `2025-08-10 18:45 UTC` $\rightarrow$ `2025-08-10 20:15 UTC` representing actual Energinet TSO telemetry gaps.
  3. **Empirical Impact:** Across 19,219 total M1 moderate scarcity events ($\ge €100/\text{MWh}$ across 13 calendar months, 6 zones), 19,212 events ($99.964\%$) contained ZERO internal timestamp gaps. Enforcing strict timestamp gap termination split exactly **7 bridged events** (8 total gap breaches).
  4. €250 extreme scarcity metrics and daily BESS M2 metrics are 100% unaffected. €100 mean durations shifted by $-0.1\text{ min}$ in BE (76.0m $\rightarrow$ 75.9m) and NL (67.4m $\rightarrow$ 67.3m). Maximum event duration in BE remained exactly 1,545 minutes ($25.75\text{ hours}$).
  5. Remediated baseline result hash under strict timestamp gap termination: `a10c0aae107b52147e98bb269c44a3fac6d9656c7b70af5b398352545a03635c`.
- **Status:** Pending Ratification (Pre-Merge on `feature/omn-003-preregistration-draft`)
