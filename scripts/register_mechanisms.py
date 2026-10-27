"""Build a registered research batch and its derived catalog/commitments.

Explicit --batch binds every input/review hash. No source payload is copied.
Run without --batch to reproducibly regenerate an already registered catalog.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import os
import tempfile


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def module(root):
    spec = importlib.util.spec_from_file_location('registered_families', root / 'dst-kb-service/dst_kb/family_registry.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def _build_staged(root, batch=None, replace_topics=()):
    root = Path(root).resolve()
    kb = root / 'knowledge'
    family = module(root)
    path = kb / family.FILE
    if path.exists():
        registry = family.load(kb)
    else:
        registry = {'schema_version': family.SCHEMA, 'families': []}
        for name, relative in [('legacy', 'data/entries.json'), ('native_ai', 'data/native001/canonical-native001-ai-knowledge.json'), ('native_core', 'data/nativecore/native-core.json')]:
            raw = (kb / relative).read_bytes()
            entries = json.loads(raw)['entries']
            if len(entries) != family.HISTORICAL[name]:
                raise ValueError('Historical family count differs')
            identities = {e['id']: family.digest(e) for e in entries}
            registry['families'].append({'name': name, 'documents': [{'file': relative, 'sha256': hashlib.sha256(raw).hexdigest(),
                'entry_ids': [e['id'] for e in entries], 'record_sha256': identities, 'published_record_sha256': identities.copy()}]})
    if batch is not None:
        entries = json.loads(Path(batch).read_bytes())['documents']
        registered = [dict(row,topic=row.get('topic',Path(row['file']).stem.rsplit('-',1)[0])) for f in registry['families'] if f['name']=='native_mechanism' for row in f['documents']]
        seen_topics=set()
        for item in entries:
            source = Path(item['candidate']).resolve()
            raw = source.read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            if actual != item['sha256']:
                raise ValueError('Candidate differs from independently reviewed batch: ' + str(source))
            document = family.decode(raw)
            spec=importlib.util.spec_from_file_location('registration_contract',root/'dst-kb-service/dst_kb/mechanism_contract.py')
            contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
            contract.validate(document)
            review_source = Path(item['review']).resolve()
            review_raw = review_source.read_bytes()
            if hashlib.sha256(review_raw).hexdigest() != item['review_sha256']:
                raise ValueError('Independent review hash differs')
            review = json.loads(review_raw)
            if review.get('candidate_sha256') != actual or review.get('runtime_verified') is not False:
                raise ValueError('Review does not bind this exact candidate/no-runtime boundary')
            topic = item['topic']
            if topic in seen_topics:raise ValueError('Duplicate batch topic')
            seen_topics.add(topic)
            if not topic.isidentifier():
                raise ValueError('Topic must be a simple identifier')
            relative = 'research/native-mechanisms/' + topic + '-' + actual[:12] + '.json'
            review_relative = 'research/native-mechanisms/reviews/' + topic + '-' + item['review_sha256'][:12] + '.json'
            for destination, payload in ((kb / relative, raw), (kb / review_relative, review_raw)):
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and destination.read_bytes() != payload:
                    raise ValueError('Refusing to overwrite a different research artifact')
                destination.write_bytes(payload)
            dependencies=[]
            for dependency in item.get('review_dependencies',[]):
                dependency_raw=Path(dependency['path']).read_bytes()
                if hashlib.sha256(dependency_raw).hexdigest()!=dependency['sha256'] or not dependency.get('role'):
                    raise ValueError('Review dependency identity/role differs')
                dependency_file='research/native-mechanisms/reviews/'+topic+'-dependency-'+dependency['sha256'][:12]+'.json'
                family.decode(dependency_raw)
                destination=kb/dependency_file
                if destination.exists() and destination.read_bytes()!=dependency_raw:raise ValueError('Review dependency collision')
                destination.write_bytes(dependency_raw)
                dependencies.append({'file':dependency_file,'sha256':dependency['sha256'],'role':dependency['role']})
            prior=review.get('previous_review',{}).get('sha256')
            if prior and not any(d['sha256']==prior for d in dependencies):raise ValueError('Revision review requires its exact prior review dependency')
            position=next((i for i,row in enumerate(registered) if row['topic']==topic),len(registered))
            old=next((row for row in registered if row['topic']==topic),None)
            if old and old['sha256']!=actual and topic not in replace_topics:
                raise ValueError('Topic revision requires explicit --replace-topic: '+topic)
            registered=[row for row in registered if row['topic']!=topic]
            registered.insert(position,{'topic':topic,'file': relative, 'sha256': actual, 'entry_ids': [e['id'] for e in document['entries']],
                'record_sha256': {e['id']: family.digest(e) for e in document['entries']},
                'review': {'file': review_relative, 'sha256': item['review_sha256'], 'status': 'explicit_reviewer_research_only', 'runtime_verified': False,'dependencies':dependencies}})
        registry['families'] = [f for f in registry['families'] if f['name'] != 'native_mechanism'] + [{'name': 'native_mechanism', 'documents': registered}]
    write(path, registry)
    catalog = json.loads((kb / 'CATALOG.json').read_bytes())
    catalog['entries'] = family.catalog_rows(kb, registry)
    catalog['counts'] = family.counts(registry)
    write(kb / 'CATALOG.json', catalog)
    manifest = {'schema_version': 'dst-public-package-manifest/1', 'public_derivative': True, 'files': []}
    for file in sorted(kb.rglob('*')):
        if file.is_file() and file.name != 'PACKAGE-MANIFEST.json' and '__pycache__' not in file.parts:
            raw = file.read_bytes()
            manifest['files'].append({'path': file.relative_to(kb).as_posix(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    write(kb / 'PACKAGE-MANIFEST.json', manifest)
    epochs = json.loads((root / 'source-epochs.json').read_bytes())
    for epoch in epochs['epochs'].values():
        epoch['knowledge_manifest']['sha256'] = hashlib.sha256((kb / 'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()
    write(root / 'source-epochs.json', epochs)
    family.validate_catalog(kb, catalog, family.load(kb))
    return {'counts': catalog['counts'], 'registry_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'runtime_verified': False}


def rebuild(root,batch=None,replace_topics=()):
    root=Path(root).resolve()
    snapshot={file.relative_to(root):file.read_bytes() for file in (root/'knowledge').rglob('*') if file.is_file() and '__pycache__' not in file.parts}
    snapshot[Path('source-epochs.json')]=(root/'source-epochs.json').read_bytes()
    # Stage a full public knowledge snapshot. No active package byte is changed
    # until every document/review/ID/contract and generated commitment validates.
    with tempfile.TemporaryDirectory(prefix='.registration-',dir=root) as directory:
        stage=Path(directory)
        shutil.copytree(root/'knowledge',stage/'knowledge',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(root/'source-epochs.json',stage/'source-epochs.json')
        helpers=stage/'dst-kb-service/dst_kb';helpers.mkdir(parents=True)
        for name in ('family_registry.py','mechanism_contract.py'):
            shutil.copyfile(root/'dst-kb-service/dst_kb'/name,helpers/name)
        result=_build_staged(stage,batch,replace_topics)
        changes=[]
        for source in sorted((stage/'knowledge').rglob('*'))+[stage/'source-epochs.json']:
            if not source.is_file():continue
            relative=source.relative_to(stage)
            target=root/relative
            previous=snapshot.get(relative)
            if previous!=source.read_bytes():changes.append((source,target,previous))
        applied=[]
        try:
            if any(not (root/relative).is_file() or (root/relative).read_bytes()!=raw for relative,raw in snapshot.items()):
                raise ValueError('Package changed during registration staging')
            for source,target,previous in changes:
                # Protect against another maintainer writing between snapshot and commit.
                if (target.read_bytes() if target.exists() else None)!=previous:raise ValueError('Package changed during registration')
                target.parent.mkdir(parents=True,exist_ok=True)
                os.replace(source,target)
                applied.append((target,previous))
        except BaseException:
            for index,(target,previous) in enumerate(reversed(applied)):
                if previous is None:target.unlink(missing_ok=True)
                else:
                    restore=stage/('rollback-'+str(index))
                    restore.write_bytes(previous)
                    os.replace(restore,target)
            raise
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--batch', type=Path)
    parser.add_argument('--replace-topic',action='append',default=[],help='Explicitly replace only this registered topic; other topics remain')
    args = parser.parse_args()
    print(json.dumps(rebuild(args.root, args.batch,args.replace_topic), ensure_ascii=False, indent=2))
