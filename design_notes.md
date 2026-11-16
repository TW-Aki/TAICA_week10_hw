# 設計說明：Loop / Graph、重複節點、檢查與重新生成、反思

這份文件是第十週作業要求的核心說明，可直接貼到作業繳交欄或 Colab。

---

## 一、整體 Graph 設計

我把 Wiki 建置看成一個有向圖（directed graph），而不是一條單純的直線管線：

```
ingest → chunk → index → draft → check
                            ↑        │
                            │        ├─ FAIL → regenerate ─┐
                            │        │                    │
                            └────────┴──── PASS ─→ reflect → export
                                        （重複節點）
```

| 節點 | 做什麼 | 輸出 |
|---|---|---|
| `ingest` | 讀 `sources/*.md`，解析標題、來源網址、日期、資料類型；檢查至少 5 篇，不足即停止 | `Doc` 物件 |
| `chunk` | 依 Markdown 標題切小節，再依 700 字切段 | `wiki/chunks/*.txt`、`manifest.csv`（44 塊） |
| `index` | 字元 unigram + bigram + TF-IDF Lite | 可檢索的索引 |
| `draft` | 用檢索到的 chunk 當 context，請 LLM 產生結構化 Wiki 條目 | 6 個條目草稿 |
| `check` | 驗證 5 個欄位是否符合格式 | PASS / FAIL + 缺失欄位 |
| `regenerate` | 把缺失欄位帶回 prompt，重新生成 | 新草稿 |
| `reflect` | 統計通過率、輪數，寫下學到什麼、限制、改進 | `out/reflection.md` |
| `export` | 輸出條目與 HTML 簡報 | `wiki/entries/`、`out/*.html` |

---

## 二、Loop 設計與重複節點

關鍵在於 **check 與 regenerate 構成一個可以重複進入的迴圈**：

```python
for round_no in range(1, MAX_ROUNDS + 1):
    raw = call_llm(prompt_with(missing))
    entry = parse(raw)
    issues = check_entry(entry)          # ← 重複節點：check

    if issues and round_no < MAX_ROUNDS:
        missing = issues
        continue                         # ← regenerate 後再回到 check

    entry.status = "accepted" if not issues else "accepted_with_risk"
    break
```

- `MAX_ROUNDS = 3`：避免無限迴圈。
- 每輪都把上一輪的 `missing` 欄位放進 prompt，這就是「檢查與重新生成」的具體實作。
- 若三輪都沒通過，不會無條件丟掉，而是標成 `accepted_with_risk` 並在反思裡記錄風險。

實際執行結果（節錄 `out/run_log.md`）：

```
[node:draft] 主題：常見問題與效能瓶頸
[node:check] 第 1 輪
  FAIL -> 缺少：「sources, related」
[node:regenerate] 補齊 sources, related 後回到 check
[node:check] 第 2 輪
  PASS -> 接受條目
```

這個例子就是「重複節點」的證據：check 被執行了兩次，中間插入一次 regenerate。

---

## 三、檢查（validator）檢查什麼

`check_entry()` 檢查五件事：

1. `title` 非空白
2. `definition` 至少 20 字（避免只丟一句「某工具的說明」）
3. `bullets` 至少 3 點
4. `sources` 至少一個 `http` 開頭的網址（可追溯來源）
5. `related` 至少 1 個關聯條目（讓 Wiki 形成網絡，而不是孤立頁面）

檢查不看主觀品質，只看「格式是否可被下游簡報使用」，這樣才不會陷入 LLM 自己評自己、永遠通過的陷阱。

---

## 四、重新生成策略

不是把整個 prompt 重送一次而已，而是做**差異修補**：

- 第一輪缺失 `sources`、`related` → 第二輪的 prompt 明確帶 `missing: ["sources", "related"]`。
- 本地模板收到 `missing` 後，只補那兩個欄位，其他重點保留。
- 如果有真實 LLM API，同一個 prompt 也能直接作用，不需要改程式。

這樣設計的好處是：成本和時間都花在真正有問題的地方，而不是每次都全部重寫。

---

## 五、反思（reflect 節點）

反思不是手寫在簡報最後，而是由程式統計後產生 `out/reflection.md`：

- 算出 Wiki 條目數、完全通過檢查的數量、累計檢查輪數、來源文件數。
- 寫下三層反思：
  1. **最常出錯**：不是程式節點，而是 `ingest` 的資料本身——過時、不夠權威、與實機不符。
  2. **怎麼調整**：來源分級、補 metadata、交叉驗證、實際操作驗證（`speedtest.py`）、把驗證結果寫回 Wiki。
  3. **限制**：validator 只驗格式不驗真假；抽取式文字可讀性有限；bigram 對同義詞不敏感。

反思的核心結論是「**程式錯 validator 抓得到，資料錯只有實跑才知道**」，簡報第 22 頁呈現同一個觀點，形成「做過 → 檢查 → 修正 → 回頭看」的證據鏈。

---

## 六、為什麼這樣設計能呼應作業要求

| 作業要求 | 設計上的對應 |
|---|---|
| 至少 ingest 5 篇 | `ingest` 節點明確檢查篇數，不足直接報錯 |
| 用 Wiki 製作 HTML | `export` 節點把條目寫成 json/md，`build_slides.py` 讀它產生 24 頁簡報 |
| loop / graph | `GRAPH` 常數定義節點與邊；簡報第 11 頁畫成 SVG |
| 重複節點 | `check`、`regenerate` 在 for 迴圈裡重複執行 |
| 檢查與重新生成 | validator + `missing` 差異修補 prompt |
| 反思 | `reflect` 節點統計並寫檔，簡報第 13 頁呈現 |

---

## 七、對應繳交項目

| 繳交要求 | 對照檔案 |
|---|---|
| LLM Wiki 主題與簡短介紹 | `submission.md` 第一節 |
| LLM Wiki 連結或成果 | `submission.md` 第二節、`wiki/` 整個資料夾 |
| 教學 HTML 簡報連結 | `submission.md` 第三節、`out/strata_deployment_teaching.html` |
| loop / graph 流程圖或文字說明 | `submission.md` 第四節、簡報第 11 頁、本文件第一／二節 |
| 實際執行結果或檢查紀錄 | `submission.md` 第五節、`out/run_log.md` |
| 反思：最常出錯節點與檢查流程調整 | `submission.md` 第六節、`out/reflection.md`、本文件第八節 |

---

## 八、可直接貼的「簡短說明」

> 我的 Agent 式 Wiki pipeline 把流程畫成一個 graph：先 ingest 7 篇本地文件、切成 44 個 chunk、建立 bigram + TF-IDF 索引，再針對六個主題檢索並請 LLM 產生 Wiki 條目草稿。關鍵設計是 check 與 regenerate 形成一個可重複的迴圈：驗證器檢查標題、定義、重點、來源網址與關聯條目五個欄位，若失敗就把缺失欄位帶回 prompt 重新生成，最多三輪；實際執行中「常見問題」條目在第一輪缺少來源與關聯，經 regenerate 後第二輪通過，這個紀錄被存到 run_log.md。最後 reflect 節點統計通過率與輪數，寫出限制與改進，並把 Wiki 條目與執行紀錄一起交給 build_slides.py，產生 24 頁的單檔教學 HTML 簡報。
