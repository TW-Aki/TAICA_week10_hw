#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_slides.py — 由 LLM Wiki 產生教學型 HTML 簡報

讀取 wiki/entries.json 與 out/run_log.md，輸出單檔 HTML：
  out/strata_deployment_teaching.html
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI = ROOT / "wiki"
OUT = ROOT / "out"


def esc(s: str) -> str:
    return html.escape(s or "")


def load_wiki():
    entries = json.loads((WIKI / "entries.json").read_text(encoding="utf-8"))
    manifest_lines = (WIKI / "manifest.csv").read_text(encoding="utf-8-sig").splitlines()
    return entries, max(0, len(manifest_lines) - 1)


STYLE = r"""
:root{
  --bg:#0b1220; --panel:#162238; --panel2:#1e3050; --line:#2b4066;
  --txt:#e8eefc; --muted:#9fb0cf; --accent:#38bdf8; --accent2:#a78bfa;
  --ok:#34d399; --warn:#fbbf24; --bad:#f87171;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{
  background:radial-gradient(1200px 700px at 15% -10%,#1c2f52 0%,transparent 60%),
             radial-gradient(900px 600px at 110% 110%,#2a1d4d 0%,transparent 55%),var(--bg);
  color:var(--txt);font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,-apple-system,sans-serif;
  overflow:hidden;
}
#deck{position:relative;width:100vw;height:100vh}
.slide{
  position:absolute;inset:0;padding:6vh 8vw;display:none;
  flex-direction:column;justify-content:flex-start;
  animation:fade .35s ease;
}
.slide.active{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.kicker{color:var(--accent);font-size:14px;letter-spacing:.18em;font-weight:700;margin-bottom:10px}
h1{font-size:clamp(34px,5.2vw,68px);margin:0 0 18px;line-height:1.15}
h2{font-size:clamp(26px,3.4vw,44px);margin:0 0 22px;line-height:1.2}
h3{font-size:18px;margin:0 0 10px;color:var(--accent2)}
p{font-size:clamp(15px,1.45vw,20px);line-height:1.75;color:var(--muted);margin:8px 0}
ul{font-size:clamp(15px,1.45vw,20px);line-height:1.8;color:var(--muted);padding-left:22px;margin:8px 0}
li{margin:6px 0}
strong{color:var(--txt)}
code{
  background:#0a1426;border:1px solid var(--line);border-radius:6px;
  padding:2px 7px;font-family:"Cascadia Code",Consolas,monospace;font-size:.9em;color:#7dd3fc;
}
pre{
  background:#0a1426;border:1px solid var(--line);border-radius:12px;padding:18px 20px;
  overflow:auto;font-family:"Cascadia Code",Consolas,monospace;font-size:14px;line-height:1.6;
}
pre code{background:none;border:0;padding:0;color:#c7d7f5}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:repeat(2,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.card{
  background:linear-gradient(160deg,var(--panel),var(--panel2));
  border:1px solid var(--line);border-radius:16px;padding:20px 22px;
}
.card p,.card ul{font-size:clamp(13px,1.15vw,17px)}
.tag{display:inline-block;background:#123055;color:#7dd3fc;border:1px solid #26588f;
  border-radius:999px;padding:4px 12px;font-size:12px;margin:0 6px 6px 0}
table{width:100%;border-collapse:collapse;font-size:clamp(12px,1.1vw,16px)}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:#142746;color:#9dd6ff}
tr:nth-child(even) td{background:#101d33}
.badge-ok{color:var(--ok);font-weight:700}
.badge-warn{color:var(--warn);font-weight:700}
.badge-bad{color:var(--bad);font-weight:700}
.quote{border-left:4px solid var(--accent2);padding-left:18px;color:#cbd5f5}
.big{font-size:clamp(22px,2.5vw,34px);font-weight:700;line-height:1.5}
.cover{justify-content:center}
.cover .sub{font-size:clamp(16px,1.8vw,24px);color:var(--muted);margin-top:8px}
.cover .meta{margin-top:36px;color:#7890b8;font-size:14px}
svg{max-width:100%;height:auto}
.foot{
  position:absolute;left:8vw;right:8vw;bottom:3vh;display:flex;align-items:center;gap:14px;
  color:#6f86ad;font-size:12px;
}
.bar{flex:1;height:4px;background:#1d2c47;border-radius:4px;overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));width:0;transition:width .3s}
.btn{
  background:#152744;border:1px solid var(--line);color:var(--txt);border-radius:10px;
  padding:8px 14px;cursor:pointer;font-size:13px;
}
.btn:hover{border-color:var(--accent);background:#1b3257}
.hint{position:absolute;right:8vw;bottom:3vh;color:#5f769e;font-size:12px}
.log{font-size:12px!important;line-height:1.55!important}
"""

SCRIPT = r"""
let i=0;
const S=[...document.querySelectorAll('.slide')];
function show(n){
  i=(n+S.length)%S.length;
  S.forEach((s,k)=>s.classList.toggle('active',k===i));
  document.querySelector('.bar i').style.width=((i+1)/S.length*100)+'%';
  document.getElementById('num').textContent=(i+1)+' / '+S.length;
}
document.addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){e.preventDefault();show(i+1)}
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();show(i-1)}
  if(e.key==='Home')show(0); if(e.key==='End')show(S.length-1);
});
show(0);
"""


def slide(kicker: str, title: str, body: str, cls: str = "") -> str:
    return f'<section class="slide {cls}"><div class="kicker">{esc(kicker)}</div><h2>{esc(title)}</h2>{body}</section>'


def build() -> Path:
    entries, chunk_count = load_wiki()
    by_topic = {e["topic"]: e for e in entries}

    def wiki_card(topic: str) -> str:
        e = by_topic.get(topic, {})
        bullets = "".join(f"<li>{esc(b)}</li>" for b in e.get("bullets", [])[:3])
        return (f'<div class="card"><h3>{esc(topic)}</h3>'
                f'<p>{esc(e.get("definition", ""))}</p><ul>{bullets}</ul></div>')

    slides: list[str] = []

    # 1 封面
    slides.append(
        '<section class="slide cover">'
        '<div class="kicker">NTU COOL 第十週作業 · LLM WIKI</div>'
        '<h1>如何用 Strata<br>部署本地模型</h1>'
        '<div class="sub">從硬體選型、安裝啟動到 API 串接的一次完整實作</div>'
        '<div class="meta">教材來源：Strata 官方 GitHub + 技術評論共 6 篇　|　'
        '由 LLM Wiki 自動整理並產出　|　2026-11-16</div>'
        '</section>'
    )

    # 2 為什麼本地部署
    slides.append(slide("動機", "為什麼要本地部署？", """
    <div class="grid g3">
      <div class="card"><h3>隱私</h3><p>文件、程式碼與對話都不必離開電腦。Strata 主打 <strong>No account needed</strong>、完全本機運行。</p></div>
      <div class="card"><h3>成本</h3><p>一次性硬體成本取代長期 API 帳單。本機 <code>localhost</code> API 可取代付費端點。</p></div>
      <div class="card"><h3>離線</h3><p>沒有網路也能聊天、寫程式；模型與推論引擎都存放在本機。</p></div>
    </div>
    <p class="quote">但代價是：要自己處理模型下載、量化選擇、記憶體配置與速度取捨。</p>
    """))

    # 3 Strata 是什麼
    slides.append(slide("定義", "Strata 是什麼？", f"""
    <p class="big">{esc(by_topic.get("Strata 是什麼", {}).get("definition", ""))}</p>
    <div class="grid g2" style="margin-top:18px">
      <div class="card"><h3>形態</h3><ul>
        <li>桌面 App（Windows / Linux / macOS arm64）</li>
        <li>終端機 App（<code>strata launch</code>）</li>
        <li>開源、MIT、不需註冊帳號</li>
      </ul></div>
      <div class="card"><h3>主打模型</h3><ul>
        <li><code>Qwen3.8-Flash-Next</code>（ISTA-DASLab）</li>
        <li>量化：<code>Q2_0</code>、<code>IQ2_XS</code>、<code>IQ3_XXS</code>、<code>IQ3_S</code></li>
        <li>Coder：<code>IQ1_M</code></li>
      </ul></div>
    </div>
    """))

    # 4 比較
    slides.append(slide("選型", "跟 Ollama / vLLM / SGLang 差在哪？", """
    <table>
      <tr><th>工具</th><th>定位</th><th>核心技術</th><th>硬體門檻</th><th>強項</th></tr>
      <tr><td><strong>Strata</strong></td><td>消費級跑超顯存 MoE</td><td>C++ 異構分層排程、CPU/GPU 平行</td><td>12–24G 顯卡 + 32–64G+ RAM</td><td>單併發極致優化</td></tr>
      <tr><td>Ollama</td><td>輕量個人應用</td><td>llama.cpp / GGUF</td><td>一般 PC、Mac、甚至純 CPU</td><td>一鍵上手、模型庫完整</td></tr>
      <tr><td>vLLM</td><td>企業級生產服務</td><td>PagedAttention + Continuous Batching</td><td>資料中心卡</td><td>高併發吞吐</td></tr>
      <tr><td>SGLang</td><td>Complex Agent / 長文本</td><td>RadixAttention</td><td>多卡集群</td><td>前綴快取、結構化解碼</td></tr>
    </table>
    <p style="margin-top:14px">簡單記：<strong>Strata 是把「放不下」的模型跑起來，Ollama 是把「放得下」的模型跑得最快。</strong></p>
    """))

    # 5 硬體與量化
    slides.append(slide("硬體", "先查記憶體，再選模型", """
    <div class="grid g2">
      <div class="card"><h3>量化光譜</h3><ul>
        <li><code>IQ1_M</code> / <code>IQ2_XS</code> / <code>IQ3_XXS</code>：最省記憶體，但複雜推理可能退化</li>
        <li><code>UD-Q4_K_XL</code> / <code>UD-Q6_K_XL</code>：品質與資源的平衡</li>
        <li><code>Q8_0</code>：品質最好，但最吃 VRAM / RAM</li>
        <li><code>Gyro-S</code> / <code>Gyro-M</code>：更省記憶體但更慢</li>
      </ul></div>
      <div class="card"><h3>決策流程</h3><ul>
        <li>查自己的 VRAM 與 RAM</li>
        <li>對照 <code>docs/MODELS.md#pick-by-memory</code></li>
        <li>記憶體緊 → 低 bit；充裕 → 高 bit</li>
        <li>確認 GPU 在支援清單內（RTX 20/30/40/50、AMD RX 7700+ 、Apple Silicon M1+…）</li>
      </ul></div>
    </div>
    <p class="quote">MoE 模型的「總參數」不等於每次推理的計算量，但全部專家仍要放進記憶體。</p>
    """))

    # 6 安裝
    slides.append(slide("安裝", "三條安裝路線", """
    <div class="grid g3">
      <div class="card"><h3>A · 桌面 App</h3><p>下載 Releases 安裝檔，Windows 用 <code>.exe</code>、Linux 用 <code>.AppImage</code>、macOS 用 <code>.dmg</code>。首次啟動會自動下載對應引擎。</p></div>
      <div class="card"><h3>B · 終端機</h3>
        <pre><code># Linux / macOS
curl -fsSL .../install.sh -o install.sh &amp;&amp; sh install.sh

# Windows PowerShell
irm .../install.ps1 | iex

strata launch</code></pre>
      </div>
      <div class="card"><h3>C · 原始碼 / Docker</h3><p>倉庫提供 <code>Dockerfile</code>、<code>CMakeLists.txt</code>、<code>setup.py</code>，適合要修改或特殊部署的人。</p></div>
    </div>
    <p>裝完請<strong>開新的終端機</strong>讓 PATH 生效，再執行 <code>strata launch</code>。</p>
    """))

    # 7 第一次啟動
    slides.append(slide("實作", "第一次啟動與對話", f"""
    <p>{esc(by_topic.get("安裝與第一次啟動", {}).get("definition", ""))}</p>
    <pre><code>strata launch     # 依精靈提示下載並啟動模型
strata connect    # 查看External tool 串接設定
BENCH.bat / bench.sh   # 效能測試
UPDATE.bat / update.sh # 更新</code></pre>
    <div class="grid g2" style="margin-top:14px">
      <div class="card"><h3>檢查清單</h3><ul><li>模型是否成功下載</li><li>能否正常對話</li><li>圖片輸入是否可用</li></ul></div>
      <div class="card"><h3>常見誤區</h3><ul><li>以為要註冊帳號（不用）</li><li>以為只能 NVIDIA（AMD / Intel / Apple 都支援）</li><li>以為任何模型都能拉（其實針對特定 MoE 調校）</li></ul></div>
    </div>
    """))

    # 8 API
    slides.append(slide("串接", "把 Strata 變成其他工具的後端", """
    <p>Strata 在本機 <code>localhost</code> 同時提供 <strong>OpenAI 相容</strong>與 <strong>Anthropic 相容</strong> API，且支援圖片輸入。</p>
    <pre><code>strata connect</code></pre>
    <p>可接入：</p>
    <div>
      <span class="tag">Claude Code</span><span class="tag">Codex CLI</span><span class="tag">OpenCode</span>
      <span class="tag">oh-my-pi</span><span class="tag">pi.dev</span><span class="tag">Hermes Agent</span><span class="tag">OpenClaw</span>
    </div>
    <p style="margin-top:14px">做法：把工具的 API base URL 指向 Strata 本機位置，model 欄填 Strata 提供的模型名稱。敏感資料不必出電腦。</p>
    """))

    # 9 常見問題
    slides.append(slide("限制", "常見問題與效能瓶頸", f"""
    <div class="grid g2">
      <div class="card"><h3>模型支援較窄</h3><p>為壓榨特定 MoE 的效率，Strata 不像 Ollama 能隨意拉任何小模型。</p></div>
      <div class="card"><h3>記憶體與 CPU 門檻</h3><p>全量專家駐留 RAM，通常要 32–64GB，且 CPU 需支援 AVX2 / AVX-512。</p></div>
      <div class="card"><h3>低量化劣化</h3><p>IQ2 / Q4 等極低 bit 會讓複雜推理能力下降。</p></div>
      <div class="card"><h3>併發不是強項</h3><p>針對 Batch=1 優化；若要上百人同時用，應改選 vLLM。</p></div>
    </div>
    <p class="quote" style="margin-top:14px">{esc(by_topic.get("常見問題與效能瓶頸", {}).get("definition", ""))}</p>
    """))

    # 10 Wiki 摘要
    wiki_cards = "".join(wiki_card(t) for t in [
        "Strata 是什麼", "安裝與第一次啟動", "模型與記憶體選擇",
        "API 與外部工具串接", "與其他工具的比較", "常見問題與效能瓶頸",
    ])
    slides.append(slide("LLM WIKI", f"這份簡報是怎麼被「寫」出來的？", f"""
    <p>先建立自己的 LLM Wiki：<strong>ingest 6 篇 → 切成 {chunk_count} 個 chunk → 索引 → 生成 6 個條目 → 檢查 → 重新生成 → 反思</strong>。</p>
    <div class="grid g3" style="margin-top:12px">{wiki_cards}</div>
    """))

    # 11 Graph
    slides.append(slide("GRAPH 設計", "Loop / Graph 設計圖", """
    <svg viewBox="0 0 1000 430" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/>
        </marker>
      </defs>
      <g font-family="sans-serif" font-size="15" fill="#e8eefc">
        <rect x="20"  y="60" width="140" height="56" rx="12" fill="#1e3050" stroke="#38bdf8"/>
        <text x="90"  y="94" text-anchor="middle">ingest 6 篇</text>
        <rect x="200" y="60" width="140" height="56" rx="12" fill="#1e3050" stroke="#38bdf8"/>
        <text x="270" y="94" text-anchor="middle">chunk 36 塊</text>
        <rect x="380" y="60" width="140" height="56" rx="12" fill="#1e3050" stroke="#38bdf8"/>
        <text x="450" y="94" text-anchor="middle">index 檢索</text>
        <rect x="560" y="60" width="140" height="56" rx="12" fill="#1e3050" stroke="#a78bfa"/>
        <text x="630" y="94" text-anchor="middle">draft 草稿</text>
        <rect x="740" y="60" width="140" height="56" rx="12" fill="#1e3050" stroke="#fbbf24"/>
        <text x="810" y="94" text-anchor="middle">check 檢查</text>

        <rect x="740" y="230" width="140" height="56" rx="12" fill="#1e3050" stroke="#f87171"/>
        <text x="810" y="264" text-anchor="middle">regenerate 重生成</text>
        <rect x="500" y="330" width="150" height="56" rx="12" fill="#1e3050" stroke="#34d399"/>
        <text x="575" y="364" text-anchor="middle">reflect 反思</text>
        <rect x="700" y="330" width="150" height="56" rx="12" fill="#1e3050" stroke="#34d399"/>
        <text x="775" y="364" text-anchor="middle">export HTML</text>

        <path d="M160,88 H195" stroke="#38bdf8" stroke-width="2" marker-end="url(#a)"/>
        <path d="M340,88 H375" stroke="#38bdf8" stroke-width="2" marker-end="url(#a)"/>
        <path d="M520,88 H555" stroke="#38bdf8" stroke-width="2" marker-end="url(#a)"/>
        <path d="M700,88 H735" stroke="#38bdf8" stroke-width="2" marker-end="url(#a)"/>
        <path d="M810,116 V225" stroke="#fbbf24" stroke-width="2" marker-end="url(#a)"/>
        <text x="825" y="175" fill="#fbbf24" font-size="13">FAIL</text>
        <path d="M740,258 H640 Q610,258 610,228 V130 Q610,116 625,116 H690"
              stroke="#f87171" stroke-width="2" fill="none" marker-end="url(#a)"/>
        <text x="620" y="205" fill="#f87171" font-size="13">回到 check（重複節點）</text>
        <path d="M780,286 V330 H775" stroke="#34d399" stroke-width="2" fill="none" marker-end="url(#a)"/>
        <text x="790" y="310" fill="#34d399" font-size="13">PASS</text>
        <path d="M650,358 H695" stroke="#34d399" stroke-width="2" marker-end="url(#a)"/>
      </g>
    </svg>
    <p>關鍵：<strong>check 與 regenerate 形成迴圈</strong>，最多 3 輪；通過後才進入反思與輸出。</p>
    """))

    # 12 重複節點實證
    run_log = (OUT / "run_log.md").read_text(encoding="utf-8")
    log_slice = "\n".join(
        line for line in run_log.splitlines()
        if "常見問題" in line or "check" in line or "FAIL" in line
        or "regenerate" in line or "PASS" in line or "檢索命中" in line
    )[:1400]
    slides.append(slide("LOOP 實證", "重複節點、檢查與重新生成", f"""
    <p> validator 會檢查五件事：<code>title</code>、<code>definition</code>（≥20 字）、<code>bullets</code>（≥3）、<code>sources</code>（要有網址）、<code>related</code>（≥1）。</p>
    <p>下面是實際執行紀錄：第一輪草稿少了來源與關聯 → <span class="badge-bad">FAIL</span> → regenerate 補齊 → 回到 check → <span class="badge-ok">PASS</span>。</p>
    <pre class="log"><code>{esc(log_slice)}</code></pre>
    """))

    # 13 反思
    reflection = (OUT / "reflection.md").read_text(encoding="utf-8")
    reflect_error = reflection.split("## 哪個節點最常出錯")[-1].split("## 限制")[0].strip()
    slides.append(slide("REFLECTION", "反思：哪個節點最常出錯？", f"""
    <div class="grid g2">
      <div class="card"><h3>最常出錯：draft → check</h3><p>{esc(reflect_error[:850])}</p></div>
      <div class="card"><h3>我怎麼調整檢查流程</h3><ul>
        <li>把 definition 下限（≥20 字）寫進 validator</li>
        <li>sources / related 改為必要欄位，missing 只回補缺失鍵</li>
        <li>把教學大綱從 context 排除，避免定義變成標題列表</li>
        <li>為六個主題各寫檢索詞（TOPIC_QUERIES）</li>
        <li>本地模板抽取可讀性有限 → 有 API key 時換真實 LLM</li>
      </ul></div>
    </div>
    <p class="quote" style="margin-top:16px">最大的收穫：與其相信 LLM 一次就寫對，不如把「檢查—修正」做成 graph 裡會重複執行的節點。</p>
    """))

    # 14 總結
    slides.append(slide("總結", "帶得走的五句話", """
    <div class="grid g2">
      <div class="card"><h3>技術面</h3><ul>
        <li>Strata 適合「低顯卡 + 大記憶體」跑大型 MoE</li>
        <li>先查 <code>docs/MODELS.md</code> 再選量化</li>
        <li><code>strata launch</code> 啟動，<code>strata connect</code> 串接</li>
      </ul></div>
      <div class="card"><h3>方法面</h3><ul>
        <li>LLM Wiki = ingest → chunk → index → draft</li>
        <li>用 check ↔ regenerate 迴圈代替一次生成</li>
        <li>反思節點把限制與改進寫下來</li>
      </ul></div>
    </div>
    <p class="big" style="margin-top:20px">謝謝！歡迎提問。</p>
    """))

    html_doc = (
        "<!DOCTYPE html><html lang='zh-Hant'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>如何用 Strata 部署本地模型｜LLM Wiki 教學簡報</title>"
        f"<style>{STYLE}</style></head><body><div id='deck'>"
        + "\n".join(slides)
        + "<div class='foot'><span id='num'></span><div class='bar'><i></i></div>"
        "<button class='btn' onclick='show(i-1)'>← 上一頁</button>"
        "<button class='btn' onclick='show(i+1)'>下一頁 →</button></div>"
        "<div class='hint'>← → / 空白鍵 切換</div>"
        f"</div><script>{SCRIPT}</script></body></html>"
    )

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "strata_deployment_teaching.html"
    path.write_text(html_doc, encoding="utf-8")
    return path


if __name__ == "__main__":
    p = build()
    print(f"已產生：{p}")
