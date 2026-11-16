標題：Strata vs Ollama vs vLLM vs SGLang 選型比較
來源網址：https://zhuanlan.zhihu.com/p/2101327443474883150
教材整理日期：2026-11-16
資料類型：技術評論

# 四套工具的定位差異

這篇技術評論把 Strata 放在「消費級硬體上跑超大模型」的位置，並與 Ollama、vLLM、SGLang 比較。

## 核心定位

| 工具 | 主要定位 |
|---|---|
| Strata | 消費級極限跨層推理：單機跑超顯存 MoE |
| Ollama | 輕量個人應用：極簡桌面、一鍵運行 |
| vLLM | 企業級生產高吞吐：集群、高並發 |
| SGLang | 複雜 Agent / 長文本服務：快取與結構化推理 |

## 技術核心

- Strata：C++ 異構分層排程 + CPU/GPU 平行執行
- Ollama：基於 llama.cpp（GGUF 跨平台執行）
- vLLM：PagedAttention + Continuous Batching
- SGLang：RadixAttention（前綴快取）+ 結構化約束解碼

## 硬體門檻

- Strata：消費級顯卡 12~24G + 大記憶體 32~64G+
- Ollama：一般的 PC、Mac 統一記憶體、甚至是沒有顯卡的 CPU 環境
- vLLM：資料中心卡或高顯存工作站，權重大多要塞進 VRAM
- SGLang：資料中心卡或多卡集群，需要大顯存支撐高並發快取

## 併發與吞吐

- Strata：針對單併發（Batch=1）極致優化
- Ollama：單併發尚可，併發擴充能力較弱
- vLLM：針對吞吐量（Throughput）調校，極高多併發吞吐
- SGLang：針對吞吐量調校，在多輪對話與樹搜尋特別高效

## Strata 的技術原理（評論所述）

1. 多級分層專家管理（Expert Tiering）：GPU VRAM 放注意力層、路由器、共享專家、輸出頭與熱點專家池；Host RAM 鎖住全部專家；NVMe SSD 放大型靜態查找表，靠 page cache 按需讀取。
2. CPU 與 GPU 異構平行：token 路由到冷專家時，直接用 CPU 的 AVX2 / AVX-512 在記憶體內計算，gpu 同時算熱門部分，兩條管線重疊，避開 PCIe 瓶頸。
3. 投機解碼與多 token 預測（MTP）：單次前向驗證多個候選 token。評論聲稱在 RTX 4070/5070（12GB）+ 64GB 記憶體的機器上，可把 125B MoE 推到 50~90+ token/s。

## Strata 的局限

1. 模型支援較單一，主要針對特定大型稀疏 MoE 調校，不像 Ollama 能隨意拉小模型。
2. 對系統記憶體與 CPU 有硬門檻，通常要 32~64GB RAM 與支援 AVX2/AVX-512 的現代多核 CPU。
3. 低 bit 量化（如 IQ2_XS、Q4）會讓複雜推理能力一定程度劣化。

## 選擇建議

- 12~16GB 顯卡 + 64GB 記憶體、想離線跑大型 MoE coding 模型：選 Strata。
- Mac、辦公筆電、想零配置跑 7B~32B：選 Ollama。
- 企業後台、私有雲 API、上百人併發：選 vLLM。
- 多輪工作流、多 Agent、需要前綴快取：選 SGLang。
