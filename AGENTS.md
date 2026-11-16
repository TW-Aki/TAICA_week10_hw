# AGENTS.md

這份文件提供給 AI 程式代理（Antigravity / Claude Code / Codex CLI 等）操作本 repo 時遵循。任何修改都應先讀過這份文件。

## 專案概覽

- 第十週作業：用 LLM Wiki 做一份教學 HTML 簡報
- 主題：如何用 Strata 部署本地模型
- 狀態：已完成並交付，repo 位於 https://github.com/TW-Aki/TAICA_week10_hw
- 語言：全程使用繁體中文，不可出現簡體字

## 目錄結構

| 路徑 | 角色 | 是否可直接編輯 |
|---|---|---|
| `sources/*.md` | 7 篇原始資料（唯一資料來源） | ✅ 可 |
| `llm_wiki.py` | Wiki pipeline：ingest → chunk → index → draft → check → regenerate → reflect | ✅ 可 |
| `build_slides.py` | 讀 Wiki 成果產生 17 頁單檔 HTML | ✅ 可 |
| `README.md` / `design_notes.md` / `submission.md` / `AGENTS.md` | 文件與繳交內容 | ✅ 可 |
| `wiki/chunks/` | 44 個切塊 txt | ❌ 生成檔，勿手改 |
| `wiki/entries/`、`wiki/entries.json` | 6 個 Wiki 條目 | ❌ 生成檔，勿手改 |
| `wiki/manifest.csv` | chunk 清單 | ❌ 生成檔，勿手改 |
| `out/run_log.md`、`out/reflection.md` | 執行紀錄與反思 | ❌ 生成檔，勿手改 |
| `out/strata_deployment_teaching.html` | 最終簡報 | ❌ 生成檔，勿手改 |

## 黃金流程（修改時務必遵守）

1. 只編輯 `sources/*.md` 與兩支 `*.py`。
2. 重新執行：`python llm_wiki.py all`
3. 重新產生簡報：`python build_slides.py`
4. 檢查 `out/run_log.md` 是否仍有 FAIL → regenerate → PASS 紀錄，以及 HTML 是否仍是 17 頁。
5. 絕對不要手動修改 `wiki/` 與 `out/` 底下的生成檔，下次執行會被覆蓋。

## 關鍵設計（不要輕易改動）

- `TOPICS` 六個主題是繳交要求的骨幹，增刪要同步改 `submission.md` 與簡報。
- `TOPIC_QUERIES` 為每個主題指定檢索詞，避免全部命中 `06_teaching_outline`。
- `check_entry()` 驗證五個欄位：`title`、`definition`（≥20 字）、`bullets`（≥3）、`sources`（含 http 網址）、`related`（≥1）。
- `MAX_ROUNDS = 3` 防止無限迴圈；失敗達上限會標為 `accepted_with_risk`。
- `regenerate` 只補 `missing` 帶回的欄位，不重寫整段。
- `06_teaching_outline` 被排除在 context 之外，避免定義變成簡報大綱。
- `call_llm()` 優先讀 `GROQ_API_KEY` / `OPENAI_API_KEY`，沒有則退回本地模板，保證離線可跑。

## 常見任務

| 任務 | 步驟 |
|---|---|
| 換主題或加資料 | 改 `sources/`，必要的話改 `TOPICS`、`TOPIC_QUERIES`，再跑黃金流程 |
| 調整簡報文字或版面 | 改 `build_slides.py`，再跑 `python build_slides.py` |
| 修正反思內容 | 改 `llm_wiki.py` 的 `reflect()`，再跑黃金流程 |
| 換成真實 LLM | 設定 `GROQ_API_KEY`、`LLM_MODEL` 環境變數後重跑 |
| 更新繳交說明 | 改 `submission.md`，commit 後 push |

## 驗證

```bash
python llm_wiki.py graph       # 印出 graph 節點與邊
python llm_wiki.py ask "怎麼選模型"
python -c "import zhconv"      # 僅檢查用，非執行依賴
```

基本檢查：來源 7 篇、chunk 44 個、Wiki 條目 6 個、簡報 17 頁、run_log 含 FAIL → PASS 紀錄、無簡體字殘留。

## Git

- remote：`origin` → `https://github.com/TW-Aki/TAICA_week10_hw.git`
- 分支：`main`
- 提交後執行：`git push origin HEAD:main`
- 提交訊息請用英文簡述，例如 `Update slide reflection section`。
