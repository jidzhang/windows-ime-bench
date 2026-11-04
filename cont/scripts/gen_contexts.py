# Build context chains for ambiguous target words from real sentences.
# Usage: python gen_contexts.py <ambiguous.tsv> <out.tsv>
# ambiguous.tsv: word<TAB>pinyin (or rank1 output with header word/pinyin/...)
import io
import sys
from pathlib import Path
from collections import defaultdict

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin
import jieba

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
SRC = [
    Path(r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare\data\corpus\zhihu120.txt"),
    Path(r"Z:\dev\IME\windows-ime-bench\corpus\human1023.txt"),
    Path(r"Z:\dev\IME\google-input-tools\reference\corpus\eval-zhihu-3466.txt"),
]


def hanzi(w):
    return all("\u4e00" <= c <= "\u9fff" for c in w)


def load_amb(path):
    amb = {}
    with open(path, encoding="utf-8") as f:
        first = True
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if first and parts[0] == "word":
                first = False
                continue
            first = False
            if len(parts) >= 2 and len(parts[0]) >= 2:
                if len(parts) > 2:
                    # rich format: filter ambiguous rows (last column false/0)
                    exact = parts[-1].strip().lower()
                    if exact not in ("false", "0"):
                        continue
                amb[parts[0]] = parts[1]
    return amb


def main():
    amb = load_amb(sys.argv[1])
    out_path = sys.argv[2]
    per_target = defaultdict(int)
    rows = []
    seen = set()
    for path in SRC:
        if not path.exists():
            continue
        for line in io.open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            words = [w for w in jieba.cut(line) if 2 <= len(w) <= 4 and hanzi(w)]
            for i, w in enumerate(words):
                if w not in amb:
                    continue
                # 2-word chain: prev + target
                if i >= 1 and per_target[w] < 4:
                    ctx = [words[i - 1], w]
                    chain = "".join(ctx)
                    if chain not in seen:
                        py = [sentence_to_continuous_pinyin(x) for x in ctx]
                        if all(py):
                            seen.add(chain)
                            rows.append((2, chain, ctx[0], py[0], ctx[1], py[1]))
                            per_target[w] += 1
                # 3-word chain: prev2 + prev1 + target
                if i >= 2 and per_target[w] < 4:
                    ctx = [words[i - 2], words[i - 1], w]
                    chain = "".join(ctx)
                    if chain not in seen:
                        py = [sentence_to_continuous_pinyin(x) for x in ctx]
                        if all(py):
                            seen.add(chain)
                            rows.append((3, chain, ctx[0], py[0], ctx[1], py[1], ctx[2], py[2]))
                            per_target[w] += 1
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("nwords\tchain\twords\tpinyin\n")
        for r in rows:
            n = r[0]
            words = ",".join(r[2 + 2 * j] for j in range(n))
            py = ",".join(r[3 + 2 * j] for j in range(n))
            f.write("%d\t%s\t%s\t%s\n" % (n, r[1], words, py))
    print("contexts:", len(rows), "targets:", len(per_target))


if __name__ == "__main__":
    main()