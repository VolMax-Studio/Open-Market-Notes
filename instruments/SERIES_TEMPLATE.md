# SERIES TEMPLATE — Scheduled Series Specification Template

> **Document Status:** RATIFIED — FROZEN for Series Operation
> **Version:** v0.2.0 · supersedes v0.1.0 (defects resolved — see §8)
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection mode:** S₁ (Scheduled) — `S1_SCHEDULED_SELECTION.md`
> **Measurement:** M₁ — `M1_SCARCITY_PERSISTENCE.md`
> **Classifier:** C — `C_CLASSIFIER_SCARCITY_PERSISTENCE.md`
> **Isolation:** `INSTANCE_ISOLATION_PROTOCOL.md`
> **Scope:** This document is the canonical specification template (`SERIES_TEMPLATE.md`). When a new scheduled series instance is created under `instances/<series-id>/`, this template is instantiated into `instances/<series-id>/SERIES.md`.

---

## 1. Instance, run, series — the three units

These were previously conflated, producing one directory per window and one copy of the
inputs per window. They are separated here.

| Unit | Definition | Created when |
|---|---|---|
| **Instance** | One frozen rule set: `PARAMS.md` plus the pinned versions of M, C, S | Any parameter or specification version changes |
| **Run** | One window W evaluated under that instance | Each scheduled cadence step |
| **Series** | The ordered set of all runs of one instance | Once, with the instance |

**The rule that decides where anything goes:** *does `PARAMS.md` change?* Yes → a new
instance directory. No → a new `runs/YYYY-MM/` inside the existing one.

A parameter change does not migrate earlier runs. They stay in the instance that produced
them, and the new instance starts a new series. Two series are never concatenated into one
chart or one frequency without stating that they are two.

---

## 2. Layout

```
instruments/
├── INSTRUMENT_SPEC.md              domain and visibility boundaries
├── M1_SCARCITY_PERSISTENCE.md       metric M1
├── C_CLASSIFIER_SCARCITY_PERSISTENCE.md classifier C
├── S1_SCHEDULED_SELECTION.md       scheduled selection rule S1
├── INSTANCE_ISOLATION_PROTOCOL.md  isolation doctrine
├── SERIES_TEMPLATE.md              this template
└── SERIES_LOG_SCHEMA.json          index schema

instances/<series-id>/
├── PARAMS.md            frozen once for the whole series
├── PROVENANCE.md        inherited inputs, per Isolation Protocol §4
├── SERIES.md            instantiated from SERIES_TEMPLATE.md
├── src/
│   └── run_window.py    single entry point, --window YYYY-MM
├── inputs/
│   ├── MANIFEST.json    append-only; one record per file, per addition
│   └── <zone files>     grow forward; existing bytes never rewritten
└── runs/
    ├── SERIES_LOG.json  one record per calendar window, including unevaluated
    └── YYYY-MM/
        ├── result.json        the measurement — deterministic, hashed, registered
        └── completeness.json  admitted vs nominal, per zone, per M₁ §4
```

---

## 3. Inputs grow; they are not re-copied

The baseline rolls forward, so each run adds one month of data per zone. Copying the whole
input set per run would multiply identical bytes by the number of runs and destroy the
point of hashing them.

Instead:

- Input files are **extended forward**. Bytes already present are never rewritten.
- `MANIFEST.json` is **append-only**: each addition writes a new record with the file, the
  covered period, its SHA-256 after the addition, the source, and the date. Earlier records
  are never edited.
- Each run records the manifest state it read (`inputs_manifest_sha256`), so a run remains
  tied to the exact input state that produced it even though the files later grow.
- **Upstream Data Revision Rule:**
  - Upstream telemetry revisions published *prior* to publication lag $L$ are incorporated into the input files before freezing $R$ and running evaluation.
  - If an upstream data revision occurs *after* publication lag $L$ and alters any previously published measurement $M_1(m, W)$ or label $L(W)$: **It requires a new instance with a new DOI under `INSTANCE_ISOLATION_PROTOCOL.md` §6.** The existing instance and published record remain immutable.
  - If an upstream data revision touches only data outside any published operating window $W$ or baseline window $B$: It is recorded in `inputs/MANIFEST.json` without triggering a new instance.

---

## 4. What is hashed, and what is not

**`result.json` is a measurement.** It contains no timestamp, no commit hash, no
specification version string, and no hash of any other file. It depends only on the input
data and the parameter *values*. It is byte-deterministic under the recreation test
(rename → rerun → byte-compare) and its SHA-256 is registered.

**`SERIES_LOG.json` is an index, not a measurement.** It is regenerated from the individual
`result.json` files and references their hashes. Its own hash is not a claim about
anything and is not registered.

This separation exists because three earlier attempts embedded a spec version, a params
hash, or an evaluator hash inside the measurement, and each time a cosmetic edit changed a
number that was supposed to represent physics.

---

## 5. The calendar is the denominator

`SERIES_LOG.json` carries **one record per calendar window in the operating period**,
without exception — including windows that produced no label.

- `N_calendar_total` = every record in the log.
- `N_classified_total` = records whose `evaluation_status` is `EVALUATED`.

Empirical label frequencies (`P(NULL)`, `P(ISOLATED)`, `P(REGIONAL)`) are computed over
`N_classified_total`. Unevaluated windows are visible, counted separately, and never
imputed. This realises S₁ §2.4; without the log the distinction exists only on paper.

---

## 6. Archival cadence

- **One concept DOI per series.** New versions are issued **annually**, covering a full
  calendar cycle, or immediately on any of: a wrong number, a licensing defect, or a change
  in the data (Isolation Protocol §6).
- **Monthly cross-sections carry no DOI.** They are rendered *from* `SERIES_LOG.json` for
  posts, analysis, and instrument development. They are never computed independently — two
  computations of one month produce two numbers, and only one of them is the measurement.
- A parameter change ends the series' version line. The new instance gets its own concept
  DOI, and the old record stays resolvable under its own rules.

Annual rather than semi-annual: a seasonal split invites readers to compare two archives as
two populations. Seasonality is the reason B spans a full year (S₁ §3.4); it is not a thing
this instrument measures.

---

## 7. Registry

The series holds **one registry entry**, not one per run. Per-run hashes live in
`SERIES_LOG.json`, which the entry points to.

Fields specific to a scheduled series: `selection_mode: "S1_scheduled"`, `series_id`,
`instance_dir`, `spec_commit` (the commit pinning M/C/S and PARAMS together),
`series_log_path`, `operating_start`, `runs_completed`, `runs_unevaluated`.

---

## 8. Amendment Record

**v0.1.0 → v0.2.0.**
1. Formalized template designation scope in header and §2 layout (`instruments/SERIES_TEMPLATE.md`).
2. Co-located `INSTANCE_ISOLATION_PROTOCOL.md` in §2 instruments layout.
3. Codified normative deterministic Upstream Data Revision Rule in §3 under Isolation Protocol §6.

*Amendments require a version bump with stated rationale. Definitions are never edited
silently.*

*VolMax Studio Lab · P10 Verification Protocol*
