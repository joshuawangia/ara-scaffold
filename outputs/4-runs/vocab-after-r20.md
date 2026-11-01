# Vocabulary after r20 — accepted consolidation subset

Measured 2026-11-01T08:01:25.592725+00:00. **All 22 accepted batches (indices 0–21), comprising 181 distinct SOURCE commitments, were counted.** No partial counting remains within this requested subset.

**Result: 160 bare atoms (88.40%), 21 structured formulas (11.60%), zero predicate symbols, zero constant terms, and zero symbols shared across source papers. No source papers are linked by shared vocabulary.** The 21 structured formulas are implications; their components are atoms/conjunctions. Consolidation has not repaired paper isolation in the accepted subset.

## Counts and baseline comparison

| Metric | Gap3 full baseline | Same 181 commitments before r20 | Accepted r20 subset |
|---|---:|---:|---:|
| Commitments | 243 | 181 | 181 |
| Bare atoms | 212 (87.24%) | 160 (88.40%) | 160 (88.40%) |
| Structured formulas | 31 | 21 | 21 |
| Symbols shared by ≥2 SOURCE papers | 0 (recorded baseline) | 0 (subset of baseline) | 0 (computed actual uses) |
| SOURCE papers represented | 23 | 22 | 22 |

The operator’s “87% atoms” baseline is exactly 212/243 = 87.242798% in the retained baseline receipt. The r20 subset is 1.15 percentage points more atomic than that full baseline, but the matched 181-commitment baseline is already 88.397790% atomic. **There is no change in the atom/structured split within the counted subset.** The full-baseline difference is a coverage/composition difference, not evidence that consolidation made these commitments more atomic.

| Vocabulary metric, accepted formulas only | Count |
|---|---:|
| Distinct predicate signatures (`op=predicate`, name + arity) | 0 |
| Distinct atom symbols (`op=atom`; zero-place propositions) | 160 |
| Distinct predicate-like names if atoms are included | 160 |
| Distinct constant terms | 0 |
| Variable names encountered (excluded from semantic sharing) | 0 |
| Predicates shared across ≥2 SOURCE papers | 0 |
| Atoms shared across ≥2 SOURCE papers | 0 |
| Constant terms shared across ≥2 SOURCE papers | 0 |
| Papers linked by any such shared predicate/atom/term | 0 |
| Symbols used by ≥2 commitments within one paper | 72 |
| Explicit reuse declarations across accepted batches | 0 |

## Top shared predicates and papers

**None.** There are no predicate nodes in the accepted formulas, and broadening “predicate” to include zero-place atoms still yields no shared symbols. Every one of the 160 atom symbols occurs in commitments from exactly one SOURCE paper. No predicate-to-paper ranking can be populated from these receipts.

The 72 symbols appearing in multiple commitments are reused **within** their source paper; that does not create cross-paper links. The accepted batches have 0 explicit reuse declarations. Receipt structure-reuse rates must therefore not be interpreted as cross-paper sharing.

## Scope and interpretation

The run is terminal, not currently live: its retained handoff and terminal audit record exit code 2 after batch 23 exhausted its three attempts. It never froze or completed the final consolidation. This report supplies a descriptive census of accepted batch results, **not** a frozen-T metric or a claim that the whole 243-commitment consolidation succeeded. The other 62 original commitments and every rejected output are excluded.

The accepted subset covers 22 SOURCE papers. Provenance stances are 22 attacked, 149 endorsed, 10 reported. “Accepted” means the consolidation output passed its native gates; it does not mean every source commitment is endorsed. SOURCE attribution is read from the original commitment provenance by exact commitment ID, never inferred from symbol names or catalogue evidence labels. No alignment calls or bridge formulas contributed to this count.

Zero sharing establishes continued formal vocabulary isolation in this subset. It does not prove that the papers lack related ideas, that every conceivable bank rule is unusable, or that the semantic formalizations are faithful. No inference search or model generation was performed for this audit.

## Method and evidence

