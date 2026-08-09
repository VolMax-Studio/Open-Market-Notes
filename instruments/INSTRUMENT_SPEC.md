# Instrument Specification — Measurement Domain and Visibility Boundaries

> **Document Status:** Draft — SPREMNO ZA GEJT (not ratified)
> **Version:** v0.3.0 · supersedes v0.2.0, v0.1.0 (none ratified — see §8)
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Contains no:** thresholds, percentiles, market names, operator names, dates, or
> reference to any executed run. If a future revision needs one of these to be
> understood, that revision has failed this document's purpose.

---

## 0. Standing and purpose

This document specifies an instrument: what it measures, what it labels, when it runs,
what it cannot see, and the condition under which two independent implementers must
produce the same result from it.

It is not a description of a probe that was run. An instrument defined by the event it
first detected is not an instrument; it is a record of one experiment wearing the
costume of a method.

A specification makes no empirical claim and therefore cannot be falsified. Its sole
formal acceptance criterion is in §7.

---

## 1. Architecture — what actually constitutes the instrument

The instrument is not any single quantity. It is four separately frozen, separately
versioned components and the fixed relations between them:

| Component | Symbol | What it fixes |
|---|---|---|
| Measurement domain | **M** | The scalar quantity computed per market per window |
| Classifier | **C** | The deterministic rule mapping M-values to one label |
| Selection rule | **S** | Which windows are run, and therefore which population is measured |
| Visibility constraints | **V** | What the instrument is structurally unable to observe |

**M, C, and S may each be replaced without replacing the instrument.** V is derived
from the data sources M draws on and changes only when those sources change.

The architecture — the separation itself, the freeze-before-observation discipline
applied to each component independently, the requirement that each carries its own
version and changelog — is what persists across event classes. This is the generality
claim, stated at exactly its true width: a shared structure, not a shared quantity.

**Consequence for event classes.** A different event class (a different phenomenon one
might wish to detect) requires its own **M**, frozen separately, and normally its own
**C** and label vocabulary. It does not require a new instrument. Whether the
architecture in fact transfers across event classes is settled by instances that exist,
not by this document.

---

## 2. M — the measurement domain

**M is a deterministic function over a bounded, pre-fixed window producing one scalar
per market per unit time.** It answers *how much*. It never answers *what it means*.

The specific quantity, its reference definition, its units, and its temporal resolution
are fixed in a frozen `PARAMS.md` per event class. **This document points to that file
and does not restate any part of it.** A definition copied into governance prose drifts
silently from its source; the copy then contradicts the original with nothing to mark
the divergence.

What holds for every M, and therefore belongs here:

- **M is computed per market independently.** No cross-market operation occurs inside
  M. Cross-market structure is an input to C, never an output of M.
- **M is referenced market-locally, never to a shared absolute level.** Markets differ
  in rules, caps, settlement design, and resolution; a shared absolute reference
  silently compares things that are not comparable, and the comparison looks valid.
- **The window is identical across every market in the comparison set**, and fixed
  before the data is read.
- **The comparison set is determined by a stated admissibility rule applied before the
  data is read** — never by which markets turned out to produce interesting values.

---

## 3. C — the classifier

**C consumes the per-market M-values for one window and emits exactly one label from a
closed vocabulary.** The vocabulary and the conditions are frozen in the classifier
specification, not here.

Three properties are required of any C:

1. **A null label exists and is reachable.** There must be a label meaning *no signal*,
   and it must be the outcome for ordinary windows. A classifier that cannot return
   "nothing happened" is not measuring; it is asserting, and it will assert on every
   window it is ever shown.
2. **C is expressible before the window is observed**, in the form: *this window is
   labelled L if and only if [condition on M-values]*.
3. **C is expressed in units of the instrument's own reference distribution**, not in
   absolute quantities. A rule fitted to a remembered window classifies that window
   correctly by construction and carries no information.

**A label is not a property of the world.** It is the output of a stated rule applied to
a measurement. Changing C changes the label with no change whatever in the world — which
is precisely why C is frozen, versioned, and never adjusted after a window is seen.

---

## 4. Layer assignment (correction recorded)

**M and C are both L1 (Measured)** under `P10_LAYER_SEPARATION.md` v1.0.1. Both are
deterministic, both regenerate byte-identically from source, and both are bounded by
reproducibility. If two implementers derive the same label from the same input, that
label is a reproducible result, not an inference.

**Explicitly corrected here:** an earlier framing placed classification at L2 by analogy
with the conventional measurement → classification → inference sequence. That analogy
does not hold in this architecture, because C is not a heuristic or a fitted model but a
deterministic function of a frozen rule. Treating a deterministic classification as L2
would apply the wrong standard in both directions: it would demand an inference marker
where none is due, and it would license the looser scrutiny appropriate to L2 over
output that must meet the L1 reproducibility bar.

**L2 (Inference) begins at explanation** — why the labelled pattern occurred, what
mechanism produced it, what it implies about anything outside the measured quantity.
**L3 (Decision) is human-owned without exception.** Neither is part of the instrument.
The instrument supplies input to those layers and never output.

**Invariant:** confidence does not flow downward. A correctly executed M and C license
no L2 sentence whatever. The quality of the measurement is not evidence for any
explanation of it.

---

## 5. S — selection, and the population it defines

**Selection is not an operational convenience. It determines the population to which
every future statement about this instrument refers.** A scheduled instrument measures
the distribution of all windows. A triggered instrument measures the distribution of
windows that passed a trigger. These are different populations, and the difference is
invisible in the code: the denominator changes while every line stays identical.

