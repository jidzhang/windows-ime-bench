# Summarize one benchmark run into results/summary_<Label>.md
# Called automatically by run.bat; can also be run manually:
#   python scripts/collect_results.py <repo_root> <label>
import glob
import io
import os
import re
import sys

root, label = sys.argv[1], sys.argv[2]
rows = {}
for kind, sub in (("sentences", "sentences"), ("words", "words")):
    best = {}
    for f in glob.glob(os.path.join(root, "results", "run", label, sub, "benchmark_*_report.txt")):
        s = io.open(f, encoding="utf-8").read()
        i = s.find("Overall")
        if i < 0:
            i = s.find("【Overall】")
        if i < 0:
            continue
        m = re.search(r"benchmark_(\w+?)_(?:zhihu120|words234)_", f)
        if not m:
            continue
        ime = m.group(1)
        for line in s[i:i + 400].splitlines():
            if "sentence accuracy" in line or "句子正确率" in line:
                try:
                    pct = float(line.split(":")[1].split("%")[0])
                except ValueError:
                    continue
                if ime not in best or pct > best[ime]:
                    best[ime] = pct
    rows[kind] = best

titles = {"sentences": "Sentences (zhihu120)", "words": "High-frequency words (words234)"}
out = [f"# Benchmark summary [{label}]", ""]
for kind in ("sentences", "words"):
    out.append(f"## {titles[kind]}")
    for k, v in sorted(rows[kind].items(), key=lambda x: -x[1]):
        out.append(f"- {k}: {v:.2f}%")
    out.append("")
dst = os.path.join(root, "results", f"summary_{label}.md")
io.open(dst, "w", encoding="utf-8").write("\n".join(out))
print("summary written:", dst)
