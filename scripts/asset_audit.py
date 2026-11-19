"""Fail the build if the packaged HTML references a file that is not shipped.

Usage: asset_audit.py <index.html> <asset_root_dir> [more files to check]

Every relative src/href/url() the page asks for must exist under asset_root,
otherwise the WebView shows a broken-image box and the UI silently half-renders.
"""
import os
import re
import sys

SAFE_PREFIX = ("http://", "https://", "data:", "#", "javascript:", "mailto:", "tel:", "blob:")

REF_PATTERNS = [
    re.compile(r'(?:src|href)\s*=\s*"([^"]+)"'),
    re.compile(r"(?:src|href)\s*=\s*'([^']+)'"),
    re.compile(r"url\(\s*'([^']+)'\s*\)"),
    re.compile(r'url\(\s*"([^"]+)"\s*\)'),
]


def refs_in(html: str):
    out = set()
    for pat in REF_PATTERNS:
        for m in pat.finditer(html):
            v = m.group(1).strip()
            if v and not v.startswith(SAFE_PREFIX):
                out.add(v.split("?")[0].split("#")[0])
    return out


def main() -> int:
    index = sys.argv[1]
    root = sys.argv[2]
    extra = sys.argv[3:]

    html = open(index, encoding="utf-8", errors="replace").read()
    wanted = refs_in(html)
    for f in extra:
        if os.path.exists(f):
            wanted |= refs_in(open(f, encoding="utf-8", errors="replace").read())

    missing = []
    for r in sorted(wanted):
        if r in ("", "/", "./"):
            continue
        path = os.path.normpath(os.path.join(root, r.lstrip("/")))
        if not os.path.exists(path):
            missing.append(r)

    print(f"relative references found : {len(wanted)}")
    for r in sorted(wanted):
        mark = "MISSING" if r in missing else "ok"
        print(f"  [{mark:7s}] {r}")

    if missing:
        print(f"\nFAIL: {len(missing)} referenced file(s) not shipped: {', '.join(missing)}")
        return 1
    print("\nPASS: every referenced asset is present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
