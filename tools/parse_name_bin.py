"""Parse NAME.BIN: table de 64-byte records (8B texte SJIS + null + padding 0xCC)."""
import sys, os, json

def parse(path):
    data = open(path, 'rb').read()
    recs = []
    n = len(data) // 64
    for i in range(n):
        off = i * 64
        raw = data[off:off+64]
        # texte jusqu'au null
        end = raw.find(b'\x00')
        text_bytes = raw[:end] if end != -1 else raw
        try:
            text = text_bytes.decode('shift_jis')
        except Exception:
            text = text_bytes.decode('shift_jis', 'replace')
        pad_ok = all(b == 0xCC for b in raw[end+1:])
        recs.append({'index': i, 'offset': off, 'text': text, 'pad_0xcc': pad_ok})
    return recs

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'work/extracted/DATA/NAME.BIN'
    recs = parse(path)
    out = os.path.join(os.path.dirname(__file__), '..', 'strings', 'ja', 'name.bin.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)
    print(f'{len(recs)} records -> {out}')
    for r in recs[:10]:
        print(r['index'], repr(r['text']), 'pad_ok=', r['pad_0xcc'])
    # stats padding
    bad = [r['index'] for r in recs if not r['pad_0xcc']]
    print('records avec padding non-0xCC:', len(bad), bad[:20])
