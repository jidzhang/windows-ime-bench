# Generate 3-word chains from real corpus via jieba, with pinyin.
import io
import sys
import json
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin

import jieba

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
OUT.mkdir(parents=True, exist_ok=True)
CORPORA = [
    Path(r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare\data\corpus\zhihu120.txt"),
    Path(r"Z:\dev\IME\windows-ime-bench\corpus\human1023.txt"),
]


def hanzi(w):
    return all("\u4e00" <= c <= "\u9fff" for c in w)


def main():
    chains = []
    seen = set()
    for path in CORPORA:
        if not path.exists():
            continue
        for line in io.open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            words = [w for w in jieba.cut(line) if len(w) >= 2 and hanzi(w)]
            for i in range(len(words) - 2):
                w = words[i:i + 3]
                chain = "".join(w)
                if chain in seen:
                    continue
                # skip overly long words (rare); keep 2-4 chars each
                if any(len(x) > 4 for x in w):
                    continue
                py = [sentence_to_continuous_pinyin(x) for x in w]
                if any(not p for p in py):
                    continue
                seen.add(chain)
                chains.append((chain, w, py))
    with (OUT / "items3.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tchain\tw1\tp1\tw2\tp2\tw3\tp3\n")
        for i, (chain, w, py) in enumerate(chains):
            f.write("%d\t%s\t%s\n" % (i, chain, "\t".join(
                [w[0], py[0], w[1], py[1], w[2], py[2]])))
    print("3-word chains:", len(chains), "->", OUT / "items3.tsv")


if __name__ == "__main__":
    main()