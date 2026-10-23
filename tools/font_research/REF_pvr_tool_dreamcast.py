#!/usr/bin/env python3
"""PVR texture decode/encode (Dreamcast).

Supported:
  - PAL8 twiddled (with external PVPL palette file)
  - ARGB1555 / ARGB4444 / RGB565 square twiddled and rectangle

Commands:
  decode <pvr> <out.png> [--pal PALETTE.PVP]
  encode <edited.png> <original.pvr> <out.pvr> [--pal PALETTE.PVP]
      Re-encodes the PNG in the ORIGINAL file's exact format and size.
      Output is byte-length-identical to the original (safe for fixed-place
      patching). PAL8 pixels are quantized to the palette.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image


def _untwiddle(x: int, y: int, bits: int = 10) -> int:
    v = 0
    for b in range(bits):
        v |= ((y >> b) & 1) << (2 * b)
        v |= ((x >> b) & 1) << (2 * b + 1)
    return v


def load_pvp(path: Path):
    d = path.read_bytes()
    if d[:4] != b"PVPL":
        raise ValueError("not a PVPL palette")
    count = struct.unpack_from("<H", d, 12)[0] or 256
    pal = []
    for i in range(count):
        b, g, r, a = d[16 + i * 4 : 16 + i * 4 + 4]
        pal.append((r, g, b, a))
    return pal


def parse_pvr(d: bytes):
    i = d.find(b"PVRT")
    if i < 0:
        raise ValueError("no PVRT chunk")
    size, px, df, _, w, h = struct.unpack_from("<IBBHHH", d, i + 4)
    return i, px, df, w, h, i + 16


def px16_to_rgba(v: int, px: int):
    if px == 0:  # ARGB1555
        return ((v >> 10 & 31) << 3, (v >> 5 & 31) << 3, (v & 31) << 3, 255 if v & 0x8000 else 0)
    if px == 1:  # RGB565
        return ((v >> 11 & 31) << 3, (v >> 5 & 63) << 2, (v & 31) << 3, 255)
    if px == 2:  # ARGB4444
        return ((v >> 8 & 15) * 17, (v >> 4 & 15) * 17, (v & 15) * 17, (v >> 12 & 15) * 17)
    raise ValueError(f"unsupported 16bpp format {px}")


def rgba_to_px16(r: int, g: int, b: int, a: int, px: int) -> int:
    if px == 0:
        return (0x8000 if a >= 128 else 0) | ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)
    if px == 1:
        return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
    if px == 2:
        return ((a >> 4) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
    raise ValueError(f"unsupported 16bpp format {px}")


def decode(pvr_path: Path, out_path: Path, pal_path: Path | None):
    d = pvr_path.read_bytes()
    _, px, df, w, h, off = parse_pvr(d)
    img = Image.new("RGBA", (w, h))
    P = img.load()
    if df in (5, 7):  # paletted twiddled
        if pal_path is None:
            raise SystemExit("paletted texture: pass --pal PALETTE.PVP")
        pal = load_pvp(pal_path)
        for y in range(h):
            for x in range(w):
                P[x, y] = pal[d[off + _untwiddle(x, y)]]
    elif df in (1, 2, 13):  # 16bpp twiddled
        for y in range(h):
            for x in range(w):
                v = struct.unpack_from("<H", d, off + _untwiddle(x, y) * 2)[0]
                P[x, y] = px16_to_rgba(v, px)
    elif df in (9, 11):  # 16bpp rectangle
        for y in range(h):
            for x in range(w):
                v = struct.unpack_from("<H", d, off + (y * w + x) * 2)[0]
                P[x, y] = px16_to_rgba(v, px)
    else:
        raise SystemExit(f"unsupported data format {df}")
    img.save(out_path)
    print(f"decoded {pvr_path} ({w}x{h} px={px} df={df}) -> {out_path}")


def encode(png_path: Path, orig_path: Path, out_path: Path | None, pal_path: Path | None) -> bytes:
    orig = bytearray(orig_path.read_bytes())
    _, px, df, w, h, off = parse_pvr(bytes(orig))
    img = Image.open(png_path).convert("RGBA")
    if img.size != (w, h):
        raise SystemExit(f"PNG must be {w}x{h}, got {img.size}")
    P = img.load()
    if df in (5, 7):
        if pal_path is None:
            raise SystemExit("paletted texture: pass --pal PALETTE.PVP")
        pal = load_pvp(pal_path)

        # nearest-color quantization (full RGBA distance; palettes can contain
        # semi-transparent entries)
        def nearest(c):
            r, g, b, a = c
            best, bi = 1 << 30, 0
            for i, (pr, pg, pb, pa) in enumerate(pal):
                dd = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2 + 2 * (a - pa) ** 2
                if dd < best:
                    best, bi = dd, i
                    if dd == 0:
                        break
            return bi

        cache: dict[tuple, int] = {}
        for y in range(h):
            for x in range(w):
                c = P[x, y]
                if c not in cache:
                    cache[c] = nearest(c)
                orig[off + _untwiddle(x, y)] = cache[c]
    elif df in (1, 2, 13):
        for y in range(h):
            for x in range(w):
                struct.pack_into("<H", orig, off + _untwiddle(x, y) * 2,
                                 rgba_to_px16(*P[x, y], px))
    elif df in (9, 11):
        for y in range(h):
            for x in range(w):
                struct.pack_into("<H", orig, off + (y * w + x) * 2,
                                 rgba_to_px16(*P[x, y], px))
    else:
        raise SystemExit(f"unsupported data format {df}")
    data = bytes(orig)
    assert len(data) == orig_path.stat().st_size, "size changed - refusing"
    if out_path:
        out_path.write_bytes(data)
        print(f"encoded {png_path} -> {out_path} ({len(data)} bytes)")
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode")
    d.add_argument("pvr", type=Path)
    d.add_argument("out", type=Path)
    d.add_argument("--pal", type=Path)
    e = sub.add_parser("encode")
    e.add_argument("png", type=Path)
    e.add_argument("orig", type=Path)
    e.add_argument("out", type=Path)
    e.add_argument("--pal", type=Path)
    a = ap.parse_args()
    if a.cmd == "decode":
        decode(a.pvr, a.out, a.pal)
    else:
        encode(a.png, a.orig, a.out, a.pal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
