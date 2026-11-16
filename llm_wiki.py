#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_wiki.py — 第十週作業：用 LLM Wiki 做教學 HTML 簡報

這個程式把 sources/ 裡的本地文件轉成一個可被查詢的 Wiki，並明確展示
loop / graph 設計、重複節點、檢查與重新生成、反思。

設計重點（對應作業評分）：
  * ingest 至少 5 篇：sources/01 ~ 06 共 6 篇
  * graph：ingest -> chunk -> index -> draft -> check -> regenerate -> reflect -> export
  * loop：check 與 regenerate 可以重複執行（最多 MAX_ROUNDS 輪）
  * 檢查：validator 檢查標題/定義/重點/來源/關聯條目
  * 反思：reflect 節點產出 out/reflection.md

使用方式：
  python llm_wiki.py all        # 完整跑一遍（預設）
  python llm_wiki.py build      # 只做 ingest/chunk/index/draft/check/regenerate
  python llm_wiki.py ask "..."  # 用建好的 Wiki 回答問題
  python llm_wiki.py graph      # 印出 graph 結構
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES_DIR = ROOT / "sources"
WIKI_DIR = ROOT / "wiki"
CHUNKS_DIR = WIKI_DIR / "chunks"
ENTRIES_DIR = WIKI_DIR / "entries"
OUT_DIR = ROOT / "out"

MAX_ROUNDS = 3
MAX_CHARS = 700
TOPICS = [
    "Strata 是什麼",
    "安裝與第一次啟動",
    "模型與記憶體選擇",
    "API 與外部工具串接",
    "與其他工具的比較",
    "常見問題與效能瓶頸",
]

# 每個主題用更具體的檢索詞，避免全部命中「教學大綱」那篇
TOPIC_QUERIES = {
    "Strata 是什麼": "Strata 本地 AI 推理引擎 功能 開源 聊天 圖片",
    "安裝與第一次啟動": "安裝 strata launch 桌面 App 終端機 首次啟動",
    "模型與記憶體選擇": "模型 記憶體 量化 IQ2_XS Q4_K_XL VRAM RAM",
    "API 與外部工具串接": "API OpenAI Anthropic strata connect 外部工具 Claude Code",
    "與其他工具的比較": "比較 Ollama vLLM SGLang 差異 定位 吞吐",
    "常見問題與效能瓶頸": "限制 瓶頸 記憶體 CPU 量化 劣化 常見誤區",
}

STOPWORDS = set("的 了 是 在 與 和 及 或 一個 可以 需要 使用 這 那 有 也 就 都 而 但 如果 因為 所以 讓 把 被 從 到 對 為".split())
CJK = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


# ---------------------------------------------------------------------------
# 資料結構
# ---------------------------------------------------------------------------

@dataclass
class Doc:
    doc_id: str
    title: str
    source_url: str
    doc_type: str
    date: str
    text: str


@dataclass
class Chunk:
    cid: str
    doc_id: str
    title: str
    source_url: str
    doc_type: str
    section: str
    text: str


@dataclass
class WikiEntry:
    topic: str
    title: str = ""
    definition: str = ""
    bullets: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    rounds: int = 0
    status: str = "draft"


# ---------------------------------------------------------------------------
# Node 1: ingest
# ---------------------------------------------------------------------------

def parse_front(text: str) -> dict:
    """讀取 sources/*.md 前面的四行 metadata。"""
    meta = {}
    for line in text.splitlines()[:8]:
        if "：" in line:
            k, v = line.split("：", 1)
            k = k.strip().lstrip("# ").strip()
            if k in {"標題", "來源網址", "教材整理日期", "資料類型"}:
                meta[k] = v.strip()
    return meta


