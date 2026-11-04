# Raw mode stats without reachability: A/C/B on items where A is wrong & ctx ok.
import sys
from pathlib import Path

C = Path(r"F:\work\IME\ms-anatomy\corpus")
O = Path(r"F:\work\IME\ms-anatomy\contest")
MODE = sys.argv[1].upper()


def load_corpus():
    meta = {}
    with (C / "cont_pairs_v2.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            meta[int(p[0])] = {"control": int(p[5])}
    return meta


def load(round_no, ime, arm):
    path = O / ("R%d_%s_%s_%s.tsv" % (round_no, ime, arm, MODE))
    rows = {}
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            rows[int(p[0])] = {"exact": p[7] == "1", "ctx_ok": p[9] == "1"}
    return rows


for ime in ("ms", "mq"):
    META = load_corpus()
    def meta_control(i):
        return META[i]["control"] == 1
    print("\n===== %s [%s raw] =====" % (ime, MODE))
    for r in range(1, 5):
        a = load(r, ime, "a"); c = load(r, ime, "c"); b = load(r, ime, "b")
        pool = [i for i in a if a[i] and c.get(i) and b.get(i)
                and not a[i]["exact"] and c[i]["ctx_ok"] and b[i]["ctx_ok"]]
        for label, sel in (("natural", [i for i in pool if not meta_control(i)]),
                           ("control", [i for i in pool if meta_control(i)])):
            if not sel:
                continue
            ap = sum(1 for i in sel if a[i]["exact"])
            cp = sum(1 for i in sel if c[i]["exact"])
            bp = sum(1 for i in sel if b[i]["exact"])
            n = len(sel)
            print("R%d %s n=%d | A %.1f C %.1f B %.1f | dCtx %+0.1f" %
                  (r, label, n, 100 * ap / n, 100 * cp / n, 100 * bp / n, 100 * (bp - cp) / n))