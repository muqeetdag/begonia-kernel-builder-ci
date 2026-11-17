---
name: modal
description: Use Modal.com for free AI infrastructure — serverless GPUs and endpoints with free credit (up to $30 free as shown in the reel). Use to run LLM inference, batch jobs, or web endpoints without managing servers.
---

# Modal — Free AI Infrastructure ($30 Free)

- Website: https://modal.com · Reel: @ezsnippet — "You can use this up to $30 free"
- What: High-performance AI infrastructure — serverless GPUs, endpoints,
  apps, and batch jobs.

## How to use

1. Sign up at https://modal.com (free credit applied to new accounts).
2. Install the Python SDK:

```bash
pip install modal
modal setup
```

3. Deploy a function / endpoint:

```python
import modal
app = modal.App("begonia-llm")

@app.function(gpu="T4", image=modal.Image.debian_slim().pip_install("openai"))
def hello():
    return "Hello from Modal GPU"
```

4. Call it via its web endpoint URL (Modal prints a `…modal.run` URL).

## Free tier notes

- The reel says "up to $30 free" — check modal.com/pricing for the
  current free-credit amount; it changes over time.
- Free credit is for trying things — set spending limits in the dashboard
  so a runaway job doesn't burn it.
- Modal endpoints are OpenAI-compatible in many examples — you can point
  `scripts/free_llm.py` at a Modal endpoint with `--base-url`.

## Begonia kernel use

Offload heavy work (e.g. running a local LLM to summarize a kernel build
log, or batch-analyzing REA output) to a Modal GPU endpoint instead of
your laptop — free credit covers experimentation.
