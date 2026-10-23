"""Compare l'ISO JP originale et l'ISO patchee EN, cartographie les regions modifiees par fichier.

Sortie: work/text_map.json — {fichier: [[start, end], ...]} (offsets relatifs au fichier)
+ stats: nb de regions, octets modifies par fichier.
"""
import sys, os, json
import pycdlib

JP = 'Dai-2-Ji Super Robot Taisen Alpha (Japan) (SLPS-25228)/Dai-2-Ji Super Robot Taisen Alpha (Japan) (SLPS-25228).iso'
EN = r'C:/Users/ax_95/AppData/Local/hermes/cache/scratch/xdelta_out/patched_en.iso'
OUT = os.path.join(os.path.dirname(__file__), '..', 'work', 'text_map.json')
CHUNK = 4 * 1024 * 1024

def file_extents(iso_path):
    """Retourne {nom_fichier: (start_byte, size)} pour tous les fichiers de l'ISO."""
    iso = pycdlib.PyCdlib()
    fp = open(iso_path, 'rb')
    iso.open_fp(fp)
    extents = {}
    for path, dirs, files in iso.walk(iso_path='/'):
        d = path.replace('\\', '/')
        for f in files:
            raw = f if isinstance(f, str) else str(f)
            name = '/' + d.strip('/') + '/' + raw
            from pycdlib import utils
            rec = iso._find_iso_record(utils.normpath(name))
            lba = rec.extent_location()
            size = rec.get_data_length()
            extents[raw.split(';')[0]] = (lba * 2048, size)
    fp.close()
    return extents

def diff_regions(jp_path, en_path, chunk=CHUNK):
    """Yield (start, end) des regions differentes entre les deux fichiers."""
    f1 = open(jp_path, 'rb')
    f2 = open(en_path, 'rb')
    off = 0
    region_start = None
    while True:
        b1 = f1.read(chunk)
        b2 = f2.read(chunk)
        if not b1 and not b2:
            break
        if b1 != b2:
            # localise precisement dans le chunk
            n = min(len(b1), len(b2))
            i = 0
            while i < n and b1[i] == b2[i]:
                i += 1
            j = 1
            while j < n - i and b1[n - j] == b2[n - j]:
                j += 1
            s = off + i
            e = off + n - j + 1
            if region_start is None:
                region_start = s
            region_end = e
        else:
            if region_start is not None:
                yield (region_start, region_end)
                region_start = None
        off += chunk
    if region_start is not None:
        yield (region_start, region_end)
    f1.close()
    f2.close()

def main():
    print('Collecte des extents de fichiers...')
    ext = file_extents(JP)
    print(f'{len(ext)} fichiers')

    print('Comparaison des ISO...')
    by_file = {}
    total_regions = 0
    total_bytes = 0
    for s, e in diff_regions(JP, EN):
        # trouve le fichier contenant [s, e)
        placed = False
        for name, (start, size) in ext.items():
            if start <= s < start + size:
                rel_s = max(0, s - start)
                rel_e = min(size, e - start)
                by_file.setdefault(name, []).append([rel_s, rel_e])
                total_regions += 1
                total_bytes += (e - s)
                placed = True
                break
        if not placed:
            by_file.setdefault('<hors-fichiers>', []).append([s, e])
            total_regions += 1
            total_bytes += (e - s)

    # fusion des regions adjacentes par fichier
    for name in by_file:
        rs = sorted(by_file[name])
        merged = []
        for r in rs:
            if merged and r[0] <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], r[1])
            else:
                merged.append(r)
        by_file[name] = merged

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(by_file, f, ensure_ascii=False, indent=1)

    print(f'\nTotal: {total_regions} regions, {total_bytes} octets modifies')
    print(f'{"fichier":<28} {"regions":>8} {"octets":>12}')
    for name in sorted(by_file, key=lambda k: -sum(e - s for s, e in by_file[k])):
        b = sum(e - s for s, e in by_file[name])
        print(f'{name:<28} {len(by_file[name]):>8} {b:>12}')

if __name__ == '__main__':
    main()
