# Unique target list from corpus for reachability sweep.
import io
from pathlib import Path

C = Path(r"F:\work\IME\ms-anatomy\corpus")
seen = {}
with (C / "cont_pairs_v2.tsv").open(encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        tgt = p[2].split(",")[-1]
        py = p[3].split(",")[-1]
        if tgt not in seen:
            seen[tgt] = py
with (C / "targets.tsv").open("w", encoding="utf-8", newline="\n") as f:
    f.write("word\tpinyin\n")
    for w, p in seen.items():
        f.write("%s\t%s\n" % (w, p))
print("unique targets:", len(seen))