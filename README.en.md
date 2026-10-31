# DST Mod Engineering

Version `v2026.10.31.3` contains 227 registered records: the preserved historical 187 and 40 native_mechanism research records covering Brain, world generation, cooking/seasoning, growth/regeneration, temperature/moisture, freezing/heat interactions, survival completion and presentation mechanisms. `FAMILY-REGISTRY` generates `CATALOG.counts`. Research remains `research/restricted/hold` with explicit Reviewer access. See [research-family integration](docs/native-mechanisms.md).

An engineering Skill and knowledge base for Don't Starve Together mod development: retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文 README](README.md)

The public KB is in `knowledge/`: **227 records comprising 64 foundation records, 13 Native AI records, 110 Native Core records and 40 mechanism research records**. One complete distribution includes the Skill, public knowledge data, development helpers, source preparation and MCP. Scope, claim types, versions, corrections and Coding HOLD remain binding; record availability does not grant Coding admission.

## Download

Release: [v2026.10.31.3](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.31.3). Download the single complete package for Skill installation, file reading or MCP. Historical [v2026.10.25.4](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.4) retains its original 187-record release identity.

| File | Contents |
|---|---|
| [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.31.3/dst-mod-engineering.zip) | Complete Skill, 227 registered public records in one `knowledge/` tree, development helpers, local source preparation and MCP |

Check downloads against the release's `SHA256SUMS.txt`. No game Lua source, third-party executables or private mod projects are bundled. Most detailed references are in Chinese.

This release adds a Skill-driven source update assistant. Bind an explicitly supplied authorized `scripts.zip` once; the Skill checks that same path before substantive KB use and attempts preparation where source ranges can be recovered. Changed source is reviewed for the current task, while historical Scope and admission stay intact. See [update workflow](references/source-update-assist.md) and [limits](docs/public-limits.md).

## Start

Extract the package completely and install the directory containing `SKILL.md` in a supported agent skill location. Invoke `dst-mod-engineering` with your task, mod directory, actual game version and authorized local source. Without MCP, read a small relevant subset from the knowledge files. See [installation](docs/install-and-use.md) and [KB integration](docs/knowledge-integration.md).

For full MCP, run from the package root with Python 3.10+ and SQLite FTS5:

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<absolute path to scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

Later tasks use `run_kb.py update-sources ensure` with the remembered binding. Identical inputs return without rebuilding; unchanged failures are not retried automatically. The assistant does not edit client configuration or restart connections. Apply the printed configuration in your client and verify nine tools plus a real query. If a catalog session is already connected, restart it after preparation to switch tools. Printed configuration does not prove a successful connection or query. See [installation](docs/install-and-use.md).

Default `--mode auto` uses full mode when preparation is valid. Missing preparation or PACKAGE_CHANGED permits public review after public-manifest validation, with the reason reported. Damaged cache, invalid activation and public-file mismatch remain errors; explicit full stays strict. Use `run_kb.py maintain-sources --help` for independent target-source navigation and local review. The assessed 761239 input does not imply automatic full-mode support or behavioral compatibility with every future DST archive.

Prepared `cache/runtime/` contains locally restored game source excerpts and must stay local. A `$dst_source_payload_slot` in public JSON is a missing local-source slot, not source already read or behavioral evidence. Public evidence consists of reviewed excerpts, not complete original research; withheld private context remains `UNK`.

Use [SKILL.md](SKILL.md) for topic routing, [retrieval rules](references/kb-retrieval.md) for Scope and admission, and [testing](references/testing-release.md) for validation. Real game, remote-client, visual, audio and cross-version behavior need separate evidence; see [limits](docs/public-limits.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission. Valid historical MIT grants and third-party terms remain in force; see [licensing](docs/licensing.md).

This release supports source preparation for 761239, improves research retrieval and adds fire/FX mechanism contracts. See [phase notes](docs/phase6-retrieval-fx.md). New research retains 761239 evidence; historical records keep their original identities.
