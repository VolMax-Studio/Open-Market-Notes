# Note #001: NEM Duration Baseline

## Pre-Registration & Provenance
To guarantee strict data provenance, the parameters for Note #001 were frozen and committed directly inside the AEMO dispatch audit repository (where the AEMO NEMWEB raw datasets are historically indexed and hashed):

- **Frozen Commit:** `b350e9b` (AEMO Dispatch Audit Repository)
- **Frozen Path:** [`volmax-aemo-dispatch-audit/notes/nem-duration-baseline/PARAMS.md`](https://github.com/VolMax-Studio/volmax-aemo-dispatch-audit/blob/main/notes/nem-duration-baseline/PARAMS.md)
- **Frozen Timestamp:** `2026-07-18T19:49:00+02:00`

---

## Calculations & Reproduction
Calculations for this note are scheduled to run in the AEMO dispatch audit environment on the pre-downloaded primary NEMWEB data. Once completed:
1. The resulting metrics will be logged in `results.json`.
2. The execution code will be pushed to the dispatch audit repo.
3. The results summary will be linked here.
