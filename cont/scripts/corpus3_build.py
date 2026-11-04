# Rank probe for 3-word chains (items3.tsv).
# modes: rank1 <ime> | sweep <ime> <targets.tsv> | sweep3 <ime> <targets.tsv>
import sys
import time
import json
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness

OUT = Path(r"F:\work\IME\ms-anatomy\corpus")
VK_DOWN = 0x28
_orig = H._run_powershell


def _safe(cmd):
    try:
        return _orig(cmd)
    except Exception:
        return ""


H._run_powershell = _safe


def load_items3():
    items = []
    with (OUT / "items3.tsv").open(encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            idx, chain = int(parts[0]), parts[1]
            words = parts[2::2]
            py = parts[3::2]
            items.append({"idx": idx, "chain": chain, "words": words, "py": py})
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
    items = load_items3()
    t0 = time.perf_counter()
    try:
        for n, it in enumerate(items):
            for pos, (w, p) in enumerate(zip(it["words"], it["py"])):
                got = commit(h, p, 0)
                rows.append((it["idx"], pos, w, p, got, got == w))
            if (n + 1) % 20 == 0:
                print("[rank1-3 %s] %d/%d %.1fs" % (ime, n + 1, len(items), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    out = OUT / ("rank1_3_%s.tsv" % ime)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tpos\tword\tpinyin\ttop1\texact\n")
        for r in rows:
            f.write("%d\t%d\t%s\t%s\t%s\t%d\n" % (r[0], r[1], r[2], r[3], r[4], int(r[5])))
    print("rank1-3 done:", out, "time %.1fs" % (time.perf_counter() - t0))


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
            for downs in range(1, 8):
                got = commit(h, pinyin, downs)
                if got == word:
                    found = downs + 1
                    break
            rows.append((idx, pos, word, pinyin, found))
            if (n + 1) % 10 == 0:
                print("[sweep-3 %s] %d/%d %.1fs" % (ime, n + 1, len(targets), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    out = OUT / ("sweep_3_%s.tsv" % ime)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tpos\tword\tpinyin\trank\n")
        for r in rows:
            f.write("%d\t%d\t%s\t%s\t%d\n" % r)
    print("sweep-3 done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "rank1":
        cmd_rank1(sys.argv[2])
    elif mode == "sweep":
        cmd_sweep(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("unknown mode")