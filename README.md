# 第十週作業：用 LLM Wiki 做教學 HTML 簡報

主題：**如何用 Strata 部署本地模型**

Strata 是類似 Ollama 的本地模型運行工具，主打在消費級硬體上跑大型 MoE 模型。

---

## 資料夾結構

```
week10_hw/
├── submission.md                # 六項繳交內容（可直接貼到 NTU COOL）
├── design_notes.md              # loop / graph / 檢查流程設計說明
├── sources/                     # 至少 5 篇原始資料（目前 6 篇）
│   ├── 01_strata_overview.md    # 官方 README 摘要
│   ├── 02_install_guide.md      # 安裝與第一次啟動
│   ├── 03_model_and_memory.md   # 模型與記憶體 / 量化選擇
│   ├── 04_api_connect.md        # API 與外部工具串接
│   ├── 05_compare_tools.md      # 與 Ollama/vLLM/SGLang 比較
│   └── 06_teaching_outline.md   # 自行整理的教學大綱
├── llm_wiki.py                  # Wiki pipeline（graph + loop）
├── build_slides.py              # 由 Wiki 產生 HTML 簡報
├── wiki/
│   ├── chunks/                  # 36 個切好的 txt（含 metadata）
│   ├── manifest.csv
│   ├── entries/                 # 6 個 Wiki 條目（markdown）
│   └── entries.json
└── out/
    ├── run_log.md               # 執行紀錄（可看到 check FAIL → regenerate → PASS）
    ├── reflection.md            # 反思
    └── strata_deployment_teaching.html   # 最終教學簡報（單檔，14 頁）
```

---

## 怎麼重跑

```bash
cd week10_hw

# 1. 建立 / 更新 Wiki（ingest → chunk → index → draft → check → regenerate → reflect）
python llm_wiki.py all

# 2. 由 Wiki 產生 HTML 簡報
python build_slides.py

# 3. 其他用法
python llm_wiki.py graph       # 印出 graph 節點與邊
python llm_wiki.py ask "怎麼選模型"
```

完成後直接用瀏覽器開 `out/strata_deployment_teaching.html`，可用 ← → 或空白鍵翻頁。

---

## 有 API key 時可切換成真的 LLM

`llm_wiki.py` 的 `call_llm()` 會優先讀環境變數：

```bash
set GROQ_API_KEY=你的key
set LLM_MODEL=llama-3.3-70b-versatile
python llm_wiki.py all
```

沒有 API key 時會自動退回本地模板產生器，仍可完整示範 graph 與 loop，只是文字是從原文抽取、可讀性較低。

---

## 對應作業評分標準

| 要求 | 本專案做法 |
|---|---|
| 建立自己的 LLM Wiki，至少 ingest 5 篇 | `sources/` 共 6 篇，`llm_wiki.py` 會檢查不得少於 5 篇 |
| 用 Wiki 製作教學型 HTML 簡報 | `build_slides.py` 讀 `wiki/entries.json` 與 `out/run_log.md` 產生 14 頁單檔 HTML |
| 說明 loop / graph 設計 | `design_notes.md`、簡報第 11 頁 SVG 流程圖 |
| 重複節點 | `check ↔ regenerate` 形成迴圈，最多 3 輪 |
| 檢查與重新生成 | `check_entry()` 驗證 5 個欄位；失敗時呼叫 `regenerate` 後回到 `check` |
| 反思 | `out/reflection.md` 與簡報第 13 頁 |

---

## 資料來源

1. Strata 官方 GitHub：<https://github.com/Niko1221/Strata>
2. 技術評論（知乎）：<https://zhuanlan.zhihu.com/p/2101327443474883150>
3. 其餘檔案為由上述來源整理的本機文件，每篇開頭都有「標題 / 來源網址 / 教材整理日期 / 資料類型」metadata。
