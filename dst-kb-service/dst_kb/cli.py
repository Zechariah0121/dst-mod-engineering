import argparse
import json
from .config import KBError,settings
from .service import Service
from .validation import validate
from .mcp_server import serve

def main():
    parser=argparse.ArgumentParser(description='Read-only DST KB service; derived index only.')
    parser.add_argument('--config');parser.add_argument('command',choices=['serve','status','reindex','validate','call'])
    parser.add_argument('--tool');parser.add_argument('--arguments',default='{}')
    args=parser.parse_args();service=None
    try:
        if args.command=='serve':serve(args.config);return
        if args.command=='validate':result=validate(settings(args.config)[0])[1]
        elif args.command=='call':
            from .mcp_server import Server
            server=Server(args.config)
            try:result=server.call(args.tool,json.loads(args.arguments))
            finally:server.close()
        else:
            service=Service(args.config)
            result=service.reindex() if args.command=='reindex' else service.status()
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (KBError,OSError,ValueError) as exc:
        print(json.dumps({'error':{'code':getattr(exc,'code','CONFIG_ERROR'),'message':str(exc)}},ensure_ascii=False))
        raise SystemExit(1)
    finally:
        if service:service.close()
