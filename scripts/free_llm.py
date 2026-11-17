#!/usr/bin/env python3
"""Call any free LLM provider (OpenAI-compatible) — from the screenshots.

Providers: Cohere, Hugging Face, Cloudflare, xAI, DeepSeek, OpenRouter,
Alibaba Cloud, Google Gemini, FreeLLMAPI gateway, Modal endpoints, …

Usage:
    cp config/.env.example .env          # paste your free API keys
    python3 scripts/free_llm.py "Hello" --provider cohere
    python3 scripts/free_llm.py "Summarize driver_loader_builtin.c" \\
        --provider deepseek --model deepseek-chat
    python3 scripts/free_llm.py "Hello" --base-url http://localhost:3001/v1 \\
        --model auto --api-key freellmapi-...   # FreeLLMAPI gateway
    python3 scripts/free_llm.py --list   # list providers + models

Stdlib only (urllib) — no pip install needed.
Keys come from .env / environment (never commit them).
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "free-llm-providers.json"


def load_env():
    """Load .env (repo root or config/) into os.environ without overwriting."""
    for p in (ROOT / ".env", ROOT / "config" / ".env"):
        if p.exists():
            for line in p.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def load_providers():
    return json.loads(CONFIG.read_text())["providers"]


def chat(base_url, api_key, model, prompt, system=None):
    url = base_url.rstrip("/") + "/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} from {url}:\n{e.read().decode()[:2000]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error calling {url}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"Unexpected response:\n{json.dumps(data, indent=2)[:2000]}", file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Call a free LLM provider")
    ap.add_argument("prompt", nargs="?", help="Prompt to send")
    ap.add_argument("--provider", help="Provider id (see --list)")
    ap.add_argument("--base-url", help="Override base URL (e.g. FreeLLMAPI/Modal)")
    ap.add_argument("--model", help="Override model")
    ap.add_argument("--api-key", help="Override API key")
    ap.add_argument("--system", help="System prompt")
    ap.add_argument("--list", action="store_true", help="List providers")
    args = ap.parse_args()

    load_env()
    providers = load_providers()

    if args.list:
        for pid, p in providers.items():
            print(f"{pid:22} {p['name']:20} base={p['base_url']}")
            print(f"{'':22} key_page={p['key_page']}")
            print(f"{'':22} models={', '.join(p.get('free_models', [])[:4])}")
            print(f"{'':22} notes={p.get('notes', '')}\n")
        return

    if not args.prompt:
        ap.error("prompt is required (or use --list)")

    if args.base_url:
        base_url = args.base_url
        model = args.model or "auto"
        api_key = args.api_key or os.environ.get("FREELLMAPI_API_KEY", "")
        if not api_key:
            print("No API key: pass --api-key or set FREELLMAPI_API_KEY in .env",
                  file=sys.stderr)
            sys.exit(1)
    else:
        pid = args.provider or "openrouter"
        if pid not in providers:
            print(f"Unknown provider '{pid}'. Known: {', '.join(providers)}",
                  file=sys.stderr)
            sys.exit(1)
        p = providers[pid]
        base_url = p["base_url"]
        model = args.model or p.get("default_model", "")
        env_var = p.get("env_var", "")
        api_key = args.api_key or (os.environ.get(env_var, "") if env_var else "")
        if not api_key:
            print(f"No key for {p['name']}: set {env_var} in .env "
                  f"(get one free at {p['key_page']})", file=sys.stderr)
            sys.exit(1)

    print(chat(base_url, api_key, model, args.prompt, args.system))


if __name__ == "__main__":
    main()
