"""Bounded stdio MCP adapter (legacy initialize protocol family). No listening port."""
import json
import sys
from . import __version__
from .config import KBError
from .service import Service,MODE_TYPES,FILTERS
from .native_mechanism import IDENTITY_KINDS
from .source_epoch_runtime import resolve_epoch, bind_epoch

STR={'type':'string'}
ARRAY={'type':'array','items':STR}
INT={'type':'integer'}
PROJECTION={'type':'string','enum':['coding','reviewer'],'default':'coding'}
REVIEWER_PROJECTION=PROJECTION|{'default':'reviewer'}
VIEW={'type':'string','enum':['decision','reviewer','evidence']}
DECISION_VIEW=VIEW|{'default':'decision'}
SEARCH_FILTERS=tuple(dict.fromkeys((*FILTERS,'families','tracks','claim_types')))
def tool(name,description,properties,required=()):
    return {'name':name,'description':description,'inputSchema':{'type':'object','properties':properties,
        'required':list(required),'additionalProperties':False},
        'annotations':{'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':False}}

TOOLS=[
 tool('search_kb','Search a unified, ranked pool of Legacy, N001 and Native Core candidates for DST engineering. Deliver only whole original atoms admitted for this task and its positive/negative scope. Named samples require their own bounded original evidence and task relation under a fixed source version; relevance of the containing record alone is insufficient. Use projection=reviewer and view=decision for existing-code review or Native API research, then expand only useful IDs. Ranking explains relevance; it does not grant Coding admission or prove evidence. projection controls admission independently from view. Coding hold/prohibited remain excluded in every mode and view. scope_logic=and intersects filter dimensions; or unions them. Not for gameplay advice.',
      {'query':STR,'top_k':INT,'mode':{'type':'string','enum':list(MODE_TYPES)},'projection':PROJECTION,'view':DECISION_VIEW,
       'scope_logic':{'type':'string','enum':['and','or'],'default':'and'}}|{k:ARRAY for k in SEARCH_FILTERS}),
 tool('lookup_api','Default family=legacy preserves the historical physical declaration lookup. Explicit family=native_mechanism requires projection=reviewer and returns whole research API atoms, Scope, unknowns and version locators under max_bytes. Research identity is authored, never a public/physical API guarantee; ambiguous owners, sources, visibility or evidence versions require explicit disambiguation. Bare leaf or exact qualified identities including require("module").field are supported; signatures and dynamic expressions are not. owner and identity_kind narrow only the research route. Navigate an exact declaration identity to mapped preserved typed claims; contract_delivery separates actual claim delivery, partial delivery and identity-only navigation. Use source_file to select the exact original scripts/...lua path when accepted physical declarations are ambiguous. Repeated records of one physical declaration do not create ambiguity. File-local declarations remain file-local. A catalog scope gap never establishes that the API is absent. Same-name methods of different owners do not substitute. Exact symbols alone are not method contracts. Defaults to projection=reviewer and compact view=decision; exact lookup is research navigation, not a Coding default or admission promotion. Inspect scope, corrections and current vanilla source; expand a selected ID only as needed.',
      {'symbol':STR,'top_k':INT,'projection':REVIEWER_PROJECTION,'view':DECISION_VIEW,
       'family':{'type':'string','enum':['legacy','native_mechanism'],'default':'legacy'},
       'owner':{'type':'string','maxLength':256},
       'identity_kind':{'type':'string','enum':list(IDENTITY_KINDS)},
       'max_bytes':{'type':'integer','minimum':1000,'maximum':64000,'default':24000},
       'source_file':{'type':'string','maxLength':512,
                      'description':'Optional exact original scripts/...lua path. Required when accepted same-name declarations belong to different sources; does not promote file-local declarations to public APIs.'}},['symbol']),
 tool('get_entry','Read one canonical knowledge ID. Omitting view preserves the legacy call shape; explicit view=decision is compact, reviewer adds research detail, evidence exposes evidence navigation. projection separately controls admission: selecting a view never bypasses Coding HOLD. For research use projection=reviewer, then resolve one exact evidence reference if necessary.',
      {'id':STR,'projection':PROJECTION,'view':VIEW,'pointer':{'type':'string','maxLength':2000},'max_bytes':{'type':'integer','minimum':1000,'maximum':64000}},['id']),
 tool('resolve_evidence','Resolve one evidence reference for one knowledge ID, optionally narrowed by a relative JSON subpointer. Defaults to Reviewer research navigation. Returns bounded referenced evidence only, with locator/hash and truncation metadata; never fetches an entire evidence corpus or changes Coding admission.',
      {'id':STR,'reference_index':{'type':'integer','minimum':0,'maximum':9999,'default':0},
       'projection':REVIEWER_PROJECTION,'subpointer':{'type':'string','maxLength':2000},
       'max_bytes':{'type':'integer','minimum':1000,'maximum':24000,'default':24000}},['id']),
 tool('get_related','Traverse typed relations with explicit edge direction. Source/Claim nodes may be returned. No assertion that a related node proves another.',
      {'id':STR,'relation_types':ARRAY,'depth':INT,'entry_types':ARRAY,'direction':{'type':'string','enum':['both','outgoing','incoming']},'limit':INT,'projection':PROJECTION},['id']),
 tool('get_klei_facts','Search only Klei source facts for DST engine/API behavior. Snapshot scoped; never substitute case observations for vanilla API evidence.',{'query':STR,'top_k':INT}),
 tool('get_tests','Find applicable DST test candidates by query or related entry IDs. Returned tests may be unexecuted; inspect their status.',{'query':STR,'entry_ids':ARRAY,'top_k':INT}),
 tool('get_context_bundle','Start a substantial DST engineering task with a bounded selection from the unified ranked pool. For existing-code review or Native API research choose projection=reviewer, view=decision and normally budget=normal. Pack complete original atoms with their necessary original Scope and evidence metadata under the unchanged total payload budget. Never cut a branch or rewrite a fact to fit; withheld atoms and unresolved Scope or evidence remain explicit gaps. Named samples are bounded references only when their own original evidence and task relation qualify. Inspect gaps and progressively expand selected IDs. metadata_ref and metadata_template resolve within that card shared_metadata table. mode changes task priorities, never admission. Coding keeps its existing admitted defaults and hold/prohibited exclusions.',
      {'task_description':STR,'mode':{'type':'string','enum':list(MODE_TYPES)},'budget':{'type':'string','enum':['compact','normal','deep']},'projection':PROJECTION,'view':DECISION_VIEW},['task_description']),
 tool('validate_kb','Maintenance/curator only: verify current KB schema, index, sources, relations and manifest. Do not run on every ordinary coding request.',{})]
