"""从 canonical entries.json 生成可读视图、JSON Schema、索引与关系图。标准库即可运行。"""
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TYPES=['source_fact','case','pattern','rule','anti_pattern','decision','failure_case','correction','test_case','playbook']
EVIDENCE=['E0','E1','E2','E3','E4','E5']
CONF=['Experimental','Low','Medium','High','Very High']
STATUS=['candidate','validated_single_case','supported_by_klei','needs_runtime_validation','superseded','corrected','deprecated']

def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def docpath(e):
    t=e['entry_type']; id=e['id']
    if t=='case': return 'cases/CASE-001-sora/README.md'
    if t=='pattern': return 'patterns/'+id+'.md'
    if t=='rule': return 'rules/'+id.split('-')[1].lower()+'.md'
    return {'source_fact':'facts/klei-lua.md','anti_pattern':'anti-patterns/case001.md',
      'decision':'decisions/candidates.md','failure_case':'failures/case001.md',
      'correction':'corrections/CASE-001.md','test_case':'tests/candidates.md','playbook':'playbooks/ARP-DST-001.md'}[t]

def shape(v,key=''):
    if key=='origin_round6_rule': return {'type':['integer','null']}
    if v is None:
        return {'type':['null','integer']} if key=='unique_mod_total' else {'type':['null','string']} if key=='release_build' else {'type':['null','object']}
    if isinstance(v,bool):return {'type':'boolean'}
    if isinstance(v,int):return {'type':'integer'}
    if isinstance(v,str):return {'type':'string'}
    if isinstance(v,list):return {'type':'array','items':shape(v[0]) if v else {}}
    return {'type':'object','required':list(v),'properties':{k:shape(x,k) for k,x in v.items()},'additionalProperties':False}

def make_schema(entries):
    # Schema由版本迁移显式维护，不再按第一个条目推断并覆盖。
    return json.loads((ROOT/'schemas/entries.schema.json').read_text(encoding='utf-8'))


