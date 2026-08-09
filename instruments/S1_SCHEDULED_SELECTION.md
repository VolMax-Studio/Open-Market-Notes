# S₁ — Scheduled Selection

> **Document Status:** Draft — SPREMNO ZA GEJT (not frozen, not ratified)
> **Version:** v0.3.1 · supersedes v0.3.0, v0.2.0, v0.1.0 (defects resolved — see §8)
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Role:** Selection rule **S** for scheduled operation, under
> `INSTRUMENT_SPEC — Measurement Domain and Visibility Boundaries` (v0.3.0).
> **Scope:** This document defines one selection mode. Triggered selection is a
> **separate document** (`S2`) defining a **different population**, and results produced
> under S₁ and S₂ are never pooled or compared as one distribution.

---

## 1. What S determines

S does not decide what is measured (**M**) or how a result is labelled (**C**). It decides
**which windows are measured at all**, and therefore **which population every statement
about this instrument refers to**.

Under S₁, the population is: *all calendar windows in the operating period that yield complete telemetry across all comparison zones ($\mathcal{M}$) under M₁ §4.2 and yield determinate elevation states under M₁ §4.4.*

Windows failing telemetry completeness floor or yielding indeterminate elevation states are published as unclassified record entries bearing evaluation status `NOT_EVALUATED — INCOMPLETE_SET` or `NOT_EVALUATED — INDETERMINATE_SET` (`label: null`).

---

## 2. Selection rule

1. **Cadence.** One run per calendar month, covering the immediately preceding complete
   calendar month as W. No partial months.

   **W is a calendar month in UTC**, from `YYYY-MM-01T00:00:00Z` to the final interval
   ending at `YYYY-MM-<last>T23:59:59Z`. Local market months are never used.

   This is not a preference. `INSTRUMENT_SPEC` §2 requires that *the window is identical
   across every market in the comparison set*, and a local month is a different interval
   for each timezone: the six CET/CEST zones and a UTC/BST companion do not share a local
   month, so a local-month window would compare different periods under one name. A local
   month is also not a fixed length — DST transitions make it 2975 or 2977 fifteen-minute
   intervals in March and October — which makes the nominal denominator of M₁ §4.1 unstable
   across the year.

   `nominal_intervals` for W is therefore always `days_in_month × (86400 / Δt)`, with `Δt`
   the market's frozen interval duration.

   **Consequence for acquisition.** Telemetry must be requested for the UTC range, not for
   the market's operational month. Where a source publishes on local-month boundaries, the
   request spans both adjacent local months and is sliced to UTC before evaluation. A run
   that evaluates whatever the source happened to return is measuring an undeclared window
   — see `FAILURES.md` Entry #025.
2. **No manual window choice.** The window is a function of the calendar and nothing
   else. A window is never chosen, skipped, re-run for a different period, or deferred
   because its result is uninteresting or inconvenient.
3. **Publication lag.** The run executes no earlier than L days after the end of W, where
   L is frozen in `PARAMS.md`. **L is declared under Option B as provisional ($L = 10$ calendar days)** — defined as the estimated number of calendar days after the end of W required for all designated comparison series across set $\mathcal{M}$ (the 6 ENTSO-E zones) to reach final published completeness (crossing M₁ §4 floor). Prospective monitoring during scheduled operation will establish the empirical publication curve. Descriptive companion markets (e.g. GB Elexon BMRS) carry non-voting status and do not alter or delay $L$. The measurement is recorded at freeze time. Prior to the elapsing of $L$ days post-W, the window record in `SERIES_LOG.json` carries evaluation status `NOT_EVALUATED — PENDING_PUBLICATION_LAG`. Upstream telemetry revisions published *prior* to $L$ are incorporated before freezing $R(W)$. Any post-$L$ upstream data revision altering a previously published measurement $M_1(m, W)$ or label $L(W)$ requires a new instance under `INSTANCE_ISOLATION_PROTOCOL.md` §6.
