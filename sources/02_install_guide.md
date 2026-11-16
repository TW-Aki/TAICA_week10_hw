標題：Strata 安裝與第一次啟動教學
來源網址：https://github.com/Niko1221/Strata#installation
教材整理日期：2026-11-16
資料類型：官方文件

# 安裝與第一次啟動

本文件整理 Strata 的三種安裝路線，以及第一次啟動時該做的事。

## 路線 A：桌面 App（最簡單）

1. 到 GitHub Releases 頁面下載安裝檔。
2. Windows 用 `Strata-0.2.15-windows-x64-setup.exe`，Linux 用 `.AppImage`，macOS 用 `.dmg`（arm64）。
3. 安裝後開啟 App，可直接聊天。
4. README 說明：首次啟動時，App 會根據你的顯卡自動下載對應的推理引擎。

適合：不想碰終端機、只想試試看的人。

## 路線 B：終端機 App（ recommended for CLI 工作流）

Linux / macOS：

```bash
curl -fsSL --connect-timeout 15 --max-time 120 \
  https://github.com/Niko1221/Strata/releases/latest/download/install.sh \
  -o install.sh && sh install.sh
```

Windows PowerShell：

```powershell
irm -TimeoutSec 120 https://github.com/Niko1221/Strata/releases/latest/download/install.ps1 | iex
```

裝完要「開啟新的終端機」，讓 PATH 生效，然後：

```bash
strata launch
```

依照精靈提示選擇並下載模型，完成後就能在本機對話。

## 路線 C：從原始碼或 Docker 建置

README 另外提供 `Build from source`、`Docker`、`Full install guide` 三個入口。倉庫內可見 `Dockerfile`、`docker/`、`CMakeLists.txt`、`CMakePresets.json`、`requirements.txt`、`requirements-build.txt`、`requirements-dev.txt`、`packaging/`。

適合：需要改程式、打包或部署在特殊環境的人。

## 第一次啟動後的檢查清單

- `strata launch` 是否成功列出模型並開始下載
- 模型下載完成後能否正常對話
- 若要比對效能，Windows 可執行 `BENCH.bat`，Unix-like 可執行 `bench.sh`
- 若要更新，Windows 用 `UPDATE.bat`，Unix-like 用 `update.sh`

## 常見誤區

- 以為要註冊帳號：README 明確寫「No account needed」。
- 以為一定要 NVIDIA：官方列出 AMD、Intel Arc、Apple Silicon、Ryzen AI Max、DGX Spark 等支援。
- 以為裝完就能用任何模型：實際上 Strata 主要針對特定模型與量化 pack 調校，選模型要看 `docs/MODELS.md`。