def main():
    db=json.loads((ROOT/'data/entries.json').read_text(encoding='utf-8')); entries=db['entries']; ids={e['id']:e for e in entries}
    sources=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
    claims=json.loads((ROOT/'data/claims.json').read_text(encoding='utf-8'))['claims']
    claim_ids={c['id'] for c in claims}
    source_map={s['id']:s for s in sources['sources']}; groups=defaultdict(list); context='INDEX.md'
    for e in entries:groups[docpath(e)].append(e)
    def link(id):
        if id not in ids and id not in claim_ids:return id
        dest=docpath(ids[id]) if id in ids else 'corrections/claims.md'
        target=os.path.relpath(ROOT/dest,(ROOT/context).parent).replace('\\','/')
        return f"[{id}]({target}#{id.lower()})"
    def textvalue(v):
        if isinstance(v,str):
            if v in ids or v in claim_ids:return link(v)
            if re.match(r'^[A-Z]:/',v):return '`'+v+'`（original provenance；不作为包内链接）'
            return v
        if v is None:return '未记录 / null'
        if isinstance(v,bool):return '是' if v else '否'
        if isinstance(v,list):
            if not v:return '无 / 未建立'
            if all(isinstance(x,dict) and 'source_id' not in x for x in v):
                blocks=[]
                for i,x in enumerate(v,1):
                    lines=textvalue(x).splitlines()
                    blocks.append(str(i)+'. '+lines[0].removeprefix('- ')+'\n'+'\n'.join('   '+line for line in lines[1:]))
                return '\n\n'.join(blocks)
            return '\n'.join('- '+textvalue(x).replace('\n','\n  ') for x in v)
        if isinstance(v,dict):
            if 'source_id' in v:
                s=source_map[v['source_id']]
                if s.get('available_in_package') and s.get('artifact_path'):
                    target=os.path.relpath(ROOT/s['artifact_path'],(ROOT/context).parent).replace('\\','/')
                    label=f"[{v['source_id']}](<{target}>)"
                else:label=v['source_id']+'（外部来源未随包）'
                return label+f" · {v.get('role','interpretation')} · {v['locator']}"+(f" · {v['note']}" if v.get('note') else '')
            return '\n'.join(f"- **{k}**：{textvalue(x).replace(chr(10),chr(10)+'  ')}" for k,x in v.items())
        return str(v)
    for path,items in groups.items():
        context=path
        out=['# '+('CASE-001 — 小穹 v13.80' if path.endswith('sora/README.md') else items[0]['entry_type']+' · v0.1.1'),
          '', '本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。','']
        for e in items:
            out += [f"<a id=\"{e['id'].lower()}\"></a>",'',f"## {e['id']} — {e['title']}",'',
               f"类型：{e['knowledge_kind']} · Evidence：{e['evidence_level']} · Confidence：{e['confidence']} · Status：{e['status']} · Version：{e['version']}",'',e['summary'],'',
               '**Scope**：'+e['scope'],'']
            for k,v in e['details'].items():out += ['### '+k.replace('_',' ').title(),'',textvalue(v),'']
            out += ['### Structured Scope','',textvalue(e.get('scope_structured',{})),
                '','### Typed Relations','',textvalue(e.get('typed_relations',[])),
                '','### sources','',textvalue(e['sources']),'','### related','',textvalue(e['related']),'']
        p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(out),encoding='utf-8')
    counts=Counter(e['entry_type'] for e in entries)
    edges=[]
    for e in entries:
        for target in e['related']:edges.append({'from':e['id'],'relation':'related','to':target})
        for rel in e.get('typed_relations',[]):edges.append({'from':e['id'],'relation':rel['type'],'to':rel['target']})
        for s in e['sources']:
            if s.get('role')=='direct_evidence':edges.append({'from':s['source_id'],'relation':'supports','to':e['id']})
            else:edges.append({'from':e['id'],'relation':'related','to':s['source_id']})
    graph={'schema_version':'0.1.1','nodes':[{'id':e['id'],'entry_type':e['entry_type'],'status':e['status']} for e in entries],
           'source_nodes':[{'id':s['id'],'type':s['type']} for s in sources['sources']],
           'claim_nodes':[{'id':c['id'],'type':'historical_claim','status':c['status']} for c in claims], 'edges':edges,
           'correction_edges':[x for x in edges if x['relation'] in ['corrects','supersedes']]}
    dump(ROOT/'data/relations.json',graph)
    dump(ROOT/'data/index.json',{'schema_version':'0.1.1','counts':dict(counts),'entries':[{
         k:e[k] for k in ['id','title','entry_type','knowledge_kind','tags','evidence_level','confidence','status','related','scope_structured','typed_relations']}|
         {'path':docpath(e),'anchor':e['id'].lower()} for e in entries]})
    dump(ROOT/'schemas/entries.schema.json',make_schema(entries))
    table='\n'.join(f'| {t} | {counts[t]} |' for t in TYPES)
    context='INDEX.md'
    index='\n'.join('- '+link(e['id'])+' — '+e['title'] for e in entries)
    (ROOT/'INDEX.md').write_text('# 全部知识条目\n\n'+index+'\n',encoding='utf-8')
    context='corrections/claims.md'
    out=['# 历史 Claim 节点','', '本页保留被撤回的历史判断，不是有效推荐。Claim不计入64条知识条目。','']
    for c in claims:
        out += [f'<a id="{c["id"].lower()}"></a>','',f'## {c["id"]}','',
            'Status: '+c['status'],'',c['statement'],'',textvalue(c['sources']),'',
            'Superseded by: '+link(c['superseded_by']),'']
    (ROOT/context).write_text('\n'.join(out),encoding='utf-8')
    context='SOURCES.md';out=['# Source Registry v0.1.1','', 'Direct Klei Evidence与AI Analysis Evidence分开；外部源码不随包。','']
    for s in sources['sources']:
        out += ['## '+s['id'],'','Type: '+s['type'],'',s['description'],'',
           'original_path: `'+str(s.get('original_path'))+'`','']
        if s.get('artifact_path'):out+=['artifact_path: ['+s['artifact_path']+'](<'+s['artifact_path']+'>)','']
        else:out+=['artifact_path: null；available_in_package: false','']
    (ROOT/context).write_text('\n'.join(out),encoding='utf-8')
    print('Rendered',len(groups),'entry documents;',len(entries),'entries;',len(edges),'relations.')

if __name__=='__main__':main()
