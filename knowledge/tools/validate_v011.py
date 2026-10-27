"""可移植验证：默认不访问任何original_path；--check-external只做可选指纹对照。"""
import argparse,copy,json,re
from pathlib import Path
from hashlib import sha256
from collections import Counter
from validate import schema_errors,collection_errors
ROOT=Path(__file__).resolve().parents[1]
RELATIONS={'supports','derived_from','illustrates','counterexample_of','mitigates','tests','corrects','supersedes','related'}

def semantic_migration_diff(old,new):
    """独立重算正文比较，不把迁移脚本自己的PASS当成证据。"""
    if [e['id'] for e in old['entries']] != [e['id'] for e in new['entries']]:return ['entry IDs/order']
    result=[]
    def normalize(x):
        if isinstance(x,dict):
            if 'source_id' in x:
                for k in ['role','locator_structured','claim_id']:x.pop(k,None)
            for v in x.values():normalize(v)
        elif isinstance(x,list):
            for v in x:normalize(v)
    for before,after in zip(old['entries'],new['entries']):
        a=copy.deepcopy(before);b=copy.deepcopy(after)
        oldrefs=a.pop('sources');newrefs=b.pop('sources');normalize(newrefs)
        if [x for x in newrefs if x['source_id']!='KLEI-LOCAL-20260928']!=oldrefs:result.append(after['id']+': legacy sources')
        for k in ['scope_text','scope_structured','typed_relations','schema_version','version']:a.pop(k,None);b.pop(k,None)
        normalize(b)
        if after['entry_type']=='case':b['details']['confirmed_failure_cases']=b['details'].pop('static_failure_paths')
        if after['entry_type']=='failure_case':
            b['details'].pop('static_path_confirmed');b['details'].pop('runtime_validation_status')
        if after['entry_type']=='correction':b['details'].pop('target_claim_ids')
        if a!=b:result.append(after['id']+': knowledge body')
    return result
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def contained(root,path):
    p=(root/path).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('artifact outside root: '+path)
    return p

def semantic_errors(db,src,claims):
    errors=[];es=db['entries'];byid={e['id']:e for e in es};ss={s['id']:s for s in src['sources']};cs={c['id']:c for c in claims['claims']}
    allids=set(byid)|set(ss)|set(cs)
    if len(allids)!=len(byid)+len(ss)+len(cs):errors.append('ID namespace collision')
    if len(ss)!=len(src['sources']) or len(cs)!=len(claims['claims']):errors.append('source/claim duplicate ID')
    superseded={c['id'] for c in cs.values() if c['status']=='superseded'}
    def refs(x,where):
        if isinstance(x,dict):
            if 'source_id' in x:
                if x['source_id'] not in ss:errors.append(where+': source missing')
                if x.get('claim_id') and x['claim_id'] not in cs:errors.append(where+': claim missing')
                for loc in x.get('locator_structured',[]):
                    if loc.get('end_line',loc.get('start_line',0))<loc.get('start_line',0):errors.append(where+': reversed source lines')
            for v in x.values():refs(v,where)
        elif isinstance(x,list):
            for v in x:refs(v,where)
    for e in es:
        id=e['id'];d=e['details'];refs(e,id)
        if e['entry_type']=='source_fact':
            if not any(s['source_id']=='KLEI-LOCAL-20260928' and s.get('role')=='direct_evidence' for s in e['sources']):errors.append(id+': missing direct Klei evidence')
        for r in e.get('typed_relations',[]):
            if r['type'] not in RELATIONS or r['target'] not in allids:errors.append(id+': invalid typed relation')
        for case in e['scope_structured']['cases']:
            if case not in byid or byid[case]['entry_type']!='case':errors.append(id+': invalid scope case')
        if e['scope_text']!=e['scope']:errors.append(id+': legacy scope alias differs')
        if e['entry_type']=='case' and 'confirmed_failure_cases' in d:errors.append(id+': deprecated failure field in active 0.1.1 writer')
        if e['entry_type']=='failure_case':
            if d.get('static_path_confirmed') is not True or d.get('runtime_reproduced') is not False or d.get('runtime_validation_status')!='not_runtime_reproduced':errors.append(id+': static/runtime distinction lost')
        if e['entry_type']=='correction':
            for target in d.get('target_claim_ids',[]):
                if target not in cs or cs[target]['status']!='superseded':errors.append(id+': correction target missing/not superseded')
                for kind in ['corrects','supersedes']:
                    if {'type':kind,'target':target} not in e['typed_relations']:errors.append(id+': missing '+kind+' edge')
        if e['knowledge_kind'] in ['Recommendation','Engineering Rule Candidate','Engineering Pattern Candidate'] and e['status'] not in ['superseded','deprecated']:
            # 只对显式Claim绑定做确定判断；未标注自然语言不假装可理解。
            usable=[s for s in e['sources'] if s.get('role')!='historical' and s.get('claim_id') not in superseded]
            if not usable:errors.append(id+': no active evidence; superseded/historical-only recommendation')
    for c in cs.values():
        refs(c,c['id'])
        if c['superseded_by'] not in byid:errors.append(c['id']+': superseding correction missing')
    k=ss.get('KLEI-LOCAL-20260928',{})
    if k.get('type')!='vanilla_source_snapshot' or k.get('available_in_package') is not False or k.get('artifact_path') is not None:errors.append('Klei snapshot registry invalid')
    if k.get('version_context',{}).get('steam_build') is not None:errors.append('Unexpected invented Steam build')
    return errors

