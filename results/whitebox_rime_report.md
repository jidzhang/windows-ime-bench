# Rime 全拼方案白盒横评报告

**日期**：2026-10-26（读音修正版）｜ **引擎**：librime 进程内白盒（rime.dll，sha256 `9975f25c…`）
**参评**：明月简体（基准）/ 雾凇 / 白霜 / 万象 / 薄荷 ｜ **语料**：zhihu120（整句 n=120）、words234（词级 n=450）

---

## 一、背景与动机

主仓黑盒框架测一个输入法约 15 分钟（记事本真机逐键模拟），且真机状态含本机学习
与云候选，轮间需重置取证。Rime 生态的方案（schema）本质是**词库+配置包**，同一
librime 引擎即可加载——因此对 Rime 系方案改用**进程内白盒**：Python 直接加载
rime.dll 走 librime API 喂串取候选。收益：

- 速度：全套 5 方案 × 整句语料 **41 s**（首跑含部署 98 s），对比黑盒约 15 分钟/方案；
- 口径可控：零用户词库、零云、零调优，逐句**确定性输出**（可复现验证）；
- 与桌面小狼毫（`%APPDATA%\Rime`）零交集，用户安装保持零输入状态。

魔然（rime-moran）为自然码双拼+形码体系，输入维度与连续全拼不同，不参评。

## 二、方法

- **输入**：连续全拼（无分隔、无声调），句末空格取首选；判分与主仓黑盒同一套
  归一化（他/她/它→他、的/地/得→的）与指标（整句首选判对率、Levenshtein 文字正确率）；
- **读音纪律（gold sidecar）**：语料读音冻结在 `corpus/<stem>.pin.tsv`，评测优先
  查表；sidecar 由 vendor 词库（雾凇/白霜/薄荷 dict.yaml 独立注音）交叉审计生成——
  词库一致且异于 pypinyin → ERROR 修正候选；词库互歧或 OOV 含多音字 → 人工 REVIEW。
  本轮审计抓出并修正 pypinyin「尼泊尔 ní pō ěr（湖泊音）」错误（标准 ní bó ěr，
  3 句，此前两轮人工核对均漏检）；words234 读音零修正；
- **零用户词库**：每轮启动前清 `*.userdb`，`{schema}.custom.yaml` 补丁禁用
  `translator/enable_user_dict`；
- **隔离**：每方案独立 `vendor/<dir>` 作 user_data_dir，共享只读资源走 `vendor/data`；
- **挂模型口径（+gram）**：`*_with_gram` 目录 = 裸配目录副本 + grammar 补丁
  （参数取万象 schema 原值）+ 同一 `wanxiang-lts-zh-hans.gram`（398,505,004 B，
  sha256 `1849e5e4…`，本机 MoqiIME installer dist 取用；与 RIME-LMDG LTS release
  资产为不同构建）硬链接；万象为 schema 原生 grammar 声明；
- **正式语料**仅 zhihu120 与 words234（human1023 非正式材料，未采用）。

**版本定版**：雾凇 `75e6572`、白霜 `328ded2`、万象 `b935db4`（17.8.2）、
薄荷 `5fca6ae`；语料 sha256 `a7599698…`/`18ed321b…`。完整取证见
`engine/rime-schema-compare/report/whitebox_2026-10-26.md`。

## 三、结果（读音修正后）

### 整句 zhihu120（首选判对率 / 文字正确率）

| 方案 | 裸配 | +同一 gram | 模型增益 |
|---|---|---|---|
| **白霜 rime-frost** | **55.00%** / 90.96% | **65.83%** / 93.43% | +10.8 |
| 雾凇 rime-ice | 51.67% / 90.89% | 60.83% / 92.44% | +9.2 |
| 薄荷 oh-my-rime | 49.17% / 88.70% | 60.83% / 92.58% | +11.7 |
| 万象 rime-wanxiang | 48.33% / 89.27% | 60.00% / 92.23% | +11.7 |
| 明月（基准） | 43.33% / 85.17% | 48.33% / 86.72% | +5.0 |

