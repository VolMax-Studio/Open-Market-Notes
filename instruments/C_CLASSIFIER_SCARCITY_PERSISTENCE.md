# C — Scarcity Persistence Classifier

> **Document Status:** Draft — SPREMNO ZA GEJT (not frozen, not ratified)
> **Version:** v1.4.0 · supersedes v1.3.0, v1.2.0, v1.1.0, v1.0.0 (defects resolved — see §5)
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Role:** Classifier **C** for event class *scarcity persistence*, under
> `INSTRUMENT_SPEC — Measurement Domain and Visibility Boundaries` (v0.3.0).

---

## 1. Input and Output Domain

**Input:** A complete vector of scalar values $M_1(m, W) \in [0, 1]$ and determinacy states emitted per market $m$ in comparison set $\mathcal{M}$ (containing $N_{\text{total}} = |\mathcal{M}|$ markets) over bounded window $W$, under $M_1$ v0.7.2 §4.4.

**Output:** Exactly one classification label $L \in \{\text{NULL}, \text{ISOLATED}, \text{REGIONAL}\}$ emitted for window $W$, or evaluation status `NOT_EVALUATED — INCOMPLETE_SET` / `NOT_EVALUATED — INDETERMINATE_SET` (`label: null`) if any market $m \in \mathcal{M}$ fails completeness floor or yields an indeterminate elevation state under $M_1$ §4.4.

---

## 2. Elevation Evaluation & Parameter References

Determinacy is evaluated per market $m \in \mathcal{M}$ by $M_1$ §4.4 prior to classification. **Classifier C holds no independent definition of elevation.**

For each market $m \in \mathcal{M}$, elevation is determined by the exposure bounds ($\text{Exposure}_{\text{lower}}$, $\text{Exposure}_{\text{upper}}$) against frozen threshold $S_{\text{thresh}}$:

$$\text{Elevated}(m) = \begin{cases} 
1, & \text{if } \text{Exposure}_{\text{lower}}(m, W) \ge S_{\text{thresh}} \\ 
0, & \text{if } \text{Exposure}_{\text{upper}}(m, W) < S_{\text{thresh}} \\ 
\text{INDETERMINATE}, & \text{if } \text{Exposure}_{\text{lower}}(m, W) < S_{\text{thresh}} \le \text{Exposure}_{\text{upper}}(m, W) 
\end{cases}$$

Classification never receives an indeterminate elevation state. If any zone yields $\text{INDETERMINATE}$, classification aborts immediately with status `NOT_EVALUATED — INDETERMINATE_SET` (`label: null`).

For a fully determinate comparison set, the total number of elevated markets in $\mathcal{M}$ is:

$$N_{\text{elevated}}(W) = \sum_{m \in \mathcal{M}} \text{Elevated}(m)$$

**Parameters:** $S_{\text{thresh}}$, $N_{\text{high}}$, and $N_{\text{low}}$ are abstract parameter symbols. **No numeric parameter value is hardcoded in this document.** All numeric values are frozen in `PARAMS.md` prior to data acquisition.

---

## 3. Closed Vocabulary & Complete Partition Emission Rules

The emission rules form a strict, exhaustive, non-overlapping partition over the integer domain $N_{\text{elevated}} \in \{0, 1, \dots, N_{\text{total}}\}$, where $0 \le N_{\text{low}} < N_{\text{high}} \le N_{\text{total}}$:

| Label | Condition on $N_{\text{elevated}}(W)$ | Integer Range | Interpretation |
|---|---|---|---|
| **`NULL`** | $N_{\text{elevated}}(W) \le N_{\text{low}}$ | $[0, N_{\text{low}}]$ | Ordinary baseline state; signal absent or within uncoordinated noise floor. |
| **`ISOLATED`** | $N_{\text{low}} < N_{\text{elevated}}(W) < N_{\text{high}}$ | $[N_{\text{low}}+1, N_{\text{high}}-1]$ | Localized or idiosyncratic elevation lacking regional multi-zone concurrence. |
| **`REGIONAL`** | $N_{\text{elevated}}(W) \ge N_{\text{high}}$ | $[N_{\text{high}}, N_{\text{total}}]$ | Systemic multi-zone regional elevation across the comparison set. |

