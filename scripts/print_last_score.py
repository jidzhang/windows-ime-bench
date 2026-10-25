# Print the LAST [RESULT] line's score as a percentage, and optionally
# write it to summary_<label>_sent.md. ASCII only.
# Usage: python print_last_score.py <run_log.txt> [summary_path] [label]
import io
import re
import sys

log = sys.argv[1]
lines = [l for l in io.open(log, encoding="utf-8", errors="replace") if "[RESULT]" in l]
if not lines:
    print("NO RESULT line in log - run aborted?")
    sys.exit(1)
last = lines[-1]
m = re.search(r"exact=(\d+)", last)
t = re.search(r"total=(\d+)", last)
if not (m and t):
    print("PARSE FAIL: " + last.strip())
    sys.exit(1)
exact, total = int(m.group(1)), int(t.group(1))
pct = 100.0 * exact / total
line = "Sentences (zhihu120): %.2f%% (%d/%d)" % (pct, exact, total)
print(line)
if len(sys.argv) >= 3:
    label = sys.argv[3] if len(sys.argv) >= 4 else "?"
    import time
    with io.open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("# Sentence-only summary [%s]\n" % label)
        f.write("run finished: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
        f.write("\n%s\n" % line)
