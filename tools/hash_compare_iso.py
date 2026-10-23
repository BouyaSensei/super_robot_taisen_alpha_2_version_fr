"""Compare tous les fichiers de l'ISO JP vs ISO patchee EN (hash SHA-256).
Extrait chaque fichier des deux cotes et liste les differences.
Sortie: work/modified_files.txt + table dans stdout."""
import pycdlib, os, hashlib
from pycdlib import utils

JP_ISO = 'Dai-2-Ji Super Robot Taisen Alpha (Japan) (SLPS-25228)/Dai-2-Ji Super Robot Taisen Alpha (Japan) (SLPS-25228).iso'
EN_ISO = r'C:/Users/ax_95/AppData/Local/hermes/cache/scratch/xdelta_out/patched_en.iso'

def all_files(iso_path):
    iso = pycdlib.PyCdlib()
    fp = open(iso_path, 'rb')
    iso.open_fp(fp)
    files = []
    for path, dirs, fs in iso.walk(iso_path='/'):
        d = path.replace(chr(92), '/')
        for f in fs:
            raw = f if isinstance(f, str) else str(f)
            str_path = '/' + d.strip('/') + '/' + raw
            files.append((raw.split(';')[0], str_path))
    fp.close()
    return files

def hash_all(iso_path, dest_root):
    os.makedirs(dest_root, exist_ok=True)
    iso = pycdlib.PyCdlib()
    fp = open(iso_path, 'rb')
    iso.open_fp(fp)
    out = {}
    for name, str_path in all_files(iso_path):
        dest = os.path.join(dest_root, name.replace('/', '_'))
        if not os.path.exists(dest):
            try:
                iso.get_file_from_iso(dest, iso_path=str_path)
            except Exception as e:
                print('ERR', name, e)
        h = hashlib.sha256(open(dest, 'rb').read()).hexdigest()[:16]
        out[name] = (h, os.path.getsize(dest))
    fp.close()
    return out

def main():
    jp = hash_all(JP_ISO, 'work/iso_files/jp_all')
    en = hash_all(EN_ISO, 'work/iso_files/en_all')
    diffs = []
    for f in sorted(jp):
        if jp[f][0] != en[f][0]:
            diffs.append(f)
            print(f'DIFF  {f:<28} {jp[f][1]:>10}  JP={jp[f][0]} EN={en[f][0]}')
    print(f'\n{len(diffs)} fichiers modifies sur {len(jp)}')
    open('work/modified_files.txt', 'w').write('\n'.join(diffs))

if __name__ == '__main__':
    main()
