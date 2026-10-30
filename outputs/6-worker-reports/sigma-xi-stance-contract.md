# Sigma round 9 / Xi round 16 content and stance contract

Base: main 5b512de. Status: agreed interface implemented and verified.
Helper: 1ff0f7fafd5f7c633be61525fee33be4a2c3c404.
Construction: 2d713e99743453f4746dd5324cd3832ccb241d64.
Sigma owns construction, build_t_batch prompt/schema, provenance helper and
prepare_commitments persistence. Xi owns classifier/search inputs/cache/admission,
route/report disclosure, and fork/resume copying and validation.

## Existing interfaces preserved

CommitmentSet and commitments.json remain the existing strict codec with four
commitment fields: id, text, citation, formula. New rich construction sets text to
the model-authored **content definition**, not an attribution wrapper. Citation is
copied unchanged. Exact source evidence text remains unchanged in the immutable
source artifact and in the sidecar source_text. Old frozen commitment text is
never rewritten. frozen-t.json and its symbol-catalogue-v1 format/hash stay unchanged.

## Sidecar

Path relative to run directory: `commitment-provenance.json`.

```json
{
  "schema_version": "commitment-provenance-v1",
  "definition_semantics": "content",
  "commitments_sha256": "<lowercase 64-character SHA256>",
  "catalogue_sha256": "<verified catalogue sha256>",
  "commitments": {
    "<commitment id>": {
      "source_id": "<immutable source id>",
      "source_authors": ["<source author>"],
      "attributed_to": "<exact evidence attributed_to>",
      "page_start": 1,
      "page_end": 1,
      "evidence_id": "<same immutable id as mapping key>",
      "attribution": "author_claim",
      "stance": "endorsed",
      "source_kind": "premise",
      "source_text": "<exact immutable evidence text>",
      "omitted_support_ids": []
    }
  },
  "sha256": "<lowercase 64-character SHA256>"
}
```

All shown keys are required, no additional keys. Mapping inventory equals the
frozen T id inventory. Source authors are a list of strings (empty when absent);
a single supplied author string is represented as a singleton list. Authors are
source metadata, while attributed_to preserves the evidence's attributed speaker.
Pages are positive integers with end >= start. Source text is nonempty and exact.
Omitted support IDs are a sorted unique string list, empty when support was not
cut; a nonempty list preserves the prior assumed-premise/support_omitted warning.

Stance mapping: author_claim -> endorsed, reported_view -> reported,
attacked_view -> attacked. A source_kind of reported_view or attacked_view must
agree with the attribution tag; contradictory metadata refuses rather than
silently endorsing. Other source kinds retain the attribution-derived stance.
Endorsed means the evidence was tagged as the source author's claim, **not** that
ARA independently established truth. Stance and omitted support remain distinct.

## Hashes and meaning marker

Use `ara.runtime.cache.canonical` then `digest`: JSON sort_keys=True,
separators=(',', ':'), ensure_ascii=False, allow_nan=False; SHA256 over UTF-8.

- commitments_sha256 = digest(canonical(commitments.to_dict())).
- catalogue_sha256 = the validated frozen-t symbol_catalogue.sha256.
- sha256 = digest(canonical(the entire sidecar object excluding only sha256)).

The verified sidecar's definition_semantics='content' identifies newly constructed
content-level commitment texts AND catalogue definitions. Do not infer this marker
from legacy text. Absence means legacy stance/content semantics unavailable;
it never means all commitments endorsed. A present corrupt/mismatched sidecar
refuses and must never silently downgrade to legacy handling. Cache contexts that
use this metadata must include sidecar sha256 along with T/catalogue identity.

## Helpers (Sigma-owned)

Module: `ara.runtime.commitment_provenance`.

```python
validate_commitment_provenance(value: dict, commitments: CommitmentSet,
                              catalogue: dict) -> dict
load_commitment_provenance(directory: Path, commitments: CommitmentSet,
                          catalogue: dict | None) -> dict | None
```

Both return the verified **full sidecar**, not just its commitments mapping.
`catalogue` is the full catalogue returned by validate_frozen_artifact, not merely
its symbols list. Validation verifies the catalogue against T, exact schema,
inventory, fields, stance mapping, both bindings and sidecar hash; failures raise
ValueError. The loader returns None only if the sidecar path is absent. Present
sidecar without a catalogue refuses. No reconstruction from attributed text.

Sigma's construction uses the shared attribution lexicon to screen model-authored
commitment and symbol definitions and logs correction on failure. It never strips
attribution mechanically to invent content. Frozen legacy artifacts still validate
under their existing codec; the new lexical rule applies to new construction.

## Search ownership

Xi carries metadata into classifier and search/cache contexts and handles
fork/resume preservation and validation. Reported/attacked or otherwise restricted
supports must not silently terminate ordinary premises, critical questions or
forward paths. Sigma does not alter solver or licensing semantics in this patch.

## Author-metadata evidence note

Native extraction publication currently omits the bibliographic record from
literature entries (the extraction log retains it). For those inputs,
source_authors is []; attributed_to is still copied exactly. Explicit source
authors supplied in a rich literature input are preserved. Sigma does not infer
paper authors from an attributed speaker or rewrite legacy extraction artifacts.
