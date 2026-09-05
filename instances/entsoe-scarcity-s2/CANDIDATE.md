# Candidate Definition — entsoe-scarcity-s2

**Status:** PENDING SPECIFICATION  
**Target Domain:** European Electricity Transparency (ENTSO-E / SDMX / Transparency Platform)  
**Defect Family Under Investigation:** Timezone chunking, DST transitions, and MTU interval boundary truncation across monthly series.

---

## 1. Candidate Claim Description (Draft)
The candidate audit aims to test the exact interval completeness and boundary preservation of public ENTSO-E market/generation/scarcity data series under explicit vintage/as-of timestamps.

## 2. Invariants Required for Preregistration
1. **Exact Vintage / As-Of Timestamp:** Must fix exact snapshot time $T_{\text{vintage}}$.
2. **Exact Expected MTU Count:** Formula defining the exact theoretical integer count of MTU intervals $N_{\text{expected}}$ across each bidding zone and month (including leap days and 23h/25h DST days).
3. **Zero Silent Imputation:** Missing intervals must remain explicitly missing; no silent linear interpolation or boundary forward-filling.
4. **Halting Boundary:** Any ambiguity in timezone semantics (UTC vs local market time) must trigger a formal halt.
