# Orchestrate multi-mode A/C/B runs: reset + 4 rounds x 2 IMEs x 3 arms.
# Usage: python run_modes.py <mode> [rounds]
# Modes: M (mixed), J (all initials), T (neighbor typo). F is already done.
import subprocess
import sys
import time
from pathlib import Path

PY = r"C:\Program Files\Python313\python.exe"
RUNNER = r"F:\work\IME\ms-anatomy\contest_runner_modes.py"
CORPUS = r"F:\work\IME\ms-anatomy\corpus\cont_pairs_v2.tsv"
RESET = r"F:\work\IME\ms-anatomy\light-reset.cmd"
OUT = Path(r"F:\work\IME\ms-anatomy\contest")

mode = sys.argv[1].upper()
rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4

for r in range(1, rounds + 1):
    imes = ["microsoft_pinyin", "moqi_pinyin"] if r % 2 == 1 else ["moqi_pinyin", "microsoft_pinyin"]
    arms = ["a", "c", "b"] if r % 2 == 1 else ["b", "c", "a"]
    for ime in imes:
        short = "ms" if ime.startswith("microsoft") else "mq"
        for arm in arms:
            print("==== R%d %s %s %s ====" % (r, short, arm, time.strftime("%H:%M:%S")), flush=True)
            subprocess.call([RESET], shell=True)
            out = OUT / ("R%d_%s_%s_%s.tsv" % (r, short, arm, mode))
            subprocess.call([PY, RUNNER, ime, arm, mode, CORPUS, str(out)], shell=False)
print("ALL DONE", time.strftime("%H:%M:%S"), flush=True)