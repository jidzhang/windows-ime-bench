# Black-box top-1 rank for an arbitrary vocabulary (word, pinyin).
# Usage: python rank_words.py <ime_key> <vocab.tsv> <out.tsv>
import sys
import time
import json
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness

_orig = H._run_powershell


def _safe(cmd):
    try:
        return _orig(cmd)
    except Exception:
        return ""


H._run_powershell = _safe


def main():
    ime, vocab, out = sys.argv[1], sys.argv[2], sys.argv[3]
    words = []
    with open(vocab, encoding="utf-8") as f:
        next(f)
        for line in f:
            w, p = line.rstrip("\n").split("\t")
            words.append((w, p))
    kw = {}
    if ime in ("wechat_pinyin", "ximeyao_pinyin", "shouxin_pinyin"):
        kw["commit_delay_s"] = 0.30
    h = WindowsPinyinImeHarness(**kw)
    h.start()
    extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
    sw = WindowsImeSwitcher(extra_profiles=extra)
    sw.activate_profile(ime, focus_callback=h.focus_host)
    h.self_check()
    t0 = time.perf_counter()
    rows = []
    try:
        for n, (w, p) in enumerate(words):
            h.reset_host()
            h.focus_host()
            h._open_ime()
            h._send_ascii_keys(p)
            time.sleep(h.commit_delay_s)
            h._press_space()
            got = h._wait_for_committed_text().strip()
            rows.append((w, p, got, got == w))
            if (n + 1) % 50 == 0:
                print("[rankv %s] %d/%d %.1fs" % (ime, n + 1, len(words), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("word\tpinyin\ttop1\texact\n")
        for r in rows:
            f.write("%s\t%s\t%s\t%d\n" % (r[0], r[1], r[2], int(r[3])))
    print("done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    main()