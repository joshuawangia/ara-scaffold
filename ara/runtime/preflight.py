"""Live grammar compilation through the extraction transport and accounting boundary."""
from ara.runtime.cache import canonical, digest
from ara.runtime.providers import structured_schema


def schema_preflight(calls):
    # Enumerate all response-shaping inputs, including both correction candidates.
    variants = [{'mode': 'initial'}, {'mode': 'reconcile_ranges'},
                {'mode': 'reconcile_ranges', 'obligations': [{'id': 'P'}]}]
    for base in list(variants):
        for items in ([], [{'id': 'P'}]):
            variants.append({**base, 'mode': 'targeted_correction',
                             'original_mode': base['mode'], 'candidate': {'items': items}})
    seen = set()
    wires = []
    for inputs in variants:
        schema = calls.response_schema('extract_paper', inputs)
        wire = structured_schema(schema, calls.config.get('formula_output_depth', 2))
        identity = digest(canonical(wire))
        if identity not in seen:
            seen.add(identity)
            wires.append((identity, inputs, wire))
    calls.log.record('schema_preflight_started', distinct_schemas=len(wires),
                     model=calls.requested_model('extract_paper'), maximum_output_tokens=1,
                     wires=[{'schema_id': identity, 'inputs': inputs, 'wire': wire}
                            for identity, inputs, wire in wires])
    for identity, inputs, _ in wires:
        calls.log.record('schema_preflight_case', schema_id=identity, inputs=inputs)
        calls._call_once('extract_paper', inputs, schema_smoke=True)
        calls.log.record('schema_preflight_accepted', schema_id=identity)
    result = dict(passed=True, distinct_schemas=len(wires), accounted_usd=float(calls.budget.used_cost))
    calls.log.record('schema_preflight_finished', **result)
    return result
