## Why

The HTTP bridge retry circuit and poisoned-anchor quarantine currently apply only to hard
continuity keys. A repeated eventless WebSocket failure on a soft `prompt_cache` key can therefore
clear the in-memory session while leaving the durable prompt-cache owner bound to the same account.
The next request reattaches that account and repeats the wedge until the operator changes the cache
key or disables the WebSocket bridge.

## What Changes

- Treat `prompt_cache` bridge keys as eligible for the existing retry circuit and eventless poison
  quarantine. Other soft affinity kinds retain their current behavior.
- After the existing repeated-eventless evidence authorizes an abandonment, atomically tombstone the
  durable prompt-cache bridge row and its matching `StickySession` row with expected-owner and
  expected-anchor compare-and-set predicates. Clear the bridge's continuity evidence so a new
  account cannot inherit an upstream response anchor.
- Preserve the prompt-cache key on the next request, but exclude the retired account from fresh
  selection so the replacement uses a different account/upstream lineage. The first turn on that
  account may be a cache miss; later turns warm its cache normally.
- Keep delta-only replay safety: an anchor is never stripped from a request unless the existing
  replay proof allows a fresh unanchored request.

## Not in this change

- Hard continuity-owner retirement, which already has its own request and scheduled paths.
- The separate Responses-Lite `parallel_tool_calls` image compatibility issue.
- Production deployment or direct database edits.

## Impact

No schema or new setting is required. The change uses the existing nullable continuity-abandonment
columns and retry-circuit storage, and adds product-path regression coverage for repeated eventless
prompt-cache failures, CAS races, account migration, and cache-key retention.
