# A/C/B contest runner with input modes: F full, M mixed (ctx full + target
# initials), J all initials, T full + target first-letter neighbor typo.
# Usage: python contest_runner_modes.py <ime> <arm:a|c|b> <mode:F|M|J|T> <corpus> <out> [limit]
import sys
import time
import json
import ctypes
from ctypes import wintypes
from pathlib import Path

BENCH = r"Z:\dev\IME\windows-ime-bench\engine\rime-schema-compare"
sys.path.insert(0, BENCH + r"\src")
sys.path.insert(0, BENCH + r"\scripts")

import rime_schema_compare.ms_pinyin_harness as H
from rime_schema_compare.ms_pinyin_harness import WindowsImeSwitcher, WindowsPinyinImeHarness
import rime_schema_compare.text_pipeline  # loads pypinyin phrase overrides
from pypinyin import lazy_pinyin, Style

_orig = H._run_powershell


def _safe(cmd):
    try:
        return _orig(cmd)
    except Exception:
        return ""


H._run_powershell = _safe

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

NEI = {
    "q": "wa", "w": "qea", "e": "wrs", "r": "etd", "t": "ryf", "y": "tug",
    "u": "yih", "i": "uoj", "o": "ipk", "p": "ol",
    "a": "qws", "s": "awedxz", "d": "serfcx", "f": "drtgvc", "g": "ftyhbv",
    "h": "gyujnb", "j": "huikmn", "k": "jiolm", "l": "kop",
    "z": "asx", "x": "zsdc", "c": "xdfv", "v": "cfgb", "b": "vghn",
    "n": "bhjm", "m": "njk",
}


def initials(word):
    if any(not ("\u4e00" <= ch <= "\u9fff") for ch in word):
        return ""
    pys = lazy_pinyin(word, style=Style.NORMAL, errors="ignore")
    if not pys or any(not p for p in pys):
        return ""
    return "".join(p[0] for p in pys)


def typo(pinyin):
    if not pinyin:
        return pinyin
    c = pinyin[0]
    ns = NEI.get(c)
    if not ns:
        return pinyin
    return ns[0] + pinyin[1:]


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


def transform(words, py, mode):
    if mode == "F":
        return py
    if mode == "M":
        out = list(py[:-1])
        out.append(initials(words[-1]))
        return out
    if mode == "J":
        return [initials(w) for w in words]
    if mode == "T":
        out = list(py)
        out[-1] = typo(py[-1])
        return out
    raise SystemExit("bad mode")


def main():
    ime, arm, mode, corpus, out = sys.argv[1], sys.argv[2].lower(), sys.argv[3].upper(), sys.argv[4], sys.argv[5]
    limit = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    rows = load_corpus(corpus, limit)
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
            tgt = it["words"][-1]
            keys = transform(it["words"], it["py"], mode)
            ctx_keys, tgt_key = keys[:-1], keys[-1]
            if not tgt_key or any(not k for k in ctx_keys):
                results.append((it["id"], arm, mode, it["n"], tgt, tgt_key, "", 0, "", 0, it["control"]))
                continue
            h.reset_host()
            if arm == "a":
                got = type_word(tgt_key, tgt)
                ctx_got, ctx_ok = "", True
            else:
                got_ctx = []
                for w, p in zip(ctx_words, ctx_keys):
                    got_ctx.append(type_word(p, w))
                ctx_got = got_ctx[-1].strip() if got_ctx else ""
                ctx_ok = ctx_got == "".join(ctx_words)
                base = ctx_got if arm == "b" else ""
                if arm == "c":
                    h.reset_host()
                final = type_word(tgt_key, tgt)
                got = final[len(base):].strip() if arm == "b" else final
            results.append((it["id"], arm, mode, it["n"], tgt, tgt_key, got,
                            int(got == tgt), ctx_got, int(ctx_ok), it["control"]))
            if (n + 1) % 20 == 0:
                print("[%s/%s/%s] %d/%d %.1fs" % (ime, arm, mode, n + 1, len(rows), time.perf_counter() - t0), flush=True)
    finally:
        h.close()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("id\tarm\tmode\tnwords\ttarget\ttarget_py\tgot\texact\tctx_got\tctx_ok\tcontrol\n")
        for r in results:
            f.write("\t".join(map(str, r)) + "\n")
    print("done:", out, "time %.1fs" % (time.perf_counter() - t0))


if __name__ == "__main__":
    main()