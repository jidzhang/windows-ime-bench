# cont/：续打（跨提交上下文）对标实验，2026-11-04

复现"已上屏文本能否校准下文候选"的 A/C/B 三子臂实验。方法/结论全文见
MoqiIME-docs 仓 `35-方案-续打对标测试方案-2026-11-04.md`、
`36-报告-续打对标-2026-11-04.md`。

## 语料

- `corpus/cont_pairs_v2.tsv`：129 项（103 自然 + 26 对照；2 拍 83 / 3 拍 46，
  59 个歧义靶词）。字段：id, nwords, words(逗号分隔), pinyin, target_pos,
  control, ms_amb, mq_amb, source。
- `corpus/targets.tsv`：59 个唯一靶词 + 全拼（可达性扫描用）。
- `corpus/ambiguous_words.tsv` / `ambiguous_union.tsv`：歧义靶词来源
  （微软黑盒 972 词 top-1 + 墨奇白盒 972 词 top-1 的并集，94 词入语料 59）。
- `corpus/vocab.tsv`：972 词基础词表（zhihu120/human1023/words234/d3pairs
  经 jieba 抽取）。
- `corpus/sweep_targets_*.tsv`：靶词可达性（单独输入，下翻 1~7 次提交，
  rank2~8 为可达）。F 模式用 `sweep_targets_{ms,mq}.tsv`，M/T 模式用
  `_M/_T` 后缀。

## 脚本

- `scripts/contest_runner.py`：F 全拼，A/C/B 三子臂。
- `scripts/contest_runner_modes.py`：M（上文全拼+靶词首字母）/
  J（全首字母）/ T（全拼+靶词首字母邻键替换）。
- `scripts/sweep_targets.py`：靶词可达性扫描（支持 F/M/J/T）。
- `scripts/corpus_items2.py`、`gen_vocab.py`、`merge_amb.py`、
  `gen_contexts.py`、`build_corpus.py`、`rank_words.py`：语料重建链路。
- `scripts/contest_analyze.py`、`contest_analyze_reach.py`、
  `contest_analyze_modes.py`、`contest_raw_modes.py`：汇总分析。
- `scripts/light-reset.cmd`：轻量干净门（杀 ChsIME/Moqi，清 MS
  ChsPinyin*.dat* 与 Moqi userdb，免管理员）。全量重置用
  `../scripts/reset_all_imes.bat`。

## 口径

- A=靶词独立；C=先打上文→清空编辑框→打靶词（只剩学习）；
  B=先打上文→直接打靶词（学习+可见上文）。
- 每子臂前 light-reset；4 轮（F/M）或 2 轮（T），MS/Moqi 与 A/C/B 顺序
  逐轮交替；C/B 要求上文提交正确，否则该项剔除。
- Δ_learn=C−A，Δ_ctx=B−C（主指标），对照项（无语义关联上文）验证伪影。

## 关键结果（详见 36-报告）

F 全拼 4 轮（完全一致）：
- 全部入选歧义项：MS A/C/B 11.4/11.4/25.0（n=88/轮，Δ_ctx +13.6）；
  Moqi 0/0/0。
- 可达靶词（rank2~8）：MS 20/59 可达，A/C/B 0/0/22.9，Δ_ctx **+22.9
  （CI 15.7~30.7）**；Moqi 27/59 可达，0/0/0。对照 Δ_ctx=0。

M 混拼 4 轮（纯首字母，困难靶词多数不可达，用原始口径+对照）：
- 微软自然项 A/C/B 0/0/11.3（n≈97/轮，Δ_ctx **+11.3**），对照 0；
  Moqi 全 0。
- M 可达性：MS 0/59、Moqi 7/59（纯首字母翻不到困难词，上下文是唯一路径）。

T 错键 2 轮（首字母邻键替换）：
- 两家 A/C/B 全 0；T 可达性两家均 0/59（rank0）。该错型不可纠正，
  本实验不能测上下文；T2 需改用 d7 可纠正的换位/增减错型。

## 复现

```
# 清干净（免管理员）
scripts\light-reset.cmd
# F 模式一轮：三子臂
python scripts\contest_runner.py microsoft_pinyin a corpus\cont_pairs_v2.tsv out_a.tsv
python scripts\contest_runner.py microsoft_pinyin c corpus\cont_pairs_v2.tsv out_c.tsv
python scripts\contest_runner.py microsoft_pinyin b corpus\cont_pairs_v2.tsv out_b.tsv
# M/T 模式（4/2 轮编排）
python scripts\run_modes.py M 4
```
依赖：windows-ime-bench 引擎 `engine/rime-schema-compare` 的 harness
（SendInput + Notepad 读回）、Python313（pypinyin/jieba）。

## 注意

- 靶词集是"两家独立 top-1 错"的困难集，绝对准确率不代表整体，结论只看
  Δ_ctx/Δ_learn。
- 尼泊尔读音：pypinyin 默认 nipoer，产品词典 rime-frost 为 ni bo er；
  测试转换器已加覆盖（engine 仓 41e3fdd），语料 id 8/105 分析时剔除。
- 实验期间用户重启一次：重启前批次仅作 pilot，未入结论。