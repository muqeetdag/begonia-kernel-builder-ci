---
name: ecc
description: Use ECC (affaan-m/ECC) — the agent harness performance optimization system with 72 agents, 327 skills, memory, security, and research-first development for Claude Code, Codex, Cursor, and beyond. Use to turn Claude into a full AI engineering agent.
---

# ECC — Agent Harness for Claude Code & Beyond

- Repo: https://github.com/affaan-m/ECC (MIT, 237,500★ in the reel)
- Website: https://ecc.tools · npm: `ecc-universal`, `ecc-agentshield`
- Description: "The agent harness performance optimization system. Skills,
  instincts, memory, security, and research-first development for Claude
  Code, Codex, Opencode, Cursor and beyond."
- Reel caption: "This GitHub Repo Turns Claude Into an AI…" (thevibefounder.bharat)

## What you get

| Included | Count | What it gives you |
|----------|-------|-------------------|
| Agents | 72 | Planning, review, build repair, security, architecture, domain work |
| Skills | 327 | TDD, research, security, docs, frontend, data, ML, operations, … |
| Commands | 98 | Convenient entry points (moving to skills-first) |
| Hooks + memory | Runtime | Enforcement, session summaries, continuous learning, instincts |
| Rules | Selective | Always-loaded standards by language/project |
| AgentShield | Included | Scans prompts, hooks, MCP config, permissions, secrets, agent files |

Pipeline: `plan → test → implement → review → verify → remember → improve`

## Install

Requires Node.js 18+ (Claude plugin setup also needs Git + Claude Code 2.1+).

```bash
# Recommended: universal guided setup
npx ecc-universal@2.2.3 setup
```

Or install the Claude Code plugin directly:

```bash
# inside Claude Code:
/plugin marketplace add affaan-m/ECC
/plugin install ecc@ecc
```

> ⚠️ Official sources only: github.com/affaan-m/ECC, npm `ecc-universal` /
> `ecc-agentshield`, the GitHub App (ecc-tools), plugin slug `ecc@ecc`,
> ecc.tools. Third-party mirrors may contain malware.

## Begonia kernel use

ECC's agents/skills pair well with this repo: use its code-review and
build-repair agents on `build.sh` / `driver_loader_builtin.c`, and its
research skills to study upstream kernel sources before patching.
ECC skills live in `tools/ECC/skills/` after cloning (see installer).

## Notes

- Works best with Claude Code today; native Codex/Qoder paths exist;
  adapters for Cursor, OpenCode, Gemini, Zed, Copilot, Qwen, …
- OSS stays free (MIT forever). ECC Pro is the hosted GitHub App for
  private repos.
