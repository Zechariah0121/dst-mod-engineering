"""Proposed auto fallback: source-preparation availability is separate from data integrity.

Integration preserves strict full mode and never reads a damaged prepared cache.
The release/public manifest is a local trust root, not a cryptographic signature.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat


def verify_public_files(root):
    root = (Path(root) / "knowledge").resolve()
    manifest = json.loads((root / "PACKAGE-MANIFEST.json").read_text(encoding="utf-8-sig"))
    if manifest.get("schema_version") != "dst-public-package-manifest/1":
        raise ValueError("Unsupported public manifest")
    seen = set()
    for row in manifest["files"]:
        name = row["path"]
        relative = PurePosixPath(name)
        if (not name or ":" in name or "\\" in name or relative.is_absolute()
                or any(p in ("", ".", "..") for p in name.split("/")) or name in seen):
            raise ValueError("Unsafe or duplicate public manifest path")
        seen.add(name)
        target = root / name
        if not target.resolve().is_relative_to(root):
            raise ValueError("Public path escaped root")
        for path in (target, *target.parents):
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise ValueError("Linked public input")
            if path == root:
                break
        raw = target.read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Public manifest mismatch: " + name)
    if "CATALOG.json" not in seen:
        raise ValueError("Public manifest lacks catalog")


def catalog_fallback(mode, code, root):
    """Only missing preparation/package drift are availability causes.

    Invalid activation, damaged cache, invalid path, malformed public data and
    generic exceptions remain errors. Current PublicCatalog validates IDs,
    pointers and artifact references after this complete public file check.
    """
    if mode != "auto" or code not in ("SOURCES_NOT_PREPARED", "PACKAGE_CHANGED"):
        return None
    if code == "SOURCES_NOT_PREPARED" and (Path(root) / "cache/runtime/retrieval-config.json").exists():
        return None
    verify_public_files(root)
    return {"reason_code": code, "active_mode": "public_catalog", "full_service_available": False,
            "public_manifest_verified": True, "source_evidence_restored": False,
            "coding_hold_changed": False, "runtime_verified": False,
            "recovery": "Keep baseline runtime; assess explicit target ZIP separately; reprepare when original evidence can be restored."}
