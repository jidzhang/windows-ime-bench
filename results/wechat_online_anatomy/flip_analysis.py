"""Analyze online-vs-offline flips for WeChat IME on zhihu120 (archived data).

online = results/run/online2 (20261025T100641Z, 85/120)
offline = D: copy run/offline_wechat (20261026T015230Z, 43/120)
Output: flip table + bucket stats -> F:\\work\\IME\\wechat-anatomy\\flip_report.txt
"""
import csv, io, sys

ON = r"Z:\dev\IME\windows-ime-bench\results\run\online2\sentences\benchmark_wechat_pinyin_zhihu120_20261025T100641Z.csv"
OFF = r"D:\work\github\IME\windows-ime-bench\results\run\offline_wechat\sentences\benchmark_wechat_pinyin_zhihu120_20261026T015230Z.csv"
OUT = r"F:\work\IME\wechat-anatomy\flip_report.txt"

def load(path):
    rows = {}
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            rows[int(r["index"])] = {
                "gold": r["gold"],
                "got": r.get("wechat_pinyin_prediction", ""),
                "ok": r.get("wechat_pinyin_sentence_correct", "0") == "1",
                "input": r.get("wechat_pinyin_input", ""),
            }
    return rows

on = load(ON)
off = load(OFF)
assert set(on) == set(off), "index mismatch"

flips = [i for i in sorted(on) if on[i]["ok"] and not off[i]["ok"]]
rev = [i for i in sorted(on) if off[i]["ok"] and not on[i]["ok"]]
both = [i for i in sorted(on) if on[i]["ok"] and off[i]["ok"]]
neither = [i for i in sorted(on) if not on[i]["ok"] and not off[i]["ok"]]

rep = io.open(OUT, "w", encoding="utf-8", newline="\n")
w = lambda s: rep.write(s + "\n")
w("online=%d/%d offline=%d/%d  flips(on>off)=%d reverse=%d both=%d neither=%d"
  % (sum(1 for v in on.values() if v["ok"]), len(on),
     sum(1 for v in off.values() if v["ok"]), len(off),
     len(flips), len(rev), len(both), len(neither)))

# bucket stats on flips
import statistics
lens = [len(on[i]["gold"]) for i in flips]
w("flip gold length: min=%d median=%d max=%d" % (min(lens), statistics.median(lens), max(lens)))
w("flip by length bucket: <=8:%d  9-14:%d  >=15:%d" % (
    sum(1 for L in lens if L <= 8), sum(1 for L in lens if 9 <= L <= 14), sum(1 for L in lens if L >= 15)))
has_ascii = [i for i in flips if any("a" <= c.lower() <= "z" or c.isdigit() for c in on[i]["gold"])]
w("flip gold contains ASCII/digits: %d" % len(has_ascii))
w("")

w("== flip detail (idx | len | gold | offline_got | online_got) ==")
for i in flips:
    w("%3d | %2d | %s | %s | %s" % (i, len(on[i]["gold"]), on[i]["gold"], off[i]["got"], on[i]["got"]))
rep.close()

# console mirror
txt = io.open(OUT, encoding="utf-8").read()
sys.stdout.buffer.write(txt[:3000].encode("utf-8"))
print("\n(full report -> %s)" % OUT)
