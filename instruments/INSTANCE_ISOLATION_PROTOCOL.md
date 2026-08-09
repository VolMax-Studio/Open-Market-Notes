# Instance Isolation Protocol

> **Document Status:** RATIFIED — FROZEN for Series Operation
> **Version:** v0.1.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Scope:** How a new unit of work is started, what it may read, what it may never write.
> **Justification for existing as a document:** it enables an execution class not currently
> possible — running new work without mutating a published artefact. It does not describe
> existing practice.

---

## 1. The failure this prevents

New work was performed inside the directory of a published artefact. It read that
artefact's data, wrote its own parameter file there, and overwrote that artefact's
registry hashes. The consequence is not a wrong number: it is that the published record
and the working tree describe different objects under one identity, and no hash can
reconcile them because one was replaced by the other.

Every recurrence of this has the same shape: **the new run needed something slightly
different, and the cheapest way to get it was to change the old thing.**

---

## 2. The rule

> **A published artefact is immutable. Any work that is not a correction to it is a new
> instance, in its own directory, with its own parameters and its own registry entry.**

"Published" means: a DOI exists, or the artefact is referenced by a public claim.

Three prohibitions follow, and they are absolute:

1. **No new file is written into a published artefact's directory.** Not a PARAMS, not a
   scratch folder, not a report.
2. **No existing file in a published artefact's directory is edited** to make new work
   succeed.
3. **No registry field of a published entry is overwritten.** Fields are appended, never
   replaced.

---

## 3. Instance layout

```
instances/
  <instance-id>/            e.g. 2026-08-scarcity-jul
    PARAMS.md               this instance's frozen parameters — nothing else reads it
    inputs/                 hash-verified copies, never symlinks, never ../ paths
      MANIFEST.json         one record per copied file (§4)
    src/                    this instance's code
    results/                this instance's outputs
    PROVENANCE.md           what was inherited, from where, at which commit
```

`<instance-id>` is stable and never reused. An instance is created empty and populated
by copy; it is never created by copying a previous instance wholesale, because that
carries the previous instance's facts into the new one.

---

## 4. Inheritance is by value, with a record

Data or code from an earlier artefact enters a new instance **as a copy**, and the copy
is recorded:

```json
{
  "file": "inputs/imbalance_AT.feather",
  "source_repo_path": "notes/003-entsoe-imbalance-baseline/data/processed/imbalance_AT.feather",
  "source_commit": "<sha>",
  "sha256": "<hash of the copy>",
  "copied_at_utc": "<timestamp>",
  "verified_identical_to_source": true
}
```

Three consequences:

- **Relative paths crossing an instance boundary are prohibited.** A `../` reaching into
  another artefact's directory is the mechanism by which the old artefact becomes a live
  dependency of the new one. Code that reads from outside its own instance is
  non-conforming.
- **The copy is what the instance hashes.** If the source later changes, the instance is
  unaffected, and the divergence is visible as a hash mismatch against
  `source_commit` — which is information, not a defect.
- **Inherited code is copied and versioned, not imported.** An instance that imports a
  published note's script is coupled to it; the next fix to that script silently changes
  this instance's results.

---

## 5. Registry

A new instance gets a **new entry**. The entry names its origin:

```json
{
  "id": "<instance-id>",
  "derived_from": "OMN-003",
  "inherits": ["data/processed/*"],
  "params_sha256": "...",
  "results_sha256": "..."
}
```

The parent entry is not touched. Specifically: `params_sha256`, `results_sha256`, and
`params_commit_hash` of a published entry describe **what was published** and are never
updated to describe a later recomputation. A later recomputation is a field on the child
entry, or an appended `recomputations[]` array on the parent — never a replacement.

---

## 6. Correcting a published artefact

Distinct from a new instance, and rare. It applies only when the published artefact is
**wrong**: a wrong number, a licensing defect, or a change in the source data. It does
not apply to improved method, better parameters, or newer specification versions.

The path is: new archived version with its own DOI, changelog entry stating old value /
new value / reason, and the prior version left resolvable. The registry gains a version,
not an edit.

**A new specification does not retroactively correct old work.** An artefact published
under an earlier definition stays published under that definition. Re-running it under a
new definition produces a new instance, not a correction.

---

## 7. Starting an instance — the checklist

- [ ] `<instance-id>` chosen; directory created empty under `instances/`.
- [ ] Inputs copied in and hashed; `inputs/MANIFEST.json` written from the actual copies.
- [ ] `PARAMS.md` written fresh for this instance. Values are chosen for this instance,
      not inherited implicitly.
- [ ] `PROVENANCE.md` records parent artefact, source commit, and what was inherited.
- [ ] Grep confirms no path in `src/` escapes the instance directory.
- [ ] `git status` on the parent artefact's directory shows **zero** changes.
- [ ] New registry entry created; parent entry byte-unchanged.

The sixth item is the one that catches the failure in §1, and it is one command.

---

## 8. Mechanical guard

The checklist above is a habit; a habit is not a control. The control is a CI check that
fails any commit touching a file under a published artefact's directory unless the commit
message carries an explicit correction marker (§6) — so that a correction is a deliberate,
visible act and everything else is impossible by default.

Until that check exists, this protocol is a stated intention, not an enforced rule, and
should be described as such.

---

## 9. What this protocol does not do

- It does not say what the new instance should measure. That is **M**, **C**, **S**.
- It does not make a published artefact correct. It makes it stable.
- It does not apply to unpublished drafts, which may be reorganised freely.

*Amendments require a version bump with stated rationale.*

*VolMax Studio Lab · P10 Verification Protocol*
