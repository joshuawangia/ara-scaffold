# Verified sentence carry-over

The native essay/publication audit can reuse a verified source sentence's role and
clean verdict after an ownership-prefix removal or a unanimously approved
rewording. This does not certify new claims or change repair budgets.

The source must be the current logged `final_draft`, bound to the same route and
an exact canonical draft hash in its preceding complete, clean `audit_essay`
k>=3 consensus. Matching raw model receipts supply the last complete source sample’s effective
sentence roles; all source samples must have clean verdicts, while their valid role
assignments may differ. The matching native `essay_audit` verdicts must also be
clean. Legacy source receipts need not contain later proposal-scope metadata;
current-draft validation remains strict. Current
outline, source evidence and proposal authorization must match the source audit.
A publication supplies that draft through `publication_context.original_draft`.
Missing or incompatible evidence leaves sentences on the ordinary audit path.

`ara.runtime.audit_carryover.normalized_sentence` normalizes whitespace,
typographic quotes and serial commas and removes a leading paper-owned cue.
It retains words, logical symbols and citation markers. Deterministic carry-over
permits removing the cue; adding or changing a cue requires a meaning check.
Citation markers and their bibliography records must remain unchanged.

Other wording changes may be aligned to a source sentence using text similarity.
Alignment is a candidate pairing, never evidence of equivalence. Three fresh
`audit_meaning` calls on the selected audit provider assess whether the proposition,
scope, attribution, ownership and citation role are unchanged. Only three
`equivalent` votes permit inheritance. Any dissent or uncertainty, including a
valid adverse vote in a malformed response, leaves the sentence on the normal
audit path. Persisted decisions prevent favorable rerolls of unchanged pairs.
Unaligned sentences are audited normally. Provider failures remain explicit.

The `sentence_meaning_consensus` events record pair text, source/current sentence
IDs, votes, adverse history and outcome. Native audit inputs and results include
`verified_sentence_carryover`: the exact source/gate hashes, accepted `sentences`,
and all available `meaning_checks`. Accepted methods are `prefix_only` and
`meaning_preserved`; the latter includes three equivalent votes. Raw model audit
responses remain untouched. The effective source labels apply to fresh samples
and old adverse receipts; unrelated adverse findings remain binding. Complete
sentence inventory, valid node IDs, route coverage, proposal disclosure, source
attribution, citation checks and the final k>=3 union gate still apply.

`verified_source_rows` and `aligned_pairs` expose source sentence text and exact
source offsets. `source_text` excludes node markers; `raw_source_text` retains the
original span. A caller reverting prose must preserve the current occurrence's
node-marker and citation inventory and must use an accepted carry-over row, not
an unapproved `meaning_check` alignment suggestion.

Offline tests exercise native logging, source binding, consensus and history.
They establish deterministic behavior given model responses. A live placeholder
probe separately assesses the new classifier; neither establishes candidate
acceptance or a publication export. See [verification](verification.md).
