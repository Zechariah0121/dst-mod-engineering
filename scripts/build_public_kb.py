"""Build a portable, redacted publication copy of a frozen DST knowledge base.

The source is read only. Windows paths are converted to *logical* evidence
locators; those locators do not claim to be the original filesystem paths.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path


EXCLUDED = {
    "PACKAGE-MANIFEST.json",
    "tools/seed_case001.py",
    "tools/migrate_v011.py",
    "tools/package_review.py",
    "tools/build_support_schemas.py",
}
WINDOWS_PATH = re.compile(r"(?i)(?<![a-z0-9])[a-z]:[/\\]")
REPORT_NOTE = "\n[Public release note: this is a redacted derivative of the frozen local report. Original bytes and local filesystem paths are withheld; evidence conclusions and source line numbering above are retained.]\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def jwrite(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def jread(path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_child(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path outside package: {relative}")
    return path


def replacements_from_registry(source, private_terms):
    registry = jread(source / "data/sources.json")
    sources = {entry["id"]: entry for entry in registry["sources"]}
    case_root = registry["case_snapshot"]["path"].rstrip("/\\")
    vanilla = next(entry for entry in registry["sources"] if entry["type"] == "vanilla_source_snapshot")
    vanilla_root = vanilla["source_root"].rstrip("/\\")
    zip_path = registry["vanilla_context"]["zip_path"]
    report = next(entry for entry in registry["sources"] if entry["type"] == "prior_analysis_report")
    report_root = report["original_path"].rsplit("/", 1)[0]
    mappings = {
        case_root: "case-study/CASE-001",
        vanilla_root: "vanilla-snapshot/scripts",
        zip_path: "vanilla-snapshot/scripts.zip",
        report_root + "/" + source.name: "local-frozen-kb",
        report_root: "analysis-report-location",
    }
    for term in private_terms:
        if not term or "/" in term or "\\" in term:
            raise ValueError("Private terms must be nonempty names, not paths")
        mappings[term] = "[private-name]"
    # Longest first keeps each specific source tree ahead of its parent.
    return registry, sources, sorted(mappings.items(), key=lambda row: -len(row[0]))


def redact_text(text, mappings):
    for before, after in mappings:
        text = text.replace(before, after)
        text = text.replace(before.replace("/", "\\"), after)
    return text


def assert_clean(root, private_terms):
    for path in root.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if WINDOWS_PATH.search(path.relative_to(root).as_posix()):
            raise ValueError(f"Windows path in published filename: {path.name}")
        text = path.read_text(encoding="utf-8")
        if WINDOWS_PATH.search(text):
            raise ValueError(f"Windows absolute path remains in {path.relative_to(root)}")
        for term in private_terms:
            if term.casefold() in text.casefold():
                raise ValueError(f"Private term remains in {path.relative_to(root)}")


def verify_generated_output(output):
    manifest_path = output / "PACKAGE-MANIFEST.json"
    marker_path = output / "PUBLICATION-PROVENANCE.json"
    if not manifest_path.is_file() or not marker_path.is_file():
        raise ValueError("Existing output is not a complete generated package")
    manifest = jread(manifest_path)
    expected = {entry["path"] for entry in manifest["files"]}
    actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() and p != manifest_path}
    if actual != expected:
        raise ValueError("Existing output has added or missing files; use a new output directory")
    for entry in manifest["files"]:
        data = safe_child(output, entry["path"]).read_bytes()
        if digest(data) != entry["sha256"] or len(data) != entry["bytes"]:
            raise ValueError("Existing output was modified; use a new output directory")


def build(source, output, private_terms, replace_generated=False):
    source = source.resolve()
    output = output.resolve()
    if source == output or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError("Source and output must be separate trees")
    if not (source / "data/entries.json").is_file():
        raise ValueError("--source is not a knowledge base")
    registry, original_sources, mappings = replacements_from_registry(source, private_terms)
    source_files = {p.relative_to(source).as_posix(): p for p in source.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    if output.exists() and any(output.iterdir()):
        if not replace_generated:
            raise ValueError("Output is not empty; pass --replace-generated after reviewing it, or use a new directory")
        verify_generated_output(output)
    output.mkdir(parents=True, exist_ok=True)
    published_files = set()
    original_hashes = {}
    for relative, path in sorted(source_files.items()):
        if relative in EXCLUDED:
            continue
        raw = path.read_bytes()
        original_hashes[relative] = {"sha256": digest(raw), "bytes": len(raw)}
        text = raw.decode("utf-8-sig")
        text = redact_text(text, mappings)
        if relative.startswith("review-support/reports/"):
            text = text.rstrip("\r\n") + REPORT_NOTE
        target = safe_child(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Decode and normalize line endings once. Appending a report notice at
        # its end must not shift any pre-existing evidence line number.
        target.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))
        published_files.add(relative)

    public_registry = jread(output / "data/sources.json")
    for entry in public_registry["sources"]:
        entry["original_path"] = None
        entry["path"] = None
        entry["logical_locator"] = "source-id:" + entry["id"]
        if entry.get("available_in_package"):
            artifact = safe_child(output, entry["artifact_path"])
            data = artifact.read_bytes()
            entry["sha256"], entry["bytes"] = digest(data), len(data)
            if entry["type"] == "prior_analysis_report":
                entry["publication_status"] = "redacted_derivative_not_byte_identical"
        if entry["type"] == "vanilla_source_snapshot":
            entry["source_root"] = "logical:vanilla-snapshot/scripts"
            entry["provenance"]["zip_original_path"] = None
            entry["provenance"]["extracted_source_root"] = None
            for fingerprint in entry["verification"]["file_fingerprints"]:
                fingerprint["path"] = "logical:" + fingerprint["path"]
    public_registry["vanilla_context"]["zip_path"] = None
    for fingerprint in public_registry["vanilla_context"]["current_fingerprint_only"]:
        fingerprint["path"] = "logical:" + fingerprint["path"]
    public_registry["case_snapshot"]["path"] = None
    jwrite(output / "data/sources.json", public_registry)
    jwrite(output / "review-support/source-map.json", {
        "schema_version": public_registry["schema_version"],
        "sources": [{k: entry.get(k) for k in ("id", "original_path", "artifact_path", "available_in_package")}
                    for entry in public_registry["sources"]],
    })

    # The frozen validation results are historical records. Their external
    # fingerprint checks were local; this public copy cannot repeat them.
    for relative in ("data/validation.json", "history/v0.1/data/validation.json"):
        path = output / relative
        result = jread(path)
        result["publication_note"] = "Historical local validation snapshot, redacted for publication; external checks are not reproducible from this package."
        jwrite(path, result)

    readme = output / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("第 4–6 轮原报告，按字节原样保存。", "第 4–6 轮报告的公开脱敏派生副本；原始报告仍仅在本机冻结版保存。")
    text = text.replace("原始 provenance 与包内文件映射。", "公开来源 ID 与包内文件映射。")
    text = re.sub(r"可选 `--check-external`[^。]*。", "公开副本不支持 `--check-external`；外部源码不随包。", text)
    text = text.replace("`data/validation.json` 是封包前检查快照；最终 Manifest 与搬迁验证结果另随 ZIP 提供", "`data/validation.json` 是冻结版封包前的历史检查快照；公开版 Manifest 可在本目录重新验证")
    text = re.sub(r"seed_case001\.py 是历史初次抽取工具，migrate_v011\.py 是仅接收 v0\.1 的一次性迁移工具，不应作为日常更新入口。", "公开副本不包含一次性抽取和迁移工具。", text)
    text += "\n## 公开派生版说明\n\n本目录由本机冻结版经路径与私人标识脱敏导出；冻结版原样保留。64 条知识的 ID、证据等级、置信度、Correction 关系与技术结论没有重新修订。报告和历史记录为脱敏派生副本，不能声称与冻结版逐字节相同。`PUBLICATION-PROVENANCE.json` 仅用知识库相对路径记录原始与公开文件哈希，不公开本机路径。`logical:`、`case-study/`、`vanilla-snapshot/` 和 `analysis-report-location/` 均为发布用逻辑定位符，不代表实际文件系统路径。\n"
    readme.write_text(text, encoding="utf-8", newline="\n")

    validation_doc = output / "VALIDATION.md"
    text = validation_doc.read_text(encoding="utf-8")
    text = re.sub(r"封包前通过 `--write-report --check-external`[^\n]*", "本公开副本只运行包内校验：`python -B tools/validate.py`。外部源码与原始报告均未随包，`--check-external` 不适用。冻结版历史校验结果保留为已脱敏的历史记录。", text)
    validation_doc.write_text(text, encoding="utf-8", newline="\n")

    for relative in ("KB-v0.1.1-Migration-Report.md", "KB-v0.1.1-Migration-Report.txt"):
        path = output / relative
        text = path.read_text(encoding="utf-8")
        text = text.replace("原样放入", "在冻结版原样放入；公开版提供脱敏派生副本于")
        text = text.replace("按原字节复制", "在冻结版按原字节复制；公开版为脱敏派生副本")
        text = text.replace("原路径与包内路径并存", "公开版仅保留包内路径和逻辑来源 ID")
        text += "\n[公开发布注：以上迁移结论记录冻结版本地历史。此公开副本已经脱敏，报告与历史文件不再与冻结版逐字节相同；没有重新修订知识结论。]\n"
        path.write_text(text, encoding="utf-8", newline="\n")

    lines = ["# Source Registry v0.1.1 (public derivative)", "", "外部源码不随包；original_path 已隐藏。报告是脱敏派生副本，原始与公开哈希见 [PUBLICATION-PROVENANCE.json](PUBLICATION-PROVENANCE.json)。", ""]
    for entry in public_registry["sources"]:
        lines += ["## " + entry["id"], "", "Type: " + entry["type"], "", entry["description"], "", "original_path: withheld; logical_locator: `" + entry["logical_locator"] + "`", ""]
        artifact = entry.get("artifact_path")
        lines += ["artifact_path: [" + artifact + "](<" + artifact + ">)" if artifact else "artifact_path: null; available_in_package: false", ""]
    (output / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    # Disable a validation mode whose local original paths are intentionally
    # absent. Default package validation remains unchanged.
    validator = output / "tools/validate_v011.py"
    text = validator.read_text(encoding="utf-8")
    text = text.replace("可移植验证：默认不访问任何original_path；--check-external只做可选指纹对照。", "公开派生版验证：仅校验包内材料；外部原路径指纹不可复核。")
    needle = "    if external:\n        ext_status='PASS'"
    if needle not in text:
        raise ValueError("Unsupported validator version: external check block changed")
    text = text.replace(needle, "    if external:\n        raise ValueError('External fingerprint checks require the private frozen source package')\n        ext_status='PASS'", 1)
    validator.write_text(text, encoding="utf-8", newline="\n")

    # Publication provenance is intentionally path-free: only relative KB
    # filenames, source IDs, byte counts, and hashes are retained.
    provenance = {"schema_version": "1", "kind": "public_redacted_derivative",
                  "local_frozen_source_modified": False,
                  "reports_byte_identical_to_frozen": False,
                  "knowledge_revision": False,
                  "files": [], "source_artifacts": []}
    for relative, before in sorted(original_hashes.items()):
        data = (output / relative).read_bytes()
        provenance["files"].append({"path": relative, "frozen_sha256": before["sha256"],
                                    "frozen_bytes": before["bytes"], "public_sha256": digest(data), "public_bytes": len(data)})
    for entry in public_registry["sources"]:
        original = original_sources[entry["id"]]
        provenance["source_artifacts"].append({"source_id": entry["id"], "artifact_path": entry.get("artifact_path"),
            "frozen_sha256": original.get("sha256"), "public_sha256": entry.get("sha256")})
    jwrite(output / "PUBLICATION-PROVENANCE.json", provenance)
    published_files.add("PUBLICATION-PROVENANCE.json")

    if replace_generated:
        prior = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
        stale = prior - published_files - {"PACKAGE-MANIFEST.json"}
        if stale:
            raise ValueError("Generated file set changed; use a new output directory: " + ", ".join(sorted(stale)))
    manifest = {"schema_version": public_registry["schema_version"],
                "excludes": ["PACKAGE-MANIFEST.json", "**/__pycache__/**"], "files": []}
    for relative in sorted(published_files):
        data = (output / relative).read_bytes()
        manifest["files"].append({"path": relative, "artifact_path": relative, "original_path": None,
                                  "bytes": len(data), "sha256": digest(data)})
    jwrite(output / "PACKAGE-MANIFEST.json", manifest)
    assert_clean(output, private_terms)
    return len(published_files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="read-only frozen KB root")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "dst-engineering-kb")
    parser.add_argument("--private-term", action="append", default=[], help="additional private name to redact; repeat as needed")
    parser.add_argument("--replace-generated", action="store_true", help="replace only an intact generated package")
    args = parser.parse_args()
    count = build(args.source, args.output, args.private_term, args.replace_generated)
    print(f"Published {count} files to {args.output}")


if __name__ == "__main__":
    main()
