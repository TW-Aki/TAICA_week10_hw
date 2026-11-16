標題：模型與記憶體選擇：量化 pack 怎麼挑
來源網址：https://github.com/Niko1221/Strata/blob/main/docs/MODELS.md
教材整理日期：2026-11-16
資料類型：官方文件

# 模型與記憶體選擇

Strata 的 README 指向 `docs/MODELS.md#pick-by-memory`，要使用者依照電腦記憶體挑模型。以下是 README 與模型清單中出現的資訊。

## 量化為什麼重要

本地部署最大的限制不是算力，而是「模型權重放不放得下、搬得快不快」。量化（quantization）用較少的位元表示權重，例如 Q8、Q4、IQ2、IQ1，數字越小越省記憶體，但精度與推理品質可能下降。

Strata 主打的 `Qwen3.8-Flash-Next` 提供多種量化：

| Provider | 量化 pack | 特性（README / 文件提示） |
|---|---|---|
| ISTA-DASLab | `Q2_0`、`IQ2_XS`、`IQ3_XXS`、`IQ3_S` | 官方推薦的低記憶體選項 |
| ISTA-DASLab Coder | `IQ1_M` | 編碼情境推薦 |
| Unsloth | `UD-IQ4_XS`、`UD-Q4_K_XL`、`UD-Q5_K_XL`、`UD-Q6_K_XL`、`Q8_0` | 較高品質、較吃記憶體 |
| Gyro（agentionai） | `Gyro-S`、`Gyro-M` | 更省記憶體但更慢 |
| 其他 | Swift 1.5、NVFP4、OrcaRouter | 不同硬體/路徑的選擇 |

`Qwen3.6-35B-A3B` 已記錄的 pack 則有 `UD-Q4_K_XL`、`UD-Q6_K_XL`、`Q8_0`。

## 選擇流程建議

1. 先查自己的顯存（VRAM）與系統記憶體（RAM）。
2. 到 `docs/MODELS.md#pick-by-memory` 對照模型所需記憶體。
3. 記憶體緊就想低 bit，例如 `IQ2_XS`、`IQ3_XXS`、`Q2_0`。
4. 編程用途可考慮 `Coder: IQ1_M`。
5. 記憶體充裕就往 `Q4_K_XL`、`Q6_K_XL`、`Q8_0` 走，品質較好。
6. 若更在意省記憶體而非速度，可看 `Gyro-S`、`Gyro-M`。

## 取捨

- 低量化：省記憶體、可跑更大模型，但複雜推理可能劣化。
- 高量化：品質較好，但需要更多 VRAM/RAM。
- 硬體太舊：即使量化成功，支援的 GPU 清單仍要先確認（見 01 文件）。

## 常見誤區

- 「看到 100B 就想試試看」：要注意 MoE 模型的「總參數」與「每次啟動參數」不同，還要看 RAM 是否放得下全部專家。
- 「量化越低越好」：IQ1/IQ2 在需要多步推理的任務上可能明顯退化。
