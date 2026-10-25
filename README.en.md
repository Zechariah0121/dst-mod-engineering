# DST Mod Engineering

An AI engineering skill for Don't Starve Together mod development: inspect the current source, then design, implement, review and validate. It covers characters, items, spells, assets, networking, persistence and compatibility. [中文 README](README.md)

The standalone Skill includes engineering guidance, topic references and three helper scripts. **It does not include the complete engineering KB, an MCP server, game source or private mod projects.** It can work with your legally obtained local source without an additional KB.

## Downloads

[Public Beta 1 release](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25).

| Asset | Use |
|---|---|
| [dst-mod-engineering.skill.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/dst-mod-engineering.skill.zip) | Install the Skill, references and three developer helpers |
| [web-reading.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/web-reading.zip) | Topic-based reading for web chat or offline use |
| [dst-mod-engineering-full.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/dst-mod-engineering-full.zip) | Full public repository, including the earlier 64-entry reference KB and its read-only MCP service |

Verify downloads with the release's `SHA256SUMS.txt`. The public snapshot excludes the separate private full KB and private research.

## Install and use

1. Download the standalone Skill attachment from the [repository releases](https://github.com/Zechariah0121/dst-mod-engineering/releases) and fully extract it. Locate the `dst-mod-engineering/` directory that directly contains `SKILL.md`.
2. Copy the complete directory to a skill location supported by your agent, such as `.agents/skills/dst-mod-engineering/` in a Codex project or `.claude/skills/dst-mod-engineering/` in a Claude Code project. Preserve existing customizations. See [installation](docs/install-and-use.md) for personal locations and other agents.
3. Invoke `dst-mod-engineering` and provide your task, mod directory, actual DST version and local `scripts.zip` location. Confirm that the Skill and relevant references are readable. If discovery is unavailable, explicitly provide the path to `SKILL.md`.

For web chat, use attachments or a supported native skill-import feature as described in the [web guide](references/web-chat.md). Most detailed references are in Chinese.

## Entry points

| Task | Where to start |
|---|---|
| Characters, spells, items, recipes, UI or assets | Topic index in [SKILL.md](SKILL.md) |
| Source investigation, crashes, networking or save issues | Definitions, callers, execution side, initialization, cleanup and persistence |
| Syntax, API declarations or isolated server checks | [Testing and delivery](references/testing-release.md) |
| An existing KB | [Optional KB integration](docs/knowledge-integration.md); inspect the actual service and version |

The scripts need Python 3.10+. Syntax checks additionally need `luaparser` from `requirements.txt`. The server test helper supports Windows only. Reading the Skill needs no script execution. Install asset tools only as needed; see [tool sources and validation](references/tool-bootstrap.md).

Versioned notes and examples have bounded scope. They do not guarantee compatibility with the latest game or every mod. Report static, server, real remote-client, visual and audio validation separately. See [capabilities and limits](docs/public-limits.md).

## Optional public reference KB

The full public repository retains the earlier **v0.1.1, 64-entry** reference KB and its read-only service.
See the [KB entrypoint](https://github.com/Zechariah0121/dst-mod-engineering/blob/v2026.10.25/dst-engineering-kb/README.md) and [MCP setup](https://github.com/Zechariah0121/dst-mod-engineering/blob/v2026.10.25/dst-kb-service/README.md).
The standalone Skill ZIP excludes both. This is a bounded historical reference set, not a complete or current-game knowledge claim.
Read each entry's status, source version, evidence and unexecuted test candidates.

## License

Project-owned material uses the [custom non-commercial LICENSE](LICENSE), not MIT or an OSI open-source license. Commercial use requires separate written permission. Valid historical MIT grants and third-party rights remain in force. See [licensing](docs/licensing.md).
