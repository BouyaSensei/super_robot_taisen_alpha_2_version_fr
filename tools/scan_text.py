"""Scanne des binaires PS2 a la recherche de zones de texte japonais.

Detecte deux encodages candidats:
- Shift-JIS: sequences d'octets lead 0x81-0x9F/0xE0-0xEF + trail 0x40-0xFC, ou ASCII imprimable
- UTF-16BE/LE: paires de codepoints CJK/kana (0x3000-0x9FFF)

Pour chaque zone trouvee, affiche offset, longueur, encodage probable et un echantillon.
"""
import sys, os

def is_sjis_run(data, i, min_len=8):
    """Verifie si data[i:] commence par une sequence Shift-JIS plausible de >= min_len caracteres."""
    n = len(data)
    j = i
    chars = 0
    while j < n and chars < min_len:
        b = data[j]
        if 0x20 <= b <= 0x7E:  # ASCII imprimable
            j += 1
            chars += 1
        elif 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEF:  # lead byte SJIS
            if j + 1 < n and (0x40 <= data[j+1] <= 0xFC) and data[j+1] != 0x7F:
                j += 2
                chars += 1
            else:
                break
        elif b in (0x0A, 0x0D):
            j += 1
        else:
            break
    return (j - i) if chars >= min_len else 0

def is_utf16_run(data, i, little, min_chars=8):
    n = len(data)
    j = i
    chars = 0
    while j + 1 < n and chars < min_chars:
        cp = data[j] | (data[j+1] << 8) if little else (data[j] << 8) | data[j+1]
        ok = (0x20 <= cp <= 0x7E) or (0x3000 <= cp <= 0x9FFF) or (0xFF61 <= cp <= 0xFFDC) or cp in (0x3001, 0x3002, 0xFE0F)
        if ok:
            j += 2
            chars += 1
        else:
            break
    return (j - i) if chars >= min_chars else 0

def scan(path, max_zones=60):
    data = open(path, 'rb').read()
    print(f'=== {os.path.basename(path)} ({len(data)} bytes) ===')
    zones = []
    # SJIS
    i = 0
    while i < len(data) - 16:
        L = is_sjis_run(data, i)
        if L >= 16:
            zones.append((i, L, 'sjis'))
            i += L
        else:
            i += 1
    # UTF-16 BE/LE
    for little in (False, True):
        i = 0
        while i < len(data) - 32:
            L = is_utf16_run(data, i, little)
            if L >= 32:
                zones.append((i, L, f'utf16{"LE" if little else "BE"}'))
                i += L
            else:
                i += 2
    zones.sort()
    # fusion des zones qui se chevauchent
    merged = []
    for z in zones:
        if merged and z[0] <= merged[-1][1]:
            m = merged[-1]
            merged[-1] = (m[0], max(m[1], z[1]), m[2] + '+' + z[2])
        else:
            merged.append(list(z))
    print(f'zones: {len(merged)}')
    for off, length, enc in merged[:max_zones]:
        try:
            if 'sjis' in enc:
                sample = data[off:off+length][:40].decode('shift_jis', 'replace')
            else:
                le = 'LE' in enc
                sample = data[off:off+80].decode('utf-16-le' if le else 'utf-16-be', 'replace')[:30]
        except Exception:
            sample = '?'
        print(f'  {off:>10} len={length:<6} {enc:<12} {sample!r}')

if __name__ == '__main__':
    for p in sys.argv[1:]:
        scan(p)
        print()