1. Read the native `vocabulary_consolidation_batch` events only after `construction_forked`; select indices 0–21. Match each to its preceding accepted `consolidate_vocabulary` MODEL receipt. All 22 decoded transport responses equal the accepted batch response. Exclude all 17 rejected MODEL receipts, including failed batch 23.
2. Bind each positional formula to its exact `bindings.slots` commitment ID. Resolve local `n*` handles through `bindings.introduced` and prior `s*` handles through `bindings.catalogue`; identical local handles in different batches are **not** shared symbols. Verify each catalogue key against the cumulative symbol record.
3. Recursively traverse formula `args`, counting the top-level operator separately. Collect atom names, predicate `(name, arity)` signatures and constant terms actually present in formulas. Exclude bound variable spelling from cross-source sharing. Map each use to provenance `source_id`. A symbol is shared only when its use-set contains ≥2 distinct SOURCE IDs; `papers_linked` is the union of those papers.
4. Independently compare recursively collected cumulative symbol-to-commitment uses with every batch’s `bindings.evidence_ids`; all 22 agree. Check native per-batch structural counts and the matched pre-consolidation source inventory. Verify the entire append-only event hash chain and every anchor; the full event-file hash also matches the retained terminal integrity manifest. Confirm source files did not change during reading.

- Producer: `cdec8ff7952530830105d7ca188bbd39841ffb96`.
- [Run events](/home/dev/ara-scaffold/runs/codex-gap-3v-r20/events.jsonl), 7,802 verified records; SHA-256 `e1659c879607f8a0e3f40c88cf230973d1b01d8a19b7996b647485ec243577da`.
- [Working source/provenance](/home/dev/ara-scaffold/runs/codex-gap-3v-r20/working-t-1bc62690866d98aadceaa7aadde8e42b5feee4e8d291a5fd989ef632ed997a40.json); SHA-256 `9df958c00742df476a77d6c1fa929dbe60b679139912b82a6208f7b3d9568c3c`.
- [Terminal audit](/home/dev/ara-work/reports/overnight/gap3v-r20/terminal-audit.json), [accepted-attempt summary](/home/dev/ara-work/reports/overnight/gap3v-r20/live-validation-summary.json), [terminal integrity manifest](/home/dev/ara-work/reports/overnight/gap3v-r20/terminal-integrity.json), [terminal handoff](/home/dev/ara-work/reports/overnight/gap3v-r20/handoff.md).

Accepted-event manifest (event sequence numbers are zero-based native `seq`):

