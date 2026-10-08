"""A mapper's id is a suggestion, never a commitment license."""
from ara.ports import EventSink
from ara.types import CommitmentSet, Proposition
from ara.engine.licensing import emit


def is_terminus(leaf: Proposition, t_id: str, commitments: CommitmentSet) -> bool:
    commitment = commitments.get(t_id)
    return (commitment is not None and leaf.formula is not None
            and commitment.formula.canonical() == leaf.formula.canonical())


def check_terminus(leaf: Proposition, t_id: str, commitments: CommitmentSet,
                   sink: EventSink, node_id: str) -> bool:
    closed = is_terminus(leaf, t_id, commitments)
    emit(sink, 'licensed' if closed else 'discarded',
         'FROZEN_COMMITMENT' if closed else 'NOT_IN_COMMITMENTS', node_id=node_id)
    if commitments.contains_formula(leaf.formula.negated()):
        emit(sink, 'discarded', 'OPPOSED_COMMITMENT', node_id=node_id)
    return closed