def resolve_pointer(document,pointer):
    if pointer.startswith('#'):pointer=pointer[1:]
    if not pointer:return document
    if not pointer.startswith('/'):raise ValueError('invalid JSON pointer '+pointer)
    value=document
    for token in pointer[1:].split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def validate_catalog_native(root,errors):
    """Check the single 187-entry machine catalog and retained native evidence."""
    catalog=read(root/'CATALOG.json');rows=catalog['entries'];cache={};raw_cache={};reference_count=0
    expected=[]
    families={'legacy':('data/entries.json',None),
              'native_ai':('data/native001/canonical-native001-ai-knowledge.json','native-ai.schema.json'),
              'native_core':('data/nativecore/native-core.json','native-core.schema.json')}
    for family,(relative,schemafile) in families.items():
        doc=read(contained(root,relative));cache[relative]=doc
        if schemafile:
            schema=read(root/'schemas'/schemafile);errors.extend(schema_errors(doc,schema,schema,family))
        for entry in doc['entries']:expected.append((entry['id'],family))
    counts={'total':len(rows),**dict(Counter(row['family'] for row in rows))}
    registry_path=root/'FAMILY-REGISTRY.json'
    if registry_path.is_file():
        import importlib.util
        spec=importlib.util.spec_from_file_location('knowledge_families',root.parent/'dst-kb-service/dst_kb/family_registry.py')
        registry_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(registry_module)
        registry=registry_module.load(root)
        try:registry_module.validate_catalog(root,catalog,registry)
        except ValueError as exc:errors.append(str(exc))
        expected=[(row['id'],row['family']) for row in registry_module.catalog_rows(root,registry)]
    elif counts!=catalog.get('counts') or counts!={'total':187,'legacy':64,'native_ai':13,'native_core':110}:errors.append('catalog counts mismatch')
    actual=[(row['id'],row['family']) for row in rows]
    if len(set(row['id'] for row in rows))!=len(rows) or actual!=expected:errors.append('catalog ID/family/order mismatch')
    for row in rows:
        try:
            relative=row['file'];path=contained(root,relative)
            if relative not in cache:cache[relative]=read(path)
            entry=resolve_pointer(cache[relative],row['pointer'])
            if entry['id']!=row['id'] or entry['title']!=row['title']:errors.append('catalog pointer identity '+row['id'])
            for key in ['status','knowledge_status','retrieval_status','coding_status']:
                if key in entry and row.get(key)!=entry[key]:errors.append('catalog state mismatch '+row['id']+':'+key)
        except (OSError,ValueError,KeyError,IndexError,TypeError) as exc:errors.append('catalog pointer '+row['id']+': '+str(exc))
    core=cache[families['native_core'][0]]
    for entry in core['entries']:
        if entry.get('coding_status')!='hold':errors.append('NativeCore Coding HOLD changed '+entry['id'])
    def refs(value):
        nonlocal reference_count
        if isinstance(value,dict):
            if value.get('artifact_path'):
                relative=value['artifact_path']
                try:
                    path=contained(root,relative)
                    if relative not in raw_cache:raw_cache[relative]=path.read_bytes()
                    raw=raw_cache[relative];reference_count+=1
                    expected_hash=value.get('sha256',value.get('artifact_sha256'))
                    if expected_hash and sha256(raw).hexdigest()!=expected_hash:errors.append('native artifact hash '+relative)
                    if value.get('pointer') is not None and path.suffix=='.json':
                        if relative not in cache:cache[relative]=json.loads(raw)
                        resolve_pointer(cache[relative],value['pointer'])
                except (OSError,ValueError,KeyError,IndexError,TypeError) as exc:errors.append('native artifact '+relative+': '+str(exc))
            for child in value.values():refs(child)
        elif isinstance(value,list):
            for child in value:refs(child)
    refs(core);refs(read(root/'data/native001/canonical-native001-research-map.json'))
    return len(rows),reference_count


