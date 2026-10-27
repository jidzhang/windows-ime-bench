#!/usr/bin/env python3
"""Paired comparison of two or more vendors inside one benchmark run.

Why paired: two independent 95% CIs on 120 sentences are +/-9 points each, so a
raw gap of 8 points looks inconclusive.  Comparing the *same* sentences removes
the per-sentence difficulty variance and gives a far tighter interval.

Usage:
  python scripts/family_paired.py --run results/run/online3 --corpus zhihu120 \
      --vendors moqi qingjian suyan windinput

Reads <run>/<kind>/benchmark_<vendor>_<corpus>_*_long_by_sentence.csv, pivots on
corpus index, prints accuracy plus pairwise McNemar exact test and a paired
bootstrap CI (20000 resamples) for each difference.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import random
import sys
from itertools import combinations


def load_runner(run_dir: str, kind: str, corpus: str, vendor: str):
    pattern = os.path.join(run_dir, kind, f"benchmark_{vendor}_*_{corpus}_*_long_by_sentence.csv")
    paths = sorted(glob.glob(pattern))
    if not paths:
        pattern = os.path.join(run_dir, f"benchmark_{vendor}_*_{corpus}_*_long_by_sentence.csv")
        paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(pattern)
    rows = {}
    with open(paths[-1], newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rows[int(row["index"])] = (row["exact"].strip() == "True", row.get("gold", ""), row.get("prediction", ""))
    return paths[-1], rows


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact binomial p for b vs c discordant pairs (p0=0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # P(X <= k) * 2, capped at 1
    from math import comb
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def bootstrap_diff(a_flags, b_flags, n_boot=20000, seed=20261027):
    rnd = random.Random(seed)
    n = len(a_flags)
    diffs = []
    for _ in range(n_boot):
        acc_a = acc_b = 0
        for _ in range(n):
            i = rnd.randrange(n)
            acc_a += a_flags[i]
            acc_b += b_flags[i]
        diffs.append((acc_a - acc_b) / n * 100.0)
    diffs.sort()
    lo = diffs[int(0.025 * n_boot)]
    hi = diffs[int(0.975 * n_boot) - 1]
    return lo, hi


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--corpus", default="zhihu120")
    ap.add_argument("--kind", default="sentences", choices=["sentences", "words"])
    ap.add_argument("--vendors", nargs="+", required=True)
    args = ap.parse_args()

    data = {}
    for vendor in args.vendors:
        path, rows = load_runner(args.run, args.kind, args.corpus, vendor)
        data[vendor] = rows
        ok = sum(1 for v in rows.values() if v[0])
        print(f"{vendor:12s} {ok:3d}/{len(rows):3d} = {ok / len(rows) * 100:6.2f}%   ({os.path.basename(path)})")

    idx = sorted(set.intersection(*[set(r) for r in data.values()]))
    print(f"\npaired on {len(idx)} items: {idx[0]}..{idx[-1]}\n")

    print(f"{'pair':28s} {'both':>5s} {'A only':>7s} {'B only':>7s} {'exact p':>8s} {'Δ boot 95% CI':>18s}")
    for a, b in combinations(args.vendors, 2):
        ra = [data[a][i][0] for i in idx]
        rb = [data[b][i][0] for i in idx]
        both = sum(1 for x, y in zip(ra, rb) if x and y)
        a_only = sum(1 for x, y in zip(ra, rb) if x and not y)
        b_only = sum(1 for x, y in zip(ra, rb) if y and not x)
        p = mcnemar_exact(a_only, b_only)
        lo, hi = bootstrap_diff(ra, rb)
        print(f"{a+' vs '+b:28s} {both:5d} {a_only:7d} {b_only:7d} {p:8.4f}   [{lo:+.1f}, {hi:+.1f}] pts")
    return 0


if __name__ == "__main__":
    sys.exit(main())