for _tool in TOOLS:
    _tool['inputSchema']['properties']['source_epoch'] = {
        'type': 'string', 'maxLength': 160,
        'description': 'Frozen source environment from the configured catalog. Omit for its explicit default (release default: 759671). Use the same environment when expanding entries/evidence. Record source Scope remains authoritative; selecting an environment does not verify all records for that version.'}

INSTRUCTIONS=('Use this read-only DST engineering KB for mod coding/design/review/debug/research, not gameplay advice. '
 'A delivered unit is a whole original typed atom with its necessary semantic Scope and evidence metadata. Positive-only object limits and explicit exclusions apply to direct facts and every context expansion. '
 'The unchanged payload budget never authorizes cutting text or borrowing another atom evidence; withheld atoms, missing Scope and unresolved evidence must remain explicit gaps. '
 'A unique accepted physical declaration may select its own original sample identity and bounded behavior only with that original behavior evidence; identity alone never proves behavior or public API status. '
 'The release source_epoch is 759671. Only environments explicitly present in the configured catalog are accepted. '
 'Use the same source_epoch for search, lookup, bundle, get_entry and resolve_evidence. Environment identity is separate from each record source Scope and never promotes evidence or runtime status. '
 'Search and context bundles rank a unified pool of Legacy, N001 and Native Core candidates; inspect match explanations and scope. '
 'projection selects consumption role/admission; view independently selects response detail. Neither ranking, exact symbol/ID lookup, '
 'mode=review/research nor view=reviewer/evidence upgrades Coding admission. Coding hold/prohibited remain excluded. '
 'For existing-code review and Native API research explicitly choose projection=reviewer and compact view=decision. '
 'lookup_api defaults to Reviewer research navigation, not a Coding default. Expand progressively: compact search/bundle or lookup, '
 'get_entry for a selected ID with view=reviewer/evidence, then resolve_evidence for one exact reference and optional subpointer. '
 'Do not load an entire report or evidence corpus by default. Omitting get_entry view preserves its legacy call behavior. '
 'N001 get_entry with omitted view retains its unchanged 10-field payload and admitted default boundary; search/context use compact cards. CORE13 requires positive special-lifecycle intent; negative exclusions do not enable it. Read boundary polarity, receiver, sample identity and Project Policy before implementation. '
 'Native Core Gate A research acceptance is independent from Coding admission and runtime verification. '
 'Cite KB IDs, keep evidence distinct from confidence, '
 'respect corrections and scope. Test candidates are not runtime results. If unavailable, state KB unavailable and continue with current source evidence. '
 'Never modify canonical KB during ordinary tasks.')

