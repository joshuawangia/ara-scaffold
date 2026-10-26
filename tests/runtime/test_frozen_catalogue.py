"""Frozen vocabulary identity and legacy artifact compatibility; placeholders only."""
import copy
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.frozen_catalogue import validate_frozen_artifact
from ara.runtime.orchestration import prepare_commitments
from ara.types import CommitmentSet
from test_extraction import rig, ROOT
from test_extraction_rich import rich_calls


def freeze(rig, monkeypatch):
    calls, _, path = rich_calls(rig, monkeypatch)
    commitments = prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    directory = calls.log.path.parent
    return commitments, json.loads((directory / 'frozen-t.json').read_text()), directory


def test_catalogue_identity_binds_frozen_t_without_changing_legacy(rig, monkeypatch):
    commitments, artifact, directory = freeze(rig, monkeypatch)
    assert CommitmentSet.from_json((directory / 'commitments.json').read_text()) == commitments
    catalogue = validate_frozen_artifact(artifact, commitments)
    assert catalogue['symbols']
    assert catalogue['commitments_sha256'] == digest(canonical(commitments.to_dict()))
    payload = {k: v for k, v in catalogue.items() if k not in ('catalogue_id', 'sha256')}
    assert catalogue['sha256'] == digest(canonical(payload))
    assert catalogue['catalogue_id'] == 'sha256:' + catalogue['sha256']
    assert catalogue['symbols'] == sorted(catalogue['symbols'], key=lambda s: s['name'])


@pytest.mark.parametrize('case', ['definition', 'signature', 'missing_symbol', 'identity', 'commitment', 'binding'])
def test_catalogue_refuses_tampering(rig, monkeypatch, case):
    commitments, artifact, _ = freeze(rig, monkeypatch)
    value = copy.deepcopy(artifact)
    cat = value['symbol_catalogue']
    if case == 'definition': cat['symbols'][0]['definition'] = 'Q'
    if case == 'signature': cat['symbols'][0]['arity'] = 2
    if case == 'missing_symbol': cat['symbols'].pop()
    if case == 'identity': cat['catalogue_id'] = 'sha256:' + '0' * 64
    if case == 'commitment': value['commitments']['commitments'][0]['text'] = 'Q'
    if case == 'binding': cat['commitments_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        validate_frozen_artifact(value, commitments)
