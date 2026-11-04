# Build cont_pairs_v2: filter contexts by stable context words, add 20% controls.
import io
from collections import defaultdict
from pathlib import Path

C = Path(r"F:\work\IME\ms-anatomy\corpus")
NEUTRAL = ["我们", "这个", "今天", "可以", "没有", "一个", "现在", "因为", "所以", "但是", "如果", "已经"]


def load_exact():
    ms, mq = {}, {}
    with (C / "rank1v_microsoft_pinyin.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            w, p, top1, exact = line.rstrip("\n").split("\t")
            ms[w] = exact == "1"
    with (C / "wordrank_moqi.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            w, p, top1, exact = line.rstrip("\n").split("\t")
            mq[w] = exact == "true"
    return ms, mq


def load_amb():
    amb = {}
    with (C / "ambiguous_union.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            w, p, ms_ok, mq_ok = line.rstrip("\n").split("\t")
            amb[w] = (p, ms_ok == "0", mq_ok == "0")
    return amb


def stable(w, ms, mq):
    return ms.get(w) is True and mq.get(w) is True


def main():
    ms, mq = load_exact()
    amb = load_amb()
    pool = [w for w in NEUTRAL if stable(w, ms, mq)]
    rows = []
    per_target = defaultdict(int)
    seen = set()
    with (C / "contexts_union.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            n, chain, words_s, py_s = line.rstrip("\n").split("\t")
            n = int(n)
            words = words_s.split(",")
            py = py_s.split(",")
            target = words[-1]
            if target not in amb:
                continue
            if not all(stable(w, ms, mq) for w in words[:-1]):
                continue
            if chain in seen:
                continue
            if per_target[target] >= 3:
                continue
            seen.add(chain)
            per_target[target] += 1
            p, ms_amb, mq_amb = amb[target]
            rows.append([len(rows), n, ",".join(words), ",".join(py), n - 1, 0,
                         int(ms_amb), int(mq_amb), chain])
    # controls: every 4th row, replace context with neutral words
    ctrl = []
    for i, r in enumerate(rows):
        if i % 4 != 0 or len(pool) < 2:
            continue
        n = r[1]
        words = r[2].split(",")
        py = r[3].split(",")
        for j in range(n - 1):
            words[j] = pool[j % len(pool)]
        # pinyin computed below by caller
        ctrl.append([len(rows) + len(ctrl), n, ",".join(words), "", n - 1, 1,
                     r[6], r[7], "CTRL:" + r[8]])
    # compute pinyin for controls
    import sys
    BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
    sys.path.insert(0, BENCH + r"\src")
    from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin
    for r in ctrl:
        words = r[2].split(",")
        r[3] = ",".join(sentence_to_continuous_pinyin(w) for w in words)
    rows += ctrl
    rows.sort(key=lambda r: r[0])
    with (C / "cont_pairs_v2.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("id\tnwords\twords\tpinyin\ttarget_pos\tcontrol\tms_amb\tmq_amb\tsource\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print("corpus:", len(rows), "natural:", len(rows) - len(ctrl), "controls:", len(ctrl),
          "targets:", len(per_target), "neutral_pool:", pool)


if __name__ == "__main__":
    main()