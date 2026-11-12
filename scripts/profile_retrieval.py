"""Profile direct retrieval with explicit read-only inputs and isolated outputs."""
import argparse
import cProfile
import hashlib
import json
from pathlib import Path
import platform
import pstats
import re
import sys
import time
from functools import wraps


STAGE_TIMINGS = {}


def simple_label(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise argparse.ArgumentTypeError('Labels must be nonempty simple identifiers using letters, digits, _, . or -')
    return value


def install_stage_timers():
    from dst_kb import service, retrieval_v2, source_epoch_runtime
    targets = [(service.Service, name) for name in
               ('ready', '_ranker_v2', 'search_kb', '_view_v2', 'get_context_bundle',
                '_research_navigation_rows', '_research_seed_view', '_research_coverage', '_research_followup')]
    targets += [(service, 'signature'), (service, 'serialized_payload_cost'),
                (retrieval_v2.Ranker, '__init__'), (retrieval_v2.Ranker, 'search'),
                (source_epoch_runtime.EpochContext, 'assert_current')]
    for owner, name in targets:
        original = getattr(owner, name)
        key = getattr(owner, '__name__', str(owner)) + '.' + name
        def timed(*args, _function=original, _key=key, **kwargs):
            started = time.perf_counter()
            try:
                return _function(*args, **kwargs)
            finally:
                row = STAGE_TIMINGS.setdefault(_key, {'calls': 0, 'cumulative_seconds': 0.0})
                row['calls'] += 1
                row['cumulative_seconds'] += time.perf_counter() - started
        setattr(owner, name, wraps(original)(timed))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepare_config(runtime, directory):
    """Bind installed committed inputs while keeping the derived index outside it."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / 'source-epochs.json'
    catalog = json.loads((runtime / 'source-epochs.json').read_text(encoding='utf-8'))
    for epoch, entry in catalog['epochs'].items():
        entry['knowledge_root'] = str((runtime / entry['knowledge_root']).resolve())
        entry['index_path'] = str((directory / epoch / 'index.sqlite3').resolve())
        for field in ('knowledge_manifest', 'contract_map', 'source_identity_map',
                      'applicability_ledger', 'source_preparation'):
            if field in entry:
                entry[field]['path'] = str((runtime / entry[field]['path']).resolve())
        for source in entry['source_manifests']:
            source['path'] = str((runtime / source['path']).resolve())
    if target.exists():
        if json.loads(target.read_text(encoding='utf-8')) != catalog:
            raise ValueError('Output configuration belongs to different runtime inputs: ' + str(target))
    else:
        write_json(target, catalog)
    config = directory / 'retrieval-config.json'
    options = {'source_epochs_path': str(target.resolve()), 'default_source_epoch': '759671'}
    if config.exists():
        if json.loads(config.read_text(encoding='utf-8')) != options:
            raise ValueError('Output configuration changed: ' + str(config))
    else:
        write_json(config, options)
    return config


def measured(label, function, directory, profiling):
    STAGE_TIMINGS.clear()
    profiler = cProfile.Profile() if profiling else None
    started = time.perf_counter()
    if profiler:
        profiler.enable()
    error = None
    result = None
    try:
        result = function()
    except Exception as caught:
        error = {'type': type(caught).__name__, 'message': str(caught)}
    finally:
        if profiler:
            profiler.disable()
    seconds = time.perf_counter() - started
    report = {'label': label, 'seconds': seconds, 'profiled': profiling}
    if STAGE_TIMINGS:
        report['outer_stage_timings'] = dict(STAGE_TIMINGS)
    if error is not None:
        report['error'] = error
    if profiler:
        profiler.dump_stats(str(directory / (label + '.prof')))
        stats = pstats.Stats(profiler)
        rows = []
        for (filename, line, name), (primitive, calls, total, cumulative, callers) in stats.stats.items():
            rows.append({'file': filename, 'line': line, 'function': name,
                         'calls': calls, 'primitive_calls': primitive,
                         'self_seconds': total, 'cumulative_seconds': cumulative})
        rows.sort(key=lambda row: -row['cumulative_seconds'])
        write_json(directory / (label + '-functions.json'), rows)
        report['stages'] = [row for row in rows if (
            (Path(row['file']).name == 'service.py' and row['function'] in
             ('ready', '_ranker_v2', 'get_context_bundle', 'search_kb', '_view_v2')) or
            (Path(row['file']).name == 'validation.py' and row['function'] == 'signature') or
            (Path(row['file']).name == 'source_epoch_runtime.py' and row['function'] == 'assert_current') or
            (Path(row['file']).name == 'retrieval_v2.py' and row['function'] in ('__init__', 'search')))]
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        'Use the same output directory with different labels to compare baseline and candidate. '
        'Reusing that output with different runtime inputs is rejected.'))
    parser.add_argument('--code-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--runtime-root', type=Path, required=True,
                        help='Prepared runtime_build directory containing source-epochs.json and matching projection profiles')
    parser.add_argument('--output', type=Path, required=True, help='Isolated configuration, index and evidence directory')
    parser.add_argument('--requests', type=Path, required=True,
                        help='JSON array of {"label":"case", "params":{"name":"get_context_bundle", "arguments":{...}}}')
    parser.add_argument('--label', required=True, type=simple_label,
                        help='New run subdirectory identifier, such as baseline or candidate')
    parser.add_argument('--no-profile', action='store_true', help='Measure elapsed time without cProfile tracing')
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--max-requests', type=int)
    parser.add_argument('--stage-timings', action='store_true', help='Accumulate inexpensive outer-function timings')
    args = parser.parse_args()
    requests = json.loads(args.requests.read_text(encoding='utf-8'))
    for request in requests:
        simple_label(request['label'])
    if args.max_requests is not None:
        requests = requests[:args.max_requests]
    output = args.output.resolve()
    directory = output / args.label
    directory.mkdir(parents=True, exist_ok=False)
    config = prepare_config(args.runtime_root.resolve(), output / 'isolated-config')
    sys.path.insert(0, str(args.code_root.resolve() / 'dst-kb-service'))
    from dst_kb.service import Service
    from dst_kb import projection_v2
    # Prepared records have their own content-bound projection profiles.
    projection_v2.PROFILE_PATH = args.runtime_root.resolve() / 'dst-kb-service/dst_kb/projection_profiles.json'
    if args.stage_timings:
        install_stage_timers()
    manifest = {'python': sys.version, 'platform': platform.platform(),
                'code_root': str(args.code_root.resolve()), 'runtime_root': str(args.runtime_root.resolve()),
                'config': str(config), 'requests': str(args.requests.resolve()),
                'projection_profiles': str(projection_v2.PROFILE_PATH),
                'projection_profiles_sha256': hashlib.sha256(projection_v2.PROFILE_PATH.read_bytes()).hexdigest(),
                'service_code_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                       for path in sorted((args.code_root.resolve() / 'dst-kb-service/dst_kb').glob('*.py'))},
                'operations': []}
    service, row = measured('initialize', lambda: Service(config), directory, not args.no_profile)
    manifest['operations'].append(row)
    write_json(directory / 'summary.json', manifest)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    if row.get('error'):
        raise RuntimeError(row['error'])
    try:
        for iteration in range(args.repeat):
            for request in requests:
                label = request['label'] + ('-' + str(iteration + 1) if args.repeat > 1 else '')
                params = request['params']
                result, row = measured(label, lambda: getattr(service, params['name'])(**params['arguments']),
                                       directory, not args.no_profile)
                if row.get('error'):
                    manifest['operations'].append(row)
                    write_json(directory / 'summary.json', manifest)
                    raise RuntimeError(row['error'])
                raw = json.dumps(result, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
                (directory / (label + '-response.json')).write_bytes(raw)
                row.update({'response_sha256': hashlib.sha256(raw).hexdigest(), 'response_bytes': len(raw),
                            'entries': [entry.get('id') for entry in result.get('entries', result.get('results', []))]})
                manifest['operations'].append(row)
                write_json(directory / 'summary.json', manifest)
                print(json.dumps(row, ensure_ascii=False), flush=True)
    finally:
        service.close()


if __name__ == '__main__':
    main()
