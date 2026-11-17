---
name: freellmapi
description: Use FreeLLMAPI (tashfeenahmed/freellmapi) — a local gateway that puts 87 free LLM providers and 1,300+ free model endpoints behind one OpenAI-compatible /v1 endpoint. Use to give Claude Code, Codex, Cursor, or any OpenAI client free models with smart routing and failover.
---

# FreeLLMAPI — One Gateway for All Free LLMs

- Repo: https://github.com/tashfeenahmed/freellmapi (TypeScript, MIT, ~54K★)
- Website: https://freellmapi.co · npm: `freellmapi`
- Claim: 10.1B tokens/month, 87 free providers, 1,313 free endpoints,
  one `/v1` endpoint + any custom OpenAI-compatible endpoint.
  Smart routing, automatic failover, encrypted keys.
  Personal experimentation only.

## Quick start (Docker)

```bash
curl -fsSL https://freellmapi.co/install.sh | bash
# Open http://localhost:3001 → add provider keys on the Keys page
# → grab your unified API key from the Keys page header
```

Then point any OpenAI-compatible client at it:

```bash
export OPENAI_BASE_URL=http://localhost:3001/v1
export OPENAI_API_KEY=freellmapi-...   # unified key from the dashboard
```

Launch coding agents through it (keeps credentials out of config files):

```bash
npx freellmapi launch          # Claude Code
npx freellmapi launch-codex    # Codex
```

## Features

- OpenAI surfaces: `/v1/chat/completions`, `/v1/responses`,
  `/v1/completions`, `/v1/embeddings`, `/v1/models`, images/video/speech.
- Anthropic Messages API (`/v1/messages`) — Claude Code runs on free models.
- Smart routing (6 strategies), automatic failover on 429/5xx, key rotation.
- Per-key rate tracking (RPM/RPD/TPM/TPD) — stays under every provider cap.
- Self-updating model catalog (signed feed, twice daily).
- Encrypted keys (AES-256-GCM in SQLite) — apps only see one token.
- Admin dashboard + analytics, MCP server at `/mcp`, OpenAPI at `/v1/docs`.
- Runs anywhere Node 20+ runs (incl. Raspberry Pi, ~40 MB RSS idle).

## Begonia kernel use

Run FreeLLMAPI locally, then use its free models to explain kernel code,
summarize `driver_loader_builtin.c`, or analyze REA/Ghidra output —
without paying for API credits:

```bash
python3 scripts/free_llm.py "Summarize this kernel driver" \
  --base-url http://localhost:3001/v1 --model auto
```

## Notes

- Free installs get the monthly catalog snapshot (30-day lag); premium
  ($19/yr) gets same-day updates.
- Provider keys stay on your machine; requests go directly to providers.
- Respect provider terms — free tiers are for personal experimentation.
