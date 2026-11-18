# Telegram note storage

`scripts/telegram_store.py` keeps project notes and build artifacts in your
Telegram bot chat, so you can grab them from your phone or any machine.

## Why it runs where it runs

This Arena sandbox can only reach `github.com`, `codeload.github.com`,
`api.github.com`, `registry.npmjs.org`, `pypi.org`, and
`files.pythonhosted.org`. The Telegram Bot API is **not** on that list, so
nothing can be uploaded from inside the sandbox. The script is written to
run anywhere with normal internet — your laptop, a VPS, or a CI runner.

## Setup

```bash
cp config/.env.example .env      # then paste the token + chat id
export TELEGRAM_BOT_TOKEN=...    # or rely on .env
export TELEGRAM_CHAT_ID=...
```

`.env` is git-ignored and `chmod 600`. The token is equivalent to a
password for the bot — anyone holding it can read and send as the bot.
If it is ever pasted into a chat, screenshot, or ticket, revoke it in
@BotFather (`/revoke`) and use the new one.

## Commands

| Command | What it does |
|---|---|
| `ping` | `getMe` + one test message — proves token and chat work |
| `send "text"` | send a note (auto-split at 4,096 chars) |
| `upload FILE [--caption C]` | upload a file (bot limit 50 MB) |
| `backup [paths…]` | zip `skills/ scripts/ config/ README.md` and upload |
| `fetch NAME --out DIR` | download a file back (bot limit 20 MB) |
| `list` | show the local manifest |
| `delete-log` | clear the local manifest (chat history untouched) |

Add `--dry-run` anywhere to print the exact request without sending.

## The manifest

The Bot API cannot list chat history, so the script keeps
`~/.telegram-store/manifest.json` (mode 0600) mapping filename → `file_id`.
Upload from the same machine you intend to `fetch` from, or copy the
manifest along.

## Limits worth knowing

- Bot uploads: **50 MB**; downloads via `getFile`: **20 MB**.
- Text messages: **4,096 chars** (the script splits at paragraph breaks).
- A bot cannot start a chat — press **Start** in the bot first, or
  `sendMessage` returns 403.

## Testing

`scripts/tests/mock_telegram_api.py` implements `getMe`, `sendMessage`,
`sendDocument`, `getFile`, and file download locally:

```bash
python3 scripts/tests/mock_telegram_api.py --port 8099 &
export TELEGRAM_API_BASE=http://127.0.0.1:8099 TELEGRAM_BOT_TOKEN=test
export TELEGRAM_CHAT_ID=123 TELEGRAM_STORE_DIR=/tmp/tgstore
python3 scripts/telegram_store.py ping
python3 scripts/telegram_store.py upload begonia_dtb.bin
python3 scripts/telegram_store.py fetch begonia_dtb.bin --out /tmp/back
cmp begonia_dtb.bin /tmp/back/begonia_dtb.bin   # byte-identical
```
