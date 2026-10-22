"""Liste le contenu d'une ISO PS2 (ISO9660/Joliet) et extrait des fichiers.

Usage:
  python list_iso.py <iso>                        # liste l'arborescence + tailles
  python list_iso.py <iso> --extract PATTERN      # extrait les fichiers matching (fnmatch, ex '*.bin') dans work/extracted/
"""
import sys, os, fnmatch
import pycdlib

def main():
    iso_path = sys.argv[1]
    pattern = None
    if '--extract' in sys.argv:
        pattern = sys.argv[sys.argv.index('--extract') + 1]

    iso = pycdlib.PyCdlib()
    fp = open(iso_path, 'rb')
    iso.open_fp(fp)

    extract_root = None
    if pattern:
        extract_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'work', 'extracted'))
        os.makedirs(extract_root, exist_ok=True)

    total_files = 0
    walk_kw = {'iso_path': '/'} if not iso.has_joliet() else {'joliet_path': '/'}
    for path, dirs, files in iso.walk(**walk_kw):
        d = path.replace('\\', '/')
        for f in files:
            name = f if isinstance(f, str) else str(f)
            full = (d + '/' + name).lstrip('/')
            total_files += 1
            print('F', full)
            if extract_root and fnmatch.fnmatch(name.lower(), pattern.lower()):
                dest_dir = os.path.join(extract_root, os.path.dirname(full))
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest_dir, name)
                try:
                    iso.get_file_from_iso(dest, full)
                    print('  -> EXTRACTED', dest)
                except Exception as e:
                    print('  !! extract failed:', e)
    print(f'--- total files: {total_files}')
    fp.close()

if __name__ == '__main__':
    main()
