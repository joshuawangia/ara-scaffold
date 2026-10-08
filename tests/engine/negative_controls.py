"""Run reversible production-wire mutations; evidence stays in ignored cache/."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    ('solver', 'ara/engine/licensing.py', "if verdict != 'SOLVER_UNSAT':", 'if False:', 'test_licensing.py::test_solver_rejects_affirming_consequent'),
    ('bank', 'ara/engine/licensing.py', 'entry = self.bank.get(proposal.bank_id)', 'entry = self.bank.get(proposal.bank_id) or self.bank.entries[0]', 'test_licensing.py::test_unlicensed_rejected[bank-UNKNOWN_BANK_ID]'),
    ('slots', 'ara/engine/licensing.py', "return result('SLOT_MISMATCH')", "return result('BANK_LICENSED', True)", 'test_licensing.py::test_unlicensed_rejected[slot-SLOT_MISMATCH]'),
    ('goal', 'ara/engine/licensing.py', "return result('CONCLUSION_MISMATCH')", "return result('BANK_LICENSED', True)", 'test_licensing.py::test_unlicensed_rejected[goal-CONCLUSION_MISMATCH]'),
    ('schema', 'ara/engine/licensing.py', 'if not matches_schema(schema, fills, conclusion.formula):', 'if False:', 'test_licensing.py::test_shape_required_even_when_entailment_holds'),
    ('substitution', 'ara/engine/matching.py', 'for sub in schema.substitutions:', 'for sub in ():', 'test_licensing.py::test_schema_rejects_noninstance_even_if_quantifier_entails'),
    ('scope', 'ara/engine/licensing.py', "if by_slot[scope.assumption_slot].t_id != 'open':", 'if False:', 'test_licensing.py::test_assumption_cannot_be_a_t_leaf'),
    ('unknown', 'ara/formal.py', "return 'SOLVER_TIMEOUT' if 'timeout' in solver.reason_unknown().lower() else 'SOLVER_UNKNOWN'", "return 'SOLVER_UNSAT'", 'test_licensing.py::test_solver_unknown_and_timeout_are_discards'),
    ('terminus', 'ara/engine/terminus.py', 'commitment = commitments.get(t_id)', 'return True\n    commitment = commitments.get(t_id)', 'test_search.py::test_terminus_rejects_forged_id_and_formula'),
    ('cq', 'ara/engine/routes.py', 'if any(q.id not in answers or not cq_supported', 'if False and any(q.id not in answers or not cq_supported', 'test_search.py::test_unanswered_cq_keeps_route_open'),
    ('cq_support', 'ara/engine/routes.py', 'and all(commitments.get(tid) is not None for tid in answer.supporting_t_ids)', 'and True', 'test_search.py::test_cq_support_must_exist'),
    ('seed', 'ara/engine/search.py', 'random.Random(self.config.seed)', 'random.Random(0)', 'test_search.py::test_seed_changes_equal_cost_order_and_replays'),
    ('infinite_cost', 'ara/engine/routes.py', "if any(n.kind == 'leaf' and commitments.contains_formula", "if False and any(n.kind == 'leaf' and commitments.contains_formula", 'test_search.py::test_negated_leaf_has_infinite_cost'),
    ('caps', 'ara/engine/search.py', 'if created + len(license.premises) > self.config.node_cap:', 'if False:', 'test_search.py::test_node_and_depth_caps_report_truncation'),
    ('independence', 'ara/engine/routes.py', 'if i == j or bool(s & other)', 'if i == j', 'test_search.py::test_independent_routes_use_canonical_leaves'),
    ('negation', 'ara/engine/conflicts.py', 'negative = engine.search(negate_proposition(positive.target))', 'negative = positive', 'test_search.py::test_negation_search_and_replay'),
    ('forward_depth', 'ara/engine/forward.py', 'range(1, depth + 1)', 'range(1, depth + 2)', 'test_conflicts.py::test_forward_depth_and_flag'),
    ('forward_flag', 'ara/engine/forward.py', 'flagged = commitments.contains_formula(formula.negated())', 'flagged = False', 'test_conflicts.py::test_forward_depth_and_flag'),
    ('tier1', 'ara/engine/conflicts.py', 'if opposite in group and pair not in marked:', 'if False:', 'test_conflicts.py::test_tier1_marks_same_premises_and_requests_repair'),
    ('tier2', 'ara/engine/conflicts.py', 'tier2.append(Tier2Conflict(p.id, n.id, flagged))', 'pass', 'test_conflicts.py::test_tier2_records_first_flagged_consequence'),
    ('exported_support', 'ara/engine/conflicts.py', 'register(support, premises, root.proposition)', 'pass', 'test_conflicts.py::test_tier1_compares_exported_external_support_including_cqs'),
    ('forward_history', 'ara/engine/forward.py', 'on_license(proposal, result)', 'pass', 'test_conflicts.py::test_tier1_includes_forward_licenses'),
    ('canonical_membership', 'ara/engine/terminus.py', 'commitment.formula.canonical() == leaf.formula.canonical()', 'True', 'test_search.py::test_terminus_rejects_forged_id_and_formula'),
    ('quantifier', 'ara/formal.py', "z3.ForAll if op == 'forall' else z3.Exists", 'z3.Exists', 'test_licensing.py::test_quantifier_compilation_and_substitution'),
    ('scoped_closure', 'ara/engine/search.py', 'for scope_id, assumption in reversed(context):', 'for scope_id, assumption in ():', 'test_search.py::test_conditional_scope_closes_without_turning_assumption_into_commitment'),
    ('best_first', 'ara/engine/search.py', "float('inf') if cost is None else cost, rng.random()", "float('inf') if cost is None else -cost, rng.random()", 'test_search.py::test_best_first_prefers_closed_cheaper_alternative'),
)


def check_root() -> None:
    actual = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()
    if Path(actual) != ROOT:
        raise RuntimeError('negative controls require the script checkout root')


def run_test(test: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, '-B', '-m', 'pytest', '-q', f'tests/engine/{test}'],
                          cwd=ROOT, capture_output=True, text=True)


def invalidate(path: Path) -> None:
    for cached in (path.parent / '__pycache__').glob(path.stem + '.*.pyc'):
        cached.unlink()


def main() -> None:
    check_root()
    results = []
    for name, filename, old, new, test in CASES:
        path = ROOT / filename
        original = path.read_text()
        if original.count(old) != 1:
            raise RuntimeError(f'{name}: expected one production wire')
        check_root()
        try:
            path.write_text(original.replace(old, new))
            invalidate(path)
            red = run_test(test)
        finally:
            check_root()
            path.write_text(original)
            invalidate(path)
        green = run_test(test)
        # Collection/runtime errors do not count: require an assertion failure.
        killed = red.returncode == 1 and 'AssertionError' in red.stdout
        restored = green.returncode == 0
        results.append({'control': name, 'test': test, 'red': killed, 'restored_green': restored,
                        'red_output': red.stdout, 'green_output': green.stdout})
        print(f'{name}: red={killed} restored_green={restored}', flush=True)
        if not killed or not restored:
            print(red.stdout, green.stdout)
            break
    check_root()
    (ROOT / 'cache').mkdir(exist_ok=True)
    (ROOT / 'cache/beta-negative-controls.json').write_text(json.dumps(results, indent=2) + '\n')
    if len(results) != len(CASES) or not all(r['red'] and r['restored_green'] for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
