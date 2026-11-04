# Generate items with TRUE word boundaries from d3pairs sidecar.
# key = full pinyin of W1 + initials of W2; infer split by matching.
import sys
import io
import json
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
OUT.mkdir(parents=True, exist_ok=True)
TXT = Path(r"Z:\dev\IME\windows-ime-bench\corpus\d3pairs225.txt")
PIN = Path(r"Z:\dev\IME\windows-ime-bench\corpus\d3pairs225.pin.tsv")


def load():
    pin = {}
    for l in io.open(PIN, encoding="utf-8"):
        l = l.rstrip("\n")
        if not l.strip() or l.startswith("#"):
            continue
        w, key = l.split("\t")
        pin[w] = key
    out = []
    for l in io.open(TXT, encoding="utf-8"):
        w = l.strip()
        if w:
            out.append((w, pin.get(w)))
    return out


def infer_split(chain, key):
    for k in range(1, len(chain)):
        pre, suf = chain[:k], chain[k:]
        p = sentence_to_continuous_pinyin(pre)
        if not p or not key.startswith(p):
            continue
        rest = key[len(p):]
        if len(rest) != len(suf):
            continue
        ok = True
        for ch, ini in zip(suf, rest):
            pi = sentence_to_continuous_pinyin(ch)
            if not pi or pi[0] != ini:
                ok = False
                break
        if ok:
            return k, p, suf
    return None


def main():
    rows = []
    bad = []
    for i, (chain, key) in enumerate(load()):
        if not key:
            bad.append((i, chain, "no-key"))
            continue
        split = infer_split(chain, key)
        if not split:
            bad.append((i, chain, key))
            continue
        k, p1, w2 = split
        w1 = chain[:k]
        p2 = sentence_to_continuous_pinyin(w2)
        if not p2:
            bad.append((i, chain, "no-p2"))
            continue
        rows.append((i, chain, w1, p1, w2, p2))
    with (OUT / "items.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tchain\tw1\tp1\tw2\tp2\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print("valid:", len(rows), "bad:", len(bad))
    for b in bad[:10]:
        print("BAD", b)


if __name__ == "__main__":
    main()