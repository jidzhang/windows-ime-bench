# Force-focus test for the bench harness (AttachThreadInput trick).
import ctypes
import sys
import time
import json
from ctypes import wintypes

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness

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
    extra = json.load(open(r"Z:\dev\IME\windows-ime-bench\imes.json", encoding="utf-8"))
    sw = WindowsImeSwitcher(extra_profiles=extra)
    h = WindowsPinyinImeHarness()
    h.start()
    print("window", h._window_hwnd, "edit", h._edit_hwnd, flush=True)
    print("force win:", force_fg(h._window_hwnd), flush=True)
    print("force edit:", force_fg(h._edit_hwnd), flush=True)

    def strong_focus():
        ok = force_fg(h._edit_hwnd) or force_fg(h._window_hwnd)
        if not ok:
            time.sleep(0.1)
            force_fg(h._window_hwnd)

    h._focus_host = strong_focus
    sw.activate_profile("microsoft_pinyin", focus_callback=h.focus_host)
    h.self_check()
    h.reset_host()
    h.focus_host()
    h._open_ime()
    h._send_ascii_keys("nihao")
    time.sleep(0.15)
    h._press_space()
    print("commit:", h._wait_for_committed_text().strip(), flush=True)
    h.close()


if __name__ == "__main__":
    main()