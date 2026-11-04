# Analyze A/C/B contest results with reachability filter.
# Reachable = target rank 2..8 when typed alone (gold in candidate page).
import random
from collections import defaultdict
from pathlib import Path

C = Path(r"F:\work\IME\ms-anatomy\corpus")
O = Path(r"F:\work\IME\ms-anatomy\contest")


def load_corpus():
    meta = {}
    with (C / "cont_pairs_v2.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            meta[int(p[0])] = {"n": int(p[1]), "control": int(p[5]),
                               "ms_amb": int(p[6]), "mq_amb": int(p[7]),
                               "target": p[2].split(",")[-1]}
    return meta


def load(round_no, ime, arm):
    path = O / ("R%d_%s_%s.tsv" % (round_no, ime, arm))
    rows = {}
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            rows[int(p[0])] = {"exact": p[6] == "1", "ctx_ok": p[8] == "1"}
    return rows


def load_reach(ime):
    path = C / ("sweep_targets_%s.tsv" % ime)
    rows = {}
    if path.exists():
        with path.open(encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                rows[p[0]] = int(p[2])
    return rows


def boot_ci(vals, n=1000, alpha=0.05):
    if not vals:
        return (0.0, 0.0)
    means = []
    k = len(vals)
    for _ in range(n):
        means.append(100.0 * sum(random.choice(vals) for _ in range(k)) / k)
    means.sort()
    return (means[int((alpha / 2) * n)], means[int((1 - alpha / 2) * n) - 1])


def run(ime, amb_key, reach, skip_ids=(8, 105)):
    print("\n===== %s (reachable only) =====" % ime)
    meta = load_corpus()
    reachable_targets = [w for w, r in reach.items() if 2 <= r <= 8]
    print("targets reachable: %d/%d (rank2..8)" % (len(reachable_targets), len(reach)))
    pooled = defaultdict(list)
    ctrl_pool = defaultdict(list)
    for r in range(1, 5):
        a = load(r, ime, "a"); c = load(r, ime, "c"); b = load(r, ime, "b")
        ids = []
        for i, m in meta.items():
            if i in skip_ids or m["control"] != 0 or m[amb_key] != 1:
                continue
            if not (2 <= reach.get(m["target"], 0) <= 8):
                continue
            if a.get(i) and c.get(i) and b.get(i) and c[i]["ctx_ok"] and b[i]["ctx_ok"]:
                ids.append(i)
        ctrl = []
        for i, m in meta.items():
            if i in skip_ids or m["control"] != 1 or m[amb_key] != 1:
                continue
            if not (2 <= reach.get(m["target"], 0) <= 8):
                continue
            if a.get(i) and c.get(i) and b.get(i) and c[i]["ctx_ok"] and b[i]["ctx_ok"]:
                ctrl.append(i)
        def acc(rows, sel):
            return 100.0 * sum(1 for i in sel if rows[i]["exact"]) / len(sel) if sel else 0.0
        ap, cp, bp = acc(a, ids), acc(c, ids), acc(b, ids)
        print("R%d n=%d | A %.1f C %.1f B %.1f | dLearn %+0.1f dCtx %+0.1f" %
              (r, len(ids), ap, cp, bp, cp - ap, bp - cp))
        for i in ids:
            pooled["a"].append(1 if a[i]["exact"] else 0)
            pooled["c"].append(1 if c[i]["exact"] else 0)
            pooled["b"].append(1 if b[i]["exact"] else 0)
        for i in ctrl:
            ctrl_pool["a"].append(1 if a[i]["exact"] else 0)
            ctrl_pool["c"].append(1 if c[i]["exact"] else 0)
            ctrl_pool["b"].append(1 if b[i]["exact"] else 0)
    pa, pc, pb = pooled["a"], pooled["c"], pooled["b"]
    if pa:
        ma, mc, mb = 100 * sum(pa) / len(pa), 100 * sum(pc) / len(pc), 100 * sum(pb) / len(pb)
        dl = [c - a for a, c in zip(pa, pc)]
        dc = [b - c for c, b in zip(pc, pb)]
        print("POOLED n=%d | A %.1f C %.1f B %.1f | dLearn %+0.1f (CI %.1f..%.1f) dCtx %+0.1f (CI %.1f..%.1f)" %
              (len(pa), ma, mc, mb, mc - ma, *boot_ci(dl), mb - mc, *boot_ci(dc)))
    if ctrl_pool["a"]:
        ca, cc, cb = ctrl_pool["a"], ctrl_pool["c"], ctrl_pool["b"]
        mc = 100 * sum(cc) / len(cc); mb = 100 * sum(cb) / len(cb)
        print("CONTROL n=%d | A %.1f C %.1f B %.1f | dCtx %+0.1f" %
              (len(ca), 100 * sum(ca) / len(ca), mc, mb, mb - mc))


if __name__ == "__main__":
    run("ms", "ms_amb", load_reach("ms"))
    run("mq", "mq_amb", load_reach("mq"))