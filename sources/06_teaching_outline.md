標題：教學簡報大綱：如何用 Strata 部署本地模型
來源網址：本機整理（由 01~05 來源文件綜合）
教材整理日期：2026-11-16
資料類型：自行整理

# 教學簡報大綱

這份大綱是 LLM Wiki 要產出的教學型 HTML 簡報的骨架，對象是「聽過 Ollama、但還沒自己部署過本地模型」的學生。

## 學習目標

1. 說出 Strata 與 Ollama 的定位差異。
2. 依照自己的硬體選出合適的模型與量化 pack。
3. 完成安裝、啟動、第一次對話。
4. 把 Strata 接到外部工具（OpenAI / Anthropic 相容 API）。
5. 理解本地部署的取捨：隱私、成本、速度、品質。

## 簡報章節

1. 封面：如何用 Strata 部署本地模型
2. 為什麼要本地部署：隱私、成本、離線
3. Strata 是什麼：定位與功能
4. 與 Ollama / vLLM / SGLang 的比較
5. 硬體與量化：怎麼挑模型
6. 安裝三步：下載 → 安裝 → strata launch
7. 第一次對話與模型下載
8. 串接外部工具：strata connect
9. 常見問題與效能瓶頸
10. LLM Wiki 怎麼做出這份簡報
11. Loop / Graph 設計圖
12. 重複節點、檢查與重新生成
13. 反思：限制與改進
14. 總結

## 評分標準對應

- 至少 ingest 5 篇資料：本專案準備 6 篇（01~06）。
- 用 Wiki 製作教學型 HTML：wiki/ 目錄提供條目，build_slides.py 據此產生 HTML。
- 說明 loop / graph 設計：design_notes.md 與簡報第 11 頁。
- 重複節點：check ↔ regenerate 形成迴圈。
- 檢查與重新生成：llm_wiki.py 的 validator 與 regenerate 節點。
- 反思：簡報第 13 頁與 design_notes.md。
