## 1. Durable retirement

- [ ] Add an atomic durable repository/coordinator operation that tombstones a prompt-cache bridge
      session and its matching soft sticky owner under expected account and continuity-anchor CAS.
- [ ] Return retired-owner evidence to prompt-cache selection so the next selection excludes the
      poisoned account while preserving the same cache key.

## 2. Retry and recovery

- [ ] Extend retry-circuit admission, loading, settlement, quarantine, and eventless cooldown
      handling to `prompt_cache` keys only.
- [ ] Route repeated eventless prompt-cache abandonment through the new durable retirement operation
      and preserve full-history replay guards.

## 3. Regression coverage

- [ ] Add unit coverage for prompt-cache circuit eligibility and sticky-owner CAS retirement.
- [ ] Add product-path coverage proving two repeated eventless failures retire the durable owner,
      the next request selects a different account, and the original prompt-cache key remains on
      the replacement account.
- [ ] Add race coverage proving a fresh anchor or owner change prevents retirement.

## 4. Verification

- [ ] Run focused unit/integration tests, lint/type checks, `openspec validate --specs`, and
      `git diff --check`.
