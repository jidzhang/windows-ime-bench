# Inspect d3pairs sidecar structure.
import io

p = r"Z:\dev\IME\windows-ime-bench\corpus\d3pairs225.pin.tsv"
lines = []
for l in io.open(p, encoding="utf-8"):
    l = l.rstrip("\n")
    if l.strip() and not l.startswith("#"):
        lines.append(l)
print("lines:", len(lines))
for l in lines[:3] + [x for x in lines if len(x.split("\t")[0]) in (6, 8)][:8]:
    w, key = l.split("\t")
    print(len(w), repr(w), repr(key))