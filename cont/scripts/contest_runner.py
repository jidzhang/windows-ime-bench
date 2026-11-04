# A/C/B continuation contest runner.
# Usage: python contest_runner.py <ime_key> <arm:a|c|b> <corpus.tsv> <out.tsv> [limit]
# Arms:
#   a: target alone (no context)
#   c: context committed, host text cleared, then target (learning only)
#   b: context committed, then target (visible context + learning)
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


def load_corpus(path, limit=0):
    rows = []
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            rid, n, words, py, tpos, ctrl, ms_amb, mq_amb, src = parts[:9]
            rows.append({"id": int(rid), "n": int(n), "words": words.split(","),
                         "py": py.split(","), "tpos": int(tpos),
                         "control": int(ctrl), "src": src})
    return rows[:limit] if limit else rows


def main():
    ime, arm, corpus, out = sys.argv[1], sys.argv[2].lower(), sys.argv[3], sys.argv[4]
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    rows = load_corpus(corpus, limit)
    kw = {}
    if ime in ("wechat_pinyin", "ximeyao_pinyin", "shouxin_pinyin"):
        kw["commit_delay_s"] = 0.30
    h = WindowsPinyinImeHarness(**kw)
    h.start()
    extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
    sw = WindowsImeSwitcher(extra_profiles=extra)
    sw.activate_profile(ime, focus_callback=h.focus_host)
    h.self_check()

    def type_word(py, gold):
        h.focus_host()
        h._open_ime()
        h._send_ascii_keys(py)
        time.sleep(h.commit_delay_s)
        h._press_space()
        return h._wait_for_committed_text().strip()

    results = []
    t0 = time.perf_counter()
    try:
        for n, it in enumerate(rows):
            ctx_words = it["words"][:-1]
            ctx_py = it["py"][:-1]
            tgt, tgt_py = it["words"][-1], it["py"][-1]
            h.reset_host()
            if arm == "a":
                got = type_word(tgt_py, tgt)
                ctx_got, ctx_ok = "", True
            else:
                got_ctx = []
                for w, p in zip(ctx_words, ctx_py):
                    got_ctx.append(type_word(p, w))
                ctx_got = got_ctx[-1].strip() if got_ctx else ""
                ctx_ok = ctx_got == "".join(ctx_words)
                base = ctx_got if arm == "b" else ""
                if arm == "c":
                    h.reset_host()
                final = type_word(tgt_py, tgt)
                got = final[len(base):].strip() if arm == "b" else final
            # for b, strip the context text from the final read
            results.append((it["id"], arm, it["n"], tgt, tgt_py, got,
                            int(got == tgt), ctx_got, int(ctx_ok), it["control"]))
            if (n + 1) % 20 == 0:
                print("[%s/%s] %d/%d %.1fs" % (ime, arm, n + 1, len(rows), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("id\tarm\tnwords\ttarget\ttarget_py\tgot\texact\tctx_got\tctx_ok\tcontrol\n")
        for r in results:
            f.write("\t".join(map(str, r)) + "\n")
    print("done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    main()