4. **Every window is published**, including windows classified `NULL` and unclassified windows (`NOT_EVALUATED — INCOMPLETE_SET` / `NOT_EVALUATED — INDETERMINATE_SET`). A `NULL` month is a measurement, not a non-event; the record of `NULL`s is what makes any non-`NULL` label interpretable at all. Unclassified record entries enter the denominator of total calendar operating windows ($N_{\text{calendar\_total}}$), but are strictly excluded from the denominator of classified evaluation labels ($N_{\text{classified\_total}}$) when calculating empirical label probabilities such as $P(\text{REGIONAL})$ or $P(\text{NULL})$.
5. **Abort is not skip; single retry rule.** A window that aborts under the completeness floor (M₁ §4.2) or determinacy bounds (M₁ §4.4) is published as an unclassified record entry (`evaluation_status: "NOT_EVALUATED — INCOMPLETE_SET"` or `"NOT_EVALUATED — INDETERMINATE_SET"`, `label: null`). It is never silently omitted from the calendar log. A window marked unclassified may be re-evaluated **exactly once** during the subsequent publication cycle (at $W + 1$) under **100% identical parameters and code**, explicitly using target baseline window $B(W)$ (the 12 calendar months ending immediately prior to $W$, not $B(W+1)$). If the second attempt passes telemetry completeness and determinacy, its record in `SERIES_LOG.json` updates to `EVALUATED` with provenance field `"re_evaluation_attempt": 2`. If the second attempt fails, status transitions to `NOT_EVALUATED — EXHAUSTED_RETRY_INCOMPLETE_SET` or `NOT_EVALUATED — EXHAUSTED_RETRY_INDETERMINATE_SET`. Parameter relaxation or arbitrary re-runs under altered rules remain strictly prohibited (M₁ §4.2).

---

## 3. Baseline: rolling, disjoint

B is a **rolling window ending immediately before W**, of length N calendar months, with N
frozen in `PARAMS.md` (subject to constraint $N \ge 12$).

**3.1 Disjointness.** B ∩ W = ∅, inherited from M₁ §2.1 without modification. The rolling
rule shifts B by exactly one month per run, so disjointness holds by construction rather
than by check — but the check is still executed each run.

**3.2 Why rolling.** M₁ measures a market against **its own recent régime**, not against
an absolute level. A baseline frozen years earlier measures a relationship to a different
epoch, so the quantity drifts in meaning while keeping its name. Rolling preserves the
meaning of M₁ across time.

**3.3 What comparability means here.** Under a rolling baseline, **R differs between
runs.** Two months' M₁ values are not two readings of one instrument setting; they are
two readings of the same *rule*. Comparability is therefore a property of the procedure,
not of the threshold:

> Procedure-level comparability, not reference-level identity.
> Not the same R. The same function producing R.

Every run publishes the R it used, per market, together with the B window that produced
it. An M₁ value quoted without its R and B is not quotable.

**3.4 Seasonal composition.** A rolling B shorter than twelve months contains a different
seasonal mix each run, so R oscillates with the season rather than with the market. N is
therefore constrained ($N \ge 12$) so that B always spans a full annual cycle. This constraint is motivated by the rolling baseline design and belongs here, not in M₁.

---

## 4. Visibility Constraints (V) & Design Properties

### 4.1 Structural Blindnesses (Added to Instrument V Constraints)
The following are structural blindnesses introduced **by this selection rule**, added to the instrument's visibility constraints (**V**):

1. **Régime Drift Blindness:** Under a rolling baseline, the instrument cannot observe slow régime change. If the entire comparison set drifts in the same direction over a period comparable to or longer than B, the reference drifts with it and M₁ returns approximately (1 − q) regardless. The instrument reports "ordinary" precisely because "ordinary" has moved.
2. **Variance Drift Blindness:** If market dispersion/volatility increases without shifting the median, the quantile $Q_q$ rises. Consequently, the instrument becomes less sensitive precisely during periods of elevated variance.
3. **Telemetry Outage Selection Bias:** If telemetry publication failures or data gaps correlate with severe grid stress events, scheduled evaluation fails completeness or determinacy under M₁ §4 and the window is published as `NOT_EVALUATED`. Under such co-occurring telemetry blackouts, the instrument cannot observe scarcity events.

### 4.2 Calibration & Baseline Incorporations
1. **Built-in Expectation:** By construction, approximately (1 − q) of baseline time sits at or above R, so an ordinary window yields M₁ ≈ (1 − q). Any elevation threshold in **C** is read against that expectation, never as an absolute quantity.
2. **Baseline Incorporation of Past Windows:** After W is measured, it becomes part of B for later windows. An extreme month therefore raises the reference for the months that follow it, which suppresses M₁ in those months. This is correct behaviour under a local reference and it is not a contamination of the run in which W was measured — but the effect is real and is stated in any sequence of results spanning it.

---

## 5. Parameters frozen in `PARAMS.md`

S₁ is parameter-free as a definition. Values live in `PARAMS.md`:

