# DST Mod Engineering

An engineering Skill and knowledge base for Don't Starve Together mod development: retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文 README](README.md)

The current KB is in `knowledge/`: **187 records comprising 64 foundation records, 13 Native AI records and 110 Native Core records**. All three downloads include the public knowledge data. Scope, claim types, versions, corrections and Coding HOLD remain binding; record availability does not grant Coding admission.

## Download

Release: [v2026.10.25.1](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.1). Start with the full package for local use.

| File | Contents |
|---|---|
| [dst-mod-engineering-full.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/dst-mod-engineering-full.zip) | Skill, 187 public records, development helpers, source preparation and the nine-tool MCP service `0.3.0` |
| [dst-mod-engineering.skill.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/dst-mod-engineering.skill.zip) | Installable Skill, references, 187 public records and three development helpers; no MCP service or source preparation tools |
| [web-reading.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/web-reading.zip) | Web/offline reading material and 187 public records; no MCP service or source preparation tools |

Check downloads against the release's `SHA256SUMS.txt`. No game Lua source, third-party executables or private mod projects are bundled. Most detailed references are in Chinese.

## Start

Extract the package completely and install the directory containing `SKILL.md` in a supported agent skill location. Invoke `dst-mod-engineering` with your task, mod directory, actual game version and authorized local source. Without MCP, read a small relevant subset from the knowledge files. See [installation](docs/install-and-use.md) and [KB integration](docs/knowledge-integration.md).

For MCP, run from the full package root with Python 3.10+ and SQLite FTS5:

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>" --source "<authorized retained 756039 scripts.zip or source directory>"
python -B -X utf8 run_kb.py mcp-config
```

The current `759671` ZIP alone still lacks 13 historical ranges across 9 older Lua files. Without those sources, file reading remains available, but the complete MCP runtime is not ready. Apply the printed configuration in your client; its server command is `python -B -X utf8 run_kb.py serve`. Printed configuration does not prove a successful connection or query.

Prepared `cache/runtime/` contains locally restored game source excerpts and must stay local. A `$dst_source_payload_slot` in public JSON is a missing local-source slot, not source already read or behavioral evidence. Public evidence consists of reviewed excerpts, not complete original research; withheld private context remains `UNK`.

Use [SKILL.md](SKILL.md) for topic routing, [retrieval rules](references/kb-retrieval.md) for Scope and admission, and [testing](references/testing-release.md) for validation. Real game, remote-client, visual, audio and cross-version behavior need separate evidence; see [limits](docs/public-limits.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission. Valid historical MIT grants and third-party terms remain in force; see [licensing](docs/licensing.md).
