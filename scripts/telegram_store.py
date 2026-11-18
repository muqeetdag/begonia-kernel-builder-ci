#!/usr/bin/env python3
"""Store project notes/artifacts in a Telegram bot chat — reachable from anywhere.

The Telegram Bot API is NOT reachable from every environment (this sandbox's
network only allows GitHub/npm/PyPI), so this script is designed to run
wherever you have network: your laptop, a VPS, or CI.

Setup (once):
    export TELEGRAM_BOT_TOKEN=...      # from @BotFather — never commit it
    export TELEGRAM_CHAT_ID=...        # your numeric chat id
    # or put both in .env (git-ignored)

Usage:
    python3 scripts/telegram_store.py ping
    python3 scripts/telegram_store.py send "note about the dtb patch"
    python3 scripts/telegram_store.py upload Image.gz-dtb --caption "built 2026-11-17"
    python3 scripts/telegram_store.py backup            # zip notes + upload
    python3 scripts/telegram_store.py list
    python3 scripts/telegram_store.py fetch notes-20261117.zip --out /tmp
    python3 scripts/telegram_store.py delete-log

Add --dry-run to any command to print the exact HTTP request without sending.

Telegram limits: bot uploads 50 MB, bot downloads 20 MB (getFile), text 4096
chars. A manifest of file_ids is kept locally in ~/.telegram-store/manifest.json
so files can be fetched back by name (the Bot API cannot list chat history).
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_API = "https://api.telegram.org"
MAX_UPLOAD = 50 * 1024 * 1024


# ---------------------------------------------------------------- config
def load_env() -> None:
    """Read .env from the repo root / config, without overwriting real env vars."""
    for p in (ROOT / ".env", ROOT / "config" / ".env"):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def cfg() -> tuple[str, str, str, Path]:
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    api = os.environ.get("TELEGRAM_API_BASE", DEFAULT_API).rstrip("/")
    store = Path(os.environ.get("TELEGRAM_STORE_DIR", Path.home() / ".telegram-store"))
    return token, chat, api, store


def require_token(token: str) -> str:
    if not token:
        sys.exit(
            "Missing TELEGRAM_BOT_TOKEN.\n"
            "  export TELEGRAM_BOT_TOKEN=...   (from @BotFather)\n"
            "  or add it to .env — cp config/.env.example .env"
        )
    return token


# ---------------------------------------------------------------- manifest
def manifest_path(store: Path) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    return store / "manifest.json"


def load_manifest(store: Path) -> dict:
    p = manifest_path(store)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return {"entries": []}
    return {"entries": []}


def save_manifest(store: Path, data: dict) -> None:
    p = manifest_path(store)
    p.write_text(json.dumps(data, indent=2))
    p.chmod(0o600)


# ---------------------------------------------------------------- transport
def call(api: str, token: str, method: str, fields: dict, files: dict | None = None,
         dry_run: bool = False, timeout: int = 120) -> dict:
    """POST to the Bot API, multipart when `files` is given."""
    url = f"{api}/bot{token}/{method}"
    safe_url = f"{api}/bot<TOKEN>/{method}"

    if files:
        boundary = uuid.uuid4().hex
        body = bytearray()
        for k, v in fields.items():
            body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        for k, (filename, data) in files.items():
            ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            body += (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n"
            ).encode()
            body += data + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        body = bytes(body)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        body = urllib.parse.urlencode(fields).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

    if dry_run:
        print(f"[dry-run] POST {safe_url}")
        print(f"[dry-run] fields: {json.dumps({k: (str(v)[:80]) for k, v in fields.items()})}")
        if files:
            for k, (fn, data) in files.items():
                print(f"[dry-run] file '{k}': {fn} ({len(data)} bytes)")
        print(f"[dry-run] body size: {len(body)} bytes")
        return {"ok": True, "dry_run": True}

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"ok": False, "description": raw[:500]}
        if e.code == 401:
            sys.exit("401 Unauthorized — the bot token is invalid or was revoked. "
                     "Get a fresh one from @BotFather.")
        if e.code == 403:
            sys.exit("403 Forbidden — the bot cannot message this chat. Open a chat "
                     "with the bot and press Start, then retry.")
        sys.exit(f"HTTP {e.code} from {safe_url}:\n{payload.get('description', raw[:500])}")
    except urllib.error.URLError as e:
        sys.exit(
            f"Network error reaching {api}: {e.reason}\n"
            "This environment cannot reach the Telegram API. Run this command on a "
            "machine with normal internet access (laptop / VPS / CI runner)."
        )


def chunk_text(text: str, limit: int = 4000) -> list[str]:
    """Split at paragraph/line boundaries to stay under Telegram's 4096 limit."""
    out, buf = [], ""
    for para in text.split("\n\n"):
        block = para if not buf else "\n\n" + para
        if len(buf) + len(block) <= limit:
            buf += block
            continue
        if buf:
            out.append(buf)
        while len(para) > limit:
            out.append(para[:limit])
            para = para[limit:]
        buf = para
    if buf:
        out.append(buf)
    return out


