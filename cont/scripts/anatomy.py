# MS Pinyin anatomy driver (E1-E4), built on the bench harness.
# Selects candidates by arrow-down count + space; committed text reveals rank.
# Usage: python anatomy.py <ime_key> <e1|e2|e3|e4>
import sys
import time
import json
import hashlib
from pathlib import Path

sys.path.insert(0, r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare\src")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness
from rime_schema_compare.text_pipeline import sentence_to_continuous_pinyin

_IME = sys.argv[1]
_EXP = sys.argv[2]

_orig = H._run_powershell
def _safe(cmd):
    try:
        return _orig(cmd)
    except Exception:
        return ""
H._run_powershell = _safe

VK_DOWN = 0x28
IM_DIR = Path(r"C:\Users\TEST\AppData\Roaming\Microsoft\InputMethod")

extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
switcher = WindowsImeSwitcher(extra_profiles=extra)
harness = WindowsPinyinImeHarness(commit_delay_s=0.30 if _IME in ("wechat_pinyin", "ximeyao_pinyin") else 0.15)


def snap_files(tag):
    rows = []
    if IM_DIR.exists():
        for p in sorted(IM_DIR.rglob("*")):
            if p.is_file():
                h = hashlib.md5(p.read_bytes()).hexdigest()[:8]
                rows.append("%s|%d|%s" % (p.name, p.stat().st_size, h))
    print("[%s] files: %s" % (tag, rows if rows else "none"), flush=True)


def commit_top(harness, raw):
    harness.reset_host()
    harness._focus_host()
    harness._send_ascii_keys(raw)
    time.sleep(0.1)
    harness._press_space()
    return harness._wait_for_committed_text().strip()


def commit_rank(harness, raw, down):
    """Type raw, press Down x times, space; committed text = rank-(down+1) candidate."""
    harness.reset_host()
    harness._focus_host()
    harness._send_ascii_keys(raw)
    time.sleep(0.1)
    for _ in range(down):
        harness._send_vk(VK_DOWN)
        time.sleep(0.03)
    harness._press_space()
    return harness._wait_for_committed_text().strip()


def main():
    harness.start()
    switcher.activate_profile(_IME, focus_callback=harness.focus_host)
    harness.self_check()
    print("ready:", _IME, flush=True)

    if _EXP == "e1":  # dynamic frequency: shiyan 实验/试验/...
        raw = "shiyan"
        print("== baseline rank sweep (down 0..4) ==", flush=True)
        ranks = [commit_rank(harness, raw, k) for k in range(5)]
        for i, t in enumerate(ranks):
            print("rank%d: %s" % (i + 1, t), flush=True)
        snap_files("e1-baseline")
        # find current rank of 试验 (assume present in sweep)
        target_rank = None
        for i, t in enumerate(ranks):
            if "试验" in t:
                target_rank = i
                break
        if target_rank is None:
            print("试验 not in top5; abort curve", flush=True)
            return
        print("== force-select 试验 (rank%d) x6, top-1 after each ==" % (target_rank + 1), flush=True)
        for r in range(6):
            commit_rank(harness, raw, target_rank)
            top = commit_top(harness, raw)
            print("round%d top1: %s" % (r + 1, top), flush=True)
            if "试验" in top:
                print("OVERTOOK at round", r + 1, flush=True)
                break
        snap_files("e1-after")
        # cross-context
        print("== cross-context ==", flush=True)
        for ctx, sent in [("none", "zuole yi ge shiyan"), ("zuole", "zuole shiyan")]:
            pass
        print("ctx sent top1:", commit_top(harness, "zuole yi ge shiyan"), flush=True)

    elif _EXP == "e2":  # self-learning word: moqishurufa -> 墨奇输入法
        syls = ["mo", "qi", "shu", "ru", "fa"]
        print("== assemble char-by-char ==", flush=True)
        commit_top(harness, "mo")
        print("assembled:", commit_top(harness, "moqishurufa"), flush=True)
        snap_files("e2-assemble")
        for r in range(6):
            for s in syls:
                commit_top(harness, s)
            top = commit_top(harness, "moqishurufa")
            print("round%d full-pinyin top1: %s" % (r + 1, top), flush=True)
            if "墨奇输入法" in top:
                print("WORD LEARNED at round", r + 1, flush=True)
                break
        snap_files("e2-after")

    elif _EXP == "e3":  # phrase extraction: commit long sentence x5
        gold = "冰川消融的直接结果就是冰湖面积显著扩大"
        raw = sentence_to_continuous_pinyin(gold)
        print("== probes before ==", flush=True)
        print("bingchuanxiao:", commit_top(harness, "bingchuanxiao"), flush=True)
        print("binghumianji:", commit_top(harness, "binghumianji"), flush=True)
        snap_files("e3-before")
        for r in range(5):
            got = commit_top(harness, raw)
            print("commit%d ok=%s" % (r + 1, got == gold), flush=True)
        print("== probes after ==", flush=True)
        print("bingchuanxiao:", commit_top(harness, "bingchuanxiao"), flush=True)
        print("binghumianji:", commit_top(harness, "binghumianji"), flush=True)
        snap_files("e3-after")

    elif _EXP == "e4":  # context frequency flip: yixiang / qishi
        for target in ("yixiang", "qishi"):
            print("== %s ==" % target, flush=True)
            print("bare:", commit_top(harness, target), flush=True)
            for ctx in ("wo", "ta de", "zhe shi", "ta de tai du hen"):
                commit_top(harness, ctx)  # commit context as previous text
                got = commit_top(harness, target)
                print("ctx[%s] -> %s" % (ctx, got), flush=True)
            snap_files("e4-" + target)

    harness.close()


main()
