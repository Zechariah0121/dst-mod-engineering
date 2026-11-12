# DST Mod Engineering

`v2026.11.12.5` is an engineering Skill and knowledge base for Don't Starve Together mod development. Retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文](README.md)

The knowledge base has **300 registered records: 64 foundation, 13 Native AI, 110 Native Core and 113 mechanism research records**. This update adds unified ID/API review with whole-object continuation and four bounded feature chains linking input, authoritative execution, consumers, cleanup and recovery. See [changes](docs/phase15-unified-chains.md). Detailed technical guides are mainly in Chinese.

The mechanism research family contains 420 API contracts.

Minimal examples connect active skills, fueled equipment, deployable structures and two-state creatures into concrete features. Start from the [task map](references/task-map.md); each [feature guide](docs/phase15-unified-chains.md#四条功能链) describes its scope.

## Download and setup

Download [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip) from the [latest release](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) and compare it with that release's `SHA256SUMS.txt`. Repository changes are published in batches. Extract the complete directory containing `SKILL.md`; install it in your agent's supported skill location. See [installation](docs/install-and-use.md).

Invoke `dst-mod-engineering` with the task, mod directory and authorized game source. For full MCP, use Python 3.10+ with SQLite FTS5 and run from the package root:

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<absolute path to scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

Apply the printed configuration in your client, then check nine tools and a real query. The Skill calls `update-sources ensure` before work requiring current source evidence, reusing the remembered path; identical successful inputs return quickly. Follow `reconnect_required` when activation changes. The assistant maintains local bindings/cache; client configuration and live connections stay under your control. See the [update workflow](references/source-update-assist.md).

## Knowledge and evidence

Without MCP, use `run_kb.py find` / `read` to locate and review public records, or select IDs from `knowledge/CATALOG.json` and read their `file` and JSON `pointer`; report direct file reads as file access. Examples are in [knowledge access](docs/knowledge-integration.md). Full MCP offers nine tools. Default `auto` permits two public review tools after manifest validation when preparation is missing or the package changed; damaged caches and untrusted public files remain errors. Explicit `catalog` is public review, while `full` requires prepared sources.

Read Scope, claim type, version, corrections and admission together. Native AI Coding uses its ten-field projection and at most five records per task. Core retains Coding HOLD; mechanism research remains research/restricted/hold and needs explicit Reviewer access. A declaration or search hit is navigation; read the relevant contract and evidence before using it. Private context marked `UNK` remains unknown. Exact parameters, budgets and identity rules are in [retrieval](references/kb-retrieval.md); source identities and compatibility states are in [source maintenance](docs/source-compatibility.md).

Unified review uses explicit Reviewer/purpose on `get_entry`, or `lookup_api(family="all")`. CLI equivalents are `run_kb.py review ID` and `run_kb.py review --api "symbol"`, both requiring prepared full service. Follow the returned `continuation` when the byte budget requires further pages. Parameters are in [knowledge access](docs/knowledge-integration.md).

The package excludes game Lua, private projects and third-party executables. Restored source excerpts and machine-specific state stay in local `cache/`. Public `$dst_source_payload_slot` values mark source to restore locally.

Report source research, automated checks and game observations by their tested scope. See [testing](references/testing-release.md), [release changes](docs/phase15-unified-chains.md) and [limits](docs/public-limits.md).

Use the [development task map](references/task-map.md) to find existing record IDs, guides, partial coverage, project dependencies and next validation steps. Use [SKILL.md](SKILL.md) for topic routing, [module architecture](references/complex-mod-architecture.md) for ownership and [action integration](references/action-lifecycle-architecture.md) for cancellable interactions.

Read the bounded chains for [active skills](references/chain-active-skill.md), [equipment](references/chain-equipment.md), [deployable structures](references/chain-deployable.md) and [two-state creatures](references/chain-creature-stage.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission; valid historical MIT grants and third-party terms remain in force. See [licensing](docs/licensing.md).
