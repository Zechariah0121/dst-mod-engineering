# DST Mod Engineering

An engineering Skill and knowledge base for Don't Starve Together mod development: retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文 README](README.md)

The current KB is in `knowledge/`: **187 records comprising 64 foundation records, 13 Native AI records and 110 Native Core records**. One complete distribution includes the Skill, public knowledge data, development helpers, source preparation and MCP. Scope, claim types, versions, corrections and Coding HOLD remain binding; record availability does not grant Coding admission.

## Download

Release: [v2026.10.25.2](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.2). Download the single complete package for Skill installation, file reading or MCP.

| File | Contents |
|---|---|
| [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.2/dst-mod-engineering.zip) | Complete Skill, 187 public records in one `knowledge/` tree, development helpers, local source preparation and the nine-tool MCP service |

Check downloads against the release's `SHA256SUMS.txt`. No game Lua source, third-party executables or private mod projects are bundled. Most detailed references are in Chinese.

This release installs the Skill, 187 records and MCP together. Targeted integration checks cover source preparation, nine-tool connection, data integrity, natural-language retrieval and evidence reading. It fixes missed mixed-language task-cleanup/callback-order queries and explicit method exclusions. Retrieval does not cover every possible phrasing; use the unified catalog to inspect selected records when needed. An empty result does not establish a knowledge gap. See [capabilities and limits](docs/public-limits.md).

## Start

Extract the package completely and install the directory containing `SKILL.md` in a supported agent skill location. Invoke `dst-mod-engineering` with your task, mod directory, actual game version and authorized local source. Without MCP, read a small relevant subset from the knowledge files. See [installation](docs/install-and-use.md) and [KB integration](docs/knowledge-integration.md).

For MCP, run from the package root with Python 3.10+ and SQLite FTS5:

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>" --source "<authorized retained 756039 scripts.zip or source directory>"
python -B -X utf8 run_kb.py mcp-config
```

Some current records depend on historical source ranges. Preparation reports the actual missing ranges; current source must not replace older evidence. Without those sources, file reading remains available, but the complete MCP runtime is not ready. Apply the printed configuration in your client; its server command is `python -B -X utf8 run_kb.py serve`. Printed configuration does not prove a successful connection or query.

Prepared `cache/runtime/` contains locally restored game source excerpts and must stay local. A `$dst_source_payload_slot` in public JSON is a missing local-source slot, not source already read or behavioral evidence. Public evidence consists of reviewed excerpts, not complete original research; withheld private context remains `UNK`.

Use [SKILL.md](SKILL.md) for topic routing, [retrieval rules](references/kb-retrieval.md) for Scope and admission, and [testing](references/testing-release.md) for validation. Real game, remote-client, visual, audio and cross-version behavior need separate evidence; see [limits](docs/public-limits.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission. Valid historical MIT grants and third-party terms remain in force; see [licensing](docs/licensing.md).
