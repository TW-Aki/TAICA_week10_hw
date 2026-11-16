標題：把 Strata 接給外部工具：API 與 strata connect
來源網址：https://github.com/Niko1221/Strata#connect-external-tools
教材整理日期：2026-11-16
資料類型：官方文件

# API 與外部工具串接

Strata 不只是一個聊天視窗，它會在本機 `localhost` 開放兩套相容 API，因此可以當成其他工具的模型後端。

## 兩套 API

- OpenAI-compatible API
- Anthropic-compatible API

兩者都在本機運行，且支援可選的圖片輸入。這代表大多數「可以吃 OpenAI API base URL 的程式」都能改個網址就接上 Strata。

## strata connect

```bash
strata connect
```

用途：印出或引導你完成把 Strata 接到外部工具的設定。README 明確列出的工具包括：

- Claude Code
- Codex CLI
- OpenCode
- oh-my-pi
- pi.dev
- Hermes Agent
- OpenClaw

以及更多透過 OpenAI / Anthropic 相容 API 接入的工具。

## 為什麼這很重要

本地部署的價值不只是「離線聊天」，而是把原本要花錢打 API 的工作流（寫程式、Agent、文件處理）整個搬到本機。Strata 選擇相容兩大協定，降低了轉換成本。

## 實作重點

1. 先 `strata launch` 讓模型跑起來。
2. 再執行 `strata connect` 看設定說明。
3. 在外部工具裡把 API base URL 指向 Strata 的本機位置，model 欄位填 Strata 提供的模型名稱。
4. 因為是本機 API，資料不用出電腦，適合處理敏感文件。

## 常見誤區

- 以為要申請 API key：本機 API 通常不需要對外服務的金鑰，但仍要照 `strata connect` 的指示設定。
- 以為只能用在 Claude Code：任何支援自訂 OpenAI-compatible endpoint 的程式都有機會接入。
