# 从 words23456 派生混合输入变体：词的前半部分全拼、后半部分首字母简拼。
#
# 为什么：words234 上各家都 99%+，没有区分度。长词（5/6 字）用户实际常打
# 「前几个字全拼 + 后面简拼」（如 中华人民共和国 → zhonghuarenmghg）。
# 这个考卷专测这类混合输入的选择能力。
#
# 切分规则：前半 ceil(n/2) 个字全拼，后半首字母。
#   4 字 → 2 全拼 + 2 简拼（ruhezuocd）
#   5 字 → 3 全拼 + 2 简拼
#   6 字 → 3 全拼 + 3 简拼
# 音节切分用 pypinyin（比手写状态机可靠）。
#
# 用法：python make_mixed_keys.py <corpus_dir>
import io
import os
import sys

from pypinyin import lazy_pinyin, Style

CORPUS_DIR = sys.argv[1] if len(sys.argv) > 1 else 'corpus'
WORDS = os.path.join(CORPUS_DIR, 'words23456.txt')
OUT_WORDS = os.path.join(CORPUS_DIR, 'words_mixed.txt')
OUT_PIN = os.path.join(CORPUS_DIR, 'words_mixed.pin.tsv')


def main():
    words = [w.strip() for w in io.open(WORDS, encoding='utf-8') if w.strip()]
    out_words, out_pins, skipped = [], [], []
    for w in words:
        sylls = lazy_pinyin(w, style=Style.NORMAL, errors='ignore')
        if len(sylls) != len(w):
            skipped.append(w)
            continue
        # 2/3 字词保持全拼（短词打简拼没有现实意义，且会与 words234 重复）；
        # 4-6 字词做「前半全拼 + 后半简拼」混合。
        if len(w) <= 3:
            key = ''.join(sylls)
        else:
            half = (len(w) + 1) // 2
            key = ''.join(sylls[:half]) + ''.join(s[0] for s in sylls[half:])
        out_words.append(w)
        out_pins.append(key)

    with io.open(OUT_WORDS, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out_words) + '\n')
    with io.open(OUT_PIN, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# gold key sidecar: word<TAB>mixed key (front full pinyin + rear initials)\n')
        for w, k in zip(out_words, out_pins):
            f.write('%s\t%s\n' % (w, k))

    print('mixed corpus: %d words (skipped %d) -> %s' % (len(out_words), len(skipped), OUT_WORDS))
    for w, k in list(zip(out_words, out_pins))[:8]:
        print('  %s -> %s' % (w, k))
    print('  ... 5/6-char examples:')
    for w, k in list(zip(out_words, out_pins))[600:606]:
        print('  %s -> %s' % (w, k))


if __name__ == '__main__':
    main()