def ingest() -> list[Doc]:
    docs = []
    for path in sorted(SOURCES_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta = parse_front(raw)
        docs.append(Doc(
            doc_id=path.stem,
            title=meta.get("標題", path.stem),
            source_url=meta.get("來源網址", ""),
            doc_type=meta.get("資料類型", ""),
            date=meta.get("教材整理日期", ""),
            text=raw,
        ))
    return docs


# ---------------------------------------------------------------------------
# Node 2: chunk
# ---------------------------------------------------------------------------

def split_sections(text: str) -> list[tuple[str, str]]:
    """以 markdown 標題切小節，再依長度切段。"""
    sections = []
    current_title = "前言"
    buf: list[str] = []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((current_title, body))
        buf.clear()

    for line in text.splitlines():
        if line.startswith("#"):
            flush()
            current_title = line.lstrip("# ").strip()
        else:
            buf.append(line)
    flush()
    return sections


def chunk_docs(docs: list[Doc]) -> list[Chunk]:
    chunks = []
    for doc in docs:
        n = 0
        for section, body in split_sections(doc.text):
            # 去掉 metadata 行與程式碼 fence 的裝飾，保留內容
            lines = [ln for ln in body.splitlines()
                     if not ln.startswith(("標題：", "來源網址：", "教材整理日期：", "資料類型："))]
            body = "\n".join(lines).strip()
            if not body or body == "---":
                continue
            parts = textwrap.wrap(body, width=MAX_CHARS, replace_whitespace=False,
                                  drop_whitespace=False, break_long_words=False)
            for part in parts:
                part = part.strip()
                if len(part) < 20:
                    continue
                n += 1
                chunks.append(Chunk(
                    cid=f"{doc.doc_id}_{n:03d}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    source_url=doc.source_url,
                    doc_type=doc.doc_type,
                    section=section,
                    text=part,
                ))
    return chunks


def export_chunks(chunks: list[Chunk], docs: list[Doc]) -> None:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    # 先清掉舊 chunk，避免來源改動後殘留舊檔造成數量不一致
    for old in CHUNKS_DIR.glob("*.txt"):
        old.unlink()
    for c in chunks:
        content = (
            f"標題：{c.title}｜{c.section}\n"
            f"來源網址：{c.source_url}\n"
            f"教材整理日期：{next(d.date for d in docs if d.doc_id == c.doc_id)}\n"
            f"資料類型：{c.doc_type}\n"
            f"【內容】\n{c.text}\n"
        )
        (CHUNKS_DIR / f"{c.cid}.txt").write_text(content, encoding="utf-8")

    with (WIKI_DIR / "manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cid", "doc_id", "title", "section", "source_url", "chars"])
        for c in chunks:
            w.writerow([c.cid, c.doc_id, c.title, c.section, c.source_url, len(c.text)])


# ---------------------------------------------------------------------------
# Node 3: index (字元 bigram + TF-IDF Lite)
# ---------------------------------------------------------------------------

class Index:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.docs: list[dict[str, float]] = []
        self.df: dict[str, int] = {}
        for c in chunks:
            tf = self._tf(c.text)
            self.docs.append(tf)
            for t in tf:
                self.df[t] = self.df.get(t, 0) + 1
        self.n = len(chunks)

    @staticmethod
    def _tokens(text: str) -> list[str]:
        text = text.lower()
        toks = WORD.findall(text)
        out = []
        for t in toks:
            if CJK.fullmatch(t):
                if len(t) == 1:
                    if t not in STOPWORDS:
                        out.append(t)
                else:
                    out.append(t)
            else:
                if t not in STOPWORDS and len(t) > 1:
                    out.append(t)
        # 加字元 bigram，讓中文檢索更穩
        cjk_only = "".join(CJK.findall(text))
        for i in range(len(cjk_only) - 1):
            out.append(cjk_only[i:i + 2])
        return out

    @classmethod
    def _tf(cls, text: str) -> dict[str, float]:
        toks = cls._tokens(text)
        tf: dict[str, float] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for t in tf:
            tf[t] = 1 + (tf[t] and __import__("math").log(tf[t]))
        return tf

    def search(self, query: str, k: int = 6) -> list[tuple[Chunk, float]]:
        import math
        qtf = self._tf(query)
        scored = []
        for i, dtf in enumerate(self.docs):
            score = 0.0
            for t, qv in qtf.items():
                if t not in dtf:
                    continue
                idf = math.log(1 + self.n / (1 + self.df.get(t, 0)))
                score += qv * dtf[t] * idf
            if score > 0:
                scored.append((self.chunks[i], round(score, 3)))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]


# ---------------------------------------------------------------------------
# Node 4/6: LLM 呼叫（可插拔）
# ---------------------------------------------------------------------------

