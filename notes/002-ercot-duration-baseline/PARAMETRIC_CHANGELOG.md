# Open Market Note #002 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Clarification & Code Alignment (2026-07-30)

- **Scope:** Note #002 ERCOT Duration Baseline
- **Audit Findings:**
  1. **Separation Rule (Metric 1):** `PARAMS.md` states: *"Events separated by <30 minutes (less than 2 intervals of 15 minutes)... are counted as separate events."* The frozen text is under-specified (defining behavior for gaps under 30 minutes while remaining silent on longer breaks). The executed code (`reproduce.py`) evaluates continuous sequences of $\ge \$100/\text{MWh}$ or $\ge \$250/\text{MWh}$ intervals and splits on any single interval below threshold without gap-bridging.
- **Rule of Precedence:** *Where the frozen text and the executed code differ, the executed code governs the published numbers; the frozen text governs what was pre-registered.*
- **Status:** Pending Ratification (Pre-Merge)
