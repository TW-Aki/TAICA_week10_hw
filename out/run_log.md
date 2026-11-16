=== LLM Wiki 執行紀錄 ===
時間：2026-11-17T00:16:45

[node:ingest] 讀取來源文件
  共 ingest 7 篇：01_strata_overview, 02_install_guide, 03_model_and_memory, 04_api_connect, 05_compare_tools, 06_teaching_outline, 07_why_local

[node:chunk] 切塊
  產生 44 個 chunk -> wiki/chunks/、wiki/manifest.csv

[node:index] 建立索引
  索引 44 個 chunk

[node:draft] 主題：Strata 是什麼
  檢索命中：01_strata_overview_001(27.385), 01_strata_overview_002(24.876), 02_install_guide_002(23.347), 04_api_connect_004(14.683)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：安裝與第一次啟動
  檢索命中：02_install_guide_002(46.543), 01_strata_overview_006(43.684), 01_strata_overview_001(25.029), 02_install_guide_003(18.614)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：模型與記憶體選擇
  檢索命中：03_model_and_memory_002(41.839), 03_model_and_memory_003(35.182), 05_compare_tools_006(30.604), 03_model_and_memory_004(28.17)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：API 與外部工具串接
  檢索命中：04_api_connect_003(31.755), 01_strata_overview_002(24.937), 04_api_connect_005(18.893), 07_why_local_006(18.866)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：與其他工具的比較
  檢索命中：05_compare_tools_007(20.314), 03_model_and_memory_002(7.072), 04_api_connect_005(5.405), 02_install_guide_006(2.608)
[node:check] 第 1 輪
  PASS -> 接受條目

[node:draft] 主題：常見問題與效能瓶頸
  檢索命中：03_model_and_memory_002(42.605), 03_model_and_memory_004(32.247), 05_compare_tools_006(24.279), 03_model_and_memory_003(23.073)
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
