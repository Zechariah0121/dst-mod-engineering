"""本库约束校验器。标准库；实现生成 Schema 所用子集，不冒充通用 JSON Schema 引擎。"""
import copy
import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def matches_type(v,t):
    return {'object':lambda:isinstance(v,dict),'array':lambda:isinstance(v,list),
      'string':lambda:isinstance(v,str),'boolean':lambda:isinstance(v,bool),
      'integer':lambda:isinstance(v,int) and not isinstance(v,bool),'null':lambda:v is None}[t]()

def schema_errors(v,s,root,where='$'):
    errors=[]
    if '$ref' in s:
        q=root
        for k in s['$ref'].removeprefix('#/').split('/'):q=q[k]
        return schema_errors(v,q,root,where)
    if 'type' in s:
        ts=s['type'] if isinstance(s['type'],list) else [s['type']]
        if not any(matches_type(v,t) for t in ts):return [where+': type '+str(ts)]
    if 'const' in s and v!=s['const']:errors.append(where+': const')
    if 'enum' in s and v not in s['enum']:errors.append(where+': enum')
    if isinstance(v,str) and 'pattern' in s and re.search(s['pattern'],v) is None:errors.append(where+': pattern')
    if isinstance(v,(int,float)) and not isinstance(v,bool) and 'minimum' in s and v<s['minimum']:errors.append(where+': minimum')
    if isinstance(v,dict):
        for k in s.get('required',[]):
            if k not in v:errors.append(where+': missing '+k)
        for k,x in v.items():
            if k in s.get('properties',{}):errors+=schema_errors(x,s['properties'][k],root,where+'.'+k)
            elif s.get('additionalProperties') is False:errors.append(where+': unexpected '+k)
    if isinstance(v,list):
        if len(v)<s.get('minItems',0):errors.append(where+': minItems')
        if s.get('uniqueItems') and len({json.dumps(x,sort_keys=True,ensure_ascii=False) for x in v})!=len(v):errors.append(where+': uniqueItems')
        if 'items' in s:
            for i,x in enumerate(v):errors+=schema_errors(x,s['items'],root,where+'['+str(i)+']')
    for child in s.get('allOf',[]):errors+=schema_errors(v,child,root,where)
    if 'anyOf' in s and not any(not schema_errors(v,c,root,where) for c in s['anyOf']):errors.append(where+': anyOf')
    if 'oneOf' in s and sum(not schema_errors(v,c,root,where) for c in s['oneOf'])!=1:errors.append(where+': oneOf')
    if 'if' in s and not schema_errors(v,s['if'],root,where):errors+=schema_errors(v,s.get('then',{}),root,where)
    return errors

def collection_errors(db,schema,sources):
    errors=schema_errors(db,schema,schema)
    es=db.get('entries',[]); ids=[e.get('id') for e in es]; known=set(ids); sourceids={s['id'] for s in sources['sources']}
    if len(ids)!=len(known):errors.append('duplicate entry ID')
    mapping={'source_fact':'Klei Fact','case':'Case Observation','pattern':'Engineering Pattern Candidate',
       'rule':'Engineering Rule Candidate','anti_pattern':'Recommendation','decision':'Recommendation',
       'failure_case':'Case Observation','correction':'Case Observation','test_case':'Recommendation','playbook':'Recommendation'}
    def walk(x,where):
        if isinstance(x,dict):
            if 'source_id' in x and x['source_id'] not in sourceids:errors.append(where+': unknown source')
            for k,v in x.items():walk(v,where+'.'+k)
        elif isinstance(x,list):
            for v in x:walk(v,where)
    for e in es:
        id=e.get('id','?');t=e.get('entry_type');d=e.get('details',{})
        if e.get('knowledge_kind')!=mapping.get(t):errors.append(id+': knowledge kind mismatch')
        if not e.get('sources'):errors.append(id+': missing provenance')
        for ref in e.get('related',[])+e.get('created_from_case',[]):
            if ref not in known:errors.append(id+': dangling ref '+str(ref))
        for key in ['dst_klei_basis','klei_basis','related_rules','related_rule','related_patterns','related_pattern',
                    'related_anti_patterns','related_decision_trees','applicable_patterns','identified_patterns',
                    'identified_anti_patterns','confirmed_failure_cases','static_failure_paths','corrections']:
            for ref in d.get(key,[]):
                if ref not in known:errors.append(id+': dangling details ref '+ref)
        if t=='source_fact' and e.get('evidence_level')!='E3':errors.append(id+': source_fact must remain E3 in this snapshot')
        if t=='test_case' and (d.get('execution_status')!='not_run' or d.get('result') is not None):errors.append(id+': candidate test falsely marked executed')
        if t=='failure_case' and d.get('runtime_reproduced') is not False:errors.append(id+': unsubstantiated runtime claim')
        if e.get('evidence_level')=='E2' and len(e.get('created_from_case',[]))<2:errors.append(id+': E2 lacks independent cases')
        if e.get('evidence_level') in ['E4','E5'] and not e.get('runtime_records'):errors.append(id+': runtime evidence missing')
        if id=='ANTI-WORLD-001' and (e.get('evidence_level')!='E0' or d.get('assessment')!='risk_candidate_not_established'):errors.append('God Manager overclaim')
        if t=='pattern':
            body=json.dumps({k:v for k,v in d.items() if k not in ['case_evidence']},ensure_ascii=False)
            if re.search(r'Sora|sora|ClientDB|MainDB|RegByType',body):errors.append(id+': case-specific names leaked into pattern body')
        walk(e,id)
    if 'CORRECTION-CASE001-001' not in known:errors.append('missing required correction')
    return errors

def main():
    from validate_v011 import main as run
    run()

if __name__=='__main__':main()
