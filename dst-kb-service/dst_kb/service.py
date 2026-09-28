import json
import math
import re
import sqlite3
import time
from collections import Counter
from datetime import datetime,timezone
from typing import Protocol
from .config import KBError,settings
from .validation import signature,validate,RELATIONS

INDEX_VERSION=1
ALIASES={'networking':'联机 网络 同步 rpc replica','authority':'权威 服务端','server':'服务器 服务端',
 'client':'客户端 预测','world':'世界','manager':'管理器 注册表','lifecycle':'生命周期 清理 移除',
 'persistence':'存档 保存 加载','shard':'分片 洞穴','hook':'包装 hook','resource':'资源 材料',
 'skill':'技能 施法','replica':'副本 replica','stategraph':'状态图 stategraph','registry':'注册表',
 'save':'保存 存档','reconnect':'重连','failure':'失败 故障','crash':'崩溃 nil','performance':'性能 调度'}
MODE_TYPES={
 'architect':['playbook','decision','rule','source_fact','pattern','anti_pattern','test_case'],
 'implement':['source_fact','rule','test_case','decision','pattern'],
 'review':['rule','anti_pattern','failure_case','test_case','source_fact'],
 'debug':['failure_case','source_fact','rule','test_case','anti_pattern'],
 'research':['pattern','rule','case','correction','decision'],
 'kb_curator':['correction','case','source_fact','pattern','rule']}
FILTERS={'entry_types':'type','domains':'domain','evidence_levels':'evidence','confidence':'confidence',
         'statuses':'status','cases':'case','sides':'side','runtime_environments':'runtime','tags':'tag'}

def tokens(text,expand=False):
    s=re.sub(r'([a-z])([A-Z])',r'\1 \2',text).lower()
    if expand:
        extra=[]
        for key,value in ALIASES.items():
            if key in s or any(v in s for v in value.split() if not v.isascii()):extra += [key,value]
        s += ' '+' '.join(extra)
    out=re.findall(r'[a-z_][a-z0-9_-]*|[0-9]+',s)
    for seq in re.findall(r'[\u3400-\u9fff]+',s):
        out += [seq] if len(seq)<2 else [seq[i:i+2] for i in range(len(seq)-1)]
    return list(dict.fromkeys(x for x in out if x not in {'the','a','an','and','or','to','of','for','dst','mod'}))

def searchable(x):
    if isinstance(x,dict):return ' '.join(searchable(v) for k,v in x.items() if k not in ['sources','source_file','project_hash','source_locator'])
    if isinstance(x,list):return ' '.join(searchable(v) for v in x)
    return str(x)

def compact(e):
    return {k:e[k] for k in ['id','title','entry_type','summary','evidence_level','confidence','status']} | {'scope':e['scope_structured']}

class SearchProvider(Protocol):
    def candidates(self,connection,terms): ...

class FTSSearchProvider:
    def candidates(self,connection,terms):
        if not terms:return {}
        query=' OR '.join('"'+t.replace('"','""')+'"' for t in terms[:80])
        return dict(connection.execute('SELECT id,bm25(search,0,5,3,1) FROM search WHERE search MATCH ?',(query,)))