# ---------------------------------------------------------------- commands
def cmd_ping(args) -> None:
    token, chat, api, store = cfg()
    require_token(token)
    r = call(api, token, "getMe", {}, dry_run=args.dry_run)
    if r.get("dry_run"):
        return
    me = r.get("result", {})
    print(f"bot ok: @{me.get('username')} (id {me.get('id')})")
    if not chat:
        print("TELEGRAM_CHAT_ID not set — `send`/`upload` will fail. "
              "Message the bot once, then read the chat id from getUpdates.")
        return
    r = call(api, token, "sendMessage",
             {"chat_id": chat, "text": "✅ telegram_store: connection verified."},
             dry_run=args.dry_run)
    if not r.get("dry_run"):
        print(f"message delivered to chat {chat}")


def cmd_send(args) -> None:
    token, chat, api, store = cfg()
    require_token(token)
    if not chat:
        sys.exit("Missing TELEGRAM_CHAT_ID (see config/.env.example).")
    text = " ".join(args.text)
    if not text:
        sys.exit("Nothing to send.")
    for part in chunk_text(text):
        r = call(api, token, "sendMessage", {"chat_id": chat, "text": part},
                 dry_run=args.dry_run)
        if not r.get("dry_run") and not r.get("ok"):
            sys.exit(f"send failed: {r.get('description')}")
    print("sent" if not args.dry_run else "dry-run only")


def cmd_upload(args) -> None:
    token, chat, api, store = cfg()
    require_token(token)
    if not chat:
        sys.exit("Missing TELEGRAM_CHAT_ID (see config/.env.example).")
    path = Path(args.path).expanduser()
    if not path.exists():
        sys.exit(f"No such file: {path}")
    size = path.stat().st_size
    if size > MAX_UPLOAD:
        sys.exit(f"{path.name} is {size / 1e6:.1f} MB — bots can upload max 50 MB. "
                 "Split it or upload to Drive/Dropbox and send the link.")

    caption = args.caption or f"{path.name} · {size} bytes · {time.strftime('%Y-%m-%d %H:%M')}"
    data = path.read_bytes()
    r = call(api, token, "sendDocument",
             {"chat_id": chat, "caption": caption[:1000]},
             files={"document": (path.name, data)}, dry_run=args.dry_run)
    if r.get("dry_run"):
        return
    if not r.get("ok"):
        sys.exit(f"upload failed: {r.get('description')}")
    doc = (r.get("result") or {}).get("document", {})
    entry = {
        "name": path.name,
        "bytes": size,
        "sha_hint": doc.get("file_unique_id", ""),
        "file_id": doc.get("file_id", ""),
        "message_id": (r.get("result") or {}).get("message_id"),
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "caption": caption,
    }
    m = load_manifest(store)
    m["entries"] = [e for e in m["entries"] if e["name"] != path.name] + [entry]
    save_manifest(store, m)
    print(f"uploaded {path.name} ({size} bytes) — manifest: {manifest_path(store)}")


