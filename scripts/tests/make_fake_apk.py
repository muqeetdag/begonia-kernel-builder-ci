#!/usr/bin/env python3
"""Build a *fake* APK-shaped zip for testing scripts/apk_intake.py.

It is a real ZIP with real DEX headers and a real (binary) AXML manifest
block, but it is NOT installable — it exists only so the intake report can
be exercised without a device or a real app.

    python3 scripts/tests/make_fake_apk.py /tmp/demo.apk
"""
import struct
import sys
import zipfile
from pathlib import Path


def fake_dex(classes: int = 3) -> bytes:
    """Minimal dex header (magic, checksum placeholder, version 035)."""
    hdr = bytearray(112)
    hdr[0:8] = b"dex\n035\x00"
    struct.pack_into("<I", hdr, 32, 112)          # file_size
    struct.pack_into("<I", hdr, 36, 0x70)         # header_size
    struct.pack_into("<I", hdr, 40, 0x12345678)   # endian_tag
    return bytes(hdr) + b"\x00" * 256


def fake_axml() -> bytes:
    """Tiny binary XML container shaped like AndroidManifest.xml."""
    return struct.pack("<HHI", 0x0003, 0x0008, 0x00001000) + b"\x00" * 64


def fake_arsc() -> bytes:
    return struct.pack("<HHI", 0x0002, 0x000C, 0x00000200) + b"\x00" * 128


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/demo.apk")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", fake_axml())
        z.writestr("resources.arsc", fake_arsc())
        z.writestr("classes.dex", fake_dex())
        z.writestr("classes2.dex", fake_dex(2))
        z.writestr("lib/arm64-v8a/libnative.so", b"\x7fELF" + b"\x00" * 200)
        z.writestr("lib/armeabi-v7a/libnative.so", b"\x7fELF" + b"\x00" * 180)
        z.writestr("res/layout/activity_main.xml", b"<x/>")
        z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
    print(f"wrote {out} ({out.stat().st_size} bytes) — fake, not installable")


if __name__ == "__main__":
    main()
