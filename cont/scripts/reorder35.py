# Reorder sections in 35 plan: move inserted §十一/§十二 after §十, restore §七.
import io

p = r"Z:\dev\IME\MoqiIME\35-方案-续打对标测试方案-2026-11-04.md"
s = io.open(p, encoding="utf-8", newline="").read()
start = s.index("## 十一、")
end = s.index("- 主指标：**Δ_ctx")
block = s[start:end]
s2 = s[:start] + "## 七、指标与统计\n\n" + s[end:]
anchor = "## 附录 A："
i = s2.index(anchor)
s2 = s2[:i] + block + "\n" + s2[i:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s2)
print("reordered; headings:")
for line in s2.splitlines():
    if line.startswith("## "):
        print(line)