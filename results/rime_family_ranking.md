# 回到起点：墨奇在 Rime（小狼毫）家族里是什么水平

> 2026-10-27 ｜ 口径：黑盒真机（同机同框架同语料 zhihu120 + words234，逐臂清用户词典）
> 所有数字均可在 `results/run/` 下按目录復现；配对显著性用 `scripts/family_paired.py`。

## 一、先厘清"家族成员"

实测各产品安装目录的二进制，**只有两家是 librime 核**：

| 产品 | librime | 证据 |
|---|---|---|
| 墨奇 | ✓ | `MoqiIM\moqi-ime\input_methods\rime\rime.dll`（Go 管线在外层） |
| 素言 | ✓ | `Program Files\SuYan\rime.dll`（含 lua 插件字符串）+ 自带完整 `rime/` 目录，默认方案 `rime_ice`（雾凇）、小鹤双拼、86 五笔 |
| 青简 | ✕ | 全目录无 `*rime*.dll`、二进制无 librime 字符串；`qingjian-server.exe` + `data/models/hanzhang-tongbian`（onnxruntime）自研引擎 |
| 清风 | ✕ | 全目录无 `*rime*.dll`；`wind_tsf.dll` + `data/schemas/*.schema.toml` + `pinyin_map.txt`，自研引擎（五笔血统、Rust 侧配置） |

所以严格意义上，17 家黑盒表里属于 Rime 家族的成品只有**墨奇、素言**两家；
青简、清风是独立引擎（它们的成绩照样有效，只是不能算"Rime 方案水平"）。
小狼毫本体作为参照系单独列臂。

## 二、同口径排名（黑盒，修正读音语料）

| 排名 | 配置 | 整句 | 词级 | 性质 |
|---|---|---|---|---|
| 1 | 小狼毫 + 白霜 + wanxiang-lts gram | **65.83**（79/120） | **100.00** | 手动加配（D 臂） |
| 2 | 墨奇 + 万象方案 | 63.33（76/120） | — | 换方案后的产品上限 |
| 3 | **墨奇成品（默认）** | **62.50**（75/120） | 99.11 | 开箱状态 |
| 4 | 小狼毫 + 白霜（裸） | 55.83（67/120） | **100.00** | 手动装方案（B 臂） |
| 5 | 素言（Rime 核，rime_ice + onnx） | 45.83（55/120） | **100.00** | 开箱状态 |
| — | 青简（非 Rime 核） | 49.17~50.00 | 98.89 | 开箱状态 |
| 6 | 小狼毫默认（明月简体） | 41.67（50/120） | 99.33 | 开箱状态（A 臂） |
| — | 清风（非 Rime 核） | 41.67（50/120） | **100.00** | 开箱状态 |

来源：`results/fwm_product_compare.md`（A/B/C/D 四臂，`results/run/fwm_run_log.txt`）、
`results/run/wanxiang`（墨奇挂万象方案）、`results/run/weasel_luna|weasel_frost|weasel_frost_gram`、
`results/summary_online3.md`（素言/青简/清风同轮）。

## 三、结论

1. **开箱即用维度：墨奇是 Rime 家族第一**（62.50），比小狼毫默认高 20.8 点，
   比手动装白霜高 6.7 点。
2. **但把参照系武装到同等配置，墨奇是 −3.3（65.83 vs 62.50，±9 CI 内并列）**：
   优势可完全归因于"默认就挂模型 + 默认用白霜系词库"，不是引擎或定制层。
3. **引擎层两家同水平**：白盒 A/B 词级逐位一致、整句统计打平（`results/whitebox_rime_report.md`）。
4. **素言说明"Rime 核"本身不产生成绩**：同为 librime、默认雾凇方案还叠了 onnx 模型，
   仍只有 45.83——家族内的高低由词库与模型决定，不由是否 Rime 决定。
5. 对墨奇的含义：**位置是"Rime 家族里开箱最强"，不是"比 Rime 更强"**。要越过
   65.83 这条线，只能从方案/模型/重排里找净增益（万象方案已证 +0.8 到 63.33，
   自训 wiki 模型为零增益）。

## 四、显著性别说过头

同轮可配对数据（`results/run/online3`，120 句逐句对照，McNemar 精确检验）：

| 对照 | 仅前者对 | 仅后者对 | p | Δ 95% CI |
|---|---|---|---|---|
| 墨奇 57.50 vs 青简 49.17 | 23 | 13 | 0.13 | −1.7 ~ +18.3 |
| 墨奇 57.50 vs 素言 45.83 | 20 | 6 | 0.009 | +3.3 ~ +20.0 |
| 墨奇 57.50 vs 清风 41.67 | 22 | 3 | 0.0002 | +8.3 ~ +23.3 |

- 对素言、清风是显著领先；**对青简的 +8 点在单轮口径下不显著**（三轮同向，
  失配对为 22/23/23 对 13/13/13，稳定小幅领先，但不是"大胜"）；
- 词级全员 98.89~100.00（450 词里差 1~5 个词），差异在噪声内，不构成区分度。

## 五、复现

```bash
# 逐句配对 + McNemar + bootstrap CI
python scripts/family_paired.py --run results/run/online3 --corpus zhihu120 \
    --vendors moqi qingjian suyan windinput
python scripts/family_paired.py --run results/run/online3 --corpus words234 \
    --kind words --vendors moqi qingjian suyan windinput
```

四臂 A/B/C/D 的跑法见 `results/fwm_product_compare.md` 末节；产品级模型臂见
`docs/protocol_native_stack.md`。