| Batch index | Commitments | Accepted attempt | Native event seq | Native event hash |
|---:|---:|---:|---:|---|
| 0 | 8 | 1 | 7487 | `7e2d9a757d7afaa6df8c7a1800a7af55343517f48c88184addc571c40e4f6812` |
| 1 | 8 | 1 | 7497 | `792e9825618df5ae1cbe5547af5c87ba13b2d569ed5655fb08f38435732ccde7` |
| 2 | 8 | 2 | 7513 | `e413f532a4f7a15ae6214837d39144d6a59777d8b32823d0b54369986d3ad3c9` |
| 3 | 8 | 2 | 7529 | `98c57e8717088a4f5397c3bdfd5b1d04ad2cc4c83a4461553a8b754c42796aee` |
| 4 | 8 | 1 | 7539 | `66a881354feb13bf0a7db8121a3f5d286950b04fc6eb44956900059a9d0b237c` |
| 5 | 8 | 2 | 7555 | `3dfa333acbda3a3c891262bfaf1dfb67c9e13e6c62826afcceac3a5019958697` |
| 6 | 11 | 3 | 7577 | `b73faa3212de2c9129e87dc3f06884a627a348a3dbb2b21c22ee3b5e36750c5a` |
| 7 | 8 | 1 | 7587 | `4088589ed03152ba9c37b9c071500c391b370121ff2a0074b0694eada208c9c4` |
| 8 | 8 | 2 | 7603 | `5f242b80527060e44f9e59f727508ec9e66371b839409fc4e4be6fd47ea6166c` |
| 9 | 8 | 1 | 7613 | `3d738dab7194421a4536ad721d2c925e120849aac8d9914328799dc22947782a` |
| 10 | 8 | 1 | 7623 | `a8d91242b8178ae19db92d6198475cb5bbdbd51e4d0f20986f7eb2994b32f3e0` |
| 11 | 8 | 1 | 7633 | `2868bb55535483ccdbf08f1726cf635ac0189faa9b227fec96113807365fb467` |
| 12 | 8 | 3 | 7655 | `32256e8521e60283d0c5f5628034d1c2e9aae0a3a48a5b48a686daafc00ecb11` |
| 13 | 8 | 1 | 7665 | `32b1bb0c8b1e1f21dd947418a024c74d65c13276ad55bfbc0ccbd84171bd4407` |
| 14 | 8 | 2 | 7681 | `e0632158ec944fbbcb5f36212b6aab2fc219d0f594824f0a45ec6f21b5639c45` |
| 15 | 8 | 2 | 7697 | `58602b67de4937e06d828140d4461360b269ec85ba8a7279d5784f879f2af114` |
| 16 | 8 | 2 | 7713 | `d73fb1ab46262603c7661e5312d30bddc932aa4f5695682933c6d3b54d15d7c8` |
| 17 | 8 | 2 | 7729 | `81a4220d882a9416c302c4125768999c6b3c5dbb302cb86734955de1ad347941` |
| 18 | 8 | 2 | 7745 | `a86aa1d8d0e4c2fb3043bb4fb498021c78265e62cca0278efb39bbb817995b54` |
| 19 | 8 | 2 | 7761 | `78e9fcc3d1d5092b32a2ff769a06b379ceb6271bd2cf38d15786c3fd519dd43d` |
| 20 | 10 | 1 | 7771 | `a8055e12dd8c5dade8a63a8d0deec9299b383a1cd3a8e6f26f3f646420d011c4` |
| 21 | 8 | 1 | 7781 | `8a8683f4538d86716b5eebf856a37a2663836e9ea18140248a03cc02566a54ba` |

SOURCE-paper coverage in this accepted subset:

| SOURCE paper ID | Accepted commitments | Shared predicates/atoms/terms with another paper |
|---|---:|---:|
| `beddorgoldstein2021` | 5 | 0 |
| `braun2012` | 12 | 0 |
| `egan2007` | 6 | 0 |
| `eganhawthorneweatherson2005` | 8 | 0 |
| `eganweatherson2011` | 6 | 0 |
| `gsv1996` | 6 | 0 |
| `hawkesteinertthrelkeld2021` | 6 | 0 |
| `hollidaymandelkern2024` | 31 | 0 |
| `klinedinstrothschild2012` | 5 | 0 |
| `knobeyalcin2014` | 2 | 0 |
| `macfarlane2011` | 6 | 0 |
| `macfarlane2014` | 20 | 0 |
| `moss2015` | 11 | 0 |
| `ninan2018` | 5 | 0 |
| `schaffer2011` | 6 | 0 |
| `veltman1996` | 6 | 0 |
| `vonfintelgillies2007` | 8 | 0 |
| `vonfintelgillies2011` | 5 | 0 |
| `wright2007` | 1 | 0 |
| `yalcin2007` | 9 | 0 |
| `yalcin2011` | 12 | 0 |
| `yalcin2015` | 5 | 0 |

Finding placement: (1) atomicity and matched-baseline comparison — Counts and baseline comparison; (2) no cross-source sharing and within-source reuse — Top shared predicates and papers; (3) terminal/unfrozen, partial-corpus and stance limits — Scope and interpretation; (4) handle resolution, independent use-set reconciliation and receipt integrity — Method and evidence. **4 findings, 4 placed.**

DONE fwd vocab accepted=181 atoms=88.40% shared_predicates=0 papers_linked=0
