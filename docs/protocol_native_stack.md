# 原生栈评测协议（产品级，可重复验证）

> 目的：固定"产品真实表现"的测量方式，消除跨会话口径漂移。
> 2026-10-27 立。此前多轮结论互相矛盾，根因是三套口径混用（下节）。

## 一、三套口径（不可混比）

| 口径 | 含义 | 工具 | 典型 zhihu120 整句 |
|---|---|---|---|
| **引擎白盒** | 只调 rime.dll，绕过 Go 层 | `engine/rime-schema-compare`（librime 直调） | 52~60 |
| **原生栈（产品级）** | rime.dll + Go 管线（上下文/重排/词典）+ 产品数据 | `tools/native_stack/eval-sentences-v3.exe -stack ime` | 54~63 |
| 黑盒 | TSF 真机按键（含真实输入法宿主） | `scripts/run.bat` | 与原生栈接近，慢 |

**规则：任何"产品表现"结论必须用原生栈或黑盒；引擎白盒只能用于引擎/模型对比的
相对量，且必须标注口径。** 2026-10-27 的错误结论（"万象 52.5、模型没用"）就是拿
引擎白盒当产品结论造成的。

## 二、固定输入

- 语料：`corpus/zhihu120.txt`（sha256 `a7599698…`）
- 读音：`corpus/zhihu120.pin.tsv`（sha256 `0bc9a927…`，词库交叉审计定版）
- **按键序列**：`corpus/zhihu120.keys.tsv`（sha256 `1ca9e0ba…`）——由上面两者生成，
  评测时用 `-pinyinCorpus` 强制使用，杜绝逐字推导歧义与错音。
- 生成命令（语料/读音若变更必须重生成并更新 hash）：
  ```bash
  python scripts/gen_keys.py            # corpus/zhihu120.txt + .pin.tsv -> .keys.tsv
  ```

## 三、固定工具（已归档，勿用外部副本）

| 文件 | sha256（前 16） |
|---|---|
| `tools/native_stack/eval-sentences-v3.exe` | `df0356b403349e6e` |
| `tools/native_stack/pinyin.txt` | `621f8ca9eff8519f` |
| `tools/native_stack/zh-bigram.tsv` | `dcb0aa1d6d19d706` |
| `tools/native_stack/rime.dll` | `7b7990146546a9b5`（必须与 exe 同目录，否则加载失败） |

`zh-bigram.tsv` 必须放到被测 `-data` 目录里，否则 Go 层重排静默空转（2026-10-27 踩过）。

## 四、固定被测配置（数据目录）

被测 `-data` = 产品 stage 数据目录（含词典与构建产物），按臂替换 `.gram` 与
`rime_frost.custom.yaml`：

| 臂 | grammar/language | non_collocation_penalty |
|---|---|---|
| base | （无） | — |
| wiki | zh-moqi-wiki | -6（可选 -14 档） |
| essay | zh-hans-t-essay-bgw | -4 |
| wanxiang | wanxiang-lts-zh-hans | 0 |

产品 stage 数据来自 `Z:\dev\IME\MoqiIME\moqi-im-windows\installer\stage\win32\MoqiIM\moqi-ime\input_methods\rime\data`
（构建产物，不入库；用时复制到仓库外临时目录）。

## 五、执行

```bat
scripts\bench_native_stack.bat <data_dir> [label]
```

内部等价命令：

```bat
tools\native_stack\eval-sentences-v3.exe ^
  -corpus corpus\zhihu120.txt -pinyinCorpus corpus\zhihu120.keys.tsv ^
  -input full -stack ime -data <data_dir> -user <user_dir> ^
  -pinyin tools\native_stack\pinyin.txt -limit 0
```

- 每臂用**全新 user 目录**（userdb 学习会漂移 1.5+ 点）；
- 结果判定 `top-1`（首选整句命中率）与 `macroCER`；
- **复跑要求**：同一臂连跑两次，`top-1` 与 `macroCER` 必须逐位相同，否则视为
  环境不干净（学习残留/缓存），结果作废。

## 六、基准值（2026-10-27，产品 stage 数据，zhihu120）

| 臂 | top-1 | macroCER | 备注 |
|---|---|---|---|
| base（无模型） | 54.17% (65/120) | 0.0983 | |
| wiki -6 | 54.17% (65/120) | 0.0983 | 零增益 |
| wiki -14 | 54.17% (65/120) | 0.0983 | 零增益（与引擎白盒结论不同！） |
| essay -4 | 58.33% (70/120) | 0.0957 | +4.16 |
| **wanxiang 0** | **63.33% (76/120)** | **0.0787** | +9.16；两次复跑一致 |
| wanxiang -6 | 63.33% (76/120) | 0.0787 | 与 0 同分 |

结论：**产品栈上万象显著最优，自训 wiki 模型零增益**。引擎白盒里 wiki +0.83、
万象 −2.5 的排序在产品栈上完全反转——这是 2026-10-27 最大的方法论教训。