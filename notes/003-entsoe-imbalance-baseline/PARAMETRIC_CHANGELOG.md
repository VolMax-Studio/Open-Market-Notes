# Open Market Note #003 — Parametric Changelog

*(Governance Note: All entries marked `Ratified (Merged to main)` transition to `Ratified` upon PR merge to `main`).*

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
