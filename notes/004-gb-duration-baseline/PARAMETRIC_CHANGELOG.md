# Open Market Note #004 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Clarification & Dual-Table Schema (2026-07-30)

- **Scope:** Note #004 GB BESS Duration Baseline (Elexon BMRS)
- **Audit Findings:**
  1. **Separation Rule (Metric 1 - Table 1A vs 1B):** `PARAMS.md` specifies Threshold A ($\ge £100/\text{MWh}$) and Threshold B ($\ge £250/\text{MWh}$), with separation text *"Events separated by <60 minutes (less than 2 settlement periods of 30 minutes)... are counted as separate events."* The executed script (`run_analysis.py`) outputs dual tables: **Table 1A (Pure Continuous Scarcity Runs)** which splits on any single period below threshold, and **Table 1B (Macro Event Window Spans)** which bridges isolated single-period dips ($<60\text{ minutes}$).
- **Rule of Precedence:** *Where the frozen text and the executed code differ, the executed code governs the published numbers; the frozen text governs what was pre-registered.*
- **Status:** Ratified (Merged to main)
