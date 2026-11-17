---
name: awesome-free-llm-apis
description: Use the awesome-free-llm-apis catalog (mnfst/awesome-free-llm-apis, live at freellm.net) — 513+ free LLM APIs from 30 providers with permanent free tiers. Use to find a free provider/model for any task, with base URLs, rate limits, and key pages.
---

# awesome-free-llm-apis — The Free LLM Catalog

- Repo: https://github.com/mnfst/awesome-free-llm-apis (13K★)
- Live site: https://freellm.net (Browse models · Playground · Config generator · API keys)
- Data refreshed daily · Last updated shown on the site.
- Providers include: Cohere, Hugging Face, Cloudflare, xAI, DeepSeek,
  OpenRouter, Alibaba Cloud, Google Gemini, Groq, Cerebras, Mistral,
  Together, Fireworks, and more (30 providers, 513+ APIs).

## How to use

1. Browse the catalog (site or repo README) and pick a provider + model.
2. Open the provider's API-key page (linked per provider).
3. Get a free key — most need no credit card.
4. Call the OpenAI-compatible base URL with any OpenAI SDK:

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.cohere.ai/compatibility/v1",  # example: Cohere
    api_key="YOUR_FREE_KEY",
)
resp = client.chat.completions.create(
    model="command-r", messages=[{"role": "user", "content": "Hello"}]
)
```

Or use this repo's helper (reads `config/free-llm-providers.json`):

```bash
cp config/.env.example .env   # paste your key
python3 scripts/free_llm.py "Hello" --provider cohere
python3 scripts/free_llm.py "Hello" --provider deepseek
```

## Languages

English · 简体中文 · 繁體中文 · 日本語 · 한국어 (site footer).

## Notes

- "Permanent free tier" ≠ unlimited — each provider has RPM/TPD limits.
- Some keys are trial/non-commercial only — check the provider row.
- Free-tier prompts may be used by the provider to improve products
  (e.g. Google Gemini) — don't send secrets.
- The repo also ships `data.json` + `sources.json` for programmatic use.
