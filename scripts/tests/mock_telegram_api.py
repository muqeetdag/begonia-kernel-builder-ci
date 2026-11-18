#!/usr/bin/env python3
"""Minimal mock of the Telegram Bot API, for testing telegram_store.py offline.

Serves getMe / sendMessage / sendDocument / getFile / file download.
Run:  python3 scripts/tests/mock_telegram_api.py --port 8099
Then: TELEGRAM_API_BASE=http://127.0.0.1:8099 TELEGRAM_BOT_TOKEN=test \
      TELEGRAM_CHAT_ID=123 python3 scripts/telegram_store.py ping
"""
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = {"messages": [], "files": {}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        m = re.match(r"^/bot([^/]+)/(\w+)$", self.path)
        if not m:
            return self._json({"ok": False, "description": "bad path"}, 404)
        token, method = m.groups()
        if token != "test":
            return self._json({"ok": False, "description": "Unauthorized"}, 401)

        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        ctype = self.headers.get("Content-Type", "")

        if method == "getMe":
            return self._json({"ok": True, "result": {"id": 42, "username": "mock_bot"}})

        if method == "sendMessage":
            if "multipart" in ctype:
                fields = dict(re.findall(rb'name="(\w+)"\r\n\r\n(.*?)\r\n--', raw))
                fields = {k.decode(): v.decode(errors="replace") for k, v in fields.items()}
            else:
                from urllib.parse import parse_qs
                fields = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
            if "chat_id" not in fields:
                return self._json({"ok": False, "description": "chat_id missing"}, 400)
            STATE["messages"].append(("text", fields))
            return self._json({"ok": True, "result": {"message_id": len(STATE["messages"])}})

        if method == "sendDocument":
            boundary = re.search(r"boundary=(\S+)", ctype)
            parts = raw.split(b"--" + boundary.group(1).encode()) if boundary else []
            name, payload = "file.bin", b""
            for part in parts:
                head, _, body = part.partition(b"\r\n\r\n")
                fn = re.search(rb'filename="([^"]+)"', head)
                if fn:
                    name = fn.group(1).decode()
                    payload = body.rsplit(b"\r\n", 1)[0]  # drop trailing CRLF
            file_id = f"FILE{len(STATE['files']) + 1}"
            STATE["files"][file_id] = (name, payload)
            STATE["messages"].append(("document", {"name": name, "bytes": len(payload)}))
            return self._json({"ok": True, "result": {
                "message_id": len(STATE["messages"]),
                "document": {"file_id": file_id, "file_unique_id": file_id + "u",
                             "file_name": name, "file_size": len(payload)}}})

        if method == "getFile":
            from urllib.parse import parse_qs
            fid = parse_qs(raw.decode()).get("file_id", [""])[0]
            if fid not in STATE["files"]:
                return self._json({"ok": False, "description": "file not found"}, 400)
            return self._json({"ok": True, "result": {
                "file_id": fid, "file_path": f"documents/{fid}",
                "file_size": len(STATE["files"][fid][1])}})

        return self._json({"ok": False, "description": f"unknown method {method}"}, 404)

    def do_GET(self):
        m = re.match(r"^/file/bot([^/]+)/documents/(\w+)$", self.path)
        if not m or m.group(1) != "test" or m.group(2) not in STATE["files"]:
            return self._json({"ok": False, "description": "not found"}, 404)
        payload = STATE["files"][m.group(2)][1]
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    a = ap.parse_args()
    print(f"mock Telegram Bot API on http://127.0.0.1:{a.port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", a.port), Handler).serve_forever()
