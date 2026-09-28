"""Read data only: never execute validator code supplied by a knowledge package."""
import json
import re
from hashlib import sha256
from pathlib import Path
from .config import KBError

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
        return json.dumps([(n,(root/n).stat().st_size,(root/n).stat().st_mtime_ns) for n in sorted(files)])
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
        manifest=read(root/'PACKAGE-MANIFEST.json')
        expected={x['path'] for x in manifest['files']}
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='PACKAGE-MANIFEST.json' and '__pycache__' not in p.parts}
        if expected!=actual:errors.append('manifest file set')
        for row in manifest['files']:
            p=inside(root,row['path'])
            if not p.is_file() or p.stat().st_size!=row['bytes'] or sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('manifest hash '+row['path'])
        if errors:raise KBError('CORRUPTED_KB','; '.join(errors[:12]))
        versions={e['version'] for e in entries}
        title_version=re.search(r'\bv(\d+\.\d+(?:\.\d+)?)\b',data['entries'].get('kb_title',''))
        knowledge_version=title_version.group(1) if title_version else (next(iter(versions)) if len(versions)==1 else None)
        return data, {'status':'PASS','schema_version':SCHEMA_VERSION,'kb_version':knowledge_version,
            'entries':len(entries),'relations':len(edges),'manifest':'PASS','runtime_validation_performed':False,
            'limitations':['Schema subset checked fail-closed for unknown keywords.','Correction guard covers explicit claim references, not natural-language meaning.']}
    except KBError:raise
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise KBError('CORRUPTED_KB',str(exc)) from exc
