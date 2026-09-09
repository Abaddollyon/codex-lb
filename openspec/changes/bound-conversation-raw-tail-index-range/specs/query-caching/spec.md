## MODIFIED Requirements

### Requirement: Distinct-conversation reads combine the presence rollup with a raw live tail in one statement

The dashboard conversation activity metrics (`conversation_count`, `conversation_request_count`), the dashboard conversation trend buckets, and the UNFILTERED reports summary and per-day conversation counts MUST serve folded history from the presence satellite and the remainder from raw `request_logs`, merged in a single statement per read: the fold watermark read from the state row inside the same statement (an uncorrelated scalar subquery in each branch of the UNION) so the folded segment, its exact raw complement, and the watermark come from one database snapshot, and `COUNT(DISTINCT ...)` deduplicates across the fold boundary. The raw complement MUST be expressed as bounds on `requested_at` — the sub-hour leading edge below the first folded hour and the tail at or above the watermark clamped into the window — so the raw branch is served by bounded index ranges on `requested_at`, never by a per-row filter over a joined watermark column: as an OR of the two ranges when the window bounds are statement constants (dashboard reads), and as two separate UNION ALL range arms when the bounds come from a joined window row (reports per-day reads), because an OR over join-parameterized bounds is not index-usable. Merged results MUST equal the legacy full-raw aggregation whenever the underlying raw rows still exist. With an epoch or missing watermark the reads MUST degrade to exactly the legacy raw queries (no kill switch). Reports reads carrying account, model, or useragent filters MUST keep the legacy raw statement (the satellite has no such dimensions), and non-hour-multiple dashboard display buckets MUST keep the full-raw path. This reverses the `add-request-log-usage-rollups` non-goal that kept distinct conversation counts raw-bound: conversation statistics over folded history now survive request-log retention pruning, except the documented raw-bound residues (sub-hour window edges, filtered reports reads, and daily-report day-row membership, which stays raw-driven).

#### Scenario: Switched conversation reads equal legacy reads while raw exists

- **GIVEN** a corpus with conversations spanning hours, blank and NULL conversation ids, warmup kinds, and soft-deleted rows
- **WHEN** each switched conversation read runs with the conversation watermark at epoch, mid-history on an hour boundary, and at the fold target — including states where the hourly and conversation watermarks differ
- **THEN** every result equals the legacy raw-only implementation exactly

#### Scenario: Results do not depend on where the watermark sits relative to the window

- **GIVEN** aligned, unaligned and open-ended read windows over a corpus whose conversations straddle hour boundaries and display buckets
- **WHEN** the union is aggregated with the state row missing, with the watermark at epoch, below the window, inside the window, and above the window
- **THEN** the distinct-conversation counts, conversation request totals and per-bucket counts equal the raw-only aggregation in every state

#### Scenario: Raw complement is index-bounded

- **GIVEN** a PostgreSQL corpus folded through a watermark a few hours before the window end, with an unaligned window start
- **WHEN** `EXPLAIN (ANALYZE)` runs on the conversation union statement as the application sends it (bind parameters, not literals)
- **THEN** every `request_logs` node is an index or bitmap scan whose Index Cond is on `requested_at` and removes no rows by filter
- **AND** the rows it produces equal the sub-hour leading edge plus the un-folded tail exactly, not the whole window — with the watermark below the window, at the window's first folded hour, inside the window, at the window end, and past the window end
- **AND** for a fully folded hour-aligned window the `request_logs` node returns no rows
- **AND** the reports' labeled per-day union shows the same bounded shape across all its day windows (one range arm for the day edges, one for the tail)

#### Scenario: Conversation statistics survive raw pruning

- **GIVEN** folded conversation presence whose source raw rows have been pruned by retention
- **WHEN** the dashboard conversation activity metrics, hour-multiple conversation trend buckets, or the unfiltered reports summary conversation count are read over that period
- **THEN** the distinct-conversation values equal those reported before the pruning (modulo the documented sub-bucket window edges)

#### Scenario: Filtered reports reads stay raw-bound

- **GIVEN** a reports summary or daily read filtered by account, model, or useragent group
- **WHEN** the read executes
- **THEN** it uses the legacy raw statement and reaches only as far back as raw retention keeps rows

#### Scenario: Non-hour-multiple conversation buckets degrade to full raw

- **GIVEN** a conversation trend request with a display bucket that is not a whole multiple of the rollup hour
- **WHEN** the aggregate is calculated
- **THEN** the legacy full-raw query is used unchanged
