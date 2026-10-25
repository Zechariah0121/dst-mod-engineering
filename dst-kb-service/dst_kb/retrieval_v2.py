"""Unified, explanation-bearing lexical retrieval over immutable knowledge."""
import math
from .request_analysis import analyzed_request
from . import developer_trace as dt
import json
import re
from collections import Counter
from .intent_scope import (query_scope, semantic_concepts as concepts,
                           task_subjects, task_requests, effective_task_query,
                           expand_semantic_query, BROAD_CONCEPTS, structured_record_ids, engineering_relations)
from .task_relevance import task_support, relevance_query, content_tokens, original_engineering_relations
from .facet_contracts import register_source_navigation
from .budget_priority import requested_method_identity_match
from .policy_context import (project_policy_intent, project_policy_eligible,
                             policy_units, policy_task_support)

VERSION='native-retrieval/2.13'
ABSOLUTE_RELEVANCE_FLOOR=14.
RELATIVE_RELEVANCE_FRACTION=.35
LEGACY_SEMANTIC_KEYS=set('api_mechanism observed_behaviour implication do_not_infer statement why applies_when does_not_mean counterexample failure_if_violated detection_questions symptoms why_it_happens why_it_is_dangerous when_it_is_actually_acceptable detection safer_alternatives steps question branches recommended_direction exceptions unknowns problem context forces core_idea structure state_ownership authority lifecycle networking persistence performance benefits costs use_when avoid_when implementation_notes preconditions expected_correctness limits purpose setup action expected_invariant failure_signal applicability previous_claim replacement correction_scope retrieval_policy stop_conditions revision_policy architecture_summary observations unverified exclusions availability_limit static_failure_paths'.split())
STOP={'the','a','an','and','or','to','of','for','dst','mod','with','from','this','does','can','how','is','are','not','only','please','need','ordinary','contract','contracts','knowledge','source','native','review','reviewer','research','implementation','engine','evidence','code','coding','task','normal','what','when','should','would','could','must','want','query','question','in','at','by','on','it','its','as','be','before','after','has','have','each','all','any','some','these','those','into','then','than','same','different','also','client','server','remote','host','dedicated','authority','cleanup','material','materials','resource','resources','provider','providers','callback','callbacks','result','results','success','failure','state','value','values','object','entity','player','component','components','method','methods','function','functions','return','returns','using','use','used'}
GENERIC={'物品','玩家','恢复','源码','原版','组件','接口','状态','当前','实际','分支','方法','对象','如何','什么','需要','可以','是否','知识','不能','没有','不要','普通','通用','哪里','放哪','就能','认为','涉及','不涉','只修','只看','先不'}
# 自然问题里的普通名词不能冒充精确 API；lookup_api 仍支持原样裸符号。
CONCEPT_SYMBOLS={'action','actions','entity','player','world','manager','owner','provider','getter','setter','snapshot','hunger','health','sanity','widget','hud','client','server','remote','host','false','true','nil','class','component','callback','return','source','result','timer','cooldown','contract','state','load','save','engine','native','policy','runtime','api','mod','task'}
COMMON_METHODS={'onload','onsave','onremove','remove','update','get','set','fn'}
NATURAL_ON_WORDS={'one','ones','once','only','onto','onward','onwards'}
CONTEXT_TOPICS={'cleanup','authority','load','index','class'}
# Topic vocabulary is a bounded navigation dictionary, not a task-to-answer map.
VOCAB={
 'identity':['userid','guid','ents','allplayers','clienttable','identity','identifier','account','rejoin','账号','身份','用户','旧玩家','新玩家','旧实体','退出重进','重新进来','重连','reconnect','disconnect'],
 'load':['onload','setpersistdata','load','save','restore','读档','加载','恢复','存档','保存'],
 'spawn':['onnewspawn','onload','初次出生','新玩家出生','旧存档','缺键','默认值'],
 'view':['replica','classified','getter','snapshot','dirty','panel','badge','display','change listener','change notification','initial value','current state','初值','当前值','初读','更新通知','ready','hud','ui','widget','界面','面板','显示','血条'],
 'cleanup':['cleanup','onremove','onexit','detach','清理','收尾','移除','解绑','销毁'],
 'authority':['rpc','authority','权限','权威','请求','客户端','服务端','remote','host','dedicated'],
 'action':['bufferedaction','performbufferedaction','action','动作','候选','捕获','preview','prediction','预测'],
 'stategraph':['stategraph','gotostate','eventhandler','handleevent','状态图','timeline','statemem','onexit'],
 'combat':['combat','doattack','canhittarget','onhitother','伤害','命中','攻击','战斗','redirected'],
 'projectile':['projectile','launch','onhit','onmiss','弹体','投射','投掷'],
 'modifier':['modifier','sourcekey','贡献','修饰器','modifierlist','乘区','撤销','装备'],
 'buff':['debuff','buff','adddebuff','detach','增益','刷新','替换'],
 'timer':['timer','cooldown','timerdone','timeleft','定时器','冷却','剩余时间'],
 'recharge':['rechargeable','setchargetimemod','ischarged','discharge','充能','充电','rechargechange'],
 'speed':['playerspeedmult','runspeed','setspeedmultiplier','速度','移速'],
 'builder':['builder','dobuild','makerecipe','build','制作','配方','ingredients','材料'],
 'world':['world','世界','worldstate','watchworldstate','onworldstate','世界状态','season','季节'],
 'shard':['shard','shards','mastershard','migration','migrate','洞穴','分片','writer','mirror','跨洞穴'],
 'index':['manager','registry','derived','index','管理器','派生','索引','cache'],
 'config':['getmodconfigdata','configuration','config','配置','false','缺省'],
 'module':['modimport','require','global','module','模块','导入','导出','模块依赖','hook'],
 'work':['workable','workedby','workleft','onwork','onfinish','chop','mine','工作','砍伐','敲击'],
 'pick':['pickable','pick','onpicked','采摘','再生'],
 'uses':['finiteuses','setuses','onfinished','use','耐久','次数','磨损'],
 'fuel':['fueled','fuel','initializefuellevel','燃料','startconsuming','depleted'],
 'perish':['perishable','perish','perishtime','腐败','腐烂','暂停'],
 'deploy':['deploy','candeploy','ondeploy','部署','种植'],
 'trader':['trader','give','acceptgift','testitem','交易','给予'],
 'container':['container','widgetsetup','setnumslots','maxitemslots','net_entity','容器','槽位','容量'],
 'class':['class','readonly','property','setter','继承','构造','属性'],
 'spatial':['spatial','findentities','findwalkableoffset','findentity','findpickupableitem','附近','空间','落点','偏移','坐标'],
 'nearest':['nearest','closest','ties','排序','最近','同距'],
 'collision':['collision','mask','碰撞','物理','效果送达'],
 'burn':['burnable','ignite','extinguish','burnt','燃烧','点燃','烧毁'],
 'eat':['eater','eat','oneaten','oneat','食用','进食'],
 'upgrade':['upgrade','upgrader','升级'],
 'heal':['heal','healer','onheal','治疗'],
 'boat':['boat','repair','漏点','堵漏','修船'],
 'character_lifecycle':['resurrect','resurrection','revive','ghost','reroll','death','复活','幽灵','死亡','换角'],
 'skillui':['skilltree','skilltreeupdater','技能树','background','atlas'],
}
def record_family(entry):
    kind=entry.get('entry_type')
    family='core' if kind=='native_core_knowledge' else 'n001' if kind=='native_ai_knowledge' else 'legacy'
    if 'claims' in entry and 'gate_a' in entry:family='core'
    elif 'native_fact' in entry and 'ai_coding_impact' in entry:family='n001'
    return family


