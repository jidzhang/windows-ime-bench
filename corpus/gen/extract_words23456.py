# 生成 corpus/words23456.txt（2/3/4/5/6 字高频词各 150 个 = 750 词）
# 与 words234 同源同口径（rime-frost base+ext 权重排序），只多两档长度。
# 同时生成 <stem>.pin.tsv gold 读音 sidecar（与 words234 同格式）。
#
# 用法：python extract_words23456.py <base.dict.yaml> <ext.dict.yaml> <pinyin.txt> <out_dir>
# 输出：<out_dir>/words23456.txt 与 <out_dir>/words23456.pin.tsv
import io
import os
import sys

TONE = {'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a', 'ē': 'e', 'é': 'e', 'ě': 'e',
        'è': 'e', 'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i', 'ō': 'o', 'ó': 'o',
        'ǒ': 'o', 'ò': 'o', 'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u', 'ǖ': 'v',
        'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v', 'ü': 'v', 'ń': 'n', 'ň': 'n', 'ǹ': 'n', 'ḿ': 'm'}


def strip_tone(s):
    return ''.join(TONE.get(c, c) for c in s.lower())


def main(base_path, ext_path, pinyin_path, out_dir):
    rd = {}
    for line in io.open(pinyin_path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        code, rest = line.split(':', 1)
        if '#' in rest:
            rest = rest[:rest.index('#')]
        f = [x.strip() for x in rest.split(',')]
        try:
            ch = chr(int(code[2:], 16))
        except ValueError:
            continue
        rd[ch] = strip_tone(f[0])

    cands = {2: [], 3: [], 4: [], 5: [], 6: []}
    for path in (base_path, ext_path):
        for line in io.open(path, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line or line.startswith('#') or line.startswith('---') or line.startswith('...'):
                continue
            p = line.split('\t')
            if len(p) < 3:
                continue
            w, wt = p[0], p[2]
            if not all(c in rd and rd[c] for c in w):
                continue
            try:
                wt = int(wt)
            except ValueError:
                continue
            if len(w) in cands:
                cands[len(w)].append((wt, w))

    words = []
    for n in (2, 3, 4, 5, 6):
        seen = set()
        for wt, w in sorted(cands[n], key=lambda x: (-x[0], x[1])):
            if w in seen:
                continue
            seen.add(w)
            words.append(w)
            if len(seen) >= 150:
                break

    os.makedirs(out_dir, exist_ok=True)
    with io.open(os.path.join(out_dir, 'words23456.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(words) + '\n')

    # gold 读音 sidecar：每词一行「词<TAB>连续小写拼音」
    with io.open(os.path.join(out_dir, 'words23456.pin.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# gold pinyin sidecar (frozen; audit with gold_pinyin audit)\n')
        for w in words:
            f.write('%s\t%s\n' % (w, ''.join(rd[c] for c in w)))

    print('words=%d (per-length 150) -> %s' % (len(words), out_dir))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