def validate_root(root,external=False):
    db=read(root/'data/entries.json');src=read(root/'data/sources.json');claims=read(root/'data/claims.json');schema=read(root/'schemas/entries.schema.json')
    errors=collection_errors(db,schema,src)+semantic_errors(db,src,claims)
    baseline=read(root/'data/legacy-integrity-baseline.json')
    migration_diff=[]
    baseline_paths={'data/entries.json','data/sources.json','data/claims.json','data/relations.json','data/index.json','review-support/case-metadata.json'} | {p.relative_to(root).as_posix() for p in (root/'schemas').glob('*.json') if p.name not in ('native-ai.schema.json','native-core.schema.json')}
    if baseline.get('schema')!='dst-legacy-integrity-baseline/1' or {row['path'] for row in baseline['files']}!=baseline_paths:errors.append('legacy baseline schema/file registry')
    for row in baseline['files']:
        p=contained(root,row['path'])
        if not p.is_file() or len(p.read_bytes())!=row['bytes'] or sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            errors.append('legacy baseline SHA256 mismatch '+row['path'])
    record_hashes=[{'id':e['id'],'sha256':sha256(json.dumps(e,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()} for e in db['entries']]
    if len(record_hashes)!=64 or record_hashes!=baseline['entries']:errors.append('legacy baseline record mismatch')
    catalog_count,reference_count=validate_catalog_native(root,errors)
    ids={e['id'] for e in db['entries']}
    for filename,schemafile in [('sources.json','sources.schema.json'),('claims.json','claims.schema.json'),('relations.json','relations.schema.json')]:
        sc=read(root/'schemas'/schemafile);errors+=schema_errors(read(root/'data'/filename),sc,sc,filename)
    ms=read(root/'schemas/case-metadata.schema.json');metadata=read(root/'review-support/case-metadata.json')
    errors+=schema_errors(metadata,ms,ms,'case-metadata')
    case=next(e for e in db['entries'] if e['entry_type']=='case')['details']
    for k,v in {'case_id':'CASE-001','name':case['name'],'version':case['mod_version'],'author':case['author']['declared'],
       'analysis_date':case['analysis_date'],'file_count':case['project_size']['files'],'lua_file_count':case['project_size']['lua_files'],
       'content_hash':case['project_hash'],'runtime_tested':False,'dedicated_server_tested':False,'source_available_in_package':False}.items():
        if metadata.get(k)!=v:errors.append('portable metadata mismatch '+k)
    packaged=0
    for s in src['sources']:
        if s.get('available_in_package'):
            try:p=contained(root,s['artifact_path'])
            except (ValueError,TypeError) as exc:errors.append(str(exc));continue
            if not p.is_file() or sha256(p.read_bytes()).hexdigest()!=s['sha256']:errors.append('packaged source integrity '+s['id'])
            packaged+=1
        elif s.get('artifact_path') is not None:errors.append('external source has fake artifact '+s['id'])
    ext_status='not_requested'
    if external:
        ext_status='PASS'
        for s in src['sources']:
            if s.get('original_path') and s.get('sha256'):
                p=Path(s['original_path'])
                if not p.is_file() or sha256(p.read_bytes()).hexdigest()!=s['sha256']:errors.append('external source fingerprint '+s['id'])
        base=Path(src['case_snapshot']['path']);h=sha256()
        for p in sorted(p for p in base.rglob('*') if p.is_file()):h.update(p.relative_to(base).as_posix().encode());h.update(sha256(p.read_bytes()).digest())
        if h.hexdigest()!=src['case_snapshot']['sha256']:errors.append('reference project fingerprint changed')
        for f in src['vanilla_context']['current_fingerprint_only']:
            if sha256(Path(f['path']).read_bytes()).hexdigest()!=f['sha256']:errors.append('external vanilla fingerprint changed')
    index=read(root/'data/index.json')
    if index['counts']!=dict(Counter(e['entry_type'] for e in db['entries'])):errors.append('index type counts mismatch')
    sm=read(root/'review-support/source-map.json')
    if sm['sources']!=[{k:s.get(k) for k in ['id','original_path','artifact_path','available_in_package']} for s in src['sources']]:errors.append('source map differs from registry')
    if [x['id'] for x in index['entries']]!=[x['id'] for x in db['entries']]:errors.append('index ID/order mismatch')
    for row,e in zip(index['entries'],db['entries']):
        for k in ['title','entry_type','knowledge_kind','tags','evidence_level','confidence','status','related','scope_structured','typed_relations']:
            if row[k]!=e[k]:errors.append('index content mismatch '+e['id']+':'+k)
        p=contained(root,row['path'])
        if not p.is_file() or ('id="'+row['anchor']+'"') not in p.read_text(encoding='utf-8'):errors.append('document anchor '+row['id'])
    graph=read(root/'data/relations.json');nodeids=ids|{s['id'] for s in src['sources']}|{c['id'] for c in claims['claims']}
    actual_nodes={n['id'] for group in ['nodes','source_nodes','claim_nodes'] for n in graph[group]}
    if actual_nodes!=nodeids:errors.append('graph node registry mismatch')
    edges={(x['from'],x['relation'],x['to']) for x in graph['edges']}
    for edge in graph['edges']+graph['correction_edges']:
        if edge['from'] not in nodeids or edge['to'] not in nodeids or edge['relation'] not in RELATIONS:errors.append('graph invalid typed target')
    for e in db['entries']:
        for r in e['typed_relations']:
            if (e['id'],r['type'],r['target']) not in edges:errors.append('graph omitted typed relation '+e['id'])
        for r in e['related']:
            if (e['id'],'related',r) not in edges:errors.append('graph omitted legacy related '+e['id'])
    link_count=0;external_links=[]
    for p in root.rglob('*.md'):
        if 'history' in p.relative_to(root).parts:continue
        text=p.read_text(encoding='utf-8')
        for raw in re.findall(r'\]\(([^\n]+?)\)',text):
            dest=raw.strip('<>');base,_,anchor=dest.partition('#')
            if base.startswith(('https:','http:')):continue
            if re.match(r'^[A-Za-z]:/',base):external_links.append(str(p.relative_to(root))+':'+base);continue
            target=(p.parent/base).resolve();link_count+=1
            if not target.is_file():errors.append('internal link missing '+str(p.relative_to(root))+':'+dest)
            elif anchor and target.suffix=='.md' and ('id="'+anchor+'"') not in target.read_text(encoding='utf-8'):errors.append('internal anchor missing '+dest)
    if external_links:errors.append('active Markdown still links original_path')
    negative=[]
    def check_changed(name,fn):
        b=copy.deepcopy(db);c=copy.deepcopy(claims);fn(b,c)
        base=set(collection_errors(db,schema,src)+semantic_errors(db,src,claims))
        now=set(collection_errors(b,schema,src)+semantic_errors(b,src,c));ok=bool(now-base)
        negative.append({'case':name,'detected':ok})
        if not ok:errors.append('negative test missed '+name)
    def first(b,t):return next(e for e in b['entries'] if e['entry_type']==t)
    check_changed('missing field',lambda b,c:b['entries'][0].pop('confidence'))
    check_changed('bad status',lambda b,c:b['entries'][0].update(status='universal'))
    check_changed('E4 without runtime',lambda b,c:first(b,'pattern').update(evidence_level='E4'))
    check_changed('typed target missing',lambda b,c:first(b,'pattern')['typed_relations'][0].update(target='MISSING'))
    check_changed('typed relation invalid',lambda b,c:first(b,'pattern')['typed_relations'][0].update(type='proves_forever'))
    check_changed('correction target missing',lambda b,c:c['claims'].clear())
    check_changed('superseded-only recommendation',lambda b,c:first(b,'rule').update(sources=[{
        'source_id':'REPORT-R5','locator':'1.3','note':'','claim_id':'CLAIM-CASE001-001','role':'direct_evidence'}]))
    check_changed('runtime failure overclaim',lambda b,c:first(b,'failure_case')['details'].update(runtime_reproduced=True))
    check_changed('test falsely executed',lambda b,c:first(b,'test_case')['details'].update(execution_status='passed'))
    check_changed('reversed locator',lambda b,c:first(b,'source_fact')['sources'][0].update(locator_structured=[{'type':'source_lines','file':'entityscript.lua','start_line':2000,'end_line':1900}]))
    check_changed('direct Klei removed',lambda b,c:first(b,'source_fact')['sources'].pop(0))
    check_changed('E2 with one case',lambda b,c:first(b,'pattern').update(evidence_level='E2'))
    audit=read(root/'data/migration-audit.json')
    if audit['unexpected_semantic_changes']:errors.append('migration semantic audit failed')
    manifest_status='not_present'
    mf=root/'PACKAGE-MANIFEST.json'
    if mf.is_file():
        manifest_status='PASS';manifest=read(mf);registered={row['path'] for row in manifest['files']}
        current={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=mf and '__pycache__' not in p.parts}
        if registered!=current:errors.append('manifest file set mismatch')
        for row in manifest['files']:
            p=contained(root,row['path'])
            if not p.is_file() or len(p.read_bytes())!=row['bytes'] or sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('manifest SHA256 mismatch '+row['path'])
    if any('manifest ' in error for error in errors):manifest_status='FAIL'
    return {'status':'PASS' if not errors else 'FAIL','schema_validation':'PASS' if not errors else 'see_errors',
        'schema_engine':'stdlib subset covering current schema keywords; no third-party validator',
        'entries':catalog_count,'legacy_entries':len(db['entries']),
        'legacy_preservation':'SHA256_BASELINE_CHECKED','legacy_0_1_schema_accepted':None,
        'historical_0_1_migration_comparison':baseline.get('legacy_v0_1_migration_comparison'),
        'native_artifact_references_checked':reference_count,
        'semantic_migration_diff':migration_diff,'graph_edges':len(graph['edges']),
        'evidence_levels':dict(Counter(e['evidence_level'] for e in db['entries'])),
        'packaged_sources_checked':packaged,'internal_links_checked':link_count,'external_original_path_links':external_links,
        'negative_checks':negative,'external_fingerprint_check':ext_status,'manifest':manifest_status,
        'runtime_tests_executed':0,'errors':errors,
        'limitations':['Correction guard covers explicit claim_id references, not arbitrary natural-language paraphrases.',
          'Source facts remain version-scoped prior evidence; portable validation cannot re-verify absent external source contents.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--check-external',action='store_true');p.add_argument('--write-report',action='store_true');a=p.parse_args()
    result=validate_root(a.root,a.check_external)
    if a.write_report:
        if (a.root/'PACKAGE-MANIFEST.json').exists():raise SystemExit('Do not change a sealed package; rebuild manifest explicitly first.')
        (a.root/'data/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result['errors']:raise SystemExit(1)
if __name__=='__main__':main()
