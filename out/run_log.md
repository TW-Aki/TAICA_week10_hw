=== LLM Wiki 執行紀錄 ===
時間：2026-11-16T23:29:22

[node:ingest] 讀取來源文件
  共 ingest 6 篇：01_strata_overview, 02_install_guide, 03_model_and_memory, 04_api_connect, 05_compare_tools, 06_teaching_outline

[node:chunk] 切塊
  產生 36 個 chunk -> wiki/chunks/、wiki/manifest.csv

[node:index] 建立索引
  索引 36 個 chunk

[node:draft] 主題：Strata 是什麼
  檢索命中：01_strata_overview_001(27.165), 01_strata_overview_002(24.6), 02_install_guide_002(23.27), 04_api_connect_004(15.137)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：安裝與第一次啟動
  檢索命中：02_install_guide_002(43.756), 01_strata_overview_006(40.223), 01_strata_overview_001(22.93), 02_install_guide_003(17.377)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：模型與記憶體選擇
  檢索命中：03_model_and_memory_002(37.428), 03_model_and_memory_003(31.625), 03_model_and_memory_004(25.509), 05_compare_tools_007(22.835)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：API 與外部工具串接
  檢索命中：04_api_connect_003(29.469), 01_strata_overview_002(23.713), 04_api_connect_005(17.399), 01_strata_overview_004(14.572)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：與其他工具的比較
  檢索命中：05_compare_tools_005(22.715), 05_compare_tools_002(18.201), 05_compare_tools_001(13.249), 05_compare_tools_003(7.164)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：常見問題與效能瓶頸
  檢索命中：03_model_and_memory_002(37.75), 03_model_and_memory_004(28.06), 05_compare_tools_007(25.514), 05_compare_tools_006(24.263)
[node:check] 第 1 輪
  FAIL -> 缺少：「sources, related」
[node:regenerate] 補齊 sources, related 後回到 check
[node:check] 第 2 輪
  PASS -> 接受條目

[node:reflect] 反思
  -> out/reflection.md

[node:export] 完成
  wiki/entries/ (6 個條目)
  wiki/entries.json
  out/run_log.md、out/reflection.md
