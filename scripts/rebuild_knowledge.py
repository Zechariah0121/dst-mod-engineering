"""Offline author maintenance. Writes review candidates, never the active package."""
import argparse
import json
from pathlib import Path

if __package__:
    from .maintenance_support import rebuild
else:
    from maintenance_support import rebuild


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='Current public repository')
    parser.add_argument('--baseline', required=True, type=Path, help='Unmodified knowledge directory')
    parser.add_argument('--knowledge', required=True, type=Path, help='Edited author knowledge directory')
    parser.add_argument('--output', required=True, type=Path, help='New, absent review directory')
    parser.add_argument('--private-generators', type=Path, help='Historical work directory containing build_map_v24.py and build_source_identity.py')
    parser.add_argument('--stage-candidate', type=Path, help='New external readable package for a supported Core change')
    parser.add_argument('--reviewed-technical-decision', type=Path,
                        help='Explicit decision for a single reviewed Core NSF statement correction')
    parser.add_argument('--source', type=Path, help='Actual committed scripts ZIP for the technical decision')
    parser.add_argument('--repair-retired-private-identities', action='store_true',
                        help='Apply reviewed MAINT-IDENTITY-CLAIM16-01 removal, with exact backups and audit')
    args = parser.parse_args(argv)
    if args.reviewed_technical_decision or args.source:
        if not all((args.stage_candidate, args.reviewed_technical_decision, args.source)) or args.repair_retired_private_identities:
            parser.error('Technical staging requires --stage-candidate, --reviewed-technical-decision and --source separately from identity repair')
    print(json.dumps(rebuild(args.root, args.baseline, args.knowledge, args.output,
                             args.private_generators, args.stage_candidate,
                             args.repair_retired_private_identities, args.reviewed_technical_decision,
                             args.source), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
