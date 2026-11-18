#!/usr/bin/env python3
"""APK intake & triage — what runs the moment you drop an APK in the repo.

Does everything that needs no Java: integrity hashing, ZIP/DEX inventory,
native ABI detection, manifest/ARSC extraction, split-bundle detection, and
(if androguard is installed) package identity + permission dump.

Usage:
    python3 scripts/apk_intake.py path/to/app.apk [--out analysis/app]

Writes a report to <out>/report.md and extracts AndroidManifest.xml,
resources.arsc and the raw DEX list. Never executes anything from the APK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

APK_MAGIC = b"PK\x03\x04"
SUSPICIOUS_PERMS = {
    "android.permission.READ_SMS", "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS", "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA", "android.permission.READ_CONTACTS",
    "android.permission.READ_CALL_LOG", "android.permission.CALL_PHONE",
    "android.permission.ACCESS_FINE_LOCATION", "android.permission.READ_PHONE_STATE",
    "android.permission.SYSTEM_ALERT_WINDOW", "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.BIND_ACCESSIBILITY_SERVICE", "android.permission.QUERY_ALL_PACKAGES",
    "android.permission.MANAGE_EXTERNAL_STORAGE", "android.permission.PACKAGE_USAGE_STATS",
}
NATIVE_HINTS = re.compile(r"\.so$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def androguard_python() -> str | None:
    """Find an interpreter that can import androguard."""
    for cand in (Path.home() / ".local/apk-venv/bin/python", Path(sys.executable)):
        if cand.exists():
            try:
                subprocess.run([str(cand), "-c", "import androguard"],
                               check=True, capture_output=True, timeout=60)
                return str(cand)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
    return None


def androguard_info(py: str, apk: Path) -> dict:
    """Package identity + permissions via androguard (no Java needed)."""
    code = (
        "import json,sys\n"
        "from androguard.core.apk import APK\n"
        "a=APK(sys.argv[1])\n"
        "print(json.dumps({'package':a.get_package(),'app_name':a.get_app_name(),\n"
        "'version_name':a.get_androidversion_name(),'version_code':a.get_androidversion_code(),\n"
        "'min_sdk':a.get_min_sdk_version(),'target_sdk':a.get_target_sdk_version(),\n"
        "'permissions':a.get_permissions(),'activities':a.get_activities()[:40],\n"
        "'services':a.get_services()[:40],'receivers':a.get_receivers()[:40],\n"
        "'is_signed':a.is_signed(),'cert':str(a.get_certificates()[0].subject) if a.get_certificates() else None}))\n"
    )
    try:
        r = subprocess.run([py, "-c", code, str(apk)], capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            return {"error": (r.stderr or "").strip().splitlines()[-1][:300] if r.stderr else "failed"}
        return json.loads(r.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "androguard timed out"}
    except json.JSONDecodeError:
        return {"error": "unparseable androguard output"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Triage an APK without Java")
    ap.add_argument("apk")
    ap.add_argument("--out", default=None, help="output dir (default analysis/<name>)")
    args = ap.parse_args()

    apk = Path(args.apk).expanduser().resolve()
    if not apk.exists():
        sys.exit(f"No such file: {apk}")
    out = Path(args.out) if args.out else Path("analysis") / apk.stem
    out.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    def p(s: str = "") -> None:
        lines.append(s)
        print(s)

    size = apk.stat().st_size
    p(f"# APK intake — {apk.name}")
    p()
    p(f"- path: `{apk}`")
    p(f"- size: {size:,} bytes ({size / 1e6:.2f} MB)")
    p(f"- sha256: `{sha256(apk)}`")

    with apk.open("rb") as f:
        magic = f.read(4)
    if magic != APK_MAGIC:
        p(f"- **not a ZIP/APK** (magic {magic!r}) — stop here")
        (out / "report.md").write_text("\n".join(lines) + "\n")
        sys.exit(1)

    kind = {".apk": "APK", ".apks": "APK set (split bundle)",
            ".xapk": "XAPK (split bundle)", ".aab": "Android App Bundle"}
    p(f"- container: {kind.get(apk.suffix.lower(), 'ZIP (unknown extension)')}")

    try:
        z = zipfile.ZipFile(apk)
    except zipfile.BadZipFile:
        sys.exit("Corrupt ZIP — truncated download?")

    names = z.namelist()
    dex = sorted(n for n in names if re.fullmatch(r"classes\d*\.dex", n))
    libs = sorted(n for n in names if n.startswith("lib/") and NATIVE_HINTS.search(n))
    abis = sorted({n.split("/")[1] for n in libs if n.count("/") >= 2})
    apks_in_bundle = sorted(n for n in names if n.endswith(".apk"))

    p(f"- entries: {len(names)}")
    p(f"- dex files: {len(dex)} {dex if dex else ''}")
    p(f"- native ABIs: {abis or 'none (pure Java/Kotlin)'}")
    p(f"- native libs: {len(libs)}")
    if apks_in_bundle:
        p(f"- contains {len(apks_in_bundle)} split APK(s): {apks_in_bundle[:8]}")
    for marker in ("AndroidManifest.xml", "resources.arsc", "META-INF/"):
        present = any(n.startswith(marker) for n in names)
        p(f"- {marker}: {'yes' if present else 'NO'}")

    # extract the interesting binaries
    ext = out / "extracted"
    ext.mkdir(exist_ok=True)
    for n in ("AndroidManifest.xml", "resources.arsc"):
        if n in names:
            (ext / n).write_bytes(z.read(n))
    if dex:
        (out / "dex-list.txt").write_text("\n".join(dex) + "\n")

    # --- androguard (no Java needed) ---
    py = androguard_python()
    p()
    if py:
        p("## Package identity (androguard)")
        p()
        info = androguard_info(py, apk)
        if "error" in info:
            p(f"- androguard could not parse this APK: {info['error']}")
            p("- (common for split bundles / unusual manifests — the DEX is still extractable)")
        else:
            p(f"- package: `{info.get('package')}`")
            p(f"- app name: {info.get('app_name')}")
            p(f"- version: {info.get('version_name')} (code {info.get('version_code')})")
            p(f"- minSdk {info.get('min_sdk')} / targetSdk {info.get('target_sdk')}")
            p(f"- signed: {info.get('is_signed')} — cert: {info.get('cert')}")
            perms = info.get("permissions") or []
            flagged = sorted(set(perms) & SUSPICIOUS_PERMS)
            p(f"- permissions: {len(perms)}")
            if flagged:
                p(f"- **sensitive permissions**: {', '.join(flagged)}")
            for k in ("activities", "services", "receivers"):
                v = info.get(k) or []
                if v:
                    p(f"- {k} ({len(v)}): {', '.join(v[:6])}{' …' if len(v) > 6 else ''}")
            (out / "androguard.json").write_text(json.dumps(info, indent=2))
    else:
        p("## Package identity")
        p()
        p("- androguard not available (create it: python3 -m venv ~/.local/apk-venv && "
          "~/.local/apk-venv/bin/pip install androguard)")

    # --- toolchain availability ---
    p()
    p("## Deeper analysis tooling")
    p()
    for tool, why in (("jadx", "Java decompile → readable source"),
                      ("apktool", "full resources + smali rebuild"),
                      ("java", "needed by jadx/apktool")):
        found = shutil.which(tool) or (Path.home() / f".local/jdk/bin/{tool}").exists()
        p(f"- {tool}: {'available' if found else 'MISSING'} — {why}")

    p()
    p(f"_Report: `{out/'report.md'}` · extracted: `{ext}`_")
    (out / "report.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
