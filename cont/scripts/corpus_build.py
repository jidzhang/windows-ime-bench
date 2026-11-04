# Continuation corpus builder v2 (2026-11-04).
# Step 1: parse d3pairs225 into 2-char word chains + pinyin.
# Step 2: rank1 probe per word on a given IME (commit top-1).
# Step 3: rank sweep for selected target words (rank 2..8).
# Usage:
#   python corpus_build.py items
#   python corpus_build.py rank1 <ime_key>
#   python corpus_build.py sweep <ime_key> <targets.tsv>
import sys
import os
import time
import json
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
OUT.mkdir(parents=True, exist_ok=True)
SRC = Path(r"Z:\dev\IME\windows-ime-bench\corpus\d3pairs225.txt")
VK_DOWN = 0x28

_orig = H._run_powershell


def _safe(cmd):
    try:
        return _orig(cmd)
    except Exception:
        return ""


H._run_powershell = _safe


def load_chains():
    lines = [l.strip() for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    items = []
    for i, s in enumerate(lines):
        words = [s[j:j + 2] for j in range(0, len(s), 2)]
        items.append({"idx": i, "chain": s, "words": words})
    return items


def cmd_items():
    items = load_chains()
    rows = []
    for it in items:
        py = [sentence_to_continuous_pinyin(w) for w in it["words"]]
        if any(not p for p in py):
            continue
        rows.append([str(it["idx"]), it["chain"], str(len(it["words"]))] + it["words"] + py)
    with (OUT / "items.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tchain\tnwords\twords\tpinyin\n")
        for r in rows:
            n = int(r[2])
            words = r[3:3 + n]
            py = r[3 + n:]
            f.write("%s\t%s\t%d\t%s\t%s\n" % (r[0], r[1], n, ",".join(words), ",".join(py)))
    print("items:", len(rows), "->", OUT / "items.tsv")


def load_items():
    items = []
    with (OUT / "items.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            idx, chain, w1, p1, w2, p2 = line.rstrip("\n").split("\t")
            items.append({"idx": int(idx), "chain": chain,
                          "words": [w1, w2], "py": [p1, p2]})
    return items


def make_harness(ime):
    kw = {}
    if ime in ("wechat_pinyin", "ximeyao_pinyin", "shouxin_pinyin"):
        kw["commit_delay_s"] = 0.30
    h = WindowsPinyinImeHarness(**kw)
    h.start()
    extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
    sw = WindowsImeSwitcher(extra_profiles=extra)
    sw.activate_profile(ime, focus_callback=h.focus_host)
    h.self_check()
    return h


def commit(h, pinyin, downs=0):
    h.reset_host()
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys(pinyin)
    time.sleep(h.commit_delay_s)
    for _ in range(downs):
        h._send_vk(VK_DOWN)
        time.sleep(0.03)
    h._press_space()
    return h._wait_for_committed_text().strip()


def cmd_rank1(ime):
    h = make_harness(ime)
    rows = []
    items = load_items()
    t0 = time.perf_counter()
    try:
        for n, it in enumerate(items):
            for pos, (w, p) in enumerate(zip(it["words"], it["py"])):
                got = commit(h, p, 0)
                rows.append((it["idx"], pos, w, p, got, got == w))
            if (n + 1) % 10 == 0:
                print("[rank1 %s] %d/%d %.1fs" % (ime, n + 1, len(items), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    out = OUT / ("rank1_%s.tsv" % ime)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tpos\tword\tpinyin\ttop1\texact\n")
        for r in rows:
            f.write("%d\t%d\t%s\t%s\t%s\t%d\n" % (r[0], r[1], r[2], r[3], r[4], int(r[5])))
    print("rank1 done:", out, "time %.1fs" % (time.perf_counter() - t0))


def cmd_sweep(ime, targets_path):
    h = make_harness(ime)
    targets = []
    with Path(targets_path).open(encoding="utf-8") as f:
        next(f)
        for line in f:
            idx, pos, word, pinyin = line.rstrip("\n").split("\t")
            targets.append((int(idx), int(pos), word, pinyin))
    rows = []
    t0 = time.perf_counter()
    try:
        for n, (idx, pos, word, pinyin) in enumerate(targets):
            found = 0
            for downs in range(1, 8):  # rank 2..8
                got = commit(h, pinyin, downs)
                if got == word:
                    found = downs + 1
                    break
            rows.append((idx, pos, word, pinyin, found))
            if (n + 1) % 10 == 0:
                print("[sweep %s] %d/%d %.1fs" % (ime, n + 1, len(targets), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    out = OUT / ("sweep_%s.tsv" % ime)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tpos\tword\tpinyin\trank\n")
        for r in rows:
            f.write("%d\t%d\t%s\t%s\t%d\n" % r)
    print("sweep done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "items":
        cmd_items()
    elif mode == "rank1":
        cmd_rank1(sys.argv[2])
    elif mode == "sweep":
        cmd_sweep(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("unknown mode")