读音修正影响：整句普遍 +0.8~+1.7 点（此前「尼泊尔」3 句被喂错音全员判错），
**排序不变**；词级不受影响。

### 词级 words234

| 方案 | 裸配 | +gram | 未中词（裸配 / +gram） |
|---|---|---|---|
| 雾凇 | 100.00% | 100.00% | — |
| 白霜 | 100.00% | 100.00% | — |
| 明月 | 99.78% | **99.33%** | 评论区→评论去 / 更多的是→更多的事、基本上是→基本上使 |
| 万象 | 99.78% | 99.78% | 老师→老是（两口径同） |
| 薄荷 | 99.78% | 99.78% | 老师→老是（两口径同） |

## 四、结论

1. **两种口径排序同构：白霜 > 雾凇 > 薄荷 ≈ 万象 > 明月**（gram 口径雾凇=薄荷并列）。
   白霜是唯一在裸配与挂模型口径都领跑的方案——词库质量与模型兼容性双优。
2. **万象的整句能力押在 ngram 模型上**：裸词库 48.33%（其 tarball 本就不带 .gram，
   "裸配"即多数手动安装者的真实状态）；模型增益 +11.7 但 60.00% 仍不及白霜挂
   同款模型的 65.83%。
3. **整句模型对短词有副作用**：明月挂 gram 词级反降 0.45 点；词级本就满分的
   雾凇/白霜不受影响。
4. n=120 时 95%CI≈±9 点：白霜对雾凇的领先（裸配 +3.3、+gram +5.0）属趋势性
   结论；词级 450 样本区分度不足以拉开 99.78 vs 100。

## 五、可重复验证（全过）

1. **确定性**：裸配整句 600 行、词级 2250 行、gram 600 行，两轮独立运行逐句预测
   0 差异；
2. **学习效应**：万象倒序语料复跑 120/120 句逐字一致（轮内自建 lua userdb 对候选
   零影响，属方案自身行为，保留并记录）；
3. **零外源污染**：vendor 目录与 `%APPDATA%\Rime` 零交集；裸配目录已移除 gram
   文件，可随时原样复现；
4. **读音闸**：`gold_pinyin audit` 0 未决；sidecar 启用前后 words234 逐句 0 diff
   （查表机制接线验证）。

## 六、局限

- 与黑盒商业榜**不可直接对比**：黑盒=真机默认设置（含本机学习、云候选、调优），
  白盒=零用户词库零云零调优；白盒数字普遍低于黑盒同语料成绩是口径使然；
- 单一 rime.dll 版本（小狼毫 0.17.4 自带）；gram 为 MoqiIME 构建版非 RIME-LMDG
  LTS release 原版（同源不同构建，已 sha256 定版）；
- 未模拟用户词典长期学习（Rime 的可学习性优势不在本口径内）；
- gold sidecar 审计依赖三家词库注音的共识，极生僻词仍可能漏检（OOV 只升 REVIEW
  供人工裁决）。

## 七、复现

```bash
cd engine/rime-schema-compare
# 新语料先冻结+审计读音（词级先 export RIME_BENCH_MIN_HANZI=2）
python -m rime_schema_compare.gold_pinyin freeze <corpus.txt> [out.tsv]
python -m rime_schema_compare.gold_pinyin audit  <corpus.txt> <out.tsv>

python scripts/benchmark_sentences.py --vendors mingyuepinyin rime_ice rime_frost wanxiang oh_my_rime \
  --corpus ../../../corpus/zhihu120.txt --out-dir artifacts_wb1        # 裸配整句
RIME_BENCH_MIN_HANZI=2 python scripts/benchmark_sentences.py --vendors ... --corpus ../../../corpus/words234.txt   # 词级
python scripts/benchmark_sentences.py --vendors mingyuepinyin_with_gram rime_ice_with_gram rime_frost_with_gram \
  rime_wanxiang_with_gram oh_my_rime_with_gram --corpus ../../../corpus/zhihu120.txt   # 挂模型
```

方法与取证细节、`*_with_gram` 目录构建法：`engine/rime-schema-compare/report/whitebox_2026-10-26.md`。
