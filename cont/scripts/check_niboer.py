# Product check: type niboer / nipoer in installed Moqi, print commits.
import sys
import time
import json

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

h = WindowsPinyinImeHarness()
h.start()
extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
sw = WindowsImeSwitcher(extra_profiles=extra)
sw.activate_profile("moqi_pinyin", focus_callback=h.focus_host)
h.self_check()
for text in ("niboer", "nipoer"):
    h.reset_host()
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys(text)
    time.sleep(h.commit_delay_s)
    h._press_space()
    print(text, "->", h._wait_for_committed_text().strip(), flush=True)
h.close()