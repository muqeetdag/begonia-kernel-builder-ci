"""zipalign equivalent: stores resources.arsc + *.dex uncompressed and pads each
local header so those entries begin on a 4-byte boundary.

Android 11+ rejects an APK whose resources.arsc is compressed or not 4-byte
aligned, showing only "App not installed". apksigner does not fix this.
"""
import struct, sys, zlib, zipfile

ALIGN = 4
FORCE_STORE = ("resources.arsc",)


def pad_to(offset_after_header: int) -> bytes:
    """Return an extra field making the following data 4-byte aligned."""
    for cand in (0, 4, 5, 6, 7):
        if (offset_after_header + cand) % ALIGN == 0:
            if cand == 0:
                return b""
            body = cand - 4
            return struct.pack("<HH", 0xD935, body) + b"\x00" * body
    raise AssertionError("unreachable")


def align_apk(src: str, dst: str) -> None:
    zin = zipfile.ZipFile(src)
    out = open(dst, "wb")
    central = []

    for info in zin.infolist():
        name = info.filename
        is_dir = name.endswith("/")
        data = b"" if is_dir else zin.read(name)
        store = is_dir or name in FORCE_STORE or name.endswith(".dex")

        if store:
            method, payload = zipfile.ZIP_STORED, data
        else:
            c = zlib.compressobj(9, zlib.DEFLATED, -15)
            method, payload = zipfile.ZIP_DEFLATED, c.compress(data) + c.flush()

        crc = zlib.crc32(data) & 0xFFFFFFFF
        name_b = name.encode("utf-8")
        offset = out.tell()
        extra = pad_to(offset + 30 + len(name_b))

        out.write(struct.pack(
            "<IHHHHHIIIHH", 0x04034B50, 20, 0, method, 0, 0x21,
            crc, len(payload), len(data), len(name_b), len(extra),
        ) + name_b + extra)

        if store:
            assert out.tell() % ALIGN == 0, f"{name} misaligned at {out.tell()}"
        out.write(payload)
        central.append((name_b, method, crc, len(payload), len(data), offset, extra))

    cd_start = out.tell()
    for name_b, method, crc, csize, usize, offset, extra in central:
        out.write(struct.pack(
            "<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 0, method, 0, 0x21,
            crc, csize, usize, len(name_b), len(extra), 0, 0, 0,
            0o644 << 16, offset,
        ) + name_b + extra)
    cd_size = out.tell() - cd_start

    out.write(struct.pack("<IHHHHIIH", 0x06054B50, 0, 0,
                          len(central), len(central), cd_size, cd_start, 0))
    out.close()
    zin.close()


if __name__ == "__main__":
    align_apk(sys.argv[1], sys.argv[2])
