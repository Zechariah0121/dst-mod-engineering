# DST Mod Engineering

`v2026.11.12.3` is an engineering Skill and knowledge base for Don't Starve Together mod development. Retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文](README.md)

The knowledge base has **296 registered records: 64 foundation, 13 Native AI, 110 Native Core and 109 mechanism research records**. This update adds a development task map and short find/read commands, and reduces retrieval overhead to help AI locate relevant evidence and identify remaining checks. See [changes](docs/phase14-usage-retrieval.md). Detailed technical guides are mainly in Chinese.

The mechanism research family contains 404 API contracts, counted from its records' `api_contracts` arrays. A whole-library API inventory and a source-coverage denominator have yet to be established.

Existing guides connect multi-component retrieval, timed-effect recovery and practical optimization. The previous topic expansion is documented in [phase 13](docs/phase13-practical-expansion.md).

## Download and setup

Download [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip) from the [latest release](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) and compare it with that release's `SHA256SUMS.txt`. Repository changes are published in batches. Extract the complete directory containing `SKILL.md`; install it in your agent's supported skill location. See [installation](docs/install-and-use.md).

Invoke `dst-mod-engineering` with the task, mod directory and authorized game source. For full MCP, use Python 3.10+ with SQLite FTS5 and run from the package root:

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<absolute path to scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

Apply the printed configuration in your client, then check nine tools and a real query. The Skill calls `update-sources ensure` before substantive KB use, reusing the remembered path; identical successful inputs return quickly. Follow `reconnect_required` when activation changes. The assistant maintains local bindings/cache; client configuration and live connections stay under your control. See the [update workflow](references/source-update-assist.md).

## Knowledge and evidence

Without MCP, use `run_kb.py find` / `read` to locate and review public records, or select IDs from `knowledge/CATALOG.json` and read their `file` and JSON `pointer`; report direct file reads as file access. Examples are in [knowledge access](docs/knowledge-integration.md). Full MCP offers nine tools. Default `auto` permits two public review tools after manifest validation when preparation is missing or the package changed; damaged caches and untrusted public files remain errors. Explicit `catalog` is public review, while `full` requires prepared sources.

Read Scope, claim type, version, corrections and admission together. Native AI Coding uses its ten-field projection and at most five records per task. Core retains Coding HOLD; mechanism research remains research/restricted/hold and needs explicit Reviewer access. A declaration or search hit is navigation; read the relevant contract and evidence before using it. Private context marked `UNK` remains unknown. Exact parameters, budgets and identity rules are in [retrieval](references/kb-retrieval.md); source identities and compatibility states are in [source maintenance](docs/source-compatibility.md).

The package excludes game Lua, private projects and third-party executables. Restored source excerpts and machine-specific state stay in local `cache/`. Public `$dst_source_payload_slot` values mark source to restore locally.

Report source research, automated checks and game observations by their tested scope. See [testing](references/testing-release.md), [release changes](docs/phase14-usage-retrieval.md) and [limits](docs/public-limits.md).

Use the [development task map](references/task-map.md) to find existing record IDs, guides, partial coverage, project dependencies and next validation steps. Use [SKILL.md](SKILL.md) for topic routing, [module architecture](references/complex-mod-architecture.md) for ownership and [action integration](references/action-lifecycle-architecture.md) for cancellable interactions.

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission; valid historical MIT grants and third-party terms remain in force. See [licensing](docs/licensing.md).
