"""Read data only: never execute validator code supplied by a knowledge package."""
import json
import re
from hashlib import sha256
from pathlib import Path
from .config import KBError
from . import native,nativecore

INPUTS = ['data/entries.json','data/sources.json','data/relations.json','data/index.json',
          'data/claims.json','review-support/case-metadata.json']
RELATIONS = {'supports','derived_from','illustrates','counterexample_of','mitigates','tests','corrects','supersedes','related'}
SCHEMA_VERSION = '0.1.1'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def inside(root, path):
    target = (root/path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise KBError('CORRUPTED_KB', 'Artifact outside KB root: '+path)
    return target

def signature(root):
    try:
        files = INPUTS + ['PACKAGE-MANIFEST.json'] + [p.relative_to(root).as_posix() for p in (root/'schemas').glob('*.json')]
        if native.paths(root) or nativecore.paths(root):
            files = sorted(set(files) | {p.relative_to(root).as_posix() for p in root.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts})
        rows=[]
        for n in sorted(files):
            path=inside(root,n)
            raw=path.read_bytes()
            stat=path.stat()
            rows.append((n,len(raw),stat.st_mtime_ns,sha256(raw).hexdigest()))
        return json.dumps(rows)
    except OSError as exc:
        raise KBError('KB_UNAVAILABLE', str(exc)) from exc

def schema_errors(v, s, root, path='$'):
    errors = []
    if '$ref' in s:
        if not s['$ref'].startswith('#/'):
            return [path+': external schema references unsupported']
        sub = root
        for key in s['$ref'][2:].split('/'):
            sub = sub[key.replace('~1','/').replace('~0','~')]
        return schema_errors(v,sub,root,path)
    types = {'object':lambda:isinstance(v,dict),'array':lambda:isinstance(v,list),
        'string':lambda:isinstance(v,str),'boolean':lambda:isinstance(v,bool),
        'integer':lambda:isinstance(v,int) and not isinstance(v,bool),
        'number':lambda:isinstance(v,(int,float)) and not isinstance(v,bool),'null':lambda:v is None}
    if 'type' in s:
        names = s['type'] if isinstance(s['type'],list) else [s['type']]
        if not any(types[t]() for t in names):return [path+': type mismatch']
    if 'const' in s and v != s['const']:errors.append(path+': const mismatch')
    if 'enum' in s and v not in s['enum']:errors.append(path+': enum mismatch')
    if isinstance(v,str) and 'pattern' in s and not re.search(s['pattern'],v):errors.append(path+': pattern mismatch')
    if isinstance(v,(int,float)) and not isinstance(v,bool) and 'minimum' in s and v<s['minimum']:errors.append(path+': below minimum')
    if isinstance(v,dict):
        errors += [path+': missing '+k for k in s.get('required',[]) if k not in v]
        for k,x in v.items():
            if k in s.get('properties',{}):errors += schema_errors(x,s['properties'][k],root,path+'.'+k)
            elif s.get('additionalProperties') is False:errors.append(path+': unexpected '+k)
    if isinstance(v,list):
        if len(v)<s.get('minItems',0):errors.append(path+': minItems')
        if s.get('uniqueItems') and len({json.dumps(x,sort_keys=True) for x in v})!=len(v):errors.append(path+': duplicate item')
        if 'items' in s:
            for i,x in enumerate(v):errors += schema_errors(x,s['items'],root,path+'['+str(i)+']')
    for sub in s.get('allOf',[]):errors += schema_errors(v,sub,root,path)
    if 'anyOf' in s and not any(not schema_errors(v,x,root,path) for x in s['anyOf']):errors.append(path+': anyOf')
    if 'oneOf' in s and sum(not schema_errors(v,x,root,path) for x in s['oneOf'])!=1:errors.append(path+': oneOf')
    if 'if' in s and not schema_errors(v,s['if'],root,path):errors += schema_errors(v,s.get('then',{}),root,path)
    return errors

def check_supported_schema(s):
    allowed={'$schema','$defs','$ref','title','description','type','const','enum','pattern','minimum',
             'properties','required','additionalProperties','items','minItems','uniqueItems','allOf','anyOf','oneOf','if','then'}
    if not isinstance(s,dict):raise KBError('UNSUPPORTED_SCHEMA','Boolean schemas require a new adapter.')
    unknown=set(s)-allowed
    if unknown:raise KBError('UNSUPPORTED_SCHEMA','Unsupported schema keywords: '+str(sorted(unknown)))
    for key in ['properties','$defs']:
        for sub in s.get(key,{}).values():check_supported_schema(sub)
    for key in ['allOf','anyOf','oneOf']:
        for sub in s.get(key,[]):check_supported_schema(sub)
    for key in ['items','if','then']:
        if key in s:check_supported_schema(s[key])

def validate(root):
    errors=[]
    try:
        data={Path(n).stem:read(root/n) for n in INPUTS}
        if data['entries'].get('schema_version') != SCHEMA_VERSION:
            raise KBError('UNSUPPORTED_KB_VERSION','Supported schema contract: '+SCHEMA_VERSION+'; new knowledge versions may retain this contract.')
        for name in ['entries','sources','relations','claims','case-metadata']:
            schema=read(root/'schemas'/f'{name}.schema.json')
            check_supported_schema(schema)
            errors+=schema_errors(data[name],schema,schema,name)
        if errors:raise KBError('CORRUPTED_KB','; '.join(errors[:10]))
        entries=data['entries']['entries']; sources=data['sources']['sources']; claims=data['claims']['claims']
        ids=[x['id'] for group in [entries,sources,claims] for x in group]
        if len(ids)!=len(set(ids)):errors.append('duplicate IDs / namespace collision')
        known=set(ids); byid={x['id']:x for x in entries}; src={x['id']:x for x in sources}; claim={x['id']:x for x in claims}
        if [x['id'] for x in data['index']['entries']]!=[x['id'] for x in entries]:errors.append('index ID/order mismatch')
        for row in data['index']['entries']:
            original=byid.get(row['id'],{})
            for key in ['title','entry_type','knowledge_kind','tags','evidence_level','confidence','status','related','scope_structured','typed_relations']:
                if row.get(key)!=original.get(key):errors.append('index mismatch '+row['id']+':'+key)
        nodes=[n['id'] for group in ['nodes','source_nodes','claim_nodes'] for n in data['relations'][group]]
        if set(nodes)!=known or len(nodes)!=len(known):errors.append('graph node registry mismatch')
        edges={(x['from'],x['relation'],x['to']) for x in data['relations']['edges']}
        for edge in data['relations']['edges']+data['relations']['correction_edges']:
            if edge['from'] not in known or edge['to'] not in known or edge['relation'] not in RELATIONS:errors.append('invalid graph edge')
        def refs(x):
            if isinstance(x,dict):
                if 'source_id' in x and x['source_id'] not in src:errors.append('missing source '+str(x['source_id']))
                if 'claim_id' in x and x['claim_id'] not in claim:errors.append('missing claim '+str(x['claim_id']))
                if x.get('type')=='source_lines' and x.get('end_line',x['start_line'])<x['start_line']:errors.append('reversed locator')
                for v in x.values():refs(v)
            elif isinstance(x,list):
                for v in x:refs(v)
        refs(entries); refs(claims)
        for e in entries:
            if e['evidence_level'] in ['E4','E5'] and not e.get('runtime_records'):errors.append('runtime evidence missing '+e['id'])
            if e['evidence_level']=='E2' and len(set(e.get('created_from_case',[])))<2:errors.append('cross-case evidence missing '+e['id'])
            if e['entry_type']=='source_fact' and not any(src.get(s['source_id'],{}).get('type')=='vanilla_source_snapshot' and s.get('role')=='direct_evidence' for s in e['sources']):errors.append('fact lacks direct vanilla source '+e['id'])
            if e['entry_type']=='failure_case':
                d=e['details']
                if d.get('runtime_reproduced') and not e.get('runtime_records'):errors.append('failure runtime evidence missing '+e['id'])
            if e['entry_type']=='correction':
                for target in e['details'].get('target_claim_ids',[]):
                    if target not in claim or (e['id'],'supersedes',target) not in edges:errors.append('correction claim target mismatch '+e['id'])
            for relation in e['typed_relations']:
                if (e['id'],relation['type'],relation['target']) not in edges:errors.append('missing typed edge')
            for target in e['related']:
                if target not in known or (e['id'],'related',target) not in edges:errors.append('missing legacy edge')
            if e['knowledge_kind'] in ['Recommendation','Engineering Rule Candidate','Engineering Pattern Candidate'] and e['status'] not in ['superseded','deprecated']:
                usable=[s for s in e['sources'] if s.get('role')!='historical' and claim.get(s.get('claim_id'),{}).get('status')!='superseded']
                if not usable:errors.append('superseded-only recommendation '+e['id'])
        for c in claims:
            if c.get('superseded_by') not in byid:errors.append('missing correction target')
        for s in sources:
            if s.get('available_in_package'):
                p=inside(root,s['artifact_path'])
                if not p.is_file() or sha256(p.read_bytes()).hexdigest()!=s['sha256']:errors.append('source hash '+s['id'])
            elif s.get('artifact_path') is not None:errors.append('external source artifact')
        native_data,native_report=native.load(root,schema_errors,check_supported_schema)
        data['native']=native_data
        if native_data and set(native.IDS)&known:errors.append('Native/legacy ID namespace collision')
        core_data,core_report=nativecore.load(root,schema_errors,check_supported_schema,bool(native_data),known)
        data['nativecore']=core_data
        if native_data:
            baseline=read(root/'data/legacy-integrity-baseline.json')
            required=set(INPUTS)|{p.relative_to(root).as_posix() for p in (root/'schemas').glob('*.json')
                                    if p.name not in ('native-ai.schema.json','native-core.schema.json')}
            baseline_files=baseline.get('files',[])
            if baseline.get('schema')!='dst-legacy-integrity-baseline/1' or {row['path'] for row in baseline_files}!=required:
                errors.append('legacy baseline file registry')
            for row in baseline_files:
                p=inside(root,row['path'])
                if not p.is_file() or p.stat().st_size!=row['bytes'] or sha256(p.read_bytes()).hexdigest()!=row['sha256']:
                    errors.append('legacy baseline preservation '+row['path'])
            record_hashes=[{'id':e['id'],'sha256':sha256(json.dumps(e,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()} for e in entries]
            if len(record_hashes)!=64 or record_hashes!=baseline.get('entries'):errors.append('legacy baseline record preservation')
        catalog=read(root/'CATALOG.json');catalog_rows=catalog['entries']
        documents={relative:read(inside(root,relative)) for relative in {row['file'] for row in catalog_rows}}
        catalog_ids=[]
        for row in catalog_rows:
            value=documents[row['file']]
            pointer=row['pointer']
            if not pointer.startswith('/'):errors.append('catalog invalid pointer '+row['id']);continue
            for token in pointer[1:].split('/'):
                token=token.replace('~1','/').replace('~0','~')
                value=value[int(token)] if isinstance(value,list) else value[token]
            catalog_ids.append(value['id'])
            if row['id']!=value['id'] or row['title']!=value['title']:errors.append('catalog pointer identity '+row['id'])
            for key in ('status','knowledge_status','retrieval_status','coding_status'):
                if key in value and row.get(key)!=value[key]:errors.append('catalog state '+row['id']+':'+key)
        expected_catalog_ids=[e['id'] for e in entries]+[e['id'] for e in (native_data or {}).get('entries',[])]+[e['id'] for e in (core_data or {}).get('entries',[])]
        if catalog_ids!=expected_catalog_ids or len(set(catalog_ids))!=len(catalog_ids):errors.append('catalog full ID registry')
        family_counts={name:sum(row['family']==name for row in catalog_rows) for name in ('legacy','native_ai','native_core')}
        expected_families={'legacy':64,'native_ai':13,'native_core':110} if native_data or core_data else {'legacy':64,'native_ai':0,'native_core':0}
        declared_counts={key:catalog.get('counts',{}).get(key,0) for key in ('total','legacy','native_ai','native_core')}
        if declared_counts!={'total':len(catalog_rows),**family_counts} or family_counts!=expected_families:errors.append('catalog full family counts')
        manifest=read(root/'PACKAGE-MANIFEST.json')
        expected={x['path'] for x in manifest['files']}
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=root/'PACKAGE-MANIFEST.json' and '__pycache__' not in p.parts}
        if expected!=actual:errors.append('manifest file set')
        for row in manifest['files']:
            p=inside(root,row['path'])
            if not p.is_file() or p.stat().st_size!=row['bytes'] or sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('manifest hash '+row['path'])
        if errors:raise KBError('CORRUPTED_KB','; '.join(errors[:12]))
        versions={e['version'] for e in entries}
        title_version=re.search(r'\bv(\d+\.\d+(?:\.\d+)?)\b',data['entries'].get('kb_title',''))
        knowledge_version=title_version.group(1) if title_version else (next(iter(versions)) if len(versions)==1 else None)
        return data, {'status':'PASS','schema_version':SCHEMA_VERSION,'kb_version':'0.1.2' if native_data else knowledge_version,
            'base_kb_version':knowledge_version,'native':native_report,'nativecore':core_report,
            'legacy_preservation':'SHA256_IDENTICAL_TO_RECORDED_BASELINE' if native_data else 'not_applicable',
            'catalog':'PASS','catalog_entries':len(catalog_rows),
            'entries':len(entries)+native_report['entries']+core_report['entries'],'legacy_entries':len(entries),
            'native001_entries':native_report['entries'],'nativecore_entries':core_report['entries'],
            'relations':len(edges),'manifest':'PASS','runtime_validation_performed':False,
            'limitations':['Schema subset checked fail-closed for unknown keywords.','Correction guard covers explicit claim references, not natural-language meaning.']}
    except KBError:raise
    except (OSError,ValueError,KeyError,IndexError,TypeError) as exc:
        raise KBError('CORRUPTED_KB',str(exc)) from exc
