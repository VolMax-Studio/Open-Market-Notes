# Instance & Contribution Checklist

## Instance Protocol (Repo Rules)

1. `cp -r instances/_TEMPLATE instances/<name>`
2. **L0 Legal Check:** Verify licence, terms URL, access date, verbatim attribution string.
3. **Pre-Data Freeze:** Fill and commit `PREREGISTRATION.md` BEFORE fetching data (`git commit`).
4. **Execution:** Write and run `src/run_audit.py` to evaluate lookups against frozen decision rules.
5. **Output Lock:** Save machine-readable `results.json` and tabular audit data inside the same instance directory.
6. **Isolation Invariant:** NEVER write scratch, audit, or probe files into another instance or parent note directory.

---

## Upstream Contribution Protocol (GitHub Rules)

1. **Prior Art Check:** Open `/issues` and `/pulls` on the target repository and search existing issues before drafting.
2. **Empirical Measurement First:** A finding is an exact measured number or literal trace on live/reproduced data, never a theoretical code reading.
3. **Concise Human Tone:** Comments must be 2–3 sentences: exact finding, file/line number, measured number. No unsolicited architecture advice.
