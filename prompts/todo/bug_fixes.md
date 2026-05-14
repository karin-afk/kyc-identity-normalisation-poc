
## Tier 1 — Pure list/policy edits, near-zero risk (recovers ~8 tests, half a day's work):

Add iban to PRESERVE_FIELDS → fixes A.4.
Create NUMERIC_FIELDS = [share_capital, total_assets, total_liabilities, net_assets, revenue, expenses, number_of_shares, number_of_issued_shares, voting_rights, ownership_percentage] and remove these from PRESERVE_FIELDS. Have B's numeric handler check this list. Fixes B.7–B.10, B.16–B.18.
F returns None for (field_type=person_name, language=ar) — policy gate, route to native review. Fixes I.1.
Remove the dead stub loop (lines 103–109). Cleanup only.

Do these first. They're independent, each tested in isolation, no algorithmic risk.

### Tier 1 todos

- [ ] **T1-1** Add `iban` to `PRESERVE_FIELDS` in `router.py` → fixes A.4
- [ ] **T1-2** Create `NUMERIC_FIELDS` list in `router.py`; remove financial aggregates from `PRESERVE_FIELDS`; update `_try_strategy_b` to gate on `NUMERIC_FIELDS` for numeric path → fixes B.7–B.10, B.16–B.18
- [ ] **T1-3** Add Arabic `person_name` policy gate in `_try_strategy_f`: return `None` when `field_type == "person_name"` and `language == "ar"` → fixes I.1
- [ ] **T1-4** Remove dead stub loop (lines 103–109 of `router.py`) — B and C stubs that can never fire → cleanup only


## Tier 2 — Bounded algorithmic fixes (recovers ~12 tests, 2–3 days):

Fix G's character maps against ICAO Doc 9303 — German ü→UE, ß→SS, Spanish ñ→N, Turkish İ→I, Polish Ł→L. Add French ç/é/è etc. to G's table so G handles it instead of F. Gate G to return None rather than partial output when no entry exists for a char. Fixes G.1–G.5, G.8.
C suffix-extraction mode for company names: tokenise on whitespace and CJK boundaries, scan trailing tokens against the legal-form lookup, extract+normalise the suffix, hand the residual back to F or G. Fixes C.10–C.12, E.2.
Fix calendar handlers in B — Hebrew offset (likely a base-year bug in the library wrapper), Thai Buddhist Era year-only parsing, Hijri day-first parsing. Fixes B.13–B.15.


## Tier 3 — Structural (no test recovery, reduces future bugs):

Replace the GPT-4o-mini classifier with deterministic detection (regex for emails/IBANs/dates, lookup for legal-form tokens, default to person_name with analyst-confirm badge in the UI). This recovers A.5, E.1, E.3 and removes the reproducibility floor for AIG submission. Until this is done, you can't reliably hit 100% even with perfect strategies, and you can't reproduce failures to debug them.
Once Tiers 1–2 are done, look at what's left and decide whether to refactor the router. If you're at 70+/74 with a small known residual, the dispatch table refactor is optional. If genuine cross-strategy interference keeps biting, do it then — driven by real evidence, not anticipation.