def check_arguments(spec,args):
    if not isinstance(args,dict):raise KBError('INVALID_ARGUMENT','arguments must be an object')
    properties=spec['inputSchema']['properties']
    if set(args)-set(properties):raise KBError('INVALID_ARGUMENT','Unknown arguments')
    if set(spec['inputSchema']['required'])-set(args):raise KBError('INVALID_ARGUMENT','Missing required argument')
    for k,v in args.items():
        p=properties[k];t=p['type']
        if t=='string' and (not isinstance(v,str) or len(v)>p.get('maxLength',4000)):raise KBError('INVALID_ARGUMENT','Invalid string '+k)
        if t=='integer' and (type(v) is not int or not p.get('minimum',1)<=v<=p.get('maximum',100)):raise KBError('INVALID_ARGUMENT','Invalid integer '+k)
        if t=='array' and (not isinstance(v,list) or len(v)>100 or any(not isinstance(x,str) or len(x)>256 for x in v)):raise KBError('INVALID_ARGUMENT','Invalid array '+k)
        if 'enum' in p and v not in p['enum']:raise KBError('INVALID_ARGUMENT','Invalid enum '+k)
        if k=='subpointer' and v and not v.startswith('/'):raise KBError('INVALID_ARGUMENT','subpointer must be empty or an absolute JSON pointer')

class Server:
    tools=TOOLS
    instructions=INSTRUCTIONS
    def __init__(self,config=None):
        self.config=config;self.service=None;self.services={};self.initialized=False
    def call(self,name,args):
        spec=next((x for x in self.tools if x['name']==name),None)
        if spec is None:raise KBError('INVALID_TOOL','Unknown tool '+str(name))
        check_arguments(spec,args)
        arguments=dict(args)
        context=resolve_epoch(self.config,arguments.pop('source_epoch',None))
        key=context.cache_key if context is not None else 'legacy-unbound'
        if key not in self.services:
            if len(self.services)>=8:raise KBError('SOURCE_EPOCH_LIMIT','Too many distinct source environment revisions in this session; reconnect.')
            with bind_epoch(context):
                service=Service(self.config,epoch_context=context) if context is not None else Service(self.config)
            self.services[key]=service
            if self.service is None:self.service=service
        service=self.services[key]
        with bind_epoch(context):
            if context is not None:context.assert_current()
            result=getattr(service,name)(**arguments)
        # Preserve the established omitted-view get_entry payload, notably N001's exact ten fields.
        # Research lookup already charges the complete environment. Re-attaching
        # it after a budget withhold would exceed the caller's byte limit.
        if context is not None and isinstance(result,dict) and not (
                name=='get_entry' and 'view' not in arguments or
                name=='lookup_api' and arguments.get('family')=='native_mechanism'):
            result={**result,'source_environment':context.metadata()}
        return result
    def handle(self,msg):
        if not isinstance(msg,dict) or msg.get('jsonrpc')!='2.0' or not isinstance(msg.get('method'),str):
            return {'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Invalid request'}}
        id=msg.get('id');method=msg['method'];params=msg.get('params',{})
        if 'id' not in msg:return None
        base={'jsonrpc':'2.0','id':id}
        if not isinstance(params,dict):return base|{'error':{'code':-32602,'message':'params must be an object'}}
        if method=='initialize':
            self.initialized=True
            requested=params.get('protocolVersion')
            version=requested if requested in ['2024-11-05','2025-03-26','2025-06-18','2025-11-25'] else '2025-06-18'
            return base|{'result':{'protocolVersion':version,'capabilities':{'tools':{'listChanged':False}},
                'serverInfo':{'name':'dst-kb','version':__version__},'instructions':self.instructions}}
        if method=='ping':return base|{'result':{}}
        if method not in ['tools/list','tools/call']:return base|{'error':{'code':-32601,'message':'Method not found; this server uses initialize negotiation'}}
        if not self.initialized:return base|{'error':{'code':-32000,'message':'Initialize first'}}
        if method=='tools/list':return base|{'result':{'tools':self.tools}}
        try:
            result=self.call(params.get('name'),params.get('arguments',{}))
            return base|{'result':{'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}],'structuredContent':result,'isError':False}}
        except KBError as exc:
            data={'error':{'code':exc.code,'message':str(exc)},'kb_available':False if exc.code not in ['INVALID_ARGUMENT','INVALID_ID','INVALID_TOOL'] else True,
                'guidance':'Do not claim successful KB retrieval. Continue task using current code evidence when KB is unavailable.'}
        except Exception as exc:
            print('DST KB error: '+type(exc).__name__+': '+str(exc),file=sys.stderr)
            data={'error':{'code':'SERVICE_ERROR','message':'KB operation failed; inspect local service log.'},'kb_available':False}
        return base|{'result':{'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}],'structuredContent':data,'isError':True}}
    def close(self):
        for service in self.services.values():service.close()
        self.services.clear();self.service=None

def serve(config=None):
    server=Server(config)
    try:
        while True:
            line=sys.stdin.buffer.readline(1024*1024+1)
            if not line:break
            if len(line)>1024*1024:break
            try:result=server.handle(json.loads(line))
            except (ValueError,UnicodeError):result={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid JSON'}}
            if result is not None:
                sys.stdout.buffer.write((json.dumps(result,ensure_ascii=False)+'\n').encode('utf-8'));sys.stdout.buffer.flush()
    finally:server.close()
