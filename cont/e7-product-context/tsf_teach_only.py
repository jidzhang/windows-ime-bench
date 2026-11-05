"""Teach-only TSF pass: commit ctx words + select gold via Down(rank-1)+Space.
NO measurement commits. Prints per-pair selection result.
Pairs: single-ctx-word entries from cont_pairs_v2 with sweep rank 2.
"""
import io, sys, time, json

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness

_ORIG = H._run_powershell

def _safe(cmd):
    try:
        return _ORIG(cmd)
    except Exception:
        return ""

H._run_powershell = _safe

CORPUS = r"F:\work\IME\ms-anatomy\corpus\cont_pairs_v2.tsv"
sweep = {}
for line in io.open(r"F:\work\IME\ms-anatomy\corpus\sweep_targets_mq.tsv", encoding="utf-8").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) >= 4:
        sweep[p[0]] = (p[2], p[3])

pairs = []
for line in io.open(CORPUS, encoding="utf-8").read().splitlines()[1:]:
    p = line.rstrip("\n").split("\t")
    words, py = p[2].split(","), p[3].split(",")
    tgt = words[-1]
    if p[5] == "0" and len(words) == 2 and tgt in sweep and sweep[tgt][0] == "2":
        pairs.append({"id": p[0], "ctx": words[0], "ctxpy": py[0], "tgt": tgt, "py": py[-1]})
    if len(pairs) >= 6:
        break

ime = "moqi_pinyin"
h = WindowsPinyinImeHarness()
h.start()
extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
sw = WindowsImeSwitcher(extra_profiles=extra)
sw.activate_profile(ime, focus_callback=h.focus_host)
h.self_check()

def type_commit(py):
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys(py)
    time.sleep(h.commit_delay_s)
    h._press_space()
    return h._wait_for_committed_text().strip()

res = []
for pr in pairs:
    got_ctx = type_commit(pr["ctxpy"])
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys(pr["py"])
    time.sleep(h.commit_delay_s)
    h._send_vk(0x28)  # Down x1 -> rank2
    h._press_space()
    buf = h._wait_for_committed_text().strip()
    sel_ok = buf.endswith(pr["tgt"])
    res.append((pr["id"], pr["ctx"], pr["tgt"], got_ctx, buf, sel_ok))
    print("PAIR %s ctx=%s(%s) tgt=%s buf=%r sel_ok=%s" % (pr["id"], pr["ctx"], got_ctx, pr["tgt"], buf, sel_ok), flush=True)
    h.reset_host()

h.close()
ok = sum(1 for r in res if r[5])
print("selected ok: %d/%d" % (ok, len(res)))