### Partition, Incomplete Set, & Reachability Rules:
1. **Partition Completeness:** Since $N_{\text{low}} < N_{\text{high}}$, every integer $k \in \{0, 1, \dots, N_{\text{total}}\}$ falls into exactly one range. The classifier emits exactly one classification label for every fully-determinate comparison set.
2. **Incomplete Set & Indeterminate Set Abort:** If telemetry for any market $m \in \mathcal{M}$ is incomplete under $M_1$ §4.2, the classifier emits `NOT_EVALUATED — INCOMPLETE_SET`. If any market $m \in \mathcal{M}$ yields an indeterminate elevation state under $M_1$ §4.4, the classifier emits `NOT_EVALUATED — INDETERMINATE_SET`. Imputing zero elevation or scaling thresholds dynamically is strictly forbidden ($M_1$ §4.2). The window is published as an unclassified record entry in the series log ($S_1$ §2.5).
3. **Reachability Constraint:** The `ISOLATED` label is reachable if and only if $N_{\text{high}} \ge N_{\text{low}} + 2$. If $N_{\text{high}} = N_{\text{low}} + 1$, the integer range $[N_{\text{low}}+1, N_{\text{low}}]$ is empty ($\emptyset$), and the vocabulary collapses into a clean binary partition $\{\text{NULL}, \text{REGIONAL}\}$.

---

## 4. Mandatory Classifier Properties

1. **Reachability of NULL:** The `NULL` label is reachable and is emitted whenever window elevation remains at or below ordinary expectation ($N_{\text{low}}$).
2. **Pre-Observation Freeze:** $S_{\text{thresh}}$, $N_{\text{high}}$, and $N_{\text{low}}$ are frozen in `PARAMS.md` prior to data acquisition for any scheduled series (under S₁) or pre-registered run.
3. **Reference Distribution Coupling:** The elevation threshold $S_{\text{thresh}}$ must be expressed in units of the instrument's own reference expectation $E[M_1(m)] = 1 - q$ (e.g., $S_{\text{thresh}} = k \cdot (1 - q)$ or a declared multiplier of baseline expectation), ensuring $S_{\text{thresh}}$ is not fitted post-hoc to a remembered window.

---

## 5. Amendment Record

**v1.3.0 → v1.4.0.**
1. Aligned §2 elevation condition with $M_1$ v0.7.2 §4.4 determinacy test over exposure bounds ($\text{Exposure}_{\text{lower}} \ge S_{\text{thresh}}$).
2. Added `NOT_EVALUATED — INDETERMINATE_SET` to output vocabulary and §3 incomplete set abort rules for windows containing an indeterminate zone.
3. Harmonized layer separation: classifier delegates all elevation state determinacy to $M_1$ §4.4.

**v1.2.0 → v1.3.0.**
1. Resolved $N_{\text{total}}$ handling under incomplete telemetry: defined `NOT_EVALUATED — INCOMPLETE_SET` status (`label: null`) prohibiting zero-imputation ($M_1$ §4.2) and dynamic threshold scaling.
2. Updated §1 Input to require complete vector and Output domain for unclassified entries, harmonized with S₁ §2.5.
3. Updated §4.2 parameter freeze scope for scheduled series under S₁.

**v1.1.0 → v1.2.0.** Restored Mandatory Classifier Properties in §4 (NULL reachability, pre-observation freeze, reference expectation coupling). Clarified §3 reachability constraints for `ISOLATED` label when $N_{\text{high}} = N_{\text{low}} + 1$.

**v1.0.0 → v1.1.0.** Two gate blockers resolved. (a) §3 emission rules rewritten as a strict mathematical partition over $N_{\text{elevated}}$, eliminating the unlabelled state that occurred when $N_{\text{elevated}} \ge N_{\text{high}}$ without benchmark confirmation. (b) Removed `m_benchmark` as a structural veto inside **C**, restoring market symmetry across $\mathcal{M}$ and complying with `INSTRUMENT_SPEC` §3.3. (c) Removed hardcoded numeric values ($0.150$) from the body of **C**; all values are deferred to `PARAMS.md`.

*VolMax Studio Lab · P10 Verification Protocol*