def cmd_backup(args) -> None:
    token, chat, api, store = cfg()
    require_token(token)
    targets = args.paths or ["skills", "scripts", "config", "README.md", ".gitignore"]
    out = store / f"begonia-notes-{time.strftime('%Y%m%d-%H%M%S')}.zip"
    store.mkdir(parents=True, exist_ok=True)
    added = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for t in targets:
            p = (ROOT / t).resolve()
            if not p.exists():
                continue
            if p.is_file():
                z.write(p, p.relative_to(ROOT))
                added += 1
            else:
                for f in p.rglob("*"):
                    if f.is_file() and "__pycache__" not in f.parts:
                        z.write(f, f.relative_to(ROOT))
                        added += 1
    print(f"archived {added} files -> {out} ({out.stat().st_size} bytes)")
    if args.no_send:
        return
    args.path, args.caption = str(out), f"Notes backup · {added} files"
    cmd_upload(args)


def cmd_list(args) -> None:
    _, _, _, store = cfg()
    m = load_manifest(store)
    if not m["entries"]:
        print("manifest empty — nothing uploaded yet")
        return
    for e in m["entries"]:
        print(f"{e['uploaded_at']}  {e['name']:40} {e['bytes']:>12} bytes  msg {e.get('message_id')}")


def cmd_fetch(args) -> None:
    token, _, api, store = cfg()
    require_token(token)
    m = load_manifest(store)
    entry = next((e for e in m["entries"] if e["name"] == args.name), None)
    if not entry:
        sys.exit(f"'{args.name}' not in manifest. Known: "
                 + ", ".join(e["name"] for e in m["entries"]) or "(none)")
    r = call(api, token, "getFile", {"file_id": entry["file_id"]}, dry_run=args.dry_run)
    if r.get("dry_run"):
        return
    if not r.get("ok"):
        sys.exit(f"getFile failed: {r.get('description')}")
    remote = r["result"]["file_path"]
    size = r["result"].get("file_size", 0)
    if size > 20 * 1024 * 1024:
        sys.exit("Telegram bots can only download files up to 20 MB via getFile.")
    url = f"{api}/file/bot{token}/{remote}"
    out = Path(args.out or ".").expanduser() / entry["name"]
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=180) as resp, open(out, "wb") as f:
            f.write(resp.read())
    except urllib.error.URLError as e:
        sys.exit(f"download failed: {e.reason}")
    print(f"downloaded -> {out} ({out.stat().st_size} bytes)")


def cmd_delete_log(args) -> None:
    _, _, _, store = cfg()
    p = manifest_path(store)
    if p.exists():
        p.unlink()
    print("local manifest cleared (messages stay in the chat)")


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="Store notes/artifacts in a Telegram bot chat")
    ap.add_argument("--dry-run", action="store_true", help="print requests, send nothing")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="verify token + chat")
    s = sub.add_parser("send", help="send text")
    s.add_argument("text", nargs="+")
    s = sub.add_parser("upload", help="upload one file")
    s.add_argument("path")
    s.add_argument("--caption")
    s = sub.add_parser("backup", help="zip notes and upload")
    s.add_argument("paths", nargs="*")
    s.add_argument("--no-send", action="store_true")
    s.add_argument("--caption")
    sub.add_parser("list", help="show local manifest")
    s = sub.add_parser("fetch", help="download a file back")
    s.add_argument("name")
    s.add_argument("--out", default=".")
    sub.add_parser("delete-log", help="clear the local manifest")

    args = ap.parse_args()
    {"ping": cmd_ping, "send": cmd_send, "upload": cmd_upload, "backup": cmd_backup,
     "list": cmd_list, "fetch": cmd_fetch, "delete-log": cmd_delete_log}[args.cmd](args)


if __name__ == "__main__":
    main()
