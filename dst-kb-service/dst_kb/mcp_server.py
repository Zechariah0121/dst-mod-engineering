"""Bounded stdio MCP adapter (legacy initialize protocol family). No listening port."""
import json
import sys
from .config import KBError
from .service import Service,MODE_TYPES,FILTERS

STR={'type':'string'}
ARRAY={'type':'array','items':STR}
INT={'type':'integer'}
def tool(name,description,properties,required=()):
    return {'name':name,'description':description,'inputSchema':{'type':'object','properties':properties,
        'required':list(required),'additionalProperties':False},
        'annotations':{'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':False}}

TOOLS=[
 tool('search_kb','Use for DST engineering knowledge search. Returns ranked summaries with evidence, scope and match reasons; not full text. Not for gameplay advice.',
      {'query':STR,'top_k':INT,'mode':{'type':'string','enum':list(MODE_TYPES)}}|{k:ARRAY for k in FILTERS}),
 tool('get_entry','Read a canonical knowledge ID in full, with source registry and correction warnings. Read scope before important engineering decisions.',{'id':STR},['id']),
 tool('get_related','Traverse typed relations with explicit edge direction. Source/Claim nodes may be returned. No assertion that a related node proves another.',
      {'id':STR,'relation_types':ARRAY,'depth':INT,'entry_types':ARRAY,'direction':{'type':'string','enum':['both','outgoing','incoming']},'limit':INT},['id']),
 tool('get_klei_facts','Search only Klei source facts for DST engine/API behavior. Snapshot scoped; never substitute case observations for vanilla API evidence.',{'query':STR,'top_k':INT}),
 tool('get_tests','Find applicable DST test candidates by query or related entry IDs. Returned tests may be unexecuted; inspect their status.',{'query':STR,'entry_ids':ARRAY,'top_k':INT}),
 tool('get_context_bundle','Use at start of a substantial DST architecture, coding, review, debug or research task. Returns a bounded relevant bundle, not the whole KB. Not for game strategy or lore.',
      {'task_description':STR,'mode':{'type':'string','enum':list(MODE_TYPES)},'budget':{'type':'string','enum':['compact','normal','deep']}},['task_description']),
 tool('validate_kb','Maintenance/curator only: verify current KB schema, index, sources, relations and manifest. Do not run on every ordinary coding request.',{})]
INSTRUCTIONS=('Use this read-only DST engineering KB for mod coding/design/review/debug/research, not gameplay advice. '
 'Start with a small search or context bundle; read full entries only as needed. Cite KB IDs, keep evidence distinct from confidence, '
 'respect corrections and scope. Test candidates are not runtime results. If unavailable, state KB unavailable and continue with current source evidence. '
 'Never modify canonical KB during ordinary tasks.')

def check_arguments(spec,args):
    if not isinstance(args,dict):raise KBError('INVALID_ARGUMENT','arguments must be an object')
    properties=spec['inputSchema']['properties']
    if set(args)-set(properties):raise KBError('INVALID_ARGUMENT','Unknown arguments')
    if set(spec['inputSchema']['required'])-set(args):raise KBError('INVALID_ARGUMENT','Missing required argument')
    for k,v in args.items():
        p=properties[k];t=p['type']
        if t=='string' and (not isinstance(v,str) or len(v)>4000):raise KBError('INVALID_ARGUMENT','Invalid string '+k)
        if t=='integer' and (type(v) is not int or not 1<=v<=100):raise KBError('INVALID_ARGUMENT','Invalid integer '+k)
        if t=='array' and (not isinstance(v,list) or len(v)>100 or any(not isinstance(x,str) or len(x)>256 for x in v)):raise KBError('INVALID_ARGUMENT','Invalid array '+k)
        if 'enum' in p and v not in p['enum']:raise KBError('INVALID_ARGUMENT','Invalid enum '+k)

class Server:
    def __init__(self,config=None):self.config=config;self.service=None;self.initialized=False
    def call(self,name,args):
        spec=next((x for x in TOOLS if x['name']==name),None)
        if spec is None:raise KBError('INVALID_TOOL','Unknown tool '+str(name))
        check_arguments(spec,args)
        if self.service is None:self.service=Service(self.config)
        return getattr(self.service,name)(**args)
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
                'serverInfo':{'name':'dst-kb','version':'0.1.0'},'instructions':INSTRUCTIONS}}
        if method=='ping':return base|{'result':{}}
        if method not in ['tools/list','tools/call']:return base|{'error':{'code':-32601,'message':'Method not found; this server uses initialize negotiation'}}
        if not self.initialized:return base|{'error':{'code':-32000,'message':'Initialize first'}}
        if method=='tools/list':return base|{'result':{'tools':TOOLS}}
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
        if self.service:self.service.close()

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
