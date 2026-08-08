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
     - **Dataset Totals:** Across all 6 bidding zones in the 13-month baseline, there are **59 total telemetry gaps** ($\Delta t > 15\text{ min}$): 55 gaps in Denmark (27 in DK_1, 28 in DK_2, episodic and concentrated in July/August 2025 and April 2026) and 4 gaps in non-Danish zones (1 gap each in AT, BE, FR, NL).
     - **Missing 22:00 UTC MTU Gap (5 scarcity breaches, 1 non-scarcity gap):** All 6 zones possess an identical 30-minute timestamp gap at `2026-05-31 21:45 UTC` $\rightarrow$ `22:15 UTC` (missing 22:00 UTC Market Time Unit). Cause not established; single-call window acquisition in `download_entsoe_data.py` excludes monthly stitching in analysis code. In FR, price drops to €96.3/MWh after the gap (1 non-scarcity gap); in AT, BE, DK_1, DK_2, and NL, prices remain $\ge €100/\text{MWh}$ across the gap, generating 5 gap breaches across 5 zones.
     - **Danish Telemetry Scarcity Breaches (3 breaches across 2 zones):** Out of 55 total Danish gaps, exactly 3 fall within $\ge €100/\text{MWh}$ scarcity events: 1 breach in DK_1 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC`) and 2 separate breaches in DK_2 (`2025-08-10 18:45 UTC` $\rightarrow$ `19:15 UTC` and `19:45 UTC` $\rightarrow$ `20:15 UTC`). In DK_2, both 10 August 2025 gaps occurred within a single ongoing extended scarcity event (Bridged Event #1), while the 31 May 2026 gap occurred in a separate event 10 months later (Bridged Event #2), totaling 3 gap breaches across 2 bridged events in DK_2.
     - **Scarcity vs Non-Scarcity Totals:** Exactly **8 gaps** fall inside active scarcity events ($\ge €100/\text{MWh}$) across 7 bridged events; the remaining **51 gaps** fall outside scarcity events.
  3. **Empirical Impact:** Across 19,219 total M1 moderate scarcity events ($\ge €100/\text{MWh}$ across 13 calendar months, 6 zones), 19,212 events ($99.964\%$) contained ZERO internal timestamp gaps. Enforcing strict timestamp gap termination split exactly **7 bridged events** (8 total gap breaches).
  4. €250 extreme scarcity metrics and daily BESS M2 metrics are 100% unaffected. €100 mean durations shifted by $-0.1\text{ min}$ in BE (76.0m $\rightarrow$ 75.9m) and NL (67.4m $\rightarrow$ 67.3m). Maximum event duration in BE remained exactly 1,545 minutes ($25.75\text{ hours}$).
  5. Remediated baseline result hash under strict timestamp gap termination: `a10c0aae107b52147e98bb269c44a3fac6d9656c7b70af5b398352545a03635c`.
- **Status:** Pending Ratification (Pre-Merge on `feature/omn-003-preregistration-draft`)