Exactly one mode applies to any published run, and the mode is declared before the
window is fixed.

**Scheduled.** The instrument runs on a fixed cadence under a fixed window rule,
irrespective of content. Every window is published, null labels included. Most windows
are expected to be null; that is the intended behaviour, and the record of nulls is what
makes any non-null label interpretable.

**Triggered.** The instrument runs when a stated trigger condition is met. **The trigger
is itself a frozen, deterministic rule over published data** — never a human impression
that something looked unusual. Every published triggered result carries, inside the
artefact, the count of windows over the same period on which the trigger did not fire.
Without that denominator the result cannot be interpreted at all.

**A run whose mode was not declared before the window was fixed is exploratory (not
pre-registered), and cannot carry a label into any public artefact.** This applies with
full force to a run that produced a striking result.

**Scope of this rule.** It governs runs executed after this document is ratified. It is
not asserted to be invariant over prior runs, and it does not retroactively re-label
them. Any prior run is described by the mode it actually had, recorded once in the
amendment record with its commit reference — a triggered run whose trigger was a human
observation is stated as such, which is a fact about its population and not a defect in
its results. Frozen thresholds and a frozen window satisfy pre-registration for a run's
own claims; they do not by themselves establish the selection mode, which is a separate
declaration.

S is versioned independently of M and C. A change of mode is a change of population and
requires a changelog entry stating the old population, the new population, and the
reason — never a silent switch justified by circumstance.

---

## 6. V — visibility boundaries

Visibility constraints are part of the base specification of the instrument, not a
limitations appendix. There is a difference between *this run lacked data* and *this
instrument by construction cannot distinguish A from B*. The second is a property of the
instrument and belongs here.

> **The instrument cannot distinguish the absence of an event from the absence of data.**
> A window with incomplete telemetry may return a null label for either reason, and the
> null label itself carries no indication of which.

This is not remediable by better code. It follows from the instrument observing
published telemetry that it does not produce. Three requirements follow:

1. **Every run publishes a completeness account** of the inputs actually present in the
   window, generated from the data rather than asserted.
2. **A completeness floor is frozen in advance**, below which the window yields *no
   label at all* rather than a null label. Partial telemetry aborts; it never degrades
   quietly into "nothing happened," because a degraded null is indistinguishable from a
   measured null in every downstream artefact.
3. **Absence observed across the full comparison set is reported as an observation about
   the data**, never as an observation about the markets. The instrument does not hold
   the telemetry required to separate a simultaneous physical event from a simultaneous
   publication gap, and it therefore attributes such absence to neither.

Any additional structural blindness discovered in operation is added to V by amendment,
with the date it was discovered. V is expected to grow; a V that never grows is a V that
is not being tested.

---

## 7. Completeness criterion

This is the **sole formal criterion** by which this document may be marked Complete. It
replaces falsifiability, which does not apply to a definition.

> ### Implementability criterion
>
> **Two independent implementers, working only from this document and the frozen
> component specifications it points to, without access to each other's work or to any
> existing implementation, and given identical raw inputs, produce byte-identical M
> outputs and identical C labels.**

Any divergence locates a defect **in this text**, not in the implementers. The defect is
repaired here, the version is bumped, and the criterion is re-executed.

**Until this criterion has been executed at least once against a genuinely independent
second implementation, the status of this document is `unverified as a specification`,
irrespective of how many times the instrument has run or how well its results held up.**
A specification that has only ever been implemented once has been read once; it has not
been shown to be readable.

**This status attaches to this document and to nothing else.** It is a statement about
the readability of the text, not about the correctness of any result. It does not
propagate to published artefacts, and it does not act retroactively: an artefact
published under its own frozen pre-registration retains exactly the status recorded for
it in the registry, unchanged by anything asserted here. A governance document that
downgrades an already-published result has begun rewriting history rather than
constraining future work.

This status is carried in the registry, not only in this file.

---

## 8. Amendment record and scope

**v0.2.0 → v0.3.0.** Three defects raised at gate. (a) §6 item 3 carried an unmarked
causal claim about the likelier explanation of simultaneous absence — a Layer 2 sentence
inside a document that forbids exactly that; replaced with a structural statement of
what the instrument cannot separate. (b) §5 was written as though it held invariantly
over prior runs, which was not demonstrated; the rule is now explicitly prospective, and
the distinction between frozen thresholds and a declared selection mode is stated. (c)
§7 did not bound the reach of its own status; it now states that the status attaches to
this text alone and never propagates to a published artefact.

*Prior-run declaration required by §5 is recorded in the ratification entry, not here;
this document names no run.*

**v0.1.0 → v0.2.0.** v0.1.0 was never ratified. It is superseded rather than edited, and
is retained in version history. Rationale for supersession: (a) it assigned deterministic
classification to L2 by false analogy, corrected in §4; (b) it located generality in the
classifier rather than in the architecture, corrected in §1; (c) it treated selection as
a sub-clause rather than as the definition of the measured population, corrected in §5;
(d) it placed visibility boundaries after the specification rather than inside it,
corrected in §6; (e) its acceptance test was stated in passing rather than as the sole
completeness criterion, corrected in §7.

**This document does not:**

- define any quantity, reference, threshold, cadence, vocabulary, or completeness floor
  — each lives in its own frozen, independently versioned file;
- claim the instrument works — it defines what the instrument is for, precisely enough
  that a later claim about working can be wrong;
- name a market, operator, asset, or period.

*Amendments require a version bump with stated rationale. Definitions are never edited
silently.*

*VolMax Studio Lab · P10 Verification Protocol*
