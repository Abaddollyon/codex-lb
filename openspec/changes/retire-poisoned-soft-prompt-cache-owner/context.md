## Decision record

The existing hard-key retry circuit already has the required threshold, quarantine, replay-safety,
and durable anchor-clear machinery. The missing invariant is owner migration for the soft key after
that machinery proves the upstream lineage is poisoned. Reusing those paths keeps normal prompt-cache
stickiness unchanged and avoids a new timeout or configuration knob.

The bridge row and `StickySession` row are updated in one database transaction. The bridge update is
the authority: it must still name the expected account, owner epoch, and captured response/turn
anchors. The sticky row is updated only when it still names the same account. A concurrent completion,
rebind, or new account wins the compare-and-set and the abandonment reports no retirement.

The tombstone retains the prompt-cache key but records the retired account as exclusion evidence.
Fresh selection uses the same key with the retired account removed from its candidate set; once the
replacement is persisted, subsequent turns use ordinary soft affinity and can warm the replacement
account's upstream cache.
