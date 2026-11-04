# Reachability sweep for unique target words: type pinyin, Down k, space.
# Usage: python sweep_targets.py <ime> <targets.tsv> <out.tsv>
import sys
import time
import json
import ctypes
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, r"F:\work\IME\ms-anatomy")
import contest_runner_modes as MODES

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
VK_DOWN = 0x28

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.SetFocus.argtypes = [wintypes.HWND]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]


def force_fg(hwnd):
    if not hwnd:
        return False
    fg = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    tid_fg = user32.GetWindowThreadProcessId(fg, ctypes.byref(pid)) if fg else 0
    tid_cur = kernel32.GetCurrentThreadId()
    attached = False
    if tid_fg and tid_fg != tid_cur:
        attached = bool(user32.AttachThreadInput(tid_cur, tid_fg, True))
    user32.ShowWindow(hwnd, 9)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)
    if attached:
        user32.AttachThreadInput(tid_cur, tid_fg, False)
    return user32.GetForegroundWindow() == hwnd


def main():
    ime, targets_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    mode = sys.argv[4].upper() if len(sys.argv) > 4 else "F"
    targets = []
    with open(targets_path, encoding="utf-8") as f:
        next(f)
        for line in f:
            w, p = line.rstrip("\n").split("\t")
            targets.append((w, p))
    kw = {}
    if ime in ("wechat_pinyin", "ximeyao_pinyin", "shouxin_pinyin"):
        kw["commit_delay_s"] = 0.30
    h = WindowsPinyinImeHarness(**kw)
    h.start()

    def strong_focus():
        force_fg(h._window_hwnd)
        force_fg(h._edit_hwnd)
        time.sleep(0.03)

    h._focus_host = strong_focus
    extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
    sw = WindowsImeSwitcher(extra_profiles=extra)
    sw.activate_profile(ime, focus_callback=h.focus_host)
    h.self_check()

    def commit(py, downs):
        h.reset_host()
        h.focus_host()
        h._open_ime()
        h._send_ascii_keys(py)
        time.sleep(h.commit_delay_s)
        for _ in range(downs):
            h._send_vk(VK_DOWN)
            time.sleep(0.03)
        h._press_space()
        return h._wait_for_committed_text().strip()

    rows = []
    t0 = time.perf_counter()
    try:
        for n, (w, p) in enumerate(targets):
            if mode in ("M", "J"):
                key = MODES.initials(w)
            elif mode == "T":
                key = MODES.typo(p)
            else:
                key = p
            if not key:
                rows.append((w, key, 0, ""))
                continue
            rank = 0
            top1 = commit(key, 0)
            if top1 == w:
                rank = 1
            else:
                for downs in range(1, 8):
                    if commit(key, downs) == w:
                        rank = downs + 1
                        break
            rows.append((w, key, rank, top1))
            if (n + 1) % 10 == 0:
                print("[sweep %s] %d/%d %.1fs" % (ime, n + 1, len(targets), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("word\tpinyin\trank\ttop1\n")
        for r in rows:
            f.write("%s\t%s\t%d\t%s\n" % r)
    print("done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    main()