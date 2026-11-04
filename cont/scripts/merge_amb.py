# Merge MS black-box and Moqi white-box ambiguity lists into one target set.
import io
from pathlib import Path

C = Path(r"F:\work\IME\ms-anatomy\corpus")
ms = {}
with (C / "rank1v_microsoft_pinyin.tsv").open(encoding="utf-8") as f:
    next(f)
    for line in f:
        w, p, top1, exact = line.rstrip("\n").split("\t")
        ms[w] = (p, exact == "1")
mq = {}
with (C / "wordrank_moqi.tsv").open(encoding="utf-8") as f:
    next(f)
    for line in f:
        w, p, top1, exact = line.rstrip("\n").split("\t")
        mq[w] = (p, exact == "true")

rows = []
for w in sorted(set(ms) | set(mq)):
    p = (ms.get(w) or mq.get(w))[0]
    ms_ok = ms.get(w, (None, True))[1]
    mq_ok = mq.get(w, (None, True))[1]
    if ms_ok and mq_ok:
        continue
    rows.append((w, p, int(ms_ok), int(mq_ok)))
with (C / "ambiguous_union.tsv").open("w", encoding="utf-8", newline="\n") as f:
    f.write("word\tpinyin\tms_rank1_ok\tmq_rank1_ok\n")
    for r in rows:
        f.write("%s\t%s\t%d\t%d\n" % r)
with (C / "ambiguous_words.tsv").open("w", encoding="utf-8", newline="\n") as f:
    f.write("word\tpinyin\n")
    for r in rows:
        f.write("%s\t%s\n" % (r[0], r[1]))
print("union ambiguous:", len(rows), "| ms-only:", sum(1 for r in rows if r[2] == 0 and r[3] == 1),
      "| mq-only:", sum(1 for r in rows if r[2] == 1 and r[3] == 0),
      "| both:", sum(1 for r in rows if r[2] == 0 and r[3] == 0))