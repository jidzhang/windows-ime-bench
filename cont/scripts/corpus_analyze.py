# Corpus v2 selection analysis (2-word pairs from d3pairs225 sidecar).
# step1: rank1 results -> candidates.tsv (w1 stable in both, w2 ambiguous in
#        at least one IME).
# step2: sweep results -> selected.tsv (gold reachable at rank 2..8).
import sys
from pathlib import Path

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")


def load_items():
    items = {}
    with (OUT / "items.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            idx, chain, w1, p1, w2, p2 = line.rstrip("\n").split("\t")
            items[int(idx)] = {"chain": chain, "w1": w1, "p1": p1,
                               "w2": w2, "p2": p2}
    return items


def load_rank1(ime):
    rows = {}
    p = OUT / ("rank1_%s.tsv" % ime)
    with p.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            idx, pos, word, py, top1, exact = line.rstrip("\n").split("\t")
            rows[(int(idx), int(pos))] = {"word": word, "py": py,
                                          "top1": top1, "exact": exact == "1"}
    return rows


def step1():
    items = load_items()
    ms = load_rank1("microsoft_pinyin")
    mq = load_rank1("moqi_pinyin")
    cands = []
    stats = {"total": 0, "w1_unstable": 0, "w2_weak": 0, "ok": 0}
    for idx, it in items.items():
        stats["total"] += 1
        a = ms.get((idx, 0)); b = mq.get((idx, 0))
        c = ms.get((idx, 1)); d = mq.get((idx, 1))
        if not (a and b and c and d):
            continue
        if not (a["exact"] and b["exact"]):
            stats["w1_unstable"] += 1
            continue
        if c["exact"] and d["exact"]:
            stats["w2_weak"] += 1
            continue
        stats["ok"] += 1
        cands.append((idx, it["w1"], it["p1"], it["w2"], it["p2"],
                      int(c["exact"]), c["top1"], int(d["exact"]), d["top1"]))
    with (OUT / "candidates.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tw1\tp1\tw2\tp2\tms_w2_exact\tms_top1\tmq_w2_exact\tmq_top1\n")
        for r in cands:
            f.write("\t".join(map(str, r)) + "\n")
    print("step1 stats:", stats, "candidates:", len(cands))


def load_rank(path):
    rows = {}
    with Path(path).open(encoding="utf-8") as f:
        next(f)
        for line in f:
            idx, pos, word, py, rank = line.rstrip("\n").split("\t")
            rows[int(idx)] = int(rank)
    return rows


def step2():
    items = load_items()
    ms_sweep = load_rank(OUT / "sweep_microsoft_pinyin.tsv")
    mq_sweep = load_rank(OUT / "sweep_moqi_pinyin.tsv")
    rows = []
    dropped = 0
    for idx, it in items.items():
        r1 = ms_sweep.get(idx, 0)
        r2 = mq_sweep.get(idx, 0)
        if r1 == 0 and r2 == 0:
            dropped += 1
            continue
        rank = min([r for r in (r1, r2) if r > 0])
        rows.append((idx, it["w1"], it["p1"], it["w2"], it["p2"], r1, r2, rank))
    rows.sort(key=lambda r: r[8])
    with (OUT / "selected.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tw1\tp1\tw2\tp2\tms_rank\tmq_rank\tbest_rank\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print("step2 selected:", len(rows), "dropped(unreachable):", dropped)


if __name__ == "__main__":
    if sys.argv[1] == "step1":
        step1()
    elif sys.argv[1] == "step2":
        step2()