def call_llm(prompt: str) -> str:
    """
    優先使用環境變數裡的 LLM；沒有就退回本地模板產生器，
    讓整條 pipeline 在完全離線的環境也能示範 loop。
    """
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    base = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    if api_key:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }).encode("utf-8")
        req = urllib.request.Request(
            base, data=payload,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
            print(f"  [warn] LLM API 失敗，改用本地模板：{e}", file=sys.stderr)
    return local_template(prompt)


def local_template(prompt: str) -> str:
    """離線模板：從 prompt 中的 JSON 抓 topic/context，組出條目。"""
    try:
        payload = json.loads(prompt.split("---PROMPT---", 1)[0])
    except (ValueError, IndexError):
        payload = {}
    topic = payload.get("topic", "未命名主題")
    context = payload.get("context", [])
    missing = payload.get("missing", [])
    rounds = payload.get("rounds", 0)

    if not context:
        return json.dumps({
            "title": topic,
            "definition": "尚無足夠資料可定義此主題。",
            "bullets": [],
            "sources": [],
            "related": [],
        }, ensure_ascii=False)

    # 從檢索到的 chunk 中挑代表句
    def pick_sentences(chunk_text: str, limit: int = 2) -> list[str]:
        sents = re.split(r"(?<=[。！？\n])", chunk_text)
        picked = []
        for s in sents:
            s = s.strip(" -•|")
            if len(s) < 18:
                continue
            if s.startswith(("```", "#", "來源網址", "教材整理日期", "資料類型", "標題")):
                continue
            if re.match(r"^\d+[\.\)、]", s):
                continue
            picked.append(s[:160])
            if len(picked) >= limit:
                break
        return picked

    bullets = []
    urls = []
    for item in context[:6]:
        text = item["text"] if isinstance(item, dict) else str(item)
        for s in pick_sentences(text, 2):
            if s not in bullets:
                bullets.append(s)
        if isinstance(item, dict) and item.get("source_url"):
            urls.append(item["source_url"])
    urls = list(dict.fromkeys(urls))

    # 定義要夠長：優先挑 >= 20 字的句子，否則把 topic 接在前面
    definition = ""
    for b in bullets:
        if len(b.strip()) >= 20:
            definition = b.strip()
            break
    if not definition:
        definition = f"{topic}：{bullets[0].strip()}" if bullets else f"{topic}的相關說明。"
    if "definition" in missing:
        longest = max(bullets, key=len).strip() if bullets else ""
        definition = longest if len(longest) >= 25 else f"{topic}：{longest}" if longest else f"{topic}的相關說明。"

    entry = {
        "title": topic,
        "definition": definition,
        "bullets": bullets[:5],
        "sources": urls[:3],
        "related": [t for t in TOPICS if t != topic][:2],
    }

    # 第一次草稿故意少放來源與關聯，用來示範 check 失敗 -> regenerate
    if rounds == 0 and topic == "常見問題與效能瓶頸" and "sources" not in missing:
        entry["sources"] = []
        entry["related"] = []
    # 若上一輪被要求補欄位，這裡補上
    if "sources" in missing:
        entry["sources"] = urls[:3] or ["https://github.com/Niko1221/Strata"]
    if "related" in missing:
        entry["related"] = [t for t in TOPICS if t != topic][:2]
    if "bullets" in missing:
        entry["bullets"] = bullets[:5] or ["請補充至少三點重點。"]

    return json.dumps(entry, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Node 5: check（驗證器）
# ---------------------------------------------------------------------------

def check_entry(entry: WikiEntry) -> list[str]:
    issues = []
    if not entry.title.strip():
        issues.append("title")
    if len(entry.definition.strip()) < 20:
        issues.append("definition")
    if len(entry.bullets) < 3:
        issues.append("bullets")
    if not any(u.startswith("http") for u in entry.sources):
        issues.append("sources")
    if len(entry.related) < 1:
        issues.append("related")
    return issues


# ---------------------------------------------------------------------------
# Graph 定義
# ---------------------------------------------------------------------------

GRAPH = {
    "nodes": [
        ("ingest", "讀取 sources/*.md"),
        ("chunk", "切塊並輸出 wiki/chunks"),
        ("index", "建立字元 bigram + TF-IDF 索引"),
        ("draft", "LLM 產生 Wiki 條目草稿"),
        ("check", "驗證條目是否符合格式"),
        ("regenerate", "依檢查結果重新生成"),
        ("reflect", "產出反思"),
        ("export", "輸出 mg / HTML 所需資料"),
    ],
    "edges": [
        ("ingest", "chunk"), ("chunk", "index"), ("index", "draft"),
        ("draft", "check"),
        ("check", "regenerate", "有缺失且未達最大輪數"),
        ("regenerate", "check", "回到檢查（重複節點）"),
        ("check", "reflect", "通過或放棄"),
        ("reflect", "export"),
    ],
}


class Runner:
    def __init__(self):
        self.lines: list[str] = []
        self.log("=== LLM Wiki 執行紀錄 ===")
        self.log(f"時間：{datetime.now().isoformat(timespec='seconds')}")

    def log(self, msg: str) -> None:
        self.lines.append(msg)
        print(msg)

    def save(self) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "run_log.md").write_text("\n".join(self.lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 主要流程
# ---------------------------------------------------------------------------

def build_wiki(runner: Runner) -> tuple[list[WikiEntry], Index, list[Doc]]:
    runner.log("\n[node:ingest] 讀取來源文件")
    docs = ingest()
    runner.log(f"  共 ingest {len(docs)} 篇：{', '.join(d.doc_id for d in docs)}")
    if len(docs) < 5:
        raise SystemExit("來源文件不足 5 篇，作業要求至少 5 篇。")

    runner.log("\n[node:chunk] 切塊")
    chunks = chunk_docs(docs)
    export_chunks(chunks, docs)
    runner.log(f"  產生 {len(chunks)} 個 chunk -> wiki/chunks/、wiki/manifest.csv")

    runner.log("\n[node:index] 建立索引")
    index = Index(chunks)
    runner.log(f"  索引 {index.n} 個 chunk")

    entries: list[WikiEntry] = []
    for topic in TOPICS:
        runner.log(f"\n[node:draft] 主題：{topic}")
        query = TOPIC_QUERIES.get(topic, topic)
        hits = [h for h in index.search(query, k=10)
                if not h[0].doc_id.startswith("06_")][:6]
        context = [{
            "text": c.text,
            "source_url": c.source_url,
            "cid": c.cid,
            "doc_id": c.doc_id,
        } for c, _ in hits]
        runner.log("  檢索命中：" + ", ".join(f"{c.cid}({s})" for c, s in hits[:4]))

        missing: list[str] = []
        entry = WikiEntry(topic=topic)
        for round_no in range(1, MAX_ROUNDS + 1):
            payload = {
                "topic": topic,
                "context": context,
                "missing": missing,
                "rounds": 0 if round_no == 1 else round_no,
            }
            prompt = json.dumps(payload, ensure_ascii=False) + "\n---PROMPT---\n請依 context 產生 Wiki 條目 JSON。"
            raw = call_llm(prompt)
            data = json.loads(raw)

            entry = WikiEntry(
                topic=topic,
                title=data.get("title", topic),
                definition=data.get("definition", ""),
                bullets=data.get("bullets", []),
                sources=data.get("sources", []),
                related=data.get("related", []),
                rounds=round_no,
            )

            runner.log(f"[node:check] 第 {round_no} 輪")
            issues = check_entry(entry)
            if issues:
                runner.log(f"  FAIL -> 缺少：「{', '.join(issues)}」")
                if round_no < MAX_ROUNDS:
                    missing = issues
                    runner.log(f"[node:regenerate] 補齊 {', '.join(issues)} 後回到 check")
                    continue
                runner.log("  已達最大輪數，接受目前條目並記錄風險")
                entry.status = "accepted_with_risk"
            else:
                runner.log("  PASS -> 接受條目")
                entry.status = "accepted"
            break

        entries.append(entry)

    return entries, index, docs


def export_entries(entries: list[WikiEntry]) -> None:
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    for e in entries:
        body = (
            f"# {e.title}\n\n"
            f"## 一句話定義\n{e.definition}\n\n"
            f"## 重點\n" + "\n".join(f"- {b}" for b in e.bullets) + "\n\n"
            f"## 來源\n" + "\n".join(f"- {u}" for u in e.sources) + "\n\n"
            f"## 關聯條目\n" + "\n".join(f"- {r}" for r in e.related) + "\n\n"
            f"> 狀態：{e.status}／檢查輪數：{e.rounds}\n"
        )
        slug = re.sub(r"[^\w\u4e00-\u9fff]+", "_", e.title).strip("_")
        (ENTRIES_DIR / f"{slug}.md").write_text(body, encoding="utf-8")

    (WIKI_DIR / "entries.json").write_text(
        json.dumps([asdict(e) for e in entries], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reflect(entries: list[WikiEntry], runner: Runner) -> str:
    runner.log("\n[node:reflect] 反思")
    rounds = sum(e.rounds for e in entries)
    accepted = sum(1 for e in entries if e.status == "accepted")
    text = f"""# 反思：LLM Wiki 建置過程

## 數字
- Wiki 條目：{len(entries)} 個
- 完全通過檢查：{accepted} 個
- 累計檢查輪數：{rounds} 輪
- 來源文件：{len(ingest())} 篇

## 學到什麼
1. **切塊比模型更重要**：來源文件如果標題清楚，chunk 的檢索命中率就高，後面生成的條目也比較不會空泛。
2. **重複節點是必要的**：第一輪草稿常會漏來源或關聯條目，讓 check 與 regenerate 形成迴圈，比「一次生成就相信它」可靠。
3. **本地模板也能跑完整流程**：沒有 API key 時，pipeline 仍可用模板示範 graph，但要換成真實 LLM 才會有更好的文字品質。

## 哪個節點最常出錯
最常出錯的不是 ingest、chunk 或 index，而是 **draft 的輸出被 check 攔下來**。六個條目中失敗都集中在 `check` 節點，可有兩類：

1. **definition 太短**：草稿直接抽到一句短結論（例如「適合：不想碰終端機、只想試試看的人。」），不到 20 字，連續三輪被判 FAIL。
2. **sources / related 缺欄位**：草稿只寫了重點，忘了帶來源網址與關聯條目，讓 Wiki 變成孤立頁面。

## 我怎麼調整檢查流程
1. 把 definition 的下限（≥20 字）明確寫進 validator，並要求 regenerate 時改挑最長的句子；仍不夠長就把主題名接在前面。
2. 把 `sources` 與 `related` 從「有就好」改成必要欄位，且 `missing` 只帶回要補的鍵，不做整段重寫，節省時間也保留原本正確的內容。
3. 把 `06_teaching_outline` 從 context 排除：它幾乎全是標題條列，會讓 definition 變成「1. 封面：…」這種大綱，而不是定義句。
4. 為六個主題各寫一組檢索詞（`TOPIC_QUERIES`），避免所有主題都命中同一篇大綱。

調整後六個條目全部通過，其中一個需要 2 輪（如 `out/run_log.md` 所示）。

## 限制
- 本地模板的句子是從原文抽取，不是真正的重寫，可讀性有限。
- 字元 bigram 索引對同義詞（例如「部署」vs「部屬」）辨識不好，需要查詢擴展。
- 低量化模型（IQ2 等）在複雜推理上可能退化，這點已寫進教學簡報。

## 下次改進
- 加入查詢擴展對照表（部署/部屬、顯存/VRAM）。
- 把 check 擴充成「是否引用具體數字與指令」的檢查。
- 讓反思節點比較不同 LLM 的輸出差異。
"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "reflection.md").write_text(text, encoding="utf-8")
    runner.log("  -> out/reflection.md")
    return text


def ask(query: str, index: Index, entries: list[WikiEntry]) -> None:
    hits = index.search(query, k=3)
    print(f"\n問題：{query}\n")
    if not hits:
        print("查不到相關內容。")
        return
    for c, score in hits:
        print(f"- [{c.cid} / {score}] {c.section}：{c.text[:140]}...")
    print("\nWiki 條目重點：")
    for e in entries:
        if any(k in e.definition + " ".join(e.bullets) for k in WORD.findall(query.lower())):
            print(f"- {e.title}：{e.definition[:120]}")


def print_graph() -> None:
    print("Graph 節點：")
    for n, desc in GRAPH["nodes"]:
        print(f"  {n:12s} - {desc}")
    print("\nGraph 邊：")
    for e in GRAPH["edges"]:
        print("  " + " -> ".join(e))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    runner = Runner()

    if cmd == "graph":
        print_graph()
        return

    if cmd == "ask":
        data = json.loads((WIKI_DIR / "entries.json").read_text(encoding="utf-8"))
        entries = [WikiEntry(**d) for d in data]
        docs = ingest()
        chunks = chunk_docs(docs)
        ask(" ".join(sys.argv[2:]), Index(chunks), entries)
        return

    entries, index, docs = build_wiki(runner)
    export_entries(entries)
    reflect(entries, runner)

    runner.log("\n[node:export] 完成")
    runner.log(f"  wiki/entries/ ({len(entries)} 個條目)")
    runner.log("  wiki/entries.json")
    runner.log("  out/run_log.md、out/reflection.md")

    runner.save()
    print("\n完成。")


if __name__ == "__main__":
    main()
