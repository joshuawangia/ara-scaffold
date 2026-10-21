"""Placeholder-only rich source and wire responses."""
def graph(source='p', page=1):
    def node(id, kind, text, **kw):
        return dict(id=id, source_id=source, kind=kind, text=text,
                    attribution='author_claim', attributed_to='P', page_start=page, page_end=page,
                    premise_ids=[], conclusion_id=None, qualification_ids=[], applies_to=[],
                    inference_origin=None, **kw)
    items = [node('p', 'premise', 'P'), node('q', 'premise', 'Q'),
             node('r', 'intermediate_conclusion', 'R'), node('f', 'conclusion', 'F(x)'),
             node('d', 'distinction', 'P / Q'), node('qual', 'qualification', 'F(x)'),
             node('i', 'inference', 'P, Q; R'), node('j', 'inference', 'R; F(x)')]
    items[4]['applies_to'] = ['r']
    items[5]['applies_to'] = ['f']
    items[6].update(premise_ids=['p','q'], conclusion_id='r', qualification_ids=['d'], inference_origin='paper_stated')
    items[7].update(premise_ids=['r'], conclusion_id='f', qualification_ids=['qual'], inference_origin='paper_stated')
    return dict(schema_version=2, source_id=source, coverage_complete=True, unresolved_references=[], items=items)



def batch_response(inputs):
    if 'closure' not in inputs:
        return dict(roots=[i['root_id'] for p in inputs['papers'] for i in p['items']], relevance='P', omissions=[])
    symbols = {s['name'] for s in inputs['shared_symbols']}
    commitments = []
    uses = {}
    for paper in inputs['papers']:
        for item in paper['items']:
            # Native formulas include multiple premises and intermediate conclusions.
            name = item['text'] if item['text'] in ('P', 'Q', 'R') else 'F'
            formula = {'op': 'atom', 'name': name}
            if item['kind'] == 'inference':
                name = 'R' if item['text'] == 'P, Q; R' else 'F'
                antecedent = {'op': 'and', 'args': [{'op': 'atom', 'name': 'P'}, {'op': 'atom', 'name': 'Q'}]} if name == 'R' else {'op': 'atom', 'name': 'R'}
                formula = {'op': 'implies', 'args': [antecedent, {'op': 'atom', 'name': name}]}
            def names(f):
                if f['op'] == 'atom': yield f['name']
                for arg in f.get('args', []): yield from names(arg)
            for n in set(names(formula)): uses.setdefault(n, []).append(item['id'])
            commitments.append(dict(id=item['id'], formula=formula))
    return dict(commitments=commitments,
        new_symbols=[dict(name=n, kind='atom', arity=0, definition=n, evidence_ids=ids) for n,ids in sorted(uses.items()) if n not in symbols],
        alignments=[dict(name=n, reason='P') for n in sorted(uses) if n in symbols])
