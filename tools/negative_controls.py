"""Reproducible production-wire mutations; restore each wire and prove green.

Use only in an otherwise idle checkout. No model calls or network are performed.
The evidence file is a test artifact under gitignored runs/, never a model log.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
Transform = Callable[[str], str]


def write(path: Path, text: str) -> None:
    top = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()
    if Path(top) != ROOT:
        raise RuntimeError('wrong checkout')
    path.write_text(text)


def replace(old: str, new: str) -> Transform:
    def transform(source: str) -> str:
        if old not in source:
            raise ValueError(f'mutation anchor missing: {old}')
        return source.replace(old, new, 1)
    return transform


def json_change(change: Callable[[dict], None]) -> Transform:
    def transform(source: str) -> str:
        document = json.loads(source)
        change(document)
        return json.dumps(document, indent=2) + '\n'
    return transform


def run_tests(target: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, '-m', 'pytest', target, '-q', '--tb=short'],
                          cwd=ROOT, text=True, capture_output=True)


def main() -> None:
    mutations: list[tuple[str, str, str, Transform]] = [
        ('formula-json', 'ara/types.py', 'tests/test_types.py::test_formula_roundtrip',
         replace('return cls.from_dict(json.loads(value))', 'return cls.from_dict({})')),
        ('canonical-order', 'ara/types.py', 'tests/test_types.py::test_canonical_negation',
         replace('key=lambda item: item.to_json()', 'key=lambda item: 0')),
        ('double-negation', 'ara/types.py', 'tests/test_types.py::test_canonical_negation',
         replace("if self.op == 'not' and children[0].op == 'not':", 'if False:')),
        ('negation-wrapper', 'ara/types.py', 'tests/test_types.py::test_canonical_negation',
         replace("return Formula('not', (self,)).normalized()", 'return self')),
        ('formula-shape', 'ara/types.py', 'tests/test_types.py::test_malformed_formula_rejected',
         replace('if not valid:', 'if False:')),
        ('commitment-freeze', 'ara/types.py', 'tests/test_types.py::test_commitment_set_frozen',
         replace('@dataclass(frozen=True)\nclass CommitmentSet', '@dataclass\nclass CommitmentSet')),
        ('nested-tuple-freeze', 'ara/types.py', 'tests/test_types.py::test_commitment_set_frozen',
         replace('return tuple(_convert(args[0], item) for item in value)', 'return value')),
        ('commitment-duplicate', 'ara/types.py', 'tests/test_types.py::test_duplicate_commitment_rejected',
         replace('if len(set(ids)) != len(ids):', 'if False:')),
        ('commitment-membership', 'ara/types.py', 'tests/test_types.py::test_commitment_set_frozen',
         replace('return any(c.formula.canonical() == formula.canonical() for c in self.commitments)', 'return False')),
        ('route-json', 'ara/types.py', 'tests/test_types.py::test_route_graph_roundtrip',
         replace('return cls.from_dict(json.loads(value))', 'return cls.from_dict({})')),
        ('scoped-route-json', 'ara/types.py', 'tests/test_types.py::test_scoped_graph_and_event_roundtrip',
         replace('return cls.from_dict(json.loads(value))', 'return cls.from_dict({})')),
        ('event-payload', 'ara/types.py', 'tests/test_types.py::test_scoped_graph_and_event_roundtrip',
         replace("json.loads(self.payload_json), sort_keys=True, separators=(',', ':'), allow_nan=False,", "json.loads(self.payload_json), sort_keys=False, allow_nan=False,")),
        ('unformalised-negation', 'ara/types.py', 'tests/test_types.py::test_unformalised_negation_rejected',
         replace('if proposition.formula is None:', 'if False:')),
        ('bank-duplicate', 'ara/bank.py', 'tests/test_bank.py::test_duplicate_id_rejected',
         replace('if len(set(values)) != len(values):', 'if False:')),
        ('missing-slots', 'ara/bank.py', 'tests/test_bank.py::test_missing_slots_rejected',
         replace('            _entry(entry)', '            pass')),
        ('undefined-cq-slot', 'ara/bank.py', 'tests/test_bank.py::test_undefined_cq_slot_rejected',
         replace('if field not in slots:', 'if False:')),
        ('formula-schema-meta', 'ara/bank.py', 'tests/test_bank.py::test_malformed_formula_schema_rejected[metavariable]',
         replace("if formula.op == 'atom' and formula.name not in schema.formula_variables:", 'if False:')),
        ('formula-schema-substitution', 'ara/bank.py', 'tests/test_bank.py::test_malformed_formula_schema_rejected[substitution]',
         replace("if sub.slot not in slots | {'conclusion'} or sub.body_variable not in schema.formula_variables:", 'if False:')),
        ('formula-schema-scope', 'ara/bank.py', 'tests/test_bank.py::test_malformed_formula_schema_rejected[scope]',
         replace('if scope.assumption_slot not in slots or not scope.result_slots:', 'if False:')),
        ('cross-file-duplicate', 'ara/bank.py', 'tests/test_bank.py::test_cross_file_duplicate_and_version_rejected',
         replace('if len(set(values)) != len(values):', 'if False:')),
        ('bank-version', 'ara/bank.py', 'tests/test_bank.py::test_cross_file_duplicate_and_version_rejected',
         replace('if len(versions) != 1:', 'if False:')),
        ('bank-load', 'ara/bank.py', 'tests/test_bank.py::test_load_versioned_bank',
         replace('for bank in documents for entry in bank.entries', 'for bank in documents[:1] for entry in bank.entries')),
        ('yaml-duplicate', 'ara/bank.py', 'tests/test_bank.py::test_duplicate_yaml_key_rejected',
         replace('if key in result:', 'if False:')),
        ('deductive-schema-required', 'ara/bank.py', 'tests/test_bank.py::test_deductive_schema_required',
         replace('            _entry(entry)', '            pass')),
        ('defeasible-cqs-required', 'ara/bank.py', 'tests/test_bank.py::test_defeasible_cqs_required',
         replace('            _entry(entry)', '            pass')),
        ('schema-seam-decoder', 'ara/types.py', 'tests/test_schemas.py::test_schema_payloads_deserialize_into_seam',
         replace('return cls(**value)', 'return cls()')),
    ]
    kinds = ['build_t', 'propose_targets', 'propose_cuts', 'formalise', 'map_leaf',
             'answer_cq', 'tier1_repair', 'write_essay', 'audit_essay', 'verify_originality_citations']
    for kind in kinds:
        for wire, change in [('closed-object', lambda d: d.update(additionalProperties=True)),
                             ('required-fields', lambda d: d.update(required=[]))]:
            mutations.append((f'{kind}-{wire}', f'schemas/{kind}.json',
                              f'tests/test_schemas.py::test_model_response_schema[{kind}]', json_change(change)))
    mutations.extend([
        ('schema-formula-shape', 'schemas/formalise.json', 'tests/test_schemas.py::test_formula_schema_rejects_bad_shapes',
         json_change(lambda d: d['$defs'].update(formula={}))),
        ('schema-retain-unverified', 'schemas/verify_originality_citations.json',
         'tests/test_schemas.py::test_verification_cannot_retain_unverified_item',
         json_change(lambda d: d['properties']['items']['items'].pop('allOf'))),
        ('schema-verification-evidence', 'schemas/verify_originality_citations.json',
         'tests/test_schemas.py::test_verified_item_requires_evidence',
         json_change(lambda d: d['properties']['items']['items']['allOf'][0]['then']['properties']['evidence_urls'].update(minItems=0))),
        ('schema-formula-codec', 'schemas/formula.json', 'tests/test_schemas.py::test_formula_schema_accepts_serialized_ast',
         json_change(lambda d: d['$defs']['formula']['oneOf'].pop())),
    ])
    results = []
    destination = ROOT / 'runs/alpha-proof/negative-controls.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    for name, filename, target, transform in mutations:
        path = ROOT / filename
        original = path.read_text()
        try:
            write(path, transform(original))
            red = run_tests(target)
        finally:
            write(path, original)
        green = run_tests(target)
        result = dict(name=name, file=filename, target=target, red_exit=red.returncode,
                      green_exit=green.returncode, red_output=red.stdout+red.stderr,
                      green_output=green.stdout+green.stderr)
        results.append(result)
        write(destination, json.dumps(results, indent=2)+'\n')
        print(f'{name}: red={red.returncode} restored={green.returncode}', flush=True)
        if red.returncode != 1 or green.returncode != 0:
            raise RuntimeError(f'negative control did not meet contract: {name}; see {destination}')
    print(f'{len(results)}/{len(results)} negative controls red; all restored green')


if __name__ == '__main__':
    main()
