"""Build a content-free calibration artifact from verified, measured receipts."""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.claude_code import CANARY_SCHEMA
from ara.runtime.logging import EventLog, read_log

VERSION = 'claude-code-input-v1'
KINDS = ('build_t_batch', 'select_t_roots', 'propose_targets')


def build(api_logs, cli_logs):
    sources, samples, cli_samples, seen = [], [], [], set()
    for channel, paths in (('api_count', api_logs), ('cli_usage', cli_logs)):
        for path in paths:
            path = Path(path).resolve()
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            EventLog(path)  # Verify the independent anchor as well as the chain.
            rows = read_log(path)
            source = dict(path=str(path), sha256=checksum,
                          anchor_sha256=hashlib.sha256(path.with_suffix('.anchor').read_bytes()).hexdigest(), channel=channel)
            sources.append(source)
            for row in rows:
                event = row['event']; payload = json.loads(event['payload_json'])
                if channel == 'api_count':
                    if event['stage'] not in ('context_plan', 'context_admission'):
                        continue
                    kind = payload['kind']
                    if kind not in KINDS or payload.get('token_count_method', 'provider_count') != 'provider_count':
                        continue
                    prompt, tokens = payload['prompt'], payload['input_tokens']
                    system = ''  # These receipts use no separate API system text.
                else:
                    if event['label'] != 'MODEL' or payload.get('provider') != 'claude_code' or payload.get('cache_hit'):
                        continue
                    kind, prompt, system = event['stage'], event['prompt'], payload.get('system_prompt', '')
                    usage = event['usage']
                    tokens = sum(usage[k] for k in ('input_tokens', 'cache_read_tokens', 'cache_write_tokens'))
                    if payload.get('accounting') != 'actual':
                        continue
                schema = CANARY_SCHEMA if kind == 'isolation_canary' else json.loads(prompt.split('\nINPUT_JSON\n')[0].split('\n')[-1])
                size = len((prompt + system + canonical(schema)).encode())
                assert type(tokens) is int and tokens > 0 and size > 0
                identity = (channel, kind, digest(prompt + system), digest(canonical(schema)), tokens)
                if identity in seen:
                    continue
                seen.add(identity)
                sample = dict(kind=kind, bytes=size, tokens=tokens, prompt_sha256=identity[2], schema_sha256=identity[3],
                              source_sha256=checksum, seq=row['seq'], event_sha256=row['hash'])
                (samples if channel == 'api_count' else cli_samples).append(sample)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == checksum, 'calibration source changed'
    grouped = defaultdict(list)
    for sample in samples:
        grouped[sample['kind']].append(sample['tokens'] / sample['bytes'])
    factors = {}
    for kind in KINDS:
        values = sorted(grouped[kind])
        assert values, f'no measured calibration samples for {kind}'
        q = values[math.ceil(.99 * len(values)) - 1]
        factors[kind] = dict(samples=len(values), p99=q, factor=math.ceil(q * 1.05 * 1e6) / 1e6,
                             maximum_observed_ratio=max(values))
    fallback = max(v['factor'] for v in factors.values())
    assert cli_samples, 'CLI runtime overhead requires measured CLI receipts'
    residuals = [max(0, s['tokens'] - math.ceil(s['bytes'] * factors.get(s['kind'], {'factor':fallback})['factor']))
                 for s in cli_samples]
    return dict(version=VERSION, quantile=.99, margin=1.05, quantile_method='nearest rank; deduplicated requests',
                byte_basis='UTF-8(prompt + system + canonical(full schema)); no fixed byte envelope',
                factors=factors, fallback_factor=fallback,
                runtime_overhead_tokens=math.ceil(max(residuals) * 1.05),
                overhead_basis='max positive CLI aggregate input minus calibrated text estimate, times 1.05; cache input included',
                limitations='Measured calibration, not a tokenizer or hard upper bound. CLI aggregate input conservatively bounds initial input. Unknown kinds use the largest API factor. Live observations tighten upward only.',
                sources=sources, api_samples=samples, cli_samples=cli_samples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-log', action='append', required=True, type=Path)
    parser.add_argument('--cli-log', action='append', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    table = build(args.api_log, args.cli_log)
    args.output.write_text(json.dumps(table, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:table[k] for k in ('version','factors','fallback_factor','runtime_overhead_tokens')}))


if __name__ == '__main__':
    main()