| Parameter | Meaning | Status / Constraint |
|---|---|---|
| `window_timezone` | Timezone in which W is defined | **FROZEN: `UTC`.** Not a free parameter; fixed by `INSTRUMENT_SPEC` §2 (identical window across the comparison set). Recorded in `PARAMS.md` so that any run asserting a different value is non-conforming on inspection rather than silently. |
| `L` | Publication lag in days before a run may execute | PROVISIONAL — unmeasured estimate (Option B); requires prospective monitoring |
| `N` | Rolling baseline length in calendar months | TO BE FROZEN (Constraint: $N \ge 12$) |
| `run_day` | Day of month on which the scheduled run executes | TO BE FROZEN (Constraint: $\text{run\_day} > L$) |
| `operating_start` | First window in the scheduled series | TO BE FROZEN (Constraint: $\ge 12$ months post archive start) |

An implementation that supplies a default for any of these is non-conforming.

---

## 6. Relationship to S₂ (Triggered)

S₂ is a different selection rule producing a **different population**: windows that passed
a trigger, rather than all windows. Results are recorded under the mode that produced
them and are never merged into one series, one chart, or one summary statistic. Any
document presenting both states the mode of each result in the same breath as the result.

S₂ is not defined here and does not exist until it is written and frozen. Until then, no
run is executed under a triggered rationale. Legacy pre-registered probe runs (such as OMN-003-PROBE) carry registry designation `selection_mode: legacy_triggered_human` and exist outside S₁ and S₂. An isolated instance re-evaluation of a pre-existing probe finding (such as `2026-08-scarcity-jul`) inherits the selection mode of the original finding (`selection_mode: legacy_triggered_human`).

---

## 7. What S₁ does not do

- It does not define what is measured (**M**) or how a label is assigned (**C**).
- It does not guarantee that any window will ever be non-`NULL`. If the scheduled series
  runs for years without a non-`NULL` label, that is a result about the markets, not a
  failure of the instrument.
- It does not license comparing an S₁ result to an S₂ result.

---

## 8. Amendment Record

**v0.3.0 → v0.3.1.**
1. §2.1 now defines W explicitly as a UTC calendar month, with the derivation from `INSTRUMENT_SPEC` §2 (identical window across markets) and the DST argument for a stable nominal denominator stated rather than assumed.
2. §2.1 adds the acquisition consequence: telemetry is requested for the UTC range and sliced to UTC before evaluation; a run that evaluates whatever the source returned is measuring an undeclared window (`FAILURES.md` Entry #025).
3. §5 adds `window_timezone`, frozen to `UTC`, so that a deviation is visible in `PARAMS.md` rather than only in behaviour.

**v0.2.0 → v0.3.0.**
1. Aligned population (§1) and retry rules (§2.5) with $M_1$ v0.7.2 §4.4 determinacy test and $C$ v1.4.0 output vocabulary (`INDETERMINATE_SET` and `EXHAUSTED_RETRY_INDETERMINATE_SET`).
2. Confirmed Option B provisional status for publication lag $L$ in §2.3 and §5 parameter table ($L=10$ calendar days, $\text{run\_day} = 12$).
3. Verified parameter table in §5: removed geometric gap limit $\Delta t_{\text{max}}$ for observation window $W$, matching $M_1$ v0.7.2.

**v0.1.0 → v0.2.0.**
1. Corrected §1 population definition to reflect complete telemetry condition under M₁ §4 and `NOT_EVALUATED — INCOMPLETE_SET` status.
2. Harmonized §2.5 and C §3.2: aborted windows are published as unclassified record entries (`evaluation_status: "NOT_EVALUATED — INCOMPLETE_SET"`, `label: null`). Added denominator rules for $N_{\text{calendar\_total}}$ vs $N_{\text{classified\_total}}$ in §2.4. Codified single retry rule in §2.5 using baseline $B(W)$ (`re_evaluation_attempt: 2`) and defined `EXHAUSTED_RETRY_INCOMPLETE_SET`.
3. Added Telemetry Outage Selection Bias as 3rd Structural Blindness in §4.1 with aligned modality. Separated §4 into Structural Blindnesses (§4.1) vs Calibration Properties (§4.2).
4. Specified publication lag $L$ in §2.3 across primary comparison set $\mathcal{M}$, defined `PENDING_PUBLICATION_LAG` status, codified post-$L$ upstream data revision rule under Isolation Protocol §6, added $N \ge 12$ constraint explicitly to §5 parameter table, and documented selection mode inheritance in §6.

*Amendments require a version bump with stated rationale. Definitions are never edited
silently.*

*VolMax Studio Lab · P10 Verification Protocol*
