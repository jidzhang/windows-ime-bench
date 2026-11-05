"""Re-entry test on the LIVE daemon state (taught 6 pairs, no pollution):
commit ctx word -> type target code -> Space -> does top-1 equal gold?
"""
import io, sys, time, json

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness

_ORIG = H._run_powershell
H._run_powershell = lambda cmd: (_ORIG(cmd) if True else "")

def _safe(cmd):
    try:
        return _ORIG(cmd)
    except Exception:
        return ""

H._run_powershell = _safe

pairs = [("三口", "sankou", "候补", "houbu"),
         ("那个", "nage", "座位", "zuowei"),
         ("冰川", "bingchuan", "消融", "xiaorong"),
         ("就是", "jiushi", "冰湖", "binghu"),
         ("水流", "shuiliu", "淹没", "yanmo"),
         ("主要", "zhuyao", "任务", "renwu")]

h = WindowsPinyinImeHarness()
h.start()
extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
sw = WindowsImeSwitcher(extra_profiles=extra)
sw.activate_profile("moqi_pinyin", focus_callback=h.focus_host)
h.self_check()

def type_commit(py):
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys(py)
    time.sleep(h.commit_delay_s)
    h._press_space()
    return h._wait_for_committed_text().strip()

lift = 0
n = 0
for ctx, cpy, tgt, tpy in pairs:
    got_ctx = type_commit(cpy)
    buf = type_commit(tpy)
    ok = buf.endswith(tgt)
    lift += ok
    n += 1
    print("REENTRY %s->%s : buf=%r lift=%s" % (ctx, tgt, buf, ok), flush=True)
    h.reset_host()

h.close()
print("REENTRY LIFT: %d/%d" % (lift, n))
