# Sigma round 11 alignment contract (implementation target)

CommitmentSet, commitments.json, frozen-t-v1, catalogue symbols and frozen catalogue helper signatures remain unchanged. Bridge kind/stance live in commitment-provenance.json, never in Commitment fields.

Provenance v1 remains accepted. With nonempty alignment candidates, emit commitment-provenance-v2: same top-level v1 keys plus `alignment`. Hash covers all fields except sha256; bindings cover final rewritten T/catalogue. Full sidecar remains in `commitment_provenance_frozen` before `commitments_frozen`.

Ordinary source rows retain existing v1 shape/stance/source_id. Bridge rows have exactly:
`{kind: "alignment", stance: "model_alignment", source_id: null, source_ids: [sorted source IDs], evidence_ids: [sorted original evidence IDs], definitions: [left original symbol entry, right original symbol entry], judgment: {left, right, relation, reason}}`.
Symbols in definitions have existing {name,kind,arity,definition,evidence_ids} shape. relation is entails_left_right|entails_right_left|contrary for bridges. The generated commitment citation cites both symbol definitions and original evidence citations. Bridge IDs use alignment:<digest>; kind is NOT added to Commitment codec.

`alignment` contains original_commitments (CommitmentSet dict), original_symbols (catalogue list), candidates (bounded scored symbol pairs), judgments, status (accepted|refused), refusal_reason (nullable), mapping (old symbol -> canonical symbol, including identities), candidate_limit, policy_version. All judgments include left/right names, relation (same_content|entails_left_right|entails_right_left|contrary|unrelated), reason. same_content rewrites formulas and merges evidence IDs into lexicographically first symbol, retaining originals here. Transactional consistency gate refuses whole alignment set on unsat/unknown; original T persists, no bridge or rewrites applied.

Accessors unchanged: validate_commitment_provenance(value, commitments, catalogue)->dict; load_commitment_provenance(directory, commitments, catalogue)->dict|None. Validator validates/replays mapping, bridges, type/arity, original/final T and catalogue binding; missing metadata stays unavailable legacy.

Search obligations: model_alignment can be used only as explicitly disclosed alignment premises; never source endorsement. No paper ownership for alignment rows. CLOSED-derived requires at least two endorsed source supports and existing distinct-formula/cross-paper gates. same_content use also needs disclosure via alignment metadata. Provenance hash already partitions cache inputs.

Sigma owns construction pass, prompt/schema, provider dispatch, provenance helper/persistence. Search owner to confirm eligibility/disclosure/closure integration; until confirmation Sigma will cover necessary search seam locally. No paid calls or pushes.

## Implemented refinements

- Candidate rows are `{left: <symbol name>, right: <symbol name>, score: <float>}`; order is descending weighted-cosine score, then left/right names. The policy token is `cross-source-symbol-alignment-v1`.
- No candidate -> v1 provenance, no alignment receipt, `symbol_alignment_candidates` log still records the zero candidate result. Nonempty candidate sets (even all unrelated/refused) -> v2.
- `make_commitment_provenance(commitments, catalogue, provenance, *, alignment: dict | None = None) -> dict` adds only an optional keyword. Existing call sites remain valid.
- `align_symbols(calls, commitments, symbols, provenance) -> (CommitmentSet, list[dict], dict, dict | None)` performs logged runtime judgments. `apply_judgments(commitments, symbols, provenance, judgments)` is the deterministic transactional encoder/consistency gate. Both live in ara/runtime/symbol_alignment.py.
- Accepted receipts are replayed/rechecked on load. A recorded consistency refusal stays refused even if a later solver would resolve; it requires original T, original symbols, original source rows, identity mapping and no bridges. It never grants an alignment on resume.
- Search roles carry bridge definitions/judgment, mandatory route/outline disclosure is present, source CQ evidence excludes bridges, and paper_support excludes model_alignment. Xi confirmed Sigma owns this alignment seam while Xi owns further per-paper novelty/forward changes.
- Final gates in progress; final local commit SHA follows only after green full pytest and controls. No push/paid calls.

Final local commit: `bdeaeb8444113e5c0d6d62e5ac1b494a8f0b5fee`; full pytest 1297/1301 (4 skipped), all 583 controls passed sequentially. No push or paid calls.
