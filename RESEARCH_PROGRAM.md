# Research Program: Independent Verification of Evidence-Bound Computational Claims

> **Document Status:** Draft — SPREMNO ZA GEJT  
> **Repository:** `Open-Market-Notes`  
> **Branch:** `feat/nem-s1-jul2026-verdict`  
> **DOI:** [10.5281/zenodo.22068170](https://doi.org/10.5281/zenodo.22068170) (Concept) | [10.5281/zenodo.22068171](https://doi.org/10.5281/zenodo.22068171) (v0.1.0)  
> **Date:** 2026-08-23  

---

## Abstract

When computational findings (such as energy-market scarcity determinations, asset performance audits, or regulatory compliance metrics) are packaged for third-party consumption, consumers face a fundamental verification gap. Existing provenance and attestation ecosystems (in-toto, SLSA, SCITT) excel at verifying signer identity, envelope integrity, and builder supply chains, but do not independently re-execute domain logic or verify whether declared metrics mathematically follow from the supplied evidence.

This research program experimentally characterizes the boundary between **cryptographic authenticity**, **computational reproducibility**, and **physical empirical truth**. Across an initial literature survey (Part A, Rounds 1–5) and a series of pre-registered adversarial experiments (Part B, Steps 1–3) executed over energy-market telemetry packages, we demonstrate:
1. A zero-trust package gate with cold sandbox re-execution rejects unauthorized signers (T1) and detects forged metric declarations by authorized signers (T2 Discriminant Cell), where standard attestation engines accept them.
2. When an adversary coherently forges telemetry, code, manifest, and verdict concurrently, **both the zero-trust gate and standard cryptographic attestations accept the forgery** (Symmetrical Limit).
3. Under Monte Carlo mutation fuzzing ($N = 10,000$, Seed 42), the zero-trust verifier achieved **zero observed leaks in the adjudicative core across 445–552 resigned candidates per class (upper bound $< 0.67\%$ 95% CI)**, while exhibiting an $11.31\%$ leak rate across auxiliary metadata fields (licensing, types, optional keys), establishing the architectural principle: *Gate coverage equals the output surface of the re-executed script plus explicit static schema constraints.*

---

## 1. Research Questions & Core Thesis

### The Three Verification Questions
Verification of evidence-bound empirical claims is not a monolithic operation. It decomposes into three distinct questions:

$$\begin{aligned}
\mathbf{Q_1} \text{ (Authority):} &\quad \text{Who produced and signed this evidence package?} \\
\mathbf{Q_2} \text{ (Derivation):} &\quad \text{Does the declared finding mathematically follow from the supplied raw data via the frozen rule?} \\
\mathbf{Q_3} \text{ (Truth):} &\quad \text{Does the supplied raw data accurately represent physical reality in the world?}
\end{aligned}$$

### Central Thesis
*Cryptographic signatures (in-toto/DSSE, SLSA) answer $Q_1$. Cold deterministic re-execution (zero-trust package gates) answers $Q_2$. Neither system, acting over a self-contained evidence package without an independent external witness or multi-acquisition anchor, can answer $Q_3$.*

---

## 2. Part A: Literature Survey (Rounds 1–5, May–August 2026)

> **Methodological Note:** Part A represents exploratory literature research conducted without frozen pre-registration protocols. Findings in Part A are strictly bounded as *"not found in sources searched within defined search budgets"*.

```
Part A Overview (Literature & Standards Survey):
├── Round 1: Verification Gap & DeAngelo Audit Quality (1981)
├── Round 2: Proficiency Testing vs Witness Auditing (ISO/IEC 17043)
├── Round 3: Data Quality Attestation & Data Integrity Dimensions
├── Round 4: Computational Reproducibility Frameworks (RO-Crate Workflow Profile)
└── Round 5: Supply Chain Attestation Frameworks (in-toto, SLSA, SCITT, OSCAL, UNTP)
```

### Summary of Part A Findings:
* **Round 1 (Audit Quality & Epistemic Boundaries):** DeAngelo (1981) defines audit quality as the joint probability of discovering a breach and reporting it. In computational audits, manual witness audits verify process compliance but rarely re-execute raw data calculations from scratch.
* **Round 2 (Proficiency Testing vs Witnessing):** Under ISO/IEC 17043, proficiency testing evaluates actual measurement output against inter-laboratory reference values, whereas witness auditing verifies only that an operator followed standard operating procedures.
* **Round 3 & 4 (Reproducibility vs Provenance):** Formats like RO-Crate package datasets and workflow descriptors, but leave automated sandboxed execution and adversarial rejection gates to external domain runners.
* **Round 5 (Standard Attestation Frameworks):** Evaluated whether existing metadata and supply-chain schemas natively express all 6 dimensions of an evidence-bound claim ($Q_1$ through $Q_3$, parameter freezing, data completeness, deterministic re-execution). Found that existing standards split coverage across separate domains without a unified native gate.

---

## 3. Part B: Pre-Registered Adversarial Experiments (Steps 1–3, August 2026)

> **Methodological Protocol:** All experiments in Part B were conducted under frozen pre-registration protocols with explicit threat models, declared test fixtures, published seeds, and public failure logging.

### Threat Models
* **Threat Model T1 (Holder of Package / Unauthorized External Attacker):** Full local filesystem read/write access; can compute SHA-256 hashes and re-run code locally; **does not possess the issuer private signing key**.
* **Threat Model T2 (Authorized Signer / Key Compromise / Malicious Publisher):** Possesses the **valid private cryptographic signing key**; can produce valid cryptographic signatures over arbitrary statements.
* **Threat Model T3 (Source Operator / Physical Reality Deception):** Upstream market telemetry provider (e.g., AEMO, ENTSO-E) publishes truncated or manipulated raw market data at the acquisition boundary.

---

### Step 1: Exhaustive Class II Testing & Monte Carlo Mutation Fuzzing

* **Research Question:** Can a three-tier Zero-Trust Gate (Klasa A: Static Integrity, Klasa B: Evidence Binding, Klasa C: Cold Sandbox Re-Execution) reject arbitrary, non-trivial perturbations of a verified evidence package?
* **Experimental Rig:**
  * Base Package: July 2026 NEM Scarcity Persistence Run (`nem-scarcity-s1`, SHA-256 `83f7ca73...`).
  * Classifier: `run_window.py` (SHA-256 `3d9ea127...`).
  * Fuzzer: `fuzz_gate_survival.py` executing over $N = 10,000$ strictly non-trivial draws (Seed 42).
  * Filter: All $0$-drift no-op draws discarded pre-test.
* **Empirical Fuzzing Results ($N = 10,000$, Seed 42):**
  * Total draws: $10,004$ (4 identical no-ops discarded).
  * Total strictly mutated candidates: $10,000$.
  * Resigned candidates tested (Class II Denominator): $4,528$ ($45.28\%$ of $N$).
  * Total surviving leaks: $512$ ($5.12\%$ overall, **$11.31\%$ Class II leak rate**).
  * Rejection Breakdown: Klasa A: $8,519$ ($85.19\%$), Klasa B: $219$ ($2.19\%$), Klasa C: $750$ ($7.50\%$).

#### Per-Mutation-Type Empirical Distribution & 95% Confidence Intervals:

| Mutation Class | Layer Tested | Total Draws | Resigned Tested | Leaks Observed | Class II Rate / 95% CI Upper Bound |
|---|---|---|---|---|---|
| **`admissibility_fuzz`** | Klasa A (Auxiliary Schema) | 1,042 | 552 | **267** | **48.37%** (Schema leak) |
| **`type_mutation`** | Klasa A (Auxiliary Schema) | 992 | 501 | **190** | **37.92%** (Schema leak) |
| **`delete_key`** | Klasa A (Auxiliary Schema) | 1,018 | 536 | **55** | **10.26%** (Schema leak) |
| **`arithmetic_drift`** | Klasa A (Adjudicative Core) | 1,034 | 468 | **0** | **0.00%** ($< 0.64\%$ 95% CI) |
| **`temporal_drift`** | Klasa A (Adjudicative Core) | 993 | 500 | **0** | **0.00%** ($< 0.60\%$ 95% CI) |
| **`rule_drift`** | Klasa A/B (Adjudicative Core) | 1,005 | 516 | **0** | **0.00%** ($< 0.58\%$ 95% CI) |
| **`verdict_inversion`**| Klasa A (Adjudicative Core) | 995 | 502 | **0** | **0.00%** ($< 0.60\%$ 95% CI) |
| **`metric_fuzz`** | Klasa C (Adjudicative Core) | 965 | 445 | **0** | **0.00%** ($< 0.67\%$ 95% CI) |
| **`recipe_fuzz`** | Klasa A (Static Assertion) | 974 | 508 | **0** | **0.00%** ($< 0.59\%$ 95% CI) |
| **`crypto_fuzz`** | Klasa I (SHA-256 Baseline) | 982 | 0 | **0** | **0.00%** (Klasa I only) |

#### Methodological Finding (Human Enumeration vs Automated Fuzzing):
The developer-authored hand-crafted test suite ($13/13$ passing) contained zero examples of the three leaking mutation classes. The machine fuzzer revealed that $100\%$ of leaks were concentrated in auxiliary schema fields (`source_license`, types, optional metadata) that were outside the output surface of `run_window.py` and lacked explicit regex validators in Klasa A.

---

### Step 2: Prior Art Schema-Level Falsification Matrix (Frozen Benchmark)

We evaluated existing data and supply-chain attestation formats against the three original pre-registered benchmark axes:
1. **Axis 1 (Finding Validity & Telemetry Completeness):** Does the schema natively express domain-specific interval completeness floors (e.g. $\ge 98.0\%$) and physical window boundaries?
2. **Axis 2 (Publication Admissibility & Parameter Lineage):** Does the schema enforce cryptographic freezing of calculation parameters and classifier rules prior to execution?
3. **Axis 3 (Reproducibility Status & Cold Execution):** Does the schema declare an explicit reproducible execution status verified via independent deterministic re-execution?

| Standard / Framework | Depth of Reading | Axis 1 (Finding Validity) | Axis 2 (Admissibility) | Axis 3 (Reproducibility) | Native Fit for Domain Verification |
|---|---|---|---|---|---|
| **in-toto Statement / DSSE** | Spec-level | EXT (Custom Predicate) | EXT (Config Ingestion) | EXT (Runtime Runner) | Requires external verification engine |
| **SLSA v1.0 / VSA** | Spec-level | ABSENT | NATIVE (Build Def.) | ABSENT (Dropped in v1.0) | Build provenance, not telemetry validator |
| **NIST OSCAL** | Spec-level | ABSENT | EXT (Control Params) | ABSENT | Compliance assessment documentation |
| **W3C VC / UNTP DCC** | Spec-level | EXT (Conformity Claim)| NATIVE (Scheme Lineage)| ABSENT | Credential issuance and conformity |
| **RO-Crate v1.1** | Spec-level | EXT (Context Entity) | NATIVE (Parameter Def.)| EXT (Workflow Runner) | Metadata packaging and data linking |
| **IETF SCITT (RFC 9943)** | Abstract only | ABSENT | NATIVE (Signed Claims) | ABSENT | Ledger notarization and transparency |
| **C2PA / OpenChain / EU DPP** | Not reached | — | — | — | Out of search budget / Unreached |

---

### Step 3: Comparative Control Arm Benchmark (P10 vs in-toto / DSSE)

* **Research Question:** How does the P10 Zero-Trust Gate perform side-by-side against an in-toto v1.0 Statement wrapped in a signed DSSE (Ed25519) envelope over the exact same energy market telemetry package and attack suite?
* **Harness:** [`instances/nem-scarcity-s1/src/test_step3_control_arm.py`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/instances/nem-scarcity-s1/src/test_step3_control_arm.py) (Commit `911914f`).

```text
========================================================================================================================
STEP 3: RATIFIED COMPARATIVE EVALUATION MATRIX (EXPECTED VS OBSERVED AUDIT)
========================================================================================================================
| Attack Vector / Scenario                             | TM | P10 (Exp -> Obs)       | in-toto/DSSE (Exp -> Obs)  | Verification Outcome      |
|------------------------------------------------------|----|------------------------|----------------------------|---------------------------|
| 1. Envelope Bit-Flip (Un-resigned / Un-signed)       | T1 | REJECT -> REJECT       | REJECT -> REJECT           | Static Envelope Catch     |
| 2. Payload Mutation (rationale) + Recomputed Digest  | T1 | 2026-08-22: REJ -> ACC | REJECT -> REJECT           | FAILED PREDICTION (Leak)  |
|                                                      |    | 2026-08-23: ACC -> ACC |                            | Ratified Invariant Match  |
| 2. Payload Mutation (rationale) + Signed Attestation | T2 | ACCEPT -> ACCEPT       | ACCEPT -> ACCEPT           | Key signs auxiliary data  |
| 3. Telemetry Bit-Flip on Disk (un-signed)            | T1 | REJECT -> REJECT       | REJECT -> REJECT           | File subject hash catch   |
| 3. Telemetry Incoherent Mutation + Signed Manifest   | T2 | REJECT -> REJECT       | ACCEPT -> ACCEPT           | DISCRIMINANT CELL #1      |
| 4. Declared Metric Mutation (NSW1 m1=99%)            | T1 | REJECT -> REJECT       | REJECT -> REJECT           | Re-execution failure      |
| 4. Declared Metric Mutation (NSW1 m1=99%, signed)    | T2 | REJECT -> REJECT       | ACCEPT -> ACCEPT           | DISCRIMINANT CELL #2      |
| 5. Rule+Spec Substitution (S-8b, uncoherent harness) | T1 | ACCEPT -> REJECT       | REJECT -> REJECT           | FAILED PREDICTION (Rig)   |
| 5. Rule+Spec Substitution (S-8b, T2 attacker)        | T2 | ACCEPT -> REJECT       | ACCEPT -> ACCEPT           | P10 FAILED P. / DSSE PASS |
| 6. Issuer Identity Forgery                           | T1 | ABSENT (Structural)    | REJECT -> REJECT           | Cryptographic Identity    |
| 7. Coherent Telemetry Forgery (D-1 Price Spike)      | T1 | ACCEPT -> ACCEPT       | REJECT -> REJECT           | Re-execution vs Key       |
| 8. Coherent Telemetry Forgery (D-1 Price Spike, signed)| T2| ACCEPT -> ACCEPT       | ACCEPT -> ACCEPT           | SYMMETRICAL CEILING       |
| 9. Upstream Boundary Truncation (119 int. at source) | T3 | NOT TESTED (Ext Ref)   | NOT TESTED (Ext Ref)       | Class III Boundary        |
========================================================================================================================
```

---

## 4. Research Integrity & Failed Prediction Register

Scientific credibility requires transparent recording of failed predictions and test harness limitations.

| Event / Scenario | Pre-Registered Prediction | Observed Outcome | Root Cause & Resolution |
|---|---|---|---|
| **Step 3, Row 2 (T1)** | `2026-08-22: REJECT`<br>`2026-08-23: ACCEPT` | **`ACCEPT`** | *Prediction Failure (2026-08-22).* Falsification altered `verdict.rationale`, an auxiliary string outside the output surface of `run_window.py`. Recorded as an empirical auxiliary schema leak. Aligned on 2026-08-23 under the ratified Coverage Invariant. |
| **Step 3, Row 5 (T1/T2)** | `ACCEPT` | **`REJECT`** | *Prediction Failure.* Substituted $q_{\text{ref}} = 0.50$ caused threshold bracketing ($E_{\text{lower}} < 50\% \le E_{\text{upper}}$), legitimately triggering `NOT_EVALUATED — INDETERMINATE_SET`. Proved classifier determinacy guard. |
| **S-8 Early Harness** | `ACCEPT` | **`REJECT`** | *Harness Defect.* Early 2-state harness swallowed unexpected rejections. Refactored harness to 4 discrete states (`MATCH_ACCEPT`, `MATCH_REJECT`, `FAILED_PREDICTION_UNEXPECTED_REJECTION`, `FAILED_PREDICTION_UNEXPECTED_LEAK`). |
| **Fuzzing Denominators** | 503 & 60 counts | **Withdrawn (#041)** | Preliminary counts ran on uncalibrated/unseeded rigs. Formally withdrawn in favor of strict non-trivial corpus ($N=10,000$, Seed 42, 512 leaks). |

---

## 5. Summary of Failure Register Entries (#037 to #042)

The public failure register (`FAILURES.md`) documents procedural and architectural deviations encountered during research:
* **#037 (Citation Governance):** Ingestion of unverified standard name `eFAIR-X` from search summaries without primary specification inspection.
* **#038 (Governance Boundary):** Repeated unauthorized insertion of `Ratified` headers before explicit human sign-off.
* **#039 (Instance Isolation):** Transient in-place mutation of canonical published verdict artifact on disk during adversarial script development (cleanly reverted).
* **#040 (Specification Divergence):** Divergence between gate enum vocabulary (`ELEVATED`) and ratified classifier partition (`ISOLATED`/`REGIONAL`), and threshold logic divergence ($\ge N_{\text{low}}$ vs $> N_{\text{low}}$). Aligned in commit `0034161`.
* **#041 (Measurement Stability):** Successive unstable fuzzing leak counts (503 vs 60) across uncalibrated test rigs; formally withdrawn in favor of strict non-trivial corpus (512 / 4,528 = 11.31%).
* **#042 (Execution Side-Effect):** Transient modification of `SERIES_LOG.json` during standalone script execution; cleanly restored prior to push with 100% SHA-256 hash parity.

---

## 6. What the Verification System Establishes and What It Cannot

### 6.0 Property Matrix Across Both Verification Mechanisms

Verification is not a single operation. The table below decomposes it by property, and records for each what was measured — not what is assumed. Empty cells are not omissions; they mark controls that remain open.

| Property | Zero-trust gate | in-toto / DSSE | Evidence |
|---|---|---|---|
| Issuer identity | ABSENT — no asymmetric key layer | REJECT (forged signature) | Step 3, Row 6 |
| File integrity, unsealed tamper | REJECT | REJECT | Step 3, Rows 1, 3-T1 |
| Auxiliary schema fields | ACCEPT — 512/4,528 leaked | ACCEPT under valid key | Step 1 fuzzing; Step 3, Row 2 |
| Deterministic derivation, authorised signer | REJECT | ACCEPT | Step 3, Rows 3-T2, 4-T2 |
| Frozen-rule adherence, coherent substitution | NOT TESTED | NOT TESTED | Step 3, Row 5 — rig incoherent, see §7.1 |
| Evidence authenticity, coherent forgery | ACCEPT | ACCEPT | Step 3, Rows 7, 8 |
| Source-boundary truth | NOT TESTED | NOT TESTED | Step 3, Row 9 — requires external reference, see §7.2 |

Two rows carry the comparative result of this program. **Deterministic derivation under an authorised signer** is the only property on which the two mechanisms measurably diverge: a signature verifier accepts a metric that does not follow from the evidence it is bound to, because it does not execute the domain calculation; cold re-execution rejects it. **Evidence authenticity** is the only property on which both mechanisms agree by failing: a package whose telemetry has been modified, whose true derived output has been written back into the verdict, and which has then been re-sealed and signed, is accepted by both.

The remaining rows are not contests. Issuer identity is a property the attestation layer provides and the gate does not; file integrity is provided by both, and by any checksum utility.

#### Three levels, three ceilings

The properties above group into three levels, each with a distinct limit:

**Level 1 — Integrity.** Has the artefact been altered since it was sealed? Answered by digests and signatures. Ceiling: an adversary who re-seals the package defeats it entirely; this is not a weakness of the mechanism but its stated scope.

**Level 2 — Derivation.** Does the declared result follow from the supplied evidence under the referenced rule? Answered by cold re-execution. Ceiling: coverage equals the output surface of the re-executed script plus explicit static assertions. Fields outside that surface are unchecked — measured here as a 48.37% leak rate within the admissibility-fuzz class, against zero observed leaks in the adjudicative core.

**Level 3 — Authenticity.** Does the supplied evidence correspond to the world it claims to describe? Not answered by either mechanism over a self-contained package. Nothing inside such a package can serve as the comparison, because everything inside it is under the control of whoever assembled it.

Level 3 defines the next research question, and this program does not answer it: what constitutes an independent anchor, and what would it take to test one. Candidate directions — independent re-acquisition, upstream signed measurements, transparency logs, cross-source agreement — are named here only to record that no selection has been made. Choosing a mechanism before defining the test would repeat the error this program was built to avoid.

### What the Zero-Trust Gate CAN Establish:
1. **Mathematical Derivation ($Q_2$):** Proves that declared metrics and classification labels were strictly generated by executing the referenced script over the supplied evidence files.
2. **Adversarial Resilience over Adjudicative Core:** Preserves zero leakage ($< 0.67\%$ 95% CI) against manipulated parameters, altered timestamps, inverted labels, and synthetic metrics.
3. **Detection of Malicious Authorized Signers (T2 Discriminant):** Rejects signed packages containing fabricated metric declarations that diverge from cold re-execution.

### What the Zero-Trust Gate CANNOT Establish:
1. **Physical External Truth ($Q_3$):** A closed-loop evidence package cannot distinguish real market telemetry from a 100% mathematically self-consistent synthetic forgery (Coherent S-9).
2. **Upstream Source Censorship (T3):** Truncated or censored data published at the source boundary (e.g. 119 missing intervals) is absorbed by the package baseline unless evaluated against an independent external witness acquisition.
3. **Cryptographic Identity (without DSSE layer):** Standalone P10 packages verify self-consistency but do not natively provide asymmetric cryptographic non-repudiation of the publisher.

---

## 7. Open Questions & Next Research Horizons

### 7.1 Coherent S-8b Rule Substitution
Designing an adversarial test rig that achieves 100% parameter substitution determinacy under valid baseline coverage without triggering indeterminate boundary states.

### 7.2 Multi-Acquisition Cross-Validation (T3 Mitigation)
Architecting multi-witness verification protocols where independent regional telemetry scrapers cross-validate boundary interval counts.

### 7.3 Extended Standard Mapping (Step 2 Round 2)
Expanding spec-level deep reading to European Battery Regulation (EU DPP 2023/1542), C2PA, and PROV-O.

---

## 8. Reproducibility & Artifact Index

All code, adversarial harnesses, test data, and corpora are open-source and reproducible on GitHub:

* **Repository:** `https://github.com/VolMax-Studio/Open-Market-Notes`
* **Branch:** `feat/nem-s1-jul2026-verdict`
* **Comparative Control Arm Harness:** [`instances/nem-scarcity-s1/src/test_step3_control_arm.py`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/instances/nem-scarcity-s1/src/test_step3_control_arm.py)
* **Strict Monte Carlo Fuzzer:** [`instances/nem-scarcity-s1/src/fuzz_gate_survival.py`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/instances/nem-scarcity-s1/src/fuzz_gate_survival.py)
* **Surviving Leak Corpus (512 samples, Seed 42):** [`instances/nem-scarcity-s1/runs/2026-07/fuzz_leak_corpus_seed42_10k_strict.json`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/instances/nem-scarcity-s1/runs/2026-07/fuzz_leak_corpus_seed42_10k_strict.json)
* **Zero-Trust Verification Gate:** [`instances/nem-scarcity-s1/src/gate_verify.py`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/instances/nem-scarcity-s1/src/gate_verify.py)
* **Public Failure Register:** [`FAILURES.md`](https://github.com/VolMax-Studio/Open-Market-Notes/blob/feat/nem-s1-jul2026-verdict/FAILURES.md)

---

## References

1. in-toto Project. *in-toto Attestation Framework Specification v1.0 and DSSE Envelope Specification*. https://github.com/in-toto/attestation
2. Supply-chain Levels for Software Artifacts (SLSA). *SLSA Provenance Specification v1.0 and Verification Summary Attestation (VSA)*. https://slsa.dev/spec/v1.0/provenance
3. IETF SCITT Working Group. *Signed Statements without Proof of Publication (RFC 9943 / IETF Architecture Draft)*. https://datatracker.ietf.org/wg/scitt/documents/
4. National Institute of Standards and Technology (NIST). *Open Security Controls Assessment Language (OSCAL)*. https://pages.nist.gov/OSCAL/
5. United Nations Centre for Trade Facilitation and Electronic Business (UN/CEFACT). *UNTP Digital Conformity Credential (DCC) Specification*. https://uncefact.github.io/spec-untp/
6. RO-Crate Community. *Research Object Crate (RO-Crate) Specification v1.1*. https://www.researchobject.org/ro-crate/1.1/
7. DeAngelo, L. E. (1981). *Auditor size and audit quality*. Journal of Accounting and Economics, 3(3), 183-199.
8. ISO/IEC 17043:2023. *Conformity assessment — General requirements for the competence of proficiency testing providers*. International Organization for Standardization.
