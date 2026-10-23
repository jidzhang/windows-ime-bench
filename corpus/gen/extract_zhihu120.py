# 从完整版语料截取 corpus/zhihu120.txt
# 源：作者自维护的 zhihu3466 整句语料（未公开仓库；仓库内直接提供 zhihu120 成品，
#     外部使用者无需此上游，直接用 corpus/zhihu120.txt 即可）
# 口径：取纯汉字（全部字有拼音读音）的行，前 120 句；汉字间不留空白。
# 用法：python extract_zhihu120.py <eval-zhihu-3466.txt> <pinyin.txt> > zhihu120.txt
import io
import sys

TONE = {'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a', 'ē': 'e', 'é': 'e', 'ě': 'e',
        'è': 'e', 'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i', 'ō': 'o', 'ó': 'o',
        'ǒ': 'o', 'ò': 'o', 'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u', 'ǖ': 'v',
        'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v', 'ü': 'v', 'ń': 'n', 'ň': 'n', 'ǹ': 'n', 'ḿ': 'm'}


def strip_tone(s):
    return ''.join(TONE.get(c, c) for c in s.lower())


def main(corpus_path, pinyin_path):
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
    out = []
    for line in io.open(corpus_path, encoding='utf-8'):
        s = line.strip()
        if not s:
            continue
        if all(c in rd and rd[c] for c in s):
            out.append(s)
        if len(out) >= 120:
            break
    sys.stdout.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