def source_context(entry):
    scope=entry.get('scope',{})
    if isinstance(scope,dict):
        scope=scope.get('statement','')
    # Questions and titles can name several requested systems. Only original scope
    # and a verified claim receiver may identify an omitted source subject.
    return ' '.join(strings([scope,entry.get('scope_text','')]))

def semantic_units(entry,family,source_symbols=None):
    from .facet_contracts import record_contract_context
    with record_contract_context(entry,family):
        return _semantic_units(entry,family,source_symbols)


def _semantic_units(entry,family,source_symbols=None):
    from .projection_v2 import _atoms, _boundaries, _claim_contexts
    # Rank only original atoms that a projection can actually deliver. The same
    # pointers and verified owner roles are used at both sides of selection.
    values=[atom for atom in _atoms(entry,family)+_boundaries(entry,family)
            if not set(atom.get('kind','').replace(' ','').split('/')) &
            {'PROJECT_POLICY','HISTORICAL_PRODUCT_EVIDENCE'}]
    contexts=_claim_contexts(entry,family,values)
    units=[]
    for atom in values:
        value=atom['statement'];pointer=atom['record_pointer']
        text=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,sort_keys=True)
        context=contexts[pointer]
        if text.strip():units.append({'text':norm(text),'original_text':value,'context':context,
                                     'tokens':words(text),'concepts':concepts(value),
                                     'kind':atom['kind'],'record_pointer':pointer})
    return units
DEEP_TRIGGERS={
 'DC-C04':['dug_sapling','树苗','可移植树苗'],
 'BR-P05':['chest','木箱','箱子','普通箱'],
 'SPATIAL-CODE-NEAREST-ORDER':['nearest','closest','ties','排序','最近','同距'],
 'SPATIAL-CODE-COLLISION-EFFECT':['collision','碰撞','物理','效果送达'],
}

def norm(value):return re.sub(r'\s+',' ',value.lower()).strip()
def words(value):
    value=re.sub(r'([a-z])([A-Z])',r'\1 \2',value).lower()
    out=re.findall(r'[a-z_][a-z0-9_]*',value)
    for part in re.findall(r'[\u3400-\u9fff]+',value):
        out.extend(part[i:i+2] for i in range(len(part)-1))
    return set(x for x in out if x not in STOP and x not in GENERIC)
def contains(text,term):
    term=norm(term)
    if not term:return False
    if any('\u3400'<=x<='\u9fff' for x in term):return term in text
    return re.search(r'(?<![a-z0-9_])'+re.escape(term)+r'(?![a-z0-9_])',text) is not None
def strings(obj):
    if isinstance(obj,str):return [obj]
    if isinstance(obj,list):return [s for x in obj for s in strings(x)]
    if isinstance(obj,dict):return [s for x in obj.values() for s in strings(x)]
    return []
def atoms(entry,family):
    if family=='core':return ' '.join(c['statement'] for c in entry['claims'])
    if family=='n001':
        return ' '.join(strings([entry.get('native_fact',{}).get('statement',''),entry.get('ai_coding_impact',{}).get('decisions',[]),entry.get('common_ai_failure',[]),entry.get('does_not_mean',[]),entry.get('recommended_reasoning',{}).get('steps',[])]))
    return ' '.join(strings({k:v for k,v in entry.get('details',{}).items() if k in LEGACY_SEMANTIC_KEYS}))+' '+entry.get('summary','')
def extract_symbols(text):
    left=r'(?<![A-Za-z0-9_])';right=r'(?![A-Za-z0-9_])'
    ident=r'[A-Za-z_][A-Za-z0-9_]*'
    out=set(re.findall(left+ident+r'(?::|\.)'+ident+right,text))
    out.update(re.findall(left+ident+r'(?=\s*\()',text))
    out.update(re.findall(left+r'(?:[A-Z][a-z0-9]+){2,}[A-Za-z0-9_]*'+right,text))
    # 普通数量词、时间词和介词不凭 on 前缀成为回调；显式 owner/调用仍由上面的语法识别。
    out.update(symbol for symbol in re.findall(left+r'(?:on[a-z_]+|[a-z]+_[a-z_]+)'+right,text)
               if symbol not in NATURAL_ON_WORDS)
    out.update(re.findall(left+r'[A-Z][A-Z0-9_]{2,}'+right,text))
    # Exact symbols are extracted from statements, never evidence wrappers/locators.
    return {s.lower() for s in out if len(s)>2 and s.lower() not in STOP}
def topics(text):return {name for name,aliases in VOCAB.items() if any(contains(text,a) for a in aliases)}

