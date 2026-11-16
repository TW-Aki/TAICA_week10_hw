=== LLM Wiki 執行紀錄 ===
時間：2026-11-16T23:45:58

[node:ingest] 讀取來源文件
  共 ingest 6 篇：01_strata_overview, 02_install_guide, 03_model_and_memory, 04_api_connect, 05_compare_tools, 06_teaching_outline

[node:chunk] 切塊
  產生 35 個 chunk -> wiki/chunks/、wiki/manifest.csv

[node:index] 建立索引
  索引 35 個 chunk

[node:draft] 主題：Strata 是什麼
  檢索命中：01_strata_overview_001(25.966), 01_strata_overview_002(24.247), 02_install_guide_002(22.067), 04_api_connect_004(15.056)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：安裝與第一次啟動
  檢索命中：02_install_guide_002(43.208), 01_strata_overview_006(40.753), 01_strata_overview_001(23.522), 02_install_guide_003(17.438)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：模型與記憶體選擇
  檢索命中：03_model_and_memory_002(39.868), 03_model_and_memory_003(33.871), 05_compare_tools_006(29.162), 03_model_and_memory_004(27.028)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：API 與外部工具串接
  檢索命中：04_api_connect_003(29.946), 01_strata_overview_002(23.854), 04_api_connect_005(17.784), 01_strata_overview_004(14.831)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：與其他工具的比較
  檢索命中：05_compare_tools_007(18.939), 03_model_and_memory_002(6.443), 04_api_connect_005(5.108), 02_install_guide_006(2.687)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：常見問題與效能瓶頸
  檢索命中：03_model_and_memory_002(40.762), 03_model_and_memory_004(30.454), 05_compare_tools_006(23.14), 03_model_and_memory_003(22.34)
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
