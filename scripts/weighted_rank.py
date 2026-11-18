# 综合排名：长句 + 词级加权平均（用户 2026-11-18 定调：不要太看重长句能力）
#
# 权重设计依据：
#   - 长句（zhihu120）只反映"一次全拼整句的首选命中"，用户明说不看重；
#   - 词级（words23456 / words_mixed）更贴近日常「打一个词就上屏」的实际体验，
#     且新增 5/6 字与混合输入后区分度明显提升。
#   => 长句 30% / 词级 70%（词级内部：words23456 40% + words_mixed 30%）
#
# 用法：python weighted_rank.py <repo_root> <run_label> [--online|--offline]
# 读取 results/run/<label>/ 下各 IME 的 summary，输出加权排名表。
import io
import os
import sys


def read_summary(path):
    """解析 benchmark_*_summary.csv，返回 {ime: {corpus: accuracy}}。"""
    import csv
    out = {}
    if not os.path.isfile(path):
        return out
    for r in csv.DictReader(io.open(path, encoding='utf-8-sig')):
        ime = r.get('vendor') or r.get('ime')
        acc = r.get('sentence_accuracy_percent')
        if ime and acc:
            out[ime] = float(acc)
    return out


def collect(run_dir):
    """扫描 run 目录，按语料归集各 IME 成绩。"""
    import glob
    import re
    data = {}
    known = ('zhihu120', 'words23456', 'words_mixed', 'words234')
    pat = re.compile(r'benchmark_(.+?)_(' + '|'.join(known) + r')_\d+T\d+Z_summary\.csv$')
    for kind in ('sentences', 'words'):
        for f in glob.glob(os.path.join(run_dir, kind, 'benchmark_*_summary.csv')):
            m = pat.search(os.path.basename(f))
            if not m:
                continue
            ime, corpus = m.group(1), m.group(2)
            for r in __import__('csv').DictReader(io.open(f, encoding='utf-8-sig')):
                acc = r.get('sentence_accuracy_percent')
                if acc:
                    data.setdefault(ime, {})[corpus] = float(acc)
    return data


WEIGHTS = {
    'zhihu120': 0.30,      # 长句：只占 30%
    'words23456': 0.40,    # 词级（2-6 字全拼）：40%
    'words_mixed': 0.30,   # 词级（前全拼后简拼）：30%
}


def main():
    repo, label = sys.argv[1], sys.argv[2]
    run_dir = os.path.join(repo, 'results', 'run', label)
    data = collect(run_dir)
    if not data:
        print('no data in', run_dir)
        return 1

    rows = []
    for ime, d in data.items():
        score, parts, missing = 0.0, [], []
        for corpus, w in WEIGHTS.items():
            if corpus in d:
                score += d[corpus] * w
                parts.append('%s=%.2f' % (corpus, d[corpus]))
            else:
                missing.append(corpus)
        rows.append((score, ime, parts, missing))
    rows.sort(reverse=True)

    print('# 加权综合排名 [%s]' % label)
    print('# 权重：长句 30% / words23456 40% / words_mixed 30%')
    print()
    print('| 排名 | 输入法 | 加权分 | 长句 | 词2-6字 | 词混合 |')
    print('|---|---|---|---|---|---|')
    for i, (score, ime, parts, missing) in enumerate(rows, 1):
        d = data[ime]
        def g(c):
            return ('%.2f' % d[c]) if c in d else '—'
        note = ('  (缺 %s)' % ','.join(missing)) if missing else ''
        print('| %d | %s | **%.2f** | %s | %s | %s |%s' % (
            i, ime, score, g('zhihu120'), g('words23456'), g('words_mixed'), note))
    return 0


if __name__ == '__main__':
    sys.exit(main())
