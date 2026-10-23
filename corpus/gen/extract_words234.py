# 从上游词库重新生成 corpus/words234.txt（2/3/4 字高频词各 150 个）
# 上游：rime-frost（https://github.com/gaboolic/rime-frost，GPL-3.0）
#   cn_dicts/base.dict.yaml 与 cn_dicts/ext.dict.yaml 的词频权重排序，
#   本脚本只读取词与权重生成词表子集，不复制词库本体。
# 拼音覆盖：mozillazg/pinyin-data pinyin.txt 首读音（与整句语料一致）。
# 用法：python extract_words234.py <base.dict.yaml> <ext.dict.yaml> <pinyin.txt> > words234.txt
import io
import sys

TONE = {'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a', 'ē': 'e', 'é': 'e', 'ě': 'e',
        'è': 'e', 'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i', 'ō': 'o', 'ó': 'o',
        'ǒ': 'o', 'ò': 'o', 'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u', 'ǖ': 'v',
        'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v', 'ü': 'v', 'ń': 'n', 'ň': 'n', 'ǹ': 'n', 'ḿ': 'm'}


def strip_tone(s):
    return ''.join(TONE.get(c, c) for c in s.lower())


def main(base_path, ext_path, pinyin_path):
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
    cands = {2: [], 3: [], 4: []}
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
    out = []
    for n in (2, 3, 4):
        seen = set()
        for wt, w in sorted(cands[n], key=lambda x: (-x[0], x[1])):
            if w in seen:
                continue
            seen.add(w)
            out.append(w)
            if len(seen) >= 150:
                break
    sys.stdout.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
