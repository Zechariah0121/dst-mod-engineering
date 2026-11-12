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
 tool('search_kb','Search ranked DST engineering knowledge across registered families. For code review or native API research use projection=reviewer, view=decision, then expand useful IDs. Results retain whole original atoms, Scope and evidence. scope_logic=and intersects filter dimensions; or unions them.',
      {'query':STR,'top_k':INT,'mode':{'type':'string','enum':list(MODE_TYPES)},'projection':PROJECTION,'view':DECISION_VIEW,
       'scope_logic':{'type':'string','enum':['and','or'],'default':'and'}}|{k:ARRAY for k in SEARCH_FILTERS}),
 tool('lookup_api','Look up an exact API identity. Explicit family=all with projection=reviewer navigates all four families and returns executable complete-object review calls, preserving source ambiguity and evidence limits. Default family=legacy finds preserved physical declarations and mapped claims; contract_delivery reports whether behavior claims were delivered. Explicit family=native_mechanism requires projection=reviewer and returns complete research API atoms under max_bytes. Use source_file to disambiguate sources; owner and identity_kind narrow native_mechanism only. Bare names and qualified identities such as require("module").field are supported; signatures and dynamic expressions are not. File-local functions retain their visibility. A declaration or catalog gap alone does not establish a method contract, public API or absence. Defaults to reviewer projection and compact decision view.',
      {'symbol':STR,'top_k':INT,'projection':REVIEWER_PROJECTION,'view':DECISION_VIEW,
       'family':{'type':'string','enum':['legacy','native_mechanism','all'],'default':'legacy'},
       'owner':{'type':'string','maxLength':256},
       'identity_kind':{'type':'string','enum':list(IDENTITY_KINDS)},
       'max_bytes':{'type':'integer','minimum':1000,'maximum':64000,'default':24000},
       'source_file':{'type':'string','maxLength':512,
                      'description':'Exact original scripts/...lua path; use it to disambiguate same-name declarations in different files.'}},['symbol']),
 tool('get_entry','Read a selected knowledge ID. Explicit purpose=review with projection=reviewer reads complete original objects across all four families under max_bytes. Follow continuation.arguments unchanged for content-bound paging, or select a record-relative pointer. Typed owner atoms and required Scope remain whole. view=decision is compact; reviewer adds detail; evidence adds source navigation. Omitting view preserves the legacy response. projection controls admission independently. For mechanism research, pointer selects a whole typed atom and max_bytes bounds delivery.',
      {'id':STR,'projection':PROJECTION,'view':VIEW,'purpose':{'type':'string','enum':['review']},
       'cursor':{'type':'string','maxLength':2000},'pointer':{'type':'string','maxLength':2000},'max_bytes':{'type':'integer','minimum':1000,'maximum':64000}},['id']),
 tool('resolve_evidence','Read one evidence reference for a knowledge ID, optionally narrowed by a relative JSON subpointer. Defaults to Reviewer navigation. Returns the selected evidence with its locator, hash and delivery metadata under max_bytes.',
      {'id':STR,'reference_index':{'type':'integer','minimum':0,'maximum':9999,'default':0},
       'projection':REVIEWER_PROJECTION,'subpointer':{'type':'string','maxLength':2000},
       'max_bytes':{'type':'integer','minimum':1000,'maximum':24000,'default':24000}},['id']),
 tool('get_related','Traverse typed relations in the chosen direction. Related Source or Claim nodes are navigation leads; inspect their evidence and Scope.',
      {'id':STR,'relation_types':ARRAY,'depth':INT,'entry_types':ARRAY,'direction':{'type':'string','enum':['both','outgoing','incoming']},'limit':INT,'projection':PROJECTION},['id']),
 tool('get_klei_facts','Search Klei source facts for DST engine and API behavior within their recorded source version.',{'query':STR,'top_k':INT}),
 tool('get_tests','Find relevant test candidates by query or knowledge IDs. Inspect execution status before treating a candidate as a result.',{'query':STR,'entry_ids':ARRAY,'top_k':INT}),
 tool('get_context_bundle','Select knowledge for a substantial DST engineering task. For code review or native API research use projection=reviewer, view=decision and normally budget=normal. Packs whole original atoms with required Scope and evidence within the total budget; inspect gaps and expand selected IDs. metadata_ref and metadata_template resolve in the card shared_metadata table. mode changes task priorities; projection controls admission.',
      {'task_description':STR,'mode':{'type':'string','enum':list(MODE_TYPES)},'budget':{'type':'string','enum':['compact','normal','deep']},'projection':PROJECTION,'view':DECISION_VIEW},['task_description']),
 tool('validate_kb','Maintenance check for KB schema, index, source commitments, relations and manifest. Run when maintaining the package rather than before ordinary queries.',{})]
for _tool in TOOLS:
    _tool['inputSchema']['properties']['source_epoch'] = {
        'type': 'string', 'maxLength': 160,
        'description': 'Configured service environment; omit for default 759671. Reuse when expanding results. Each record retains its own source Scope.'}

INSTRUCTIONS=('This read-only DST engineering KB supports mod coding, design, review, debugging and research. For code review or native API research use projection=reviewer and view=decision. projection controls admission; view controls detail. Coding hold/prohibited records remain excluded in every mode. Search or look up first, expand selected IDs with get_entry, then resolve one evidence reference as needed. Use get_context_bundle for task-sized selections. Consume whole original typed atoms with their required Scope and evidence. Positive object limits, explicit exclusions, receiver/sample identity, corrections and Project Policy apply to every expansion. Over-budget or unsupported content remains an explicit gap. Ranking and a unique API declaration indicate navigation relevance, not behavior evidence or public visibility. Explicit whole-object review uses get_entry purpose=review, projection=reviewer. Cross-family exact API review uses lookup_api family=all and supplied followup calls. Existing native mechanism API research also supports family=native_mechanism. source_epoch selects a configured service environment (default 759671); reuse it across calls and distinguish it from each record evidence version. Omitted get_entry view preserves the legacy shape, including N001 ten fields. CORE13 requires positive special-lifecycle intent. Read test execution status separately from recommendations; source checks and research acceptance do not establish game execution. Cite KB IDs and task-relevant limits. If the KB is unavailable, say so and continue with current source evidence. Knowledge remains read-only during ordinary tasks.')

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
                name=='get_entry' and ('view' not in arguments or arguments.get('purpose')=='review') or
                name=='lookup_api' and arguments.get('family') in ('native_mechanism','all')):
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
