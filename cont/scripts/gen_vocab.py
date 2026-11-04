# Build vocabulary from real corpora for ambiguity mining.
import io
import sys
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin
import jieba

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
OUT.mkdir(parents=True, exist_ok=True)
SRC = [
    Path(r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare\data\corpus\zhihu120.txt"),
    Path(r"Z:\dev\IME\windows-ime-bench\corpus\human1023.txt"),
    Path(r"Z:\dev\IME\windows-ime-bench\corpus\words234.txt"),
]


def hanzi(w):
    return all("\u4e00" <= c <= "\u9fff" for c in w)


def main():
    words = set()
    # segmented sentence corpora
    for path in SRC[:2]:
        if not path.exists():
            continue
        for line in io.open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            for w in jieba.cut(line):
                if 2 <= len(w) <= 4 and hanzi(w):
                    words.add(w)
    # words corpus: one word per line
    if SRC[2].exists():
        for line in io.open(SRC[2], encoding="utf-8"):
            w = line.strip()
            if 2 <= len(w) <= 4 and hanzi(w):
                words.add(w)
    # d3pairs words (true boundaries)
    items = OUT / "items.tsv"
    if items.exists():
        with items.open(encoding="utf-8") as f:
            next(f)
            for line in f:
                _, _, w1, _, w2, _ = line.rstrip("\n").split("\t")
                words.add(w1); words.add(w2)
    rows = []
    for w in sorted(words):
        p = sentence_to_continuous_pinyin(w)
        if p:
            rows.append((w, p))
    with (OUT / "vocab.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("word\tpinyin\n")
        for w, p in rows:
            f.write("%s\t%s\n" % (w, p))
    print("vocab:", len(rows))


if __name__ == "__main__":
    main()