---
name: free-llm
description: Master free-LLM workflow — use free LLM APIs for coding agents and scripts. Use when you need AI without paying: pick a provider, get a free API key, plug it into an OpenAI-compatible client. Covers FreeLLMAPI, awesome-free-llm-apis, ECC, Freebuff, Modal, and public-apis.
---

# Free LLM APIs — Master Skill

> Source: @aiwithshivang carousel ("awesome-free-llm-apis — 513+ free LLM APIs
> from 30 providers") + reels by @aru_code, @ezsnippet, @matty.buff.

## How to use (3 steps)

**Step 1 — Pick a provider**
Cohere · Hugging Face · Cloudflare · xAI · DeepSeek · OpenRouter ·
Alibaba Cloud · Google Gemini · Groq · Cerebras · … (30+ providers)

**Step 2 — Get your API key**
Visit the provider's API-key page (links in
`config/free-llm-providers.json`), sign up free, copy the key (`sk-…`).

**Step 3 — Plug it in**

```python
api_key = "sk-**********"   # your free key, from .env — never commit it
```

Most providers offer an **OpenAI-compatible endpoint**, so any OpenAI SDK
works — just change `base_url` + `api_key`. See `scripts/free_llm.py`:

```bash
cp config/.env.example .env   # paste keys
python3 scripts/free_llm.py "Explain what driver_loader_builtin.c does"
```

## Sub-skills

| Skill | Use it when |
|-------|-------------|
| [freellmapi](freellmapi/SKILL.md) | You want ONE local gateway (`http://localhost:3001/v1`) routing across 87 free providers with automatic failover |
| [awesome-free-llm-apis](awesome-free-llm-apis/SKILL.md) | You want the full catalog — 513+ free APIs, rate limits, model lists |
| [ecc](ecc/SKILL.md) | You want Claude Code / Codex / Cursor upgraded with 72 agents + 327 skills |
| [freebuff](freebuff/SKILL.md) | You want a free coding agent (web/CLI/desktop) with no key at all |
| [modal](modal/SKILL.md) | You want free GPU/AI infra ($30 free credit) to run models or jobs |
| [public-apis](public-apis/SKILL.md) | You need free non-LLM APIs too (weather, news, finance, …) |

## Providers at a glance (from the screenshots)

| Provider | Free tier | Key page |
|----------|-----------|----------|
| Cohere | Trial key, 1,000 calls/mo, non-commercial | https://dashboard.cohere.com/api-keys |
| Hugging Face | Free inference API | https://huggingface.co/settings/tokens |
| Cloudflare Workers AI | Free neurons/day | https://dash.cloudflare.com |
| xAI (Grok) | Free credits on signup | https://console.x.ai |
| DeepSeek | Free balance on signup | https://platform.deepseek.com |
| OpenRouter | Free models (`:free` suffix) | https://openrouter.ai/keys |
| Alibaba Cloud (Qwen) | Free trial models | https://bailian.console.aliyun.com |
| Google Gemini | Free tier, no card | https://aistudio.google.com/app/apikey |

Full catalog with base URLs + models: `config/free-llm-providers.json`
and [awesome-free-llm-apis](awesome-free-llm-apis/SKILL.md).

## Rules

- Free tiers have rate limits — the router (FreeLLMAPI) handles failover.
- Some free keys are **non-commercial / personal experimentation only**.
- Never commit API keys — use `.env` (git-ignored).
- Respect each provider's terms of service.
