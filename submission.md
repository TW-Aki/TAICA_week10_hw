# 第十週作業繳交

CYCU 11114224 應外三乙 曾德欣

---

## 1. LLM Wiki 主題與簡短介紹

**如何用 Strata 部署本地模型**

Strata 是類似 Ollama 的本地模型執行工具，但定位不同：Ollama 是通用型模型管理器，Strata 專為「顯存放不下的 MoE 模型」設計，讓 12–24G 顯卡的消費級電腦也能跑 100B 級別的大型模型。它在自己的電腦上跑推論，並提供 OpenAI／Anthropic 相容 API，可掛給 Claude Code、Codex CLI 等工具當後端。

做法：先把 7 篇資料（官方 README、工作原理、模型指南、社群實測、安裝指南、教學大綱、為什麼要本地部署）放進 `sources/`，用 `llm_wiki.py` 切成 44 個區塊並建立索引，針對六個主題生成 Wiki 條目，最後由 `build_slides.py` 產出一份 24 頁的教學 HTML 簡報。

---

## 2. GitHub 連結

https://github.com/TW-Aki/TAICA_week10_hw

---

## 3. HTML 簡報連結

- 檔案：`TAICA_week10_hw/out/strata_deployment_teaching.html`
- 線上直接看（會渲染成簡報，不會顯示原始碼）：
  https://htmlpreview.github.io/?https://github.com/TW-Aki/TAICA_week10_hw/blob/main/out/strata_deployment_teaching.html
- GitHub 上的檔案：
  https://github.com/TW-Aki/TAICA_week10_hw/blob/main/out/strata_deployment_teaching.html

> 註：GitHub 對 `.html` 檔預設顯示原始碼，所以另附 htmlpreview 連結，點開就是可以翻頁的簡報（← → 或空白鍵）。

---

## 4. loop / graph 的流程圖或文字說明

ingest（讀 7 篇，檢查至少 5 篇）→ chunk（切 44 塊）→ index（bigram + TF-IDF）→ draft（檢索後生成條目）→ check（驗證 title／definition／bullets／sources／related）→ FAIL 則 regenerate 回到 check（最多 3 輪）→ PASS 後 reflect → export 產生 HTML。

關鍵是 **check 與 regenerate 構成可重複的迴圈**：`check` 是重複節點，`regenerate` 只補 `missing` 帶回的欄位，不重寫整段；`MAX_ROUNDS = 3` 防止無限迴圈。流程圖畫在簡報第 21 頁，實際執行紀錄在第 22 頁。

---

## 5. 一次實際執行的結果或檢查紀錄

**個人複查**：修正簡體（全專案掃描，殘留 0）、確認資料可靠性（來源全部換成官方文件、實測 22–26 tok/s 與官方數字交叉比對）、確認簡報正常發佈（GitHub main 與 gh-pages 均已推送，htmlpreview 實際開啟確認可翻頁）。

**AI 執行節錄**（`out/run_log.md`）：

```
[node:draft] 主題：常見問題與效能瓶頸
[node:check] 第 1 輪
  FAIL -> 缺少：「sources, related」
[node:regenerate] 補齊 sources, related 後回到 check
[node:check] 第 2 輪
  PASS -> 接受條目
```

統計：7 篇來源 → 44 個 chunk → 6 個條目 → 累計 7 輪檢查 → 6 個條目全數通過（其中 1 個走了 2 輪）。

另外我實際在自己電腦（RTX 5070 Ti 16GB + 32GB RAM）部署了 Qwen3.6-35B-A3B，用 `speedtest.py` 量到 22–26 tok/s，完整紀錄在 `out/操作紀錄.md`。

---

## 6. 反思

**我的反思：資料來源最容易出錯。** 可能是過時（部落格寫的是 0.1.x 版，官方早已 0.2.15），也可能不夠權威（媒體說「比 llama.cpp 快 6 倍」，社群實測只有約 2 倍）。這些錯誤 validator 抓不到，只能靠實際操作去驗證資料的可靠性——我跑出 22–26 tok/s 與官方 48.2 對不上，追查後才發現是模型不同（35B vs 125B）與專家分配（65/256 在顯卡）造成，而不是數據造假。

**AI 補充的技術反思**：程式層面最常出錯的是 draft 輸出被 check 攔下，分兩類——definition 太短（低於 20 字，曾連續三輪 FAIL）、sources／related 缺欄位。調整方式：把 definition 下限寫進 validator 並挑最長句子；sources／related 改為必要欄位、missing 只回補缺失鍵；把教學大綱從 context 排除；為六主題各寫檢索詞；設 `MAX_ROUNDS = 3`。

完整版在 `submission.md` 與 `out/reflection.md`。

---

## 附錄：檔案對照

| 項目 | 檔案 |
|---|---|
| Wiki 來源（7 篇） | `sources/*.md` |
| 切塊（44 個）與清單 | `wiki/chunks/`、`wiki/manifest.csv` |
| Wiki 條目（6 個） | `wiki/entries/`、`wiki/entries.json` |
| 建立腳本 | `llm_wiki.py` |
| 簡報產生器 | `build_slides.py` |
| 測速程式 | `speedtest.py` |
| 執行紀錄 / 反思 | `out/run_log.md`、`out/reflection.md` |
| 實際部署紀錄 | `out/操作紀錄.md`、`out/shots/` |
| 最終簡報（24 頁） | `out/strata_deployment_teaching.html` |
