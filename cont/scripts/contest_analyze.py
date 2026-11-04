# Analyze A/C/B contest results: per-round and pooled Δ_learn/Δ_ctx.
import io
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
                               "ms_amb": int(p[6]), "mq_amb": int(p[7])}
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
            rows[int(p[0])] = {"exact": p[6] == "1", "ctx_ok": p[8] == "1",
                               "control": int(p[9])}
    return rows


def boot_ci(vals, n=1000, alpha=0.05):
    if not vals:
        return (0.0, 0.0)
    means = []
    k = len(vals)
    for _ in range(n):
        s = sum(random.choice(vals) for _ in range(k))
        means.append(100.0 * s / k)
    means.sort()
    lo = means[int((alpha / 2) * n)]
    hi = means[int((1 - alpha / 2) * n) - 1]
    return (lo, hi)


def arm_stats(rows, ids):
    if not ids:
        return 0, 0, 0.0
    ok = sum(1 for i in ids if rows.get(i, {}).get("exact"))
    return ok, len(ids), 100.0 * ok / len(ids)


def main():
    meta = load_corpus()
    for ime, amb_key in (("ms", "ms_amb"), ("mq", "mq_amb")):
        print("\n===== %s =====" % ime)
        pooled = defaultdict(list)
        for r in range(1, 5):
            a = load(r, ime, "a")
            c = load(r, ime, "c")
            b = load(r, ime, "b")
            # eligible: natural item, ambiguous for this IME; C/B context ok
            ids = [i for i, m in meta.items()
                   if m["control"] == 0 and m[amb_key] == 1
                   and a.get(i) and c.get(i) and b.get(i)
                   and c[i]["ctx_ok"] and b[i]["ctx_ok"]]
            ctrl = [i for i, m in meta.items()
                    if m["control"] == 1 and m[amb_key] == 1
                    and a.get(i) and c.get(i) and b.get(i)
                    and c[i]["ctx_ok"] and b[i]["ctx_ok"]]
            ao, an, ap = arm_stats(a, ids)
            co, cn, cp = arm_stats(c, ids)
            bo, bn, bp = arm_stats(b, ids)
            print("R%d n=%d | A %.1f%% C %.1f%% B %.1f%% | dLearn %+0.1f dCtx %+0.1f dTotal %+0.1f" %
                  (r, an, ap, cp, bp, cp - ap, bp - cp, bp - ap))
            for i in ids:
                pooled["a"].append(1 if a[i]["exact"] else 0)
                pooled["c"].append(1 if c[i]["exact"] else 0)
                pooled["b"].append(1 if b[i]["exact"] else 0)
            if ctrl:
                cao = sum(1 for i in ctrl if a[i]["exact"])
                cco = sum(1 for i in ctrl if c[i]["exact"])
                cbo = sum(1 for i in ctrl if b[i]["exact"])
                print("   control n=%d | A %.1f C %.1f B %.1f | dCtx %+0.1f" %
                      (len(ctrl), 100 * cao / len(ctrl), 100 * cco / len(ctrl),
                       100 * cbo / len(ctrl), 100 * (cbo - cco) / len(ctrl)))
        # pooled across rounds (item-round pairs)
        pa, pc, pb = pooled["a"], pooled["c"], pooled["b"]
        if pa:
            ma = 100 * sum(pa) / len(pa)
            mc = 100 * sum(pc) / len(pc)
            mb = 100 * sum(pb) / len(pb)
            dl = [c - a for a, c in zip(pa, pc)]
            dc = [b - c for c, b in zip(pc, pb)]
            print("POOLED n=%d | A %.1f C %.1f B %.1f | dLearn %+0.1f (CI %.1f..%.1f) dCtx %+0.1f (CI %.1f..%.1f)" %
                  (len(pa), ma, mc, mb, mc - ma, *boot_ci(dl), mb - mc, *boot_ci(dc)))

    print("\n(controls are excluded from pooled; C/B require ctx_ok)")


if __name__ == "__main__":
    main()