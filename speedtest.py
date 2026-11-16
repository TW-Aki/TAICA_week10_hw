#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
speedtest.py — 測試目前運行中的 Strata 模型速度

會自動從 Strata 設定檔讀出 API 位址與金鑰，不需手動複製。
只使用標準庫，不用安裝任何套件。

用法：
  python speedtest.py                 # 標準測試（3 輪）
  python speedtest.py --quick         # 快速（1 輪、短 prompt）
  python speedtest.py --long          # 加測約 8K tokens 的長 prompt
  python speedtest.py --runs 5        # 每項 5 輪取中位數
  python speedtest.py --think         # 保留思考模式（預設關閉）
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"


def find_endpoint() -> tuple[str, str, str]:
    """回傳 (base_url, api_key, model_id)。"""
    pattern = str(Path.home() / ".strata" / "data" / "native-instances" / "*.json")
    for f in glob.glob(pattern):
        try:
            cfg = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        key, port = cfg.get("api_key"), cfg.get("port")
        if not key or not port:
            continue
        base = f"http://127.0.0.1:{port}"
        try:
            req = urllib.request.Request(f"{base}/v1/models",
                                         headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=8) as r:
                r.read()
        except Exception:
            continue
        return base, key, cfg.get("model_name") or cfg["aliases"][0]
    raise SystemExit("找不到執行中的 Strata 模型，請先開啟 App 並啟動模型。")


def call(base: str, key: str, model: str, prompt: str,
         max_tokens: int, think: bool) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    if not think:
        payload["reasoning_effort"] = "none"

    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode("utf-8"))
    wall = time.perf_counter() - t0

    tim = data.get("timings", {})
    msg = data["choices"][0]["message"]
    text = msg.get("content") or msg.get("reasoning_content") or ""

    return {
        "prompt_tokens": tim.get("prompt_n") or data.get("usage", {}).get("prompt_tokens", 0),
        "prompt_ms": tim.get("prompt_ms"),
        "prompt_tok_s": tim.get("prompt_per_second"),
        "gen_tokens": tim.get("predicted_n") or data.get("usage", {}).get("completion_tokens", 0),
        "gen_ms": tim.get("predicted_ms"),
        "gen_tok_s": tim.get("predicted_per_second"),
        "wall_s": round(wall, 2),
        "text": (text or "").strip().replace("\n", " ")[:80],
    }


def make_prompt(approx_tokens: int) -> str:
    unit = ("這是一段用來測試模型讀取速度的固定文字，內容本身沒有特別意義，"
            "只是為了讓 prompt 達到指定長度，方便觀察不同長度下的處理差異。")
    return unit * max(1, approx_tokens // 30)


def run_case(name: str, base: str, key: str, model: str, prompt: str,
             max_tokens: int, runs: int, think: bool) -> dict:
    print(f"  · {name} ", end="", flush=True)
    rows = []
    for i in range(runs):
        try:
            rows.append(call(base, key, model, prompt, max_tokens, think))
            print("·", end="", flush=True)
        except urllib.error.URLError as e:
            print(f"\n    失敗：{e}")
            return {"name": name, "error": str(e)}

    med = lambda k: statistics.median([r[k] for r in rows if r.get(k) is not None])
    out = {
        "name": name,
        "runs": len(rows),
        "prompt_tokens": rows[0]["prompt_tokens"],
        "gen_tokens": rows[0]["gen_tokens"],
        "prompt_tok_s": round(med("prompt_tok_s"), 1),
        "gen_tok_s": round(med("gen_tok_s"), 1),
        "wall_s": round(med("wall_s"), 2),
        "sample": rows[-1]["text"],
    }
    print(f" → {out['gen_tok_s']} tok/s")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Strata 模型速度測試")
    ap.add_argument("--runs", type=int, default=3, help="每項輪數（預設 3）")
    ap.add_argument("--quick", action="store_true", help="只跑兩項、1 輪")
    ap.add_argument("--long", action="store_true", help="加測約 8K tokens 長 prompt")
    ap.add_argument("--think", action="store_true", help="保留思考模式（較慢）")
    args = ap.parse_args()

    base, key, model = find_endpoint()
    runs = 1 if args.quick else args.runs

    print(f"\n模型：{model}")
    print(f"端點：{base}")
    print(f"思考模式：{'開' if args.think else '關'}　每項 {runs} 輪\n")

    cases = [
        ("短問答（約 20 tokens）", "用一句話說明什麼是 MoE 模型。", 60),
        ("中文生成（約 250 字）",
         "用繁體中文寫一段 250 字左右的說明，主題是本地部署大型語言模型的好處。", 350),
    ]
    if not args.quick:
        cases.append(("中長 prompt（約 2K tokens）",
                      make_prompt(2000) + "\n\n請用一句話總結上面這段文字。", 60))
    if args.long:
        cases.append(("長 prompt（約 8K tokens）",
                      make_prompt(8000) + "\n\n請用一句話總結上面這段文字。", 60))

    print("開始測試：")
    results = [run_case(n, base, key, model, p, m, runs, args.think)
               for n, p, m in cases]

    print("\n" + "=" * 78)
    print(f"{'測試項目':<28}{'prompt':>8}{'讀取 tok/s':>12}{'生成 tok/s':>12}{'耗時 s':>9}")
    print("-" * 78)
    for r in results:
        if r.get("error"):
            print(f"{r['name']:<28}{'失敗':>8}")
            continue
        print(f"{r['name']:<28}{r['prompt_tokens']:>8}{r['prompt_tok_s']:>12}"
              f"{r['gen_tok_s']:>12}{r['wall_s']:>9}")
    print("=" * 78)
    for r in results:
        if r.get("sample"):
            print(f"\n[{r['name']}] 輸出樣本：{r['sample']}…")

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "bench_result.json"
    path.write_text(json.dumps({
        "model": model,
        "endpoint": base,
        "think": args.think,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n結果已存：{path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已中止")
        sys.exit(1)