def intent(query):
    scope=query_scope(query)
    positive=norm(scope['positive_query'])
    negative=[norm(c) for c in scope['negative_clauses']]
    symbols=extract_symbols(scope['positive_query'])-CONCEPT_SYMBOLS
    qualified={s for s in symbols if ':' in s or '.' in s}
    symbols-={s.rsplit(':',1)[-1].rsplit('.',1)[-1] for s in qualified}
    return {'positive':positive,'original_positive':scope['positive_query'],'negative_clauses':negative,
            'negative_topics':set().union(*(topics(c) for c in negative)) if negative else set(),
            'topics':topics(positive),'concepts':concepts(positive),'subjects':task_subjects(positive),'symbols':symbols,'qualified_symbols':qualified,
            'guard_clauses':scope['guard_clauses'],
            'positive_focus':scope['positive_focus'],
            'record_references':scope['record_references'],
            **{key:scope[key] for key in ('ordinary','generic','deep_requested','deep_forbidden','special_lifecycle_requested','task_role')}}

class Ranker:
    def content_focus(self, query_tokens, support):
        if not support.get('whole_atom_delivery_allowed'):
            return 0.
        witness = support.get('relevance_source_unit') or support.get('source_unit', '')
        terms = query_tokens & content_tokens(witness) & set(support.get('lexical_hits', []))
        # 已准入的原句与标题使用相同的词权重；长原子不能稀释其中的相关原句。
        return sum(sorted((self.idf.get(term, 0.) * 4. for term in terms), reverse=True)[:3])

    def __init__(self,entries,governance,routing,source_symbols=None,*,defer_semantics=False):
        from .facet_contracts import contract_symbols, register_source_navigation
        self.documents=[];self.governance=governance;self.routing=routing or {}
        self.record_ids={entry['id'].upper() for entry in entries}
        route_aliases={}
        for task in self.routing.get('tasks',[]):
            ts=[task['task']]+self.routing.get('routing_rules',{}).get('task_aliases',{}).get(task['task'],[])
            for kid in task['core_entries']:route_aliases.setdefault(kid,[]).extend(ts)
        for entry in entries:
            kid=entry['id'];family=record_family(entry)
            title=entry['title'];body=atoms(entry,family)
            aliases=entry.get('aliases',[])+strings(entry.get('retrieval_triggers',[]))+route_aliases.get(kid,[])
            triggers=entry.get('task_keywords',[])+strings(entry.get('typical_mod_tasks',[]))
            focus=' '.join([title,entry.get('engineering_question','')]+aliases)
            primary=' '.join([title,entry.get('engineering_question','')]+entry.get('aliases',[]))
            negative_focus_topics=topics(norm(' '.join([title,entry.get('engineering_question','')])))
            symbols=extract_symbols(body+' '+focus+' '+' '.join(triggers))
            nav=(source_symbols or {}).get(kid,[])
            register_source_navigation(entry,family,nav)
            symbols|={s.rsplit(':',1)[-1].rsplit('.',1)[-1] for s in symbols}
            contract_navigation={s.lower() for s in contract_symbols(entry,family)}
            lookup_symbols=symbols|{n['symbol'].lower() for n in nav}|contract_navigation
            lookup_symbols|={s.rsplit(':',1)[-1].rsplit('.',1)[-1] for s in lookup_symbols}
            ft=words(primary);bt=words(body);tt=words(' '.join(triggers))
            semantic=norm(focus+' '+body+' '+' '.join(triggers))
            self.documents.append({'id':kid,'entry':entry,'family':family,'track':entry.get('track','N001' if family=='n001' else 'legacy'),'focus':norm(focus),'primary_focus':norm(primary),'primary_topics':topics(norm(primary)),'subject_topics':topics(norm(title)),'primary_tokens':words(primary),'body':norm(body),'focus_tokens':ft,'body_tokens':bt,'trigger_tokens':tt,'symbols':symbols,'lookup_symbols':lookup_symbols,'contract_navigation':contract_navigation,'source_symbol_navigation':nav,'topics':topics(semantic),'aliases':aliases,'semantic':semantic})
            if not defer_semantics:
                self.semantic_units_for(self.documents[-1])
                self.policy_units_for(self.documents[-1])
            self.documents[-1]['negative_focus_topics']=negative_focus_topics
            self.documents[-1]['focus_concepts']=concepts(primary)
            self.documents[-1]['all_concepts']=concepts(primary+' '+body)
            scoped=entry.get('scope_structured',{})
            refs={kid.upper()} | {value.upper() for value in entry.get('created_from_case',[]) if isinstance(value,str)}
            refs|={value.upper() for value in scoped.get('cases',[]) if isinstance(value,str)}
            refs|={edge['target'].upper() for edge in entry.get('typed_relations',[])
                   if edge.get('type') in ('corrects','supersedes') and isinstance(edge.get('target'),str)}
            details=entry.get('details',{})
            refs|={value.upper() for value in details.get('target_claim_ids',[]) if isinstance(value,str)}
            refs|={edge.get('target',edge.get('target_id')).upper() for edge in entry.get('relations',[])
                   if isinstance(edge,dict) and edge.get('type',edge.get('relation_type')) in ('corrects','supersedes')
                   and isinstance(edge.get('target',edge.get('target_id')),str)}
            self.documents[-1]['record_reference_ids']=refs
        self.reference_ids=set().union(*(d['record_reference_ids'] for d in self.documents)) if self.documents else set()
        self.reference_namespaces={value.split('-',1)[0] for value in self.reference_ids if '-' in value}
        df=Counter(t for d in self.documents for t in d['focus_tokens']|d['body_tokens']|d['trigger_tokens'])
        self.idf={t:math.log(1+(len(self.documents)-v+.5)/(v+.5)) for t,v in df.items()}
        symbol_df=Counter(s for d in self.documents for s in d['symbols'])
        self.symbol_weight={s:min(60.,10.+12.*math.log(1+(len(self.documents)-v+.5)/(v+.5))) for s,v in symbol_df.items()}
        lookup_df=Counter(s for d in self.documents for s in d['lookup_symbols'])
        self.lookup_weight={s:min(60.,18.+18.*math.log(1+(len(self.documents)-v+.5)/(v+.5))) for s,v in lookup_df.items()}

    def semantic_units_for(self,document):
        # Derived once per immutable service snapshot, after the unchanged record
        # gates require it. Exact entry rendering does not need a corpus model.
        if 'semantic_units' not in document:
            document['semantic_units']=semantic_units(document['entry'],document['family'],document['source_symbol_navigation'])
        return document['semantic_units']

    def policy_units_for(self,document):
        if 'policy_units' not in document:
            units=policy_units(document['entry'],document['family'])
            for unit in units:
                text=unit['original_text'] if isinstance(unit['original_text'],str) else json.dumps(unit['original_text'],ensure_ascii=False,sort_keys=True)
                unit.update({'text':norm(text),'tokens':words(text),'concepts':concepts(unit['original_text'])})
            document['policy_units']=units
        return document['policy_units']

    def admission(self,d,projection,query,lookup=False,query_intent=None):
        g=self.governance.get(d['id'],{})
        if d['family']=='core' and not d['entry'].get('gate_a',{}).get('accepted'):return 'gate_a_not_accepted'
        if projection=='coding' and g:
            if g.get('coding_status') not in ['coding_default','coding_conditional']:return 'coding_hold_or_prohibited'
            if g.get('knowledge_status') in ['research','superseded'] or g.get('retrieval_status')=='restricted':return 'coding_knowledge_or_retrieval_restricted'
        exact=query.strip().lower()==d['id'].lower()
        if projection=='reviewer' and g.get('retrieval_status')=='restricted' and not exact:return 'restricted_requires_exact_identity'
        if g.get('knowledge_status')=='superseded' and not exact:return 'superseded_requires_exact_identity'
        if d['family']=='legacy' and d['entry'].get('status') in ['superseded','deprecated','retracted'] and not exact:return 'historical_status_requires_exact_identity'
        if d['id']=='AI-N001-13' and not exact:
            qi=query_intent or intent(query)
            if not qi['special_lifecycle_requested'] and not lookup:return 'special_lifecycle_not_requested'
        return None

    def record_gate(self,document,projection,query,filters=None,scope_logic='and',lookup=False,mode=None):
        """Shared record admission; no task support, ranking or score thresholds."""
        qi=intent(query)
        if not lookup and query.strip().upper() not in self.record_ids:
            qi['record_references']=sorted(structured_record_ids(effective_task_query(query)))
        return (self._record_admission_filters(document,projection,query,filters,scope_logic,lookup,qi)
                or self._record_scope_gate(document,query,qi))

    def _record_admission_filters(self,d,projection,query,filters,scope_logic,lookup,qi):
        g=self.governance.get(d['id'],{});e=d['entry']
        reason=self.admission(d,projection,query,lookup,qi)
        dt.record(d['id'],'ADMISSION',admission=reason or 'ADMITTED')
        if reason:return reason
        gate_checks=[]
        for key,values in (filters or {}).items():
            if not values:continue
            if key.endswith('_statuses'):got=[g.get(key[:-2], '')]
            elif key=='families':got=[d['family']]
            elif key=='tracks':got=[d['track']]
            elif key=='claim_types':got=[c['kind'] for c in e.get('claims',[])] or [e.get('native_fact',{}).get('claim_type','')]
            elif key=='entry_types':got=[e.get('entry_type','native_core_knowledge' if d['family']=='core' else 'native_ai_knowledge')]
            elif key in ['confidence','evidence_levels','statuses']:got=[e.get({'confidence':'confidence','evidence_levels':'evidence_level','statuses':'status'}[key],'')]
            else:got=e.get('scope_structured',{}).get({'domains':'domains','cases':'cases','sides':'sides','runtime_environments':'runtime_environments','tags':'tags'}.get(key,key),e.get('tags',[]) if key=='tags' else [])
            gate_checks.append(any(norm(str(x))==norm(str(v)) for x in got for v in values))
            dt.record(d['id'],'FILTER',filters=gate_checks[-1])
        if gate_checks and not (all(gate_checks) if scope_logic=='and' else any(gate_checks)):
            return 'FILTER_NOT_MATCHED'
        return None

    def _record_scope_gate(self,d,query,qi):
        g=self.governance.get(d['id'],{})
        negative_refs=set().union(*(structured_record_ids(clause) for clause in qi['negative_clauses'])) if qi['negative_clauses'] else set()
        if d['id'].upper() in negative_refs:
            return 'record_identity_explicitly_excluded'
        references=set(qi.get('record_references',[])) & self.reference_ids
        if not references and any(re.search(r'\d',value) and value.split('-',1)[0] in self.reference_namespaces
                                  for value in qi.get('record_references',[])):
            return 'record_identity_not_registered'
        if references and not references & d['record_reference_ids']:
            return 'record_identity_scope_not_matched'
        # Navigation aliases do not supply the original negated record subject.
        positive_subjects=(d['negative_focus_topics']&qi['topics'])-CONTEXT_TOPICS
        neg_focus=(d['negative_focus_topics']&(qi['negative_topics']-qi['topics']))-CONTEXT_TOPICS
        if positive_subjects and not (neg_focus&{'shard'}):neg_focus=set()
        if neg_focus:
            # A coarse title topic can describe several independent original
            # atoms. Let an actually supported, non-excluded atom reach the
            # existing per-atom admission; this does not admit the record body.
            excluded_relations = set().union(*(engineering_relations(clause) for clause in qi['negative_clauses']))
            source_partition = bool(excluded_relations) and any(
                excluded_relations & original_engineering_relations(unit['original_text'], unit['kind'])
                and task_support('; '.join(qi['negative_clauses']), unit['original_text'], unit['context'])
                    .get('whole_atom_delivery_allowed', False)
                for unit in self.semantic_units_for(d))
            bounded_positive = source_partition and any(task_support(query, unit['original_text'], unit['context'])
                                   .get('whole_atom_delivery_allowed', False)
                                   for unit in self.semantic_units_for(d))
            if not bounded_positive:return 'negative_topic'
        if g.get('retrieval_status')=='deep_only' and query.strip().lower()!=d['id'].lower():
            triggers=DEEP_TRIGGERS.get(d['id'],[])
            neg=any(contains(c,t) for c in qi['negative_clauses'] for t in triggers)
            specific=any(contains(qi['positive'],t) for t in triggers)
            if neg or qi['deep_forbidden'] or (qi['generic'] and not qi['deep_requested']) or not specific:
                return 'deep_subject_not_explicit_or_excluded'
        return None

    @analyzed_request
    def search(self,query,projection,limit,filters=None,scope_logic='and',lookup=False,mode=None,view='decision'):
        scope_intent=intent(query);qi=dict(scope_intent);filters=filters or {};rows=[];excluded=[]
        request_frames=task_requests(query)
        policy_intent=project_policy_intent(query)
        task_mode=('implement' if mode=='coding' else mode) or qi['task_role']
        identity=query.strip().lower()
        exact_target=identity if any(d['id'].lower()==identity for d in self.documents) else None
        if query.strip() and not (lookup or exact_target):
            # 同一请求框架用于支持与排名，省略主语不在纯文本往返时丢失。
            request_text='; '.join(row['effective_text']+' '+' '.join(row['inherited_subjects'])
                                  for row in request_frames)
            resolved=intent(request_text)
            resolved['subjects']|=set().union(*(set(row['inherited_subjects']) for row in request_frames))
            # 排名与原文准入使用同一任务上下文；无关背景不能单独给卡片加分。
            for key in ('positive','original_positive','topics','concepts','subjects','symbols','qualified_symbols'):
                qi[key]=resolved[key]
            scope_intent['record_references']=resolved['record_references']
            qi['record_references']=resolved['record_references']
        qt=words(expand_semantic_query(qi['original_positive']))
        alias_counts={t:sum(contains(qi['positive'],a) for a in VOCAB[t]) for t in qi['topics']}
        for d in self.documents:
            dt.record(d['id'],'RANKER_ENTER',family=d['family'])
            if exact_target and d['id'].lower()!=exact_target:
                dt.terminal(d['id'],'EXACT_TARGET','EXACT_TARGET_OTHER_RECORD')
                continue
            reason=self._record_admission_filters(d,projection,query,filters,scope_logic,lookup,scope_intent)
            if reason:
                if reason!='FILTER_NOT_MATCHED':
                    exclusion={'id':d['id'],'reason':reason}
                    if reason=='negative_topic':
                        exclusion['topics']=sorted((d['negative_focus_topics']&(qi['negative_topics']-qi['topics']))-CONTEXT_TOPICS)
                    excluded.append(exclusion)
                stage={'FILTER_NOT_MATCHED':'FILTER','negative_topic':'NEGATIVE_TOPIC',
                       'deep_subject_not_explicit_or_excluded':'DEEP_SUBJECT'}.get(reason,'ADMISSION')
                dt.terminal(d['id'],stage,reason)
                continue
            g=self.governance.get(d['id'],{});e=d['entry'];exact=query.strip().lower()==d['id'].lower()
            sym=sorted(qi['symbols']&d['symbols'])
            single_symbol=query.strip().lower()
            contract_identity=bool(re.fullmatch(r'[a-z_]\w*(?:[.:]\w+)?',single_symbol) and single_symbol not in CONCEPT_SYMBOLS and single_symbol in d['contract_navigation'])
            source_identity=bool(re.fullmatch(r'[a-z_]\w*(?:[.:]\w+)?',single_symbol) and single_symbol not in CONCEPT_SYMBOLS and single_symbol in d['lookup_symbols'])
            if contract_identity and single_symbol not in sym:sym.append(single_symbol)
            if lookup:
                # Qualified identity cannot fall back to a similarly named method.
                symbol=query.strip().lower()
                if symbol not in d['lookup_symbols'] and not exact:
                    dt.terminal(d['id'],'LOOKUP_IDENTITY','LOOKUP_IDENTITY_NOT_MATCHED')
                    continue
                sym=[symbol] if symbol in d['lookup_symbols'] else []
            elif re.fullmatch(r'[a-z_]\w*[.:]\w+',identity) and identity not in d['lookup_symbols']:
                dt.terminal(d['id'],'QUALIFIED_IDENTITY','QUALIFIED_IDENTITY_NOT_MATCHED')
                continue
            reason=self._record_scope_gate(d,query,scope_intent)
            if reason:
                exclusion={'id':d['id'],'reason':reason}
                if reason=='negative_topic':
                    exclusion['topics']=sorted((d['negative_focus_topics']&(qi['negative_topics']-qi['topics']))-CONTEXT_TOPICS)
                excluded.append(exclusion)
                dt.terminal(d['id'],{'negative_topic':'NEGATIVE_TOPIC',
                    'record_identity_scope_not_matched':'RECORD_IDENTITY_SCOPE',
                    'record_identity_explicitly_excluded':'RECORD_IDENTITY_SCOPE',
                    'record_identity_not_registered':'RECORD_IDENTITY_SCOPE'}.get(reason,'DEEP_SUBJECT'),reason)
                continue
            fm=qt&d['focus_tokens'];bm=qt&d['body_tokens'];tm=qt&d['trigger_tokens']
            phrases=[x for x in d['aliases'] if len(x)>=4 and contains(qi['positive'],x)]
            topic_hits=qi['topics']&d['topics']
            focus_topics=qi['topics']&d['primary_topics']
            rstatus=g.get('retrieval_status')
            informative_focus={t for t in fm if self.idf.get(t,0)>=1.8}
            primary_hits=qt&d['primary_tokens']
            primary_anchor={t for t in primary_hits if self.idf.get(t,0)>=1.8}
            navigation_focus=sum(sorted((self.idf.get(t,0)*4. for t in fm),reverse=True)[:3])
            named_symbols=set(sym)-COMMON_METHODS
            natural_task=bool(query.strip() and not (lookup or exact or source_identity))
            semantic_units=self.semantic_units_for(d)
            allowed_units={unit['record_pointer'] for unit in semantic_units}
            if natural_task:
                from .facet_contracts import facet_admission
                ordinary_atoms=[{'kind':unit['kind'],'statement':unit['original_text'],'record_pointer':unit['record_pointer']}
                                for unit in semantic_units]
                admitted_units,_=facet_admission(e,d['family'],ordinary_atoms,query,
                    reference_context={'projection':projection,'view':view,'role':'reviewer',
                        'existing_admitted':True,'existing_deep_admitted':True,
                        'request_frames':request_frames,
                        'atom_contexts':{unit['record_pointer']:unit['context'] for unit in semantic_units}})
                allowed_units={atom['record_pointer'] for atom in admitted_units}
            unit_matches=[]
            for unit in semantic_units:
                if unit['record_pointer'] not in allowed_units:
                    dt.atom(d['id'],unit['record_pointer'],'RANK_UNIT_SUPPORT',kind=unit['kind'],admitted=False)
                    continue
                overlap=qt&unit['tokens'];semantic_overlap=qi['concepts']&unit['concepts']
                lexical=sum(self.idf.get(t,0) for t in overlap)/math.sqrt(max(1,len(unit['tokens'])/45))
                support=task_support(query,unit['original_text'],unit['context'],request_frames=request_frames)
                # 不借标题/导航把一条原文未说的机制拼出来；多任务允许其中一个子问题。
                # 自然任务只有整条可交付原文参与排名；相关性仍单独保留诊断。
                unit_supported=support.get('whole_atom_delivery_allowed',False) if natural_task else support['supported']
                semantic_score=(6.*min(3,len(support['mechanism_hits']))+4.*min(2,len(support['subject_hits']))) if unit_supported else 0.
                content_focus=self.content_focus(qt,support) if natural_task and unit_supported else 0.
                dt.atom(d['id'],unit['record_pointer'],'RANK_UNIT_SUPPORT',kind=unit['kind'],supported=support['supported'],
                    admitted=unit_supported,
                    whole_atom_delivery_allowed=support.get('whole_atom_delivery_allowed'),
                    subject_mismatch=support.get('subject_mismatch'),excluded_source_scope=support.get('excluded_source_scope'),
                    lexical_score=lexical,semantic_score=semantic_score)
                unit_matches.append((lexical+semantic_score+max(navigation_focus,content_focus) if unit_supported else -1.,lexical,semantic_overlap,overlap,unit,support,unit_supported,content_focus))
            if not lookup and project_policy_eligible(projection,policy_intent,True):
                from .facet_contracts import facet_admission
                policy_units=self.policy_units_for(d)
                policy_atoms=[{'kind':unit['kind'],'statement':unit['original_text'],'record_pointer':unit['record_pointer']}
                              for unit in policy_units]
                admitted_policy,_=facet_admission(e,d['family'],policy_atoms,query)
                allowed_policy={atom['record_pointer'] for atom in admitted_policy}
                for unit in policy_units:
                    if unit['record_pointer'] not in allowed_policy:continue
                    overlap=qt&unit['tokens'];semantic_overlap=qi['concepts']&unit['concepts']
                    lexical=sum(self.idf.get(t,0) for t in overlap)/math.sqrt(max(1,len(unit['tokens'])/45))
                    support=policy_task_support(query,unit['original_text'],unit['context'],policy_intent)
                    unit_supported=support['whole_atom_delivery_allowed']
                    semantic_score=(6.*min(3,len(support['mechanism_hits']))+4.*min(2,len(support['subject_hits']))) if unit_supported else 0.
                    dt.atom(d['id'],unit['record_pointer'],'RANK_POLICY_SUPPORT',kind=unit['kind'],unit_lane='PROJECT_POLICY',
                        supported=unit_supported,whole_atom_delivery_allowed=unit_supported,
                        subject_mismatch=support['subject_mismatch'],excluded_source_scope=support['excluded_source_scope'],
                        lexical_score=lexical,semantic_score=semantic_score)
                    unit_matches.append((lexical+semantic_score+navigation_focus if unit_supported else -1.,lexical,semantic_overlap,overlap,unit,support,unit_supported,0.))
            unit_matches.sort(key=lambda item:-item[0])
            supported_units=[item for item in unit_matches if item[6]]
            supported_nonpolicy=[item for item in supported_units if item[4].get('unit_lane')!='PROJECT_POLICY']
            supported_policy=[item for item in supported_units if item[4].get('unit_lane')=='PROJECT_POLICY']
            best_units=supported_units if natural_task else unit_matches
            best=best_units[0] if best_units else (-1.,0.,set(),set(),{'text':''},{'supported':False,'mechanism_hits':[],'subject_hits':[],'anchors':[]},False,0.)
            coherent_concepts=best[2]
            concept_anchor=best[6] and bool(best[5]['mechanism_hits'] or best[5].get('scoped_cleanup'))
            direct_topics={t for t in focus_topics if any(contains(qi['positive'],a) and contains(d['primary_focus'],a) for a in VOCAB[t])}
            topic_anchor=bool(direct_topics and (len(bm)>=2 or (primary_hits and any(alias_counts[t]>=2 for t in direct_topics))))
            special_subject=d['id']=='AI-N001-13' and qi['special_lifecycle_requested']
            original_content_anchor=bool(best[6] and best[4].get('unit_lane')!='PROJECT_POLICY'
                                         and (best[7] or best[5].get('relevance_lane')=='ORIGINAL_CONTENT'))
            strong=bool(exact or named_symbols or concept_anchor or original_content_anchor or (best[6] and (phrases or topic_anchor or len(primary_hits)>=2 or len(informative_focus)>=2)))
            dt.record(d['id'],'STRONG_TRIGGER',strong_task_trigger=strong)
            specific_topics=d['subject_topics']-CONTEXT_TOPICS
            requested_topics=qi['topics']-CONTEXT_TOPICS
            if not query.strip():
                if rstatus and rstatus!='reviewer_default' and projection=='reviewer':
                    dt.terminal(d['id'],'EMPTY_QUERY','EMPTY_QUERY_DEFAULT_NOT_ADMITTED')
                    continue
                if g and projection=='coding' and g.get('coding_status')!='coding_default':
                    dt.terminal(d['id'],'EMPTY_QUERY','EMPTY_QUERY_DEFAULT_NOT_ADMITTED')
                    continue
                score=1.;parts={'default_admission':1.}
            else:
                if rstatus=='task_conditional' and not strong:
                    dt.terminal(d['id'],'TASK_CONDITIONAL','TASK_CONDITIONAL_STRONG_TRIGGER_REQUIRED')
                    continue
                if not (exact or source_identity or lookup or best[6]):
                    raw_score=(sum(sorted((self.idf.get(t,0)*4. for t in fm),reverse=True)[:3])
                               +max((item[1] for item in unit_matches),default=0.)
                               +sum(sorted((self.idf.get(t,0)*1.3 for t in tm),reverse=True)[:2])
                               +8.*min(3,len(phrases))+1.2*len(topic_hits)+3.*len(focus_topics))
                    reason='below_absolute_relevance_floor' if (fm or bm or tm) and raw_score<ABSOLUTE_RELEVANCE_FLOOR else 'no_source_supported_task_unit'
                    dt.record(d['id'],'UNANCHORED_SCORE',unanchored_score=raw_score)
                    excluded.append({'id':d['id'],'reason':reason,'source_supported':False,'unanchored_score':round(raw_score,5)})
                    dt.terminal(d['id'],'SOURCE_SUPPORT',reason)
                    continue
                if not (fm or bm or tm or sym or exact or phrases or focus_topics or concept_anchor or original_content_anchor):
                    dt.terminal(d['id'],'OVERLAP','NO_LEXICAL_OR_SEMANTIC_OVERLAP')
                    continue
                # topic 只能桥接中英导航；不能单靠宽泛 topic 产生一张卡。
                if not (exact or sym or phrases or informative_focus or tm or topic_anchor or concept_anchor or original_content_anchor or len(primary_hits)>=2 or (len(best[3])>=2 and best[1]>=3.5)):
                    excluded.append({'id':d['id'],'reason':'insufficient_task_anchor'})
                    dt.terminal(d['id'],'TASK_ANCHOR','insufficient_task_anchor')
                    continue
                symbol_weights=self.lookup_weight if lookup else self.symbol_weight
                # Shared lifecycle callback names navigate many owners; natural
                # tasks rank their supported relation instead of that bare name.
                scoring_symbols=(set(sym)-COMMON_METHODS) if natural_task else sym
                parts={'exact_identity':1000. if exact else 0.,'exact_symbol':sum(sorted((self.lookup_weight.get(s,20.) if s in qi['qualified_symbols'] else symbol_weights.get(s,self.lookup_weight.get(s,0.)) for s in scoring_symbols),reverse=True)[:3]),
                    'focus':navigation_focus,'body':best[1],
                    'task_trigger':sum(sorted((self.idf.get(t,0)*1.3 for t in tm),reverse=True)[:2]),'phrase':8.*min(3,len(phrases)),
                    'topic':1.2*len(topic_hits),'bilingual_focus_topic':3.*len(focus_topics),
                    'coherent_task_semantics':6.*min(3,len(best[5]['mechanism_hits'])) if concept_anchor else 0.,
                    'source_task_subject':4.*min(2,len(best[5]['subject_hits'])) if best[6] else 0.}
                references=set(qi.get('record_references',[])) & self.reference_ids
                if not exact and best[6] and references & d['record_reference_ids']:
                    parts['original_record_reference']=40. if d['id'].upper() in references else 18.
                parts['original_content_focus']=max(0.,best[7]-parts['focus'])
                score=sum(parts.values())
                dt.record(d['id'],'ABSOLUTE_FLOOR',rank_score=score,absolute_floor=ABSOLUTE_RELEVANCE_FLOOR,
                    absolute_pass=score>=ABSOLUTE_RELEVANCE_FLOOR,score_components=parts)
                if score<ABSOLUTE_RELEVANCE_FLOOR:
                    excluded.append({'id':d['id'],'reason':'below_absolute_relevance_floor','score':round(score,5),'floor':ABSOLUTE_RELEVANCE_FLOOR})
                    dt.terminal(d['id'],'ABSOLUTE_FLOOR','below_absolute_relevance_floor')
                    continue
            preferences={'architect':{'pattern','decision','playbook'},'implement':{'source_fact','rule','native_ai_knowledge'},'review':{'rule','anti_pattern','failure_case','correction'},'debug':{'failure_case','source_fact','test_case','anti_pattern'},'research':{'source_fact','pattern','correction'},'kb_curator':{'correction','source_fact'}}
            entry_type=e.get('entry_type','native_core_knowledge' if d['family']=='core' else 'native_ai_knowledge' if d['family']=='n001' else '')
            if entry_type in preferences.get(task_mode,set()):
                score+=1.5;parts['task_role_preference']=1.5
            role_factor=.65 if task_mode=='implement' and entry_type in {'test_case','failure_case','pattern'} else .85 if task_mode in {'review','debug'} and entry_type=='pattern' else 1.
            if role_factor!=1.:
                score*=role_factor;parts['task_role_factor']=role_factor
            if e.get('entry_type')=='correction':score+=3.;parts['correction_priority']=3.
            dt.record(d['id'],'RANK_SCORE',rank_score=score,role_factor=role_factor,
                role_preference=parts.get('task_role_preference',0.),correction_priority=parts.get('correction_priority',0.),
                score_components=parts)
            requested_method=natural_task and any(requested_method_identity_match(query,item[4]['context'])
                                                  for item in supported_nonpolicy)
            rows.append({'document':d,'score':round(score,5),'requested_method_priority':requested_method,'match_reason':{'pipeline':VERSION,'family':d['family'],'exact_id':exact,'matched_symbols':sorted(sym),'matched_contract_navigation':sorted(set(sym)&d['contract_navigation']),'single_symbol_contract_identity':contract_identity,'matched_focus_terms':sorted(fm),'matched_atom_terms':sorted(best[3])[:16],'matched_task_concepts':sorted(coherent_concepts),'task_semantic_anchor':concept_anchor,'source_task_support':best[5],'source_atom_pointer':best[4].get('record_pointer',''),'source_supported_atom_pointers':list(dict.fromkeys(item[4]['record_pointer'] for item in supported_nonpolicy)),
                'matched_unit_lane':best[4].get('unit_lane','ORIGINAL_NONPOLICY_ATOM'),
                'source_supported_nonpolicy_pointers':list(dict.fromkeys(item[4]['record_pointer'] for item in supported_nonpolicy)),
                'source_supported_policy_pointers':list(dict.fromkeys(item[4]['record_pointer'] for item in supported_policy)),
                'project_policy_requested':policy_intent['requested'],
                **({'policy_request':policy_intent} if policy_intent['requested'] else {}),'policy_resolved':False,
                'source_supported_task_units':list(dict.fromkeys(task for item in supported_units
                    for task in item[5].get('supported_task_units',[item[5].get('task_unit','')]) if task)),
                'source_support_universe':'ORIGINAL_DELIVERABLE_ATOMS_AND_BOUNDARIES',
                'matched_semantic_unit':best[4]['text'][:360],'absolute_relevance_floor':ABSOLUTE_RELEVANCE_FLOOR,'task_phrases':phrases[:3],'topic_hits':sorted(topic_hits),'primary_subject_hits':sorted(d['primary_topics']&requested_topics),'direct_topic_anchor':topic_anchor,'score_components':{k:round(v,4) for k,v in parts.items()},'admission':{'projection':projection,'knowledge_status':g.get('knowledge_status'),'retrieval_status':rstatus,'coding_status':g.get('coding_status'),'strong_task_trigger':strong},'negative_intent_applied':qi['negative_clauses'],'review_guards_applied':qi['guard_clauses'],'generated_metadata_ranked':False}})
        rows.sort(key=lambda x:(-x['score'],x['document']['id']))
        if rows and query.strip() and not lookup:
            floor=max(ABSOLUTE_RELEVANCE_FLOOR,rows[0]['score']*RELATIVE_RELEVANCE_FRACTION)
            topic_tops={t:max(r['score'] for r in rows if t in r['match_reason']['primary_subject_hits']) for t in qi['topics']-CONTEXT_TOPICS if any(t in r['match_reason']['primary_subject_hits'] for r in rows)}
            requests=request_frames
            independent={request['text'] for request in requests
                         if request['explicit_question'] and not request['ambiguous_owner_reference']
                         and (task_subjects(request.get('effective_text',request['text'])) or request['inherited_subjects'] or request['request_paths'])}
            task_tops={task:max(row['score'] for row in rows
                              if task in row['match_reason']['source_supported_task_units'])
                       for task in independent if any(task in row['match_reason']['source_supported_task_units'] for row in rows)}
            for row in rows:
                row_floor=floor
                if len(qi['topics']-CONTEXT_TOPICS)>1 and row['match_reason']['primary_subject_hits'] and row['match_reason']['admission']['strong_task_trigger']:
                    per_subject=[max(ABSOLUTE_RELEVANCE_FLOOR,topic_tops[t]*RELATIVE_RELEVANCE_FRACTION) for t in row['match_reason']['primary_subject_hits']]
                    if per_subject:row_floor=min([floor]+per_subject)
                supported_tasks=set(row['match_reason']['source_supported_task_units'])&independent
                if len(independent)>1 and supported_tasks:
                    # 每个明确子问题独立沿用同一floor；不伪造跨记录依赖或取消绝对门槛。
                    row_floor=min([row_floor]+[max(ABSOLUTE_RELEVANCE_FLOOR,task_tops[task]*RELATIVE_RELEVANCE_FRACTION)
                                               for task in supported_tasks if task in task_tops])
                    row['match_reason']['independent_task_recall']={
                        'method':'ORIGINAL_SUPPORTED_SUBQUESTION_POOLS',
                        'supported_task_units':sorted(supported_tasks),
                        'cross_record_dependency_proven':False,
                        'absolute_floor_unchanged':ABSOLUTE_RELEVANCE_FLOOR,
                        'relative_fraction_unchanged':RELATIVE_RELEVANCE_FRACTION}
                row['match_reason']['query_relative_relevance_floor']=round(row_floor,5)
                dt.record(row['document']['id'],'RELATIVE_FLOOR',relative_floor=row['match_reason']['query_relative_relevance_floor'],
                    relative_pass=row['score']>=row['match_reason']['query_relative_relevance_floor'])
            removed=[r for r in rows if r['score']<r['match_reason']['query_relative_relevance_floor']]
            excluded.extend({'id':r['document']['id'],'reason':'below_query_relative_relevance_floor'} for r in removed)
            for row in removed:
                dt.terminal(row['document']['id'],'RELATIVE_FLOOR','below_query_relative_relevance_floor')
            rows=[r for r in rows if r['score']>=r['match_reason']['query_relative_relevance_floor']]
        # Only order already-admitted, above-floor original task units. A direct
        # named method subject outranks incidental overlap in another method's
        # lifecycle/caller body; this supplies no new admission or task support.
        rows.sort(key=lambda row:(not row['requested_method_priority'],-row['score'],row['document']['id']))
        for ordinal,row in enumerate(rows,1):
            dt.record(row['document']['id'],'SORTED_RANK',rank_position=ordinal,rank_score=row['score'])
        for ordinal,row in enumerate(rows):
            dt.record(row['document']['id'],'RANKER_SLICE',ranker_limit_status='RETURNED' if ordinal<limit else 'RANKER_LIMIT_SLICE')
            dt.terminal(row['document']['id'],'RANKER_RETURNED' if ordinal<limit else 'RANKER_SLICE',
                'RETURNED' if ordinal<limit else 'RANKER_LIMIT_SLICE')
        for row in rows[:limit]:
            matched=set(row['match_reason']['matched_symbols'])
            nav=[n for n in row['document']['source_symbol_navigation'] if n['symbol'].lower() in matched or n['symbol'].lower().rsplit(':',1)[-1].rsplit('.',1)[-1] in matched]
            row['match_reason']['exact_source_symbol_navigation']=nav[:3]
        return rows[:limit],{'candidate_matches':len(rows),'excluded':excluded,'query_intent':{**{k:sorted(v) if isinstance(v,set) else v for k,v in scope_intent.items()},'project_policy_requested':policy_intent['requested'],**({'policy_request':policy_intent} if policy_intent['requested'] else {})},'pipeline':VERSION,'knowledge_gap_meaning':'No admitted match in this bounded catalog, not proof the knowledge or API does not exist.'}
