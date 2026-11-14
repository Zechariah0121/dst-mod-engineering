# DST Mod Engineering

`v2026.11.13.4` is an engineering Skill and knowledge base for Don't Starve Together mod development. Retrieve relevant knowledge, inspect current source, then design, implement, review and validate. [中文](README.md)

The knowledge base has **302 registered records: 64 foundation, 13 Native AI, 110 Native Core and 115 mechanism research records**. Default retrieval now discovers and reads public knowledge and task guides. Current-source evidence is assessed independently, and one maintenance entry produces correction candidates. See [public reading](docs/public-reader.md), [evidence snapshots](docs/evidence-snapshots.md), and [author maintenance](docs/author-maintenance.md). Detailed technical guides are mainly in Chinese.

The mechanism research family contains 424 API contracts.

Minimal examples cover active skills, fueled equipment, deployable structures, two-state creatures, timed effects, and a skill resource HUD. Start from the [task map](references/task-map.md) or read about the [timed effect and resource HUD examples](docs/phase16-effect-and-resource.md).

## Download and setup

Download [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip) from the [latest release](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) and compare it with that release's `SHA256SUMS.txt`. Repository changes are published in batches. Extract the complete directory containing `SKILL.md`; install it in your agent's supported skill location. See [installation](docs/install-and-use.md).

Invoke `dst-mod-engineering` with the task and mod directory. Supply authorized game source when current behavior needs verification. With Python 3.10+, generate the default public MCP configuration from the package root:

```text
python -B -X utf8 run_kb.py mcp-config
```

Apply the printed configuration, inspect the actual tools, and run a default query that returns readable objects. Public reading needs no source. For current evidence, explicitly run `python -B -X utf8 prepare_sources.py --source "<absolute path to scripts.zip>"` when maintaining this local installation. The full legacy source service also requires SQLite FTS5. See [source maintenance](docs/source-compatibility.md).

## Knowledge and evidence

Without MCP, use `run_kb.py find` / `read` to locate and review public records, or use catalog file/pointer references. Default `auto` serves public knowledge without prepared source; unavailable evidence does not block the text. Explicit `catalog` retains the two-tool compatibility protocol; `full` requires complete prepared source. See [public reading](docs/public-reader.md).

Read Scope, claim type, version, corrections and admission together. Native AI Coding uses its ten-field projection and at most five records per task. Core retains Coding HOLD; mechanism research remains research/restricted/hold ; default public reading uses Reviewer access. A declaration or search hit is navigation; read the relevant contract and evidence before using it. Private context marked `UNK` remains unknown. Exact parameters, budgets and identity rules are in [retrieval](references/kb-retrieval.md); source identities and compatibility states are in [source maintenance](docs/source-compatibility.md).

Default `search_kb` and `get_context_bundle` return relevant whole objects. Use `get_entry` for a record and `lookup_api` for declaration navigation. CLI equivalents are `run_kb.py review ID` and `run_kb.py review --api "symbol"`; neither needs prepared source. Follow `continuation` when further pages are required. Explicit Coding and legacy evidence calls retain their source and admission checks.

The package includes original example Mods. Restored game source excerpts and machine-specific state stay in local `cache/`. Public `$dst_source_payload_slot` values mark source to restore locally.

Report source research, automated checks and game observations by their tested scope. See [testing](references/testing-release.md), [evidence snapshots](docs/evidence-snapshots.md) and [limits](docs/public-limits.md).

Use the [development task map](references/task-map.md) to find existing record IDs, guides, partial coverage, project dependencies and next validation steps. Use [SKILL.md](SKILL.md) for topic routing, [module architecture](references/complex-mod-architecture.md) for ownership and [action integration](references/action-lifecycle-architecture.md) for cancellable interactions.

Read the bounded chains for [active skills](references/chain-active-skill.md), [equipment](references/chain-equipment.md), [deployable structures](references/chain-deployable.md), [two-state creatures](references/chain-creature-stage.md), [timed effects](references/chain-timed-effect.md), and [skill resources and HUD](references/chain-skill-resource-hud.md).

Project-owned material uses the [custom non-commercial LICENSE](LICENSE). Commercial use requires separate written permission; valid historical MIT grants and third-party terms remain in force. See [licensing](docs/licensing.md).