class Service:
    def __init__(self,config=None,provider=None):
        self.root,self.index,self.config=settings(config)
        self.provider=provider or FTSSearchProvider()
        self.db=None
        try:self._open()
        except Exception:
            self.close()
            raise

    def _connect(self):
        db=sqlite3.connect(self.index,timeout=30)
        db.execute('PRAGMA busy_timeout=30000')
        return db

    def _open(self):
        current=signature(self.root)
        self.index.parent.mkdir(parents=True,exist_ok=True)
        self.db=self._connect()
        try:meta=dict(self.db.execute('SELECT key,value FROM meta'))
        except sqlite3.DatabaseError:meta={}
        if meta.get('signature')!=current or meta.get('root')!=str(self.root) or meta.get('index_version')!=str(INDEX_VERSION):self.reindex()
        self.loaded_signature=current

    def ready(self):
        if signature(self.root)!=self.loaded_signature:
            raise KBError('INDEX_STALE','KB changed during this session; run reindex and reconnect. Stale evidence will not be served.')

    def reindex(self):
        data,report=validate(self.root)
        start_signature=signature(self.root)
        db=self.db
        # 单事务更换派生表；其他读取者不会看到半个索引。
        db.execute('BEGIN IMMEDIATE')
        try:
            for table in ['meta','entries','facets','edges','nodes','search']:
                db.execute('DROP TABLE IF EXISTS '+table)
            db.execute('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            db.execute('CREATE TABLE entries(id TEXT PRIMARY KEY,type TEXT,json TEXT NOT NULL)')
            db.execute('CREATE TABLE facets(id TEXT,kind TEXT,value TEXT,PRIMARY KEY(id,kind,value))')
            db.execute('CREATE INDEX facet_lookup ON facets(kind,value,id)')
            db.execute('CREATE TABLE edges(src TEXT,relation TEXT,dst TEXT,PRIMARY KEY(src,relation,dst))')
            db.execute('CREATE INDEX edge_reverse ON edges(dst,relation,src)')
            db.execute('CREATE TABLE nodes(id TEXT PRIMARY KEY,kind TEXT,json TEXT)')
            db.execute('CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,summary,body)')
            for e in data['entries']['entries']:
                db.execute('INSERT INTO entries VALUES(?,?,?)',(e['id'],e['entry_type'],json.dumps(e,ensure_ascii=False)))
                scope=e['scope_structured']
                values={'type':[e['entry_type']],'evidence':[e['evidence_level']],'status':[e['status']],
                    'confidence':[e['confidence']],'tag':e['tags'],'domain':scope['domains'],'case':scope['cases'],
                    'side':scope['sides'],'runtime':scope['runtime_environments']}
                for kind,items in values.items():
                    db.executemany('INSERT OR IGNORE INTO facets VALUES(?,?,?)',[(e['id'],kind,x.lower()) for x in items])
                db.execute('INSERT INTO search VALUES(?,?,?,?)',(e['id'],' '.join(tokens(e['title'])),
                    ' '.join(tokens(e['summary'])),' '.join(tokens(searchable(e['details'])+' '+searchable(scope)+' '+' '.join(e['tags'])))))
            for x in data['relations']['edges']:db.execute('INSERT OR IGNORE INTO edges VALUES(?,?,?)',(x['from'],x['relation'],x['to']))
            for kind,items in [('source',data['sources']['sources']),('claim',data['claims']['claims'])]:
                db.executemany('INSERT INTO nodes VALUES(?,?,?)',[(e['id'],kind,json.dumps(e,ensure_ascii=False)) for e in items])
            meta={'root':str(self.root),'signature':start_signature,'index_version':str(INDEX_VERSION),
                'last_validation':json.dumps(report,ensure_ascii=False),'kb_version':report['kb_version'],
                'schema_version':report['schema_version'],'last_index_build':datetime.now(timezone.utc).isoformat(),
                'case_metadata':json.dumps(data['case-metadata'],ensure_ascii=False)}
            db.executemany('INSERT INTO meta VALUES(?,?)',meta.items())
            if signature(self.root)!=start_signature:raise KBError('KB_CHANGED','KB changed while indexing; retry a stable snapshot.')
            db.commit();self.loaded_signature=start_signature
        except Exception:db.rollback();raise
        return report

    def status(self):
        meta=dict(self.db.execute('SELECT key,value FROM meta'))
        return {'kb_version':meta['kb_version'],'schema_version':meta['schema_version'],'kb_root':str(self.root),
            'index_path':str(self.index),'index_version':INDEX_VERSION,'entries':self.db.execute('SELECT count(*) FROM entries').fetchone()[0],
            'relations':self.db.execute('SELECT count(*) FROM edges').fetchone()[0],
            'last_validation':json.loads(meta['last_validation']),'last_index_build':meta['last_index_build'],
            'index_current':signature(self.root)==self.loaded_signature,
            'service_status':'ready_in_this_process','transport':'stdio_on_demand',
            'skill_integration_status':'requires client skill discovery and a new-session behavior check'}

    def get_entry(self,id):
        self.ready()
        row=self.db.execute('SELECT json FROM entries WHERE id=?',(id,)).fetchone()
        if not row:raise KBError('INVALID_ID','Unknown canonical knowledge ID: '+id)
        e=json.loads(row[0]); sources=[]; warnings=[]
        for ref in e['sources']:
            source=self.db.execute('SELECT json FROM nodes WHERE id=?',(ref['source_id'],)).fetchone()
            sources.append(json.loads(source[0]))
            if ref.get('claim_id'):
                c=json.loads(self.db.execute('SELECT json FROM nodes WHERE id=?',(ref['claim_id'],)).fetchone()[0])
                if c.get('status')=='superseded':warnings.append({'claim':c,'use_as_evidence':False})
        return {'kb_version':dict(self.db.execute('SELECT key,value FROM meta'))['kb_version'],
            'entry':e,'source_registry':sources,'correction_warnings':warnings}

    def search_kb(self,query='',top_k=8,mode=None,**filters):
        self.ready()
        if mode is not None and mode not in MODE_TYPES:raise KBError('INVALID_ARGUMENT','Unknown mode')
        if not isinstance(query,str) or len(query)>4000:raise KBError('INVALID_ARGUMENT','query must be at most 4000 characters')
        if type(top_k) is not int or not 1<=top_k<=30:raise KBError('INVALID_ARGUMENT','top_k must be 1..30')
        terms=tokens(query,True); ranks=self.provider.candidates(self.db,terms)
        exact=self.db.execute('SELECT id FROM entries WHERE lower(id)=?',(query.strip().lower(),)).fetchone()
        if exact:ranks[exact[0]]=-1000
        clauses=[];params=[]
        for name,items in filters.items():
            if name not in FILTERS:raise KBError('INVALID_ARGUMENT','Unknown filter '+name)
            if not isinstance(items,list) or any(not isinstance(x,str) for x in items):raise KBError('INVALID_ARGUMENT',name+' must be a string array')
            if items:
                clauses.append('EXISTS(SELECT 1 FROM facets f WHERE f.id=e.id AND f.kind=? AND f.value IN ('+','.join('?'*len(items))+'))')
                params += [FILTERS[name]]+[x.lower() for x in items]
        if query.strip():
            if not ranks:
                return {'results':[],'total_matches':0,'query':query,'filters':filters,'knowledge_gap':True,
                    'kb_version':dict(self.db.execute('SELECT key,value FROM meta'))['kb_version']}
            clauses.append('e.id IN ('+','.join('?'*len(ranks))+')');params+=list(ranks)
        sql='SELECT e.json FROM entries e'+(' WHERE '+' AND '.join(clauses) if clauses else '')
        candidates=[json.loads(row[0]) for row in self.db.execute(sql,params)]
        if query.strip():candidates=[e for e in candidates if e['id'] in ranks]
        if not filters.get('statuses'):candidates=[e for e in candidates if e['status'] not in ['superseded','deprecated','retracted']]
        candidate_ids={e['id'] for e in candidates}; out=[]; qterms=set(terms)
        priority=MODE_TYPES.get(mode,[])
        for e in candidates:
            focus=set(tokens(e['title']+' '+e['summary'],True)); overlap=len(qterms&focus)
            relevance=min(20,overlap*1.5)+math.log1p(abs(ranks.get(e['id'],0)))*3
            scope_match=sum(any(t in d.lower() for t in qterms) for d in e['scope_structured']['domains'])
            neighbor_count=sum(row[0] in candidate_ids for row in self.db.execute('SELECT dst FROM edges WHERE src=? AND relation!=?',(e['id'],'related')))
            context=min(.4,neighbor_count*.1)
            evidence={'E0':0,'E1':.1,'E2':.2,'E3':.3,'E4':.3,'E5':.3}.get(e['evidence_level'],0)
            type_score=(len(priority)-priority.index(e['entry_type']))*.12 if e['entry_type'] in priority else 0
            status_score=.05 if e['status'] in ['supported_by_klei','validated_single_case'] else 0
            score=relevance+scope_match*.7+context+evidence+type_score+status_score
            if exact and e['id']==exact[0]:score+=1000
            out.append(compact(e)|{'score':round(score,5),'match_reason':{
                'matched_terms':sorted(qterms&focus)[:12],'fts_match':e['id'] in ranks,'exact_id':bool(exact and e['id']==exact[0]),
                'scope_matches':scope_match,'typed_neighbor_bonus':context,'mode_type_bonus':round(type_score,2),
                'evidence_bonus':evidence,'status_bonus':status_score,'note':'Evidence strength and recommendation confidence are not relevance.'}})
        out.sort(key=lambda e:(-e['score'],e['id']))
        return {'results':out[:top_k],'total_matches':len(out),'query':query,'filters':filters,
            'knowledge_gap':not bool(out),'kb_version':dict(self.db.execute('SELECT key,value FROM meta'))['kb_version']}

    def get_related(self,id,relation_types=None,depth=1,entry_types=None,direction='both',limit=30):
        self.ready()
        known=self.db.execute('SELECT id FROM entries WHERE id=? UNION SELECT id FROM nodes WHERE id=?',(id,id)).fetchone()
        if not known:raise KBError('INVALID_ID','Unknown graph node '+id)
        if type(depth) is not int or not 1<=depth<=3 or type(limit) is not int or not 1<=limit<=100:raise KBError('INVALID_ARGUMENT','depth 1..3, limit 1..100')
        if direction not in ['both','outgoing','incoming']:raise KBError('INVALID_ARGUMENT','direction')
        kinds=set(relation_types or RELATIONS)
        if kinds-RELATIONS:raise KBError('INVALID_ARGUMENT','Unknown relation type')
        seen={id};front={id};paths=[];results=[];truncated=False;edge_seen=set()
        for hop in range(depth):
            nxt=set()
            for node in sorted(front):
                node_kind=self.db.execute('SELECT kind FROM nodes WHERE id=?',(node,)).fetchone()
                if node!=id and node_kind and node_kind[0]=='source':continue
                for src,rel,dst in self.db.execute('SELECT src,relation,dst FROM edges WHERE src=? OR dst=? ORDER BY src,relation,dst',(node,node)):
                    if rel not in kinds or (direction=='outgoing' and src!=node) or (direction=='incoming' and dst!=node):continue
                    target=dst if src==node else src
                    key=(src,rel,dst)
                    if key not in edge_seen:
                        if len(paths)>=300 or len(seen)>=200:truncated=True;break
                        paths.append({'from':src,'relation':rel,'to':dst,'depth':hop+1,'traversed':'outgoing' if src==node else 'incoming'})
                        edge_seen.add(key)
                    if target in seen:continue
                    seen.add(target);nxt.add(target)
                    row=self.db.execute('SELECT json FROM entries WHERE id=?',(target,)).fetchone()
                    if row:
                        e=json.loads(row[0]);item=compact(e)
                        if entry_types and e['entry_type'] not in entry_types:continue
                    else:
                        if entry_types:continue
                        kind,payload=self.db.execute('SELECT kind,json FROM nodes WHERE id=?',(target,)).fetchone()
                        obj=json.loads(payload);item={'id':target,'node_type':kind,'status':obj.get('status'),'description':obj.get('description',obj.get('statement'))}
                    results.append(item)
                    if len(results)>=limit:truncated=True;break
                if truncated:break
            if truncated:break
            front=nxt
        return {'origin':id,'results':results,'edges':paths,'truncated':truncated,'direction':direction}

    def get_klei_facts(self,query='',top_k=8):
        return self.search_kb(query,top_k,entry_types=['source_fact'])

    def get_tests(self,query='',entry_ids=None,top_k=8):
        if type(top_k) is not int or not 1<=top_k<=30:raise KBError('INVALID_ARGUMENT','top_k must be 1..30')
        result=self.search_kb(query,top_k,entry_types=['test_case']) if query or not entry_ids else {'results':[]}
        items={e['id']:e for e in result['results']}
        for id in entry_ids or []:
            for e in self.get_related(id,depth=2,entry_types=['test_case'],limit=30)['results']:items.setdefault(e['id'],e)
        return {'results':list(items.values())[:top_k],'notice':'Test candidates; not proof of executed runtime validation.'}

    def get_context_bundle(self,task_description,mode='architect',budget='normal'):
        if mode not in MODE_TYPES:raise KBError('INVALID_ARGUMENT','Unknown mode')
        if budget not in ['compact','normal','deep']:raise KBError('INVALID_ARGUMENT','Unknown budget')
        count,chars={'compact':(8,9000),'normal':(15,18000),'deep':(24,30000)}[budget]
        search=self.search_kb(task_description,top_k=30,mode=mode)
        rows=search['results'];selected={}
        if mode=='architect' and rows:
            for e in self.search_kb('',top_k=2,entry_types=['playbook'])['results']:selected[e['id']]=e
        # 相关性先筛选，再按任务覆盖类型；不靠E3把无关事实塞进结果。
        for kind in MODE_TYPES[mode]:
            hit=next((e for e in rows if e['entry_type']==kind),None)
            if hit:selected.setdefault(hit['id'],hit)
        for e in rows:
            if len(selected)>=count:break
            selected.setdefault(e['id'],e)
        if rows and len(selected)<count:
            for seed in rows[:3]:
                for e in self.get_related(seed['id'],depth=1,entry_types=['rule','anti_pattern','decision','test_case','correction'],limit=12)['results']:
                    if len(selected)>=count:break
                    selected.setdefault(e['id'],e|{'match_reason':{'related_to':seed['id']}})
        corrections=[]
        for e in list(selected.values()):
            detail=self.get_entry(e['id'])
            for warning in detail['correction_warnings']:
                corrections.append(warning)
        payload={'mode':mode,'budget':budget,'kb_version':search['kb_version'],'entries':[],
            'evidence_summary':{},'knowledge_gaps':[],'correction_warnings':corrections,
            'notice':'Summaries only; use get_entry for scope limits and sources before important decisions. No runtime tests implied.'}
        order={x:i for i,x in enumerate(MODE_TYPES[mode])}
        for e in sorted(selected.values(),key=lambda x:(order.get(x['entry_type'],99),-x.get('score',0))):
            if len(payload['entries'])>=count:break
            trial=payload|{'entries':payload['entries']+[e]}
            if len(json.dumps(trial,ensure_ascii=False))>chars-1000:continue
            payload['entries'].append(e)
        payload['evidence_summary']=dict(Counter(e['evidence_level'] for e in payload['entries']))
        if not rows:payload['knowledge_gaps'].append({'status':'no_retrieval_match','task_local_only':True,'message':'No matching KB evidence; continue with current code and Klei source.'})
        requested=set(tokens(task_description))
        for area in ['replica','stategraph','prediction','技能','预测']:
            if area in requested and not any(area.lower() in (e['title']+' '+e['summary']).lower() for e in payload['entries']):
                payload['knowledge_gaps'].append({'area':area,'status':'coverage_not_established_by_retrieval','task_local_only':True})
        payload['truncated']=len(payload['entries'])<len(selected)
        payload['max_characters']=chars
        return payload

    def validate_kb(self):
        return validate(self.root)[1]

    def close(self):
        if self.db:self.db.close();self.db=None
