# DST Mod Engineering

`v2026.11.11` is an engineering Skill and knowledge base for Don't Starve Together mod development. Retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文](README.md)

The package has **247 registered records: 64 foundation, 13 Native AI, 110 Native Core and 60 mechanism research records**. This release adds timer, entity-reference and reward-queue recovery research, improves complete API and multi-step retrieval, and automatically removes temporary test mods. See [release changes](docs/phase10-recovery-delivery.md). Detailed technical guides are mainly in Chinese.

## Download and setup

Download [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.11.11/dst-mod-engineering.zip) from [v2026.11.11](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.11.11) and compare it with that release's `SHA256SUMS.txt`. Extract the complete directory containing `SKILL.md`; install it in your agent's supported skill location. See [installation](docs/install-and-use.md).

Invoke `dst-mod-engineering` with the task, mod directory and authorized game source. For full MCP, use Python 3.10+ with SQLite FTS5 and run from the package root:

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<absolute path to scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

Apply the printed configuration in your client, then check nine tools and a real query. The Skill calls `update-sources ensure` before substantive KB use, reusing the remembered path; identical successful inputs return quickly. Follow `reconnect_required` when activation changes. The assistant maintains local bindings/cache; client configuration and live connections stay under your control. See the [update workflow](references/source-update-assist.md).

## Knowledge and evidence

Without MCP, select IDs from `knowledge/CATALOG.json` and read their `file` and JSON `pointer`; report this as file access. Full MCP offers nine tools. Default `auto` permits two public review tools after manifest validation when preparation is missing or the package changed; damaged caches and untrusted public files remain errors. Explicit `catalog` is public review, while `full` requires prepared sources.

Read Scope, claim type, version, corrections and admission together. Native AI Coding uses its ten-field projection and at most five records per task. Core retains Coding HOLD; mechanism research remains research/restricted/hold and needs explicit Reviewer access. A declaration or search hit is navigation; read the relevant contract and evidence before using it. Private context marked `UNK` remains unknown. Exact parameters, budgets and identity rules are in [retrieval](references/kb-retrieval.md); source identities and compatibility states are in [source maintenance](docs/source-compatibility.md).

The package excludes game Lua, private projects and third-party executables. Restored source excerpts and machine-specific state stay in local `cache/`. Public `$dst_source_payload_slot` values mark source to restore locally.

Report source research, automated checks and game observations by their tested scope. See [testing](references/testing-release.md), [release changes](docs/phase10-recovery-delivery.md) and [limits](docs/public-limits.md).

Use [SKILL.md](SKILL.md) for topic routing, [module architecture](references/complex-mod-architecture.md) for ownership and [action integration](references/action-lifecycle-architecture.md) for cancellable interactions.

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission; valid historical MIT grants and third-party terms remain in force. See [licensing](docs/licensing.md).
