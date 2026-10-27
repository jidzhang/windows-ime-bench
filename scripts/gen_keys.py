"""Generate frozen key sequences (gold<TAB>keys) for native-stack evaluation.

Input : corpus/<name>.txt  + corpus/<name>.pin.tsv (audited readings)
Output: corpus/<name>.keys.tsv
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine" / "rime-schema-compare" / "src"))

from rime_schema_compare import text_pipeline as tp  # noqa: E402


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "zhihu120"
    txt = ROOT / "corpus" / f"{name}.txt"
    pin_path = ROOT / "corpus" / f"{name}.pin.tsv"
    out = ROOT / "corpus" / f"{name}.keys.tsv"

    pin = {}
    for line in io.open(pin_path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        hanzi, py = line.rstrip("\n").split("\t")
        pin[hanzi] = py

    # activate sidecar so fallback conversion matches audited readings
    tp.activate_gold_pinyin_for_corpus(str(txt))

    rows, missing = [], 0
    for line in io.open(txt, encoding="utf-8"):
        gold = line.strip()
        if not gold:
            continue
        hanzi = tp.extract_hanzi(gold)
        keys = pin.get(hanzi) or tp.sentence_to_continuous_pinyin(hanzi)
        if not keys:
            missing += 1
            continue
        rows.append(f"{gold}\t{keys}\n")

    io.open(out, "w", encoding="utf-8", newline="\n").write("".join(rows))
    print(f"{out.name}: {len(rows)} rows, missing={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())