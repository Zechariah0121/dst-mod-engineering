"""Source-free fail-closed research contract. Shared by registration and reads."""
import re

REQUIRED = {
    'document': 'schema_version topic source_epoch archive_sha256 entries source_references queries limitations'.split(),
    'entry': 'id title aliases engineering_question knowledge_status retrieval_status coding_status scope claims api_contracts mechanism_steps unknowns'.split(),
    'claim': 'id kind statement evidence_refs'.split(),
    'reference': 'id source_file file_sha256 line_start line_end range_sha256 symbols'.split(),
    'api': 'symbol source_file visibility parameters returns preconditions side_effects lifecycle evidence_refs unknowns'.split(),
    'step': 'step description evidence_refs'.split(),
    'query': 'query expected_entry_ids purpose'.split(),
    'compatibility': 'dependency_coverage dependency_refs unknowns'.split(),
    'dependency': 'ref role'.split(),
}
OPTIONAL = {'entry': {'compatibility'}, 'dependency': {'claim_ids'}}
STATES = {'knowledge_status': 'research', 'retrieval_status': 'restricted', 'coding_status': 'hold'}
RUNTIME = {'runtime_verified','runtime_tested','runtime_validation_performed','runtime_game_verified','game_verified','game_tested','in_game_verified','runtime_status','runtime_validation_status','runtime_validation','runtime_verification','runtime_test_status'}
NOT_RUN = {'not_run','unverified','unknown','not_performed','not_tested','pending','planned','未运行','未验证','待运行'}


def validate(doc):
    def fail(message):
        raise ValueError('Mechanism contract: ' + message)
    def text(value):
        if not isinstance(value,str) or not value.strip():fail('expected nonempty string')
    def obj(value,kind):
        if not isinstance(value,dict) or set(REQUIRED[kind])-value.keys() or value.keys()-set(REQUIRED[kind])-OPTIONAL.get(kind,set()):
            fail('missing/unknown fields in '+kind)
    def array(value,strings=False,nonempty=False):
        if not isinstance(value,list) or nonempty and not value:fail('expected array')
        if strings:
            for item in value:text(item)
            if len(value)!=len(set(value)):fail('duplicate string in array')
        return value
    def hashed(value):
        if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):fail('expected lowercase SHA256')
    def path(value):
        text(value)
        if not value.startswith('scripts/') or any(c in value for c in ('\\',':','\x00')) or any(ord(c)<32 for c in value) or any(x in ('','.','..') for x in value.split('/')):fail('unsafe exact source member')
    ids=set()
    def register(value):
        text(value)
        if value in ids:fail('duplicate local ID: '+value)
        ids.add(value)
    obj(doc,'document')
    if doc['schema_version']!='dst-mechanism-research/1':fail('unknown schema')
    text(doc['topic']);text(doc['source_epoch']);hashed(doc['archive_sha256'])
    array(doc['limitations'],True)
    refs={}
    for ref in array(doc['source_references']):
        obj(ref,'reference');register(ref['id']);path(ref['source_file'])
        hashed(ref['file_sha256']);hashed(ref['range_sha256']);array(ref['symbols'],True)
        if type(ref['line_start']) is not int or type(ref['line_end']) is not int or not 1<=ref['line_start']<=ref['line_end']:fail('invalid line range')
        refs[ref['id']]=ref
    def evidence(value,required=False):
        values=array(value,True,required)
        if any(r not in refs for r in values):fail('dangling local source reference')
        return values
    entry_ids=set()
    for entry in array(doc['entries'],nonempty=True):
        obj(entry,'entry');register(entry['id']);entry_ids.add(entry['id'])
        text(entry['title']);text(entry['engineering_question']);array(entry['aliases'],True);array(entry['unknowns'],True)
        if any(entry[k]!=v for k,v in STATES.items()):fail('research governance state escalated')
        if not isinstance(entry['scope'],(dict,list,str)) or not entry['scope']:fail('missing Scope')
        claim_ids=set()
        for claim in array(entry['claims'],nonempty=True):
            obj(claim,'claim');register(claim['id']);claim_ids.add(claim['id']);text(claim['statement'])
            if claim['kind'] not in ('NSF','EI','REC','UNK'):fail('unknown claim kind')
            evidence(claim['evidence_refs'],claim['kind']=='NSF')
        for api in array(entry['api_contracts']):
            obj(api,'api');text(api['symbol']);text(api['visibility']);path(api['source_file'])
            api_refs=evidence(api['evidence_refs'],True)
            if not any(refs[r]['source_file']==api['source_file'] for r in api_refs):fail('API source not bound')
            for key in ('parameters','returns','preconditions','side_effects','lifecycle'):
                if not isinstance(api[key],(str,list,dict)):fail('invalid API authored field')
            array(api['unknowns'],True)
        steps=set()
        for step in array(entry['mechanism_steps']):
            obj(step,'step');text(step['description']);evidence(step['evidence_refs'],True)
            if type(step['step']) is not int or step['step']<1 or step['step'] in steps:fail('invalid/duplicate step')
            steps.add(step['step'])
        if 'compatibility' in entry:
            metadata=entry['compatibility'];obj(metadata,'compatibility')
            if metadata['dependency_coverage'] not in ('unknown','enumerated_static'):fail('unknown dependency coverage')
            array(metadata['unknowns'],True)
            for dep in array(metadata['dependency_refs']):
                obj(dep,'dependency');text(dep['role']);text(dep['ref'])
                if dep['ref'] not in refs:fail('dangling dependency ref')
                if any(c not in claim_ids for c in array(dep.get('claim_ids',[]),True)):fail('dependency claim belongs to another entry')
    for query in array(doc['queries'],nonempty=True):
        obj(query,'query');text(query['query']);text(query['purpose'])
        if any(i not in entry_ids for i in array(query['expected_entry_ids'],True)):fail('dangling query ID')
    def guard(value):
        if isinstance(value,dict):
            for key,child in value.items():
                lower=key.lower()
                if lower in STATES and child!=STATES[lower]:fail('nested governance escalation')
                if lower in RUNTIME and not (child is False or child is None or isinstance(child,str) and child in NOT_RUN):fail('runtime assertion forbidden')
                guard(child)
        elif isinstance(value,list):
            for child in value:guard(child)
    guard(doc)
    return doc
