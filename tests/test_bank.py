from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ara.bank import load_bank, validate_bank

BANK = Path(__file__).resolve().parents[1] / 'bank'


def document():
    return yaml.safe_load((BANK / 'deductive.yaml').read_text())


def test_load_versioned_bank():
    bank = load_bank(BANK)
    assert bank.bank_version == '1.0.0'
    assert len(bank.entries) == 36
    assert bank.get('modus_ponens').formula_schema is not None
    assert bank.get('expert_opinion').critical_questions
    assert bank.get('absent') is None
    cp = bank.get('conditional_proof').formula_schema
    assert cp.scopes[0].assumption_slot == 'assumption'
    assert cp.scopes[0].result_slots == ('result',)


def test_duplicate_id_rejected():
    data = document()
    data['entries'].append(deepcopy(data['entries'][0]))
    with pytest.raises(ValueError, match='duplicate'):
        validate_bank(data)


@pytest.mark.parametrize('mutation', ['empty', 'missing', 'schema_slot'])
def test_missing_slots_rejected(mutation):
    data = document()
    entry = data['entries'][0]
    if mutation == 'empty':
        entry['premise_slots'] = []
    elif mutation == 'missing':
        del entry['conclusion_slot']
    else:
        entry['formula_schema']['premises'].pop()
    with pytest.raises(ValueError):
        validate_bank(data)


def test_undefined_cq_slot_rejected():
    data = yaml.safe_load((BANK / 'schemes.yaml').read_text())
    data['entries'][0]['critical_questions'][0]['template'] = 'Is {undefined_slot} supported?'
    with pytest.raises(ValueError, match='undefined'):
        validate_bank(data)


@pytest.mark.parametrize('mutation', ['arity', 'metavariable', 'substitution', 'scope'])
def test_malformed_formula_schema_rejected(mutation):
    data = document()
    entry = data['entries'][0]
    if mutation == 'arity':
        entry['formula_schema']['conclusion'] = {'op': 'implies', 'args': []}
    elif mutation == 'metavariable':
        entry['formula_schema']['conclusion'] = {'op': 'atom', 'name': 'UNDECLARED'}
    elif mutation == 'substitution':
        entry = next(e for e in data['entries'] if e['id'] == 'universal_instantiation')
        entry['formula_schema']['substitutions'][0]['slot'] = 'missing'
    else:
        entry['formula_schema']['scopes'] = [
            {'id': 's1', 'assumption_slot': 'missing', 'result_slots': ['conditional']}]
    with pytest.raises(ValueError):
        validate_bank(data)


def test_cross_file_duplicate_and_version_rejected(tmp_path):
    data = document()
    (tmp_path / 'a.yaml').write_text(yaml.safe_dump(data))
    (tmp_path / 'b.yaml').write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match='duplicate'):
        load_bank(tmp_path)
    data['bank_version'] = '2.0.0'
    (tmp_path / 'b.yaml').write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match='version'):
        load_bank(tmp_path)


def test_duplicate_yaml_key_rejected(tmp_path):
    path = tmp_path / 'a.yaml'
    path.write_text('bank_version: 1.0.0\nbank_version: 2.0.0\nentries: []\n')
    with pytest.raises(ValueError, match='duplicate YAML'):
        load_bank(path)


def test_deductive_schema_required():
    data = document()
    data['entries'][0]['formula_schema'] = None
    with pytest.raises(ValueError, match='requires formula schema'):
        validate_bank(data)


def test_defeasible_cqs_required():
    data = yaml.safe_load((BANK / 'schemes.yaml').read_text())
    data['entries'][0]['critical_questions'] = []
    with pytest.raises(ValueError, match='requires CQs'):
        validate_bank(data)
