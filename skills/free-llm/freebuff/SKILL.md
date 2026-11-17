---
name: freebuff
description: Use Freebuff (CodebuffAI/freebuff) — the free coding agent with web, CLI, and desktop apps. Use when you want a free AI coding agent with no API key, for coding, research, and browser tasks.
---

# Freebuff — The Free Coding Agent

- Repo: https://github.com/CodebuffAI/freebuff (TypeScript, ~14K★)
- Website: https://freebuff.com · Reel: @matty.buff — "comment 'sauce'"
- Claim: 749,667 users (as shown in the reel).

## What it is

Freebuff is a free coding agent available on web, CLI, and desktop.
It uses specialized agents instead of one model + one prompt:

- **Codebase context** — file-finding agents map the project before editing.
- **Implementation & review** — agents divide work, edit, run commands, inspect.
- **Research & browser use** — investigate docs, test apps in a real browser.
- **Parallel local work** — desktop isolates concurrent agents in workspaces.
- **Hosted environments** — web/cloud sandboxes, previews, terminals.

## Free access

- Available in every country; supported regions get full access.
- Free allowance: 5 hours/day (4 on VPN/proxy), spent in "hours"
  (1 hour = 5 Freebucks since 2026-10-15).
- Free models include DeepSeek V4.1 Flash variants, Solar Mini/Pro 4,
  and experimental models (Beam 1.0, Glyph Cluster, Nemotron 3.5 Lightning).
- Paid plans add Claude Haiku, GPT-6, Muse Spark, etc.
- Text ads support the included models.

## Install / use

```bash
git clone https://github.com/CodebuffAI/freebuff.git
cd freebuff
bun install
# See CONTRIBUTING.md — local dev needs Docker + .env.local
```

Or just use the web app at https://freebuff.com — no install needed.

## Privacy note (important)

Freebuff may use your data to train AI models when a model/feature says
data may be used for training, and may share/sell it to third parties.
Check the model's data-use notice before sending sensitive code.
See https://freebuff.com/privacy-policy.

## Begonia kernel use

Use Freebuff's free agents for kernel-code Q&A and build-log debugging
without spending API credits — but don't paste private keys or
unreleased code into it.
