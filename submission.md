# 第十週作業繳交：LLM Wiki 教學 HTML 簡報

以下六項可直接複製到 NTU COOL 的線上輸入欄。

---

## 一、LLM Wiki 主題與簡短介紹

**主題：如何用 Strata 部署本地模型**

Strata 是類似 Ollama 的本地模型運行工具，主打在消費級硬體（12–24G 顯卡 + 32–64G 記憶體）上跑大型 MoE 模型，並在本機提供 OpenAI／Anthropic 相容 API。它開源、免帳號，可掛給 Claude Code、Codex CLI 等工具當後端。

我做的事情是：先將 7 篇資料（官方 README 拆分 4 篇、官方工作原理與效能實測 1 篇、自行整理的教學大綱 1 篇，以及新增的「為什麼要本地部署」1 篇）放進 `sources/`，建立自己的 LLM Wiki，再用這個 Wiki 產出一份 23 頁的教學型 HTML 簡報，內容涵蓋本地部署動機（含資料風險舉例與 API 定價）、硬體選型、量化選擇、安裝啟動、API 串接與限制取捨。來源均為官方文件與官方定價頁，並附上官方示意圖與社群實測數據。

---

## 二、LLM Wiki 連結或成果

- **本機成果**：`week10_hw/wiki/`
- **GitHub**：https://github.com/TW-Aki/TAICA_week10_hw

| 成果 | 內容 | 檔案 |
|---|---|---|
| 來源文件 | 7 篇（附標題／來源網址／日期／資料類型） | `sources/01`～`07_*.md` |
| 切塊 | 44 個 txt，每檔含 metadata 與 `【內容】` | `wiki/chunks/*.txt` |
| 清單 | chunk 與來源對照 | `wiki/manifest.csv` |
| Wiki 條目 | 6 個條目，每個有定義、重點、來源、關聯 | `wiki/entries/*.md` |
| 結構化資料 | 供簡報產生器讀取 | `wiki/entries.json` |
| 建立腳本 | ingest → chunk → index → draft → check → regenerate → reflect | `llm_wiki.py` |

---

## 三、教學 HTML 簡報連結

- **線上直接開（推薦）**：https://htmlpreview.github.io/?https://github.com/TW-Aki/TAICA_week10_hw/blob/main/out/strata_deployment_teaching.html
- **檔案**：`week10_hw/out/strata_deployment_teaching.html`
- **開啟方式**：點上面連結直接在瀏覽器渲染；或下載檔案用瀏覽器開啟（單檔，不依賴外部 CDN）
- **操作**：← → 或空白鍵翻頁
- **頁數**：23 頁

> 註：GitHub 對 `.html` 檔預設顯示原始碼，直接用 repo 裡的檔案連結會看到程式碼；上面的 htmlpreview 連結才會渲染成簡報。

章節：章節：封面 → **目錄（五段結構）** → 為什麼本地部署（隱私）→ API token 成本 → Strata 是什麼 → **為什麼用 Strata（低硬體跑大模型）** → 官方原理圖 → **Ollama/Strata 逐項對比** → 三種情境怎麼選 → 硬體與量化 → 三條安裝路線 → 第一次啟動 → **我的實際部署（含截圖）** → API 串接 → 官方社群實測 → 我的實測 → 與官方數字對照 → 限制 → Wiki 如何產生簡報 → Graph 設計圖 → Loop 執行紀錄 → 反思 → 總結。

---

## 四、loop / graph 的流程圖或文字說明

```mermaid
flowchart LR
    A[ingest 7 篇] --> B[chunk 44 塊]
    B --> C[index 檢索]
    C --> D[draft 草稿]
    D --> E{check 檢查}
    E -- FAIL --> F[regenerate 重生成]
    F --> E
    E -- PASS --> G[reflect 反思]
    G --> H[export HTML 簡報]
```

| 節點 | 職責 |
|---|---|
| `ingest` | 讀 7 篇來源，檢查是否至少 5 篇 |
| `chunk` | 依標題切小節，再切 700 字區塊 |
| `index` | 字元 bigram + TF-IDF Lite |
| `draft` | 檢索 context 後請 LLM 產生結構化條目 |
| `check` | 驗證 5 個欄位（title／definition／bullets／sources／related） |
| `regenerate` | 只補缺失欄位後回到 check（重複節點） |
| `reflect` | 統計輪數與通過率，寫出錯誤節點與調整 |
| `export` | 輸出條目並交給 `build_slides.py` 產生 HTML |

關鍵設計：**check 與 regenerate 構成可重複的迴圈**，最多 3 輪；通過後才進入反思與輸出。流程圖也畫在簡報第 11 頁。

---

## 五、一次實際執行的結果或檢查紀錄

節錄 `out/run_log.md`（完整檔在專案內）：

```
[node:ingest] 讀取來源文件
  共 ingest 7 篇：01_strata_overview, 02_install_guide,
  03_model_and_memory, 04_api_connect, 05_compare_tools, 06_teaching_outline

[node:chunk] 切塊
  產生 44 個 chunk -> wiki/chunks/、wiki/manifest.csv

[node:index] 建立索引
  索引 44 個 chunk

[node:draft] 主題：常見問題與效能瓶頸
  檢索命中：03_model_and_memory_002(37.75),
            03_model_and_memory_004(28.06),
            05_compare_tools_007(25.514), ...
[node:check] 第 1 輪
  FAIL -> 缺少：「sources, related」
[node:regenerate] 補齊 sources, related 後回到 check
[node:check] 第 2 輪
  PASS -> 接受條目

[node:reflect] 反思
  -> out/reflection.md

[node:export] 完成
  wiki/entries/ (6 個條目)
```

統計：7 篇來源 → 44 個 chunk → 6 個條目 → 累計 7 輪檢查 → 6 個條目全數通過（其中 1 個走了 2 輪）。

---

## 六、反思：哪個節點最常出錯？你如何調整檢查流程？

**最常出錯的節點**：不是 ingest、chunk 或 index，而是 **draft 的輸出被 check 攔下來**。失敗集中在兩類：

1. `definition` 太短——草稿直接抽到一句短結論（例如「適合：不想碰終端機、只想試試看的人。」），不到 20 字，一度連續三輪 FAIL。
2. `sources`／`related` 缺欄位——草稿只寫重點，忘了帶來源網址與關聯條目，Wiki 會變成孤立頁面。

**我怎麼調整檢查流程**：

1. 把 definition 下限（≥20 字）明確寫進 validator，並要求 regenerate 時改挑最長的句子；仍不夠長就把主題名接在前面。
2. 把 `sources` 與 `related` 從「有就好」改成必要欄位，且 `missing` 只帶回要補的鍵，不做整段重寫——保留原本正確的內容，也節省時間。
3. 把 `06_teaching_outline` 從 context 排除：它幾乎全是標題條列，會讓 definition 變成「1. 封面：…」這種大綱，而不是定義句。
4. 為六個主題各寫一組檢索詞（`TOPIC_QUERIES`），避免所有主題都命中同一篇大綱。
5. 設 `MAX_ROUNDS = 3` 防止無限迴圈；若三輪仍失敗，標為 `accepted_with_risk` 並在反思中記錄，而不是悄悄丟掉。

**收穫**：與其相信 LLM 一次就寫對，不如把「檢查—修正」做成 graph 裡會重複執行的節點。完整反思見 `out/reflection.md`，簡報第 13 頁也有對應說明。
