# DST Mod Engineering

An engineering Skill and knowledge base for Don't Starve Together mod development: retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文 README](README.md)

The current KB is in `knowledge/`: **187 records comprising 64 foundation records, 13 Native AI records and 110 Native Core records**. One complete distribution includes the Skill, public knowledge data, development helpers, source preparation and MCP. Scope, claim types, versions, corrections and Coding HOLD remain binding; record availability does not grant Coding admission.

## Download

Release: [v2026.10.25.4](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.4). Download the single complete package for Skill installation, file reading or MCP.

| File | Contents |
|---|---|
| [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.4/dst-mod-engineering.zip) | Complete Skill, 187 public records in one `knowledge/` tree, development helpers, local source preparation and MCP |

Check downloads against the release's `SHA256SUMS.txt`. No game Lua source, third-party executables or private mod projects are bundled. Most detailed references are in Chinese.

This release installs the Skill, 187 records and MCP together. One authorized `scripts.zip` matching the currently supported snapshot `759671` prepares the full nine-tool service; older source is not required. Historical comparisons retain their original versions and references as metadata, not restored current-source evidence. Core Coding HOLD remains binding. Retrieval does not cover every possible phrasing; use the unified catalog to inspect selected records when needed. An empty result does not establish a knowledge gap. See [capabilities and limits](docs/public-limits.md).

## Start

Extract the package completely and install the directory containing `SKILL.md` in a supported agent skill location. Invoke `dst-mod-engineering` with your task, mod directory, actual game version and authorized local source. Without MCP, read a small relevant subset from the knowledge files. See [installation](docs/install-and-use.md) and [KB integration](docs/knowledge-integration.md).

For full MCP, run from the package root with Python 3.10+ and SQLite FTS5:

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

Apply the printed configuration in your client and verify nine tools plus a real query. If a catalog session is already connected, restart it after preparation to switch tools. Printed configuration does not prove a successful connection or query. See [installation](docs/install-and-use.md).

Default `--mode auto` uses full mode when preparation is valid, and two catalog tools only when sources are unprepared. Explicit `--mode catalog` supports public review without Coding context or restored source evidence. A damaged prepared cache or changed package version causes an error instead of a silent fallback. Snapshot `759671` support does not imply automatic compatibility with future DST versions.

Prepared `cache/runtime/` contains locally restored game source excerpts and must stay local. A `$dst_source_payload_slot` in public JSON is a missing local-source slot, not source already read or behavioral evidence. Public evidence consists of reviewed excerpts, not complete original research; withheld private context remains `UNK`.

Use [SKILL.md](SKILL.md) for topic routing, [retrieval rules](references/kb-retrieval.md) for Scope and admission, and [testing](references/testing-release.md) for validation. Real game, remote-client, visual, audio and cross-version behavior need separate evidence; see [limits](docs/public-limits.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission. Valid historical MIT grants and third-party terms remain in force; see [licensing](docs/licensing.md).
