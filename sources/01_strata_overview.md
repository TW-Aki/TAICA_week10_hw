標題：Strata 是什麼：本地 AI 推理引擎與桌面/終端應用
來源網址：https://github.com/Niko1221/Strata
教材整理日期：2026-11-16
資料類型：官方文件

# Strata 是什麼

Strata 是一個開源、完全在本機運行的 AI 推理引擎，同時提供桌面 App 與終端機 App。它的口號是「Run powerful AI on your own computer.」，強調不需要帳號、不用雲端、MIT 授權。

## 核心功能

- 本機聊天、寫程式、處理圖片輸入（Chat, code and work with images, locally）
- 使用自家的 Strata inference engine
- 在本機 `localhost` 提供 OpenAI 相容與 Anthropic 相容的 HTTP API
- 可掛給 Claude Code、Codex CLI、OpenCode、oh-my-pi、pi.dev、Hermes Agent、OpenClaw 等外部工具當作後端
- 開源、免費、不需註冊帳號

## 主要模型

README 列出的主打模型是 `Qwen3.8-Flash-Next`，推薦 provider 為 `ISTA-DASLab`，量化選項包含：

- `Q2_0`
- `IQ2_XS`
- `IQ3_XXS`
- `IQ3_S`

程式碼情境另外推薦 `Coder: IQ1_M`。其他 provider 還有 Unsloth、Gyro（agentionai）、Swift 1.5、NVFP4、OrcaRouter。

另一個收錄模型是 `Qwen3.6-35B-A3B`，已記錄的 packs 有 `UD-Q4_K_XL`、`UD-Q6_K_XL`、`Q8_0`。

## 快速開始

```bash
strata launch
```

執行後依照提示下載並啟動模型即可。`strata connect` 則用來查看怎麼把 Strata 接到外部工具。

## 支援平台

作業系統：Windows、Linux、macOS（arm64）。

GPU 硬體清單：

- NVIDIA GeForce RTX 20 / 30 / 40 / 50 系列
- AMD Radeon RX 7700 / 7800 / 7900
- AMD Radeon RX 9060 / 9070
- AMD AI PRO R9700
- AMD Radeon RX 6800 / 6900（experimental）
- Intel Arc（Linux）
- Apple Silicon M1 以上
- AMD Ryzen AI Max（Strix Halo）
- NVIDIA DGX Spark（Linux）

## 安裝入口

桌面 App：從 GitHub Releases 下載對應平台的安裝檔（例如 `Strata-0.2.15-windows-x64-setup.exe`、`Strata-0.2.15-linux-x86_64.AppImage`、`Strata-0.2.15-macos-arm64.dmg`）。

終端機版：

Linux / macOS：

```bash
curl -fsSL --connect-timeout 15 --max-time 120 https://github.com/Niko1221/Strata/releases/latest/download/install.sh -o install.sh && sh install.sh
```

Windows PowerShell：

```powershell
irm -TimeoutSec 120 https://github.com/Niko1221/Strata/releases/latest/download/install.ps1 | iex
```

安裝完開啟新的終端機，再執行 `strata launch`。

## 倉庫內的檔案線索

README 與檔案列表出現 `docs/MODELS.md#pick-by-memory`、`docs/AI_SETUP.md`、`README.zh-CN.md`、`AGENTS.md`、`CONTRIBUTING.md`、`SECURITY.md`，以及 `Dockerfile`、`CMakeLists.txt`、`setup.py`、`strata.py` 等。Windows 另有 `SETUP.bat`、`START-HERE.bat`、`UPDATE.bat`、`BENCH.bat`。
