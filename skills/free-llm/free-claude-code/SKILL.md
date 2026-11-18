---
name: free-claude-code
description: Use free-claude-code (codeaashu) — a local proxy that routes Claude Code's Anthropic API calls to NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, or llama.cpp for free. Use when you want Claude Code CLI/VSCode without an Anthropic key.
---

# free-claude-code — Claude Code on free providers

- Repo: https://github.com/codeaashu/free-claude-code (Python, MIT, ~387★)
- Verified 2026-11-18: exists, actively pushed, MIT.
- What it is: a **lightweight local proxy** that intercepts Claude Code's
  Anthropic API calls and forwards them to a free provider. Set 2 env vars;
  no patching of Claude Code or the VSCode extension.

## Providers (pick one)

| Provider | Free allowance | Key page |
|---|---|---|
| NVIDIA NIM | 40 req/min free (recommended) | https://build.nvidia.com/settings/api-keys |
| OpenRouter | free `:free` models | https://openrouter.ai/keys |
| DeepSeek | signup balance | https://platform.deepseek.com/api_keys |
| LM Studio | fully local, no key | https://lmstudio.ai |
| llama.cpp | fully local, `llama-server` | — |

## Install

```bash
pip install uv                      # uv is required to run the project
git clone https://github.com/codeaashu/free-claude-code.git
cd free-claude-code
cp .env.example .env                # then edit .env
```

## .env — NVIDIA NIM (verified against the repo README)

```dotenv
NVIDIA_NIM_API_KEY="nvapi-your-key-here"

MODEL_OPUS=
MODEL_SONNET=
MODEL_HAIKU=
MODEL="nvidia_nim/z-ai/glm4.7"      # fallback

ENABLE_THINKING=true                # global switch for reasoning / thinking blocks
```

## .env — OpenRouter / DeepSeek / local

```dotenv
# OpenRouter
OPENROUTER_API_KEY="sk-or-your-key-here"
MODEL="open_router/stepfun/step-3.5-flash:free"

# DeepSeek
DEEPSEEK_API_KEY="your-deepseek-key-here"
MODEL="deepseek/deepseek-chat"

# LM Studio (no key)
MODEL="lmstudio/unsloth/GLM-4.7-Flash-GGUF"

# llama.cpp (no key)
LLAMACPP_BASE_URL="http://localhost:8080/v1"
MODEL="llamacpp/local-model"
```

`MODEL_OPUS` / `MODEL_SONNET` / `MODEL_HAIKU` let you map each Claude tier
to a different model — even across providers.

## Notes

- Free tiers are rate-limited (NIM ≈ 40 req/min); the proxy has proactive
  rolling-window throttling plus 429 backoff.
- It also ships a Discord/Telegram bot for remote coding.
- Never commit `.env`. Keep keys in `.env` (git-ignored) — see
  `config/.env.example` in this repo.
- This is a third-party proxy: it sends your prompts to whichever provider
  you configure. Don't route confidential code through a free tier whose
  terms allow training on your data.
