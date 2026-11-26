#!/usr/bin/env python3
"""Builds guide/, developers/ and notes/ from _docs/. Standard library only.

    python3 _tools/build_docs.py          write the pages
    python3 _tools/build_docs.py --check  fail if a page is out of date or a link is broken
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://bbdyno.github.io/Branchlane-Page/"
REPO = "https://github.com/bbdyno/Branchlane-Page"
STORE = "https://apps.apple.com/app/id6785129372"
VERSION = "20261126"

# area, folder of the page inside the area, source, group, {lang: (title, summary)}
G = {"start": ("Start", "시작"), "use": ("Use", "사용"), "agents": ("Agents", "에이전트"), "help": ("Help", "도움"),
     "connect": ("Connect", "연결"), "ref": ("Reference", "레퍼런스"), "files": ("Files and refs", "파일과 ref"), "build": ("Build", "만들기"),
     "notes": ("Notes", "글")}
PAGES = [
    ("guide", "", "guide-start", "start", ("Get started", "Set up Branchlane with the Git, SSH keys and remotes you already have."), ("시작하기", "이미 쓰던 Git, SSH 키, 원격으로 Branchlane을 설정합니다.")),
    ("guide", "everyday", "guide-everyday", "use", ("Everyday Git", "Stage, commit, branch, undo, stash and read history."), ("매일 쓰는 Git", "스테이징, 커밋, 브랜치, 실행 취소, 스태시, 기록을 다룹니다.")),
    ("guide", "pro", "guide-pro", "use", ("Pro tools", "Interactive rebase, the conflict editor, pull requests and AI."), ("Pro 도구", "인터랙티브 리베이스, 충돌 편집기, PR, AI 기능입니다.")),
    ("guide", "shortcuts", "guide-shortcuts", "use", ("Keyboard shortcuts", "The keys you use most. All of them are under ⌘/ in the app."), ("단축키", "자주 쓰는 키입니다. 전체는 앱에서 ⌘/로 봅니다.")),
    ("guide", "lanes", "guide-lanes", "agents", ("Agent lanes", "Give each coding agent its own branch and folder, and review its work in one place."), ("에이전트 Lane", "코딩 에이전트마다 브랜치와 폴더를 따로 주고 한 곳에서 검토합니다.")),
    ("guide", "troubleshooting", "guide-trouble", "help", ("Troubleshooting", "What to do where the App Sandbox gets in the way."), ("문제 해결", "App Sandbox 때문에 막히는 곳을 푸는 방법입니다.")),
    ("guide", "support", "guide-help", "help", ("Get help", "Where to ask, and what to include."), ("도움 받기", "물어볼 곳과 적을 내용입니다.")),
    ("developers", "", "developers-overview", "connect", ("Build on Branchlane", "Connect coding agents and your own tools through a local MCP server, and read what Branchlane keeps in the repository. No cloud API, no account."), ("Branchlane 위에 만들기", "로컬 MCP 서버로 코딩 에이전트와 내 도구를 연결하고, Branchlane이 저장소에 남기는 것을 읽으세요. 클라우드 API도 계정도 없습니다.")),
    ("developers", "connect", "developers-connect", "connect", ("Connect an agent", "Add the local MCP server to Claude Code, Codex or any MCP client."), ("에이전트 연결", "Claude Code, Codex, 다른 MCP 클라이언트에 로컬 MCP 서버를 더합니다.")),
    ("developers", "lanes", "developers-flow", "connect", ("Lane flow and states", "The order of calls, and what each state means."), ("Lane 흐름과 상태", "부르는 순서와 상태마다의 뜻입니다.")),
    ("developers", "tools", "developers-tools", "ref", ("Tools", "Every MCP tool, its arguments and what it returns."), ("도구", "MCP 도구마다의 인자와 돌려주는 값입니다.")),
    ("developers", "protocol", "developers-protocol", "ref", ("Protocol", "Address, transport, limits, authentication and MCP versions."), ("프로토콜", "주소, 전송, 한도, 인증, MCP 버전입니다.")),
    ("developers", "hook", "developers-hook", "ref", ("Checkpoint hook", "Save a checkpoint at the end of every agent turn."), ("체크포인트 훅", "에이전트 턴이 끝날 때마다 체크포인트를 남깁니다.")),
    ("developers", "policy", "developers-policy", "files", ("Policy file", "What agents may do in a repository, in one committed file."), ("정책 파일", "저장소에서 에이전트가 해도 되는 일을 커밋한 파일 하나에 적습니다.")),
    ("developers", "attribution", "developers-attribution", "files", ("Agent attribution", "Commit trailers, Agent Trace notes and lane records."), ("에이전트 출처 표시", "커밋 트레일러, Agent Trace 노트, Lane 기록입니다.")),
    ("developers", "worktrees", "developers-summary", "files", ("Worktree summary", "One JSON file that describes every worktree."), ("워크트리 요약", "모든 워크트리를 적은 JSON 파일 하나입니다.")),
    ("developers", "extend", "developers-extend", "build", ("Extend Branchlane", "Bring your own model server, or an MCP server for the assistant."), ("Branchlane 확장", "내 모델 서버나 비서용 MCP 서버를 연결합니다.")),
    ("developers", "support", "developers-support", "build", ("Questions and requests", "Ask, or request an integration."), ("질문과 요청", "질문하거나 연동을 요청합니다.")),
    ("notes", "", "notes-index", "notes", None, ("기술 노트", "Branchlane을 만들며 내린 결정과 겪은 제약을 기록합니다.")),
    ("notes", "making-branchlane", "notes-making-branchlane", "notes", None, ("계정도 서버도 없는 Mac Git 클라이언트", "Branchlane을 만들며 정한 원칙, App Sandbox와 씨름한 이야기, 에이전트 Lane의 설계입니다.")),
]
AREAS = {"guide": ("Guide", "가이드"), "developers": ("Developers", "개발자"), "notes": (None, "기술 노트")}
META = {"notes/making-branchlane": ("2026년 11월 23일", "https://bbdyno.github.io/posts/branchlane-mac-git-client/")}
# Headings of the pages these docs were until November 2026.
MOVED = {
    "guide": {"start": "", "everyday": "everyday/", "pro": "pro/", "lanes": "lanes/", "shortcuts": "shortcuts/", "trouble": "troubleshooting/", "help": "support/"},
    "developers": {"overview": "", "connect": "connect/", "protocol": "protocol/", "tools": "tools/", "flow": "lanes/", "hook": "hook/", "policy": "policy/",
                   "attribution": "attribution/", "summary": "worktrees/", "extend": "extend/", "support": "support/"},
}
T = {
    "en": dict(docs="Docs", search="Search docs", copy="Copy", copied="Copied", selected="Selected", theme="Switch between light and dark", menu="Open navigation",
               outline="On this page", prev="Previous", next="Next", edit="Edit this page", support="Support", privacy="Privacy Policy", other="한국어", otherlang="ko",
               get="Download free", home="Product", updated="Updated November 26, 2026", for_="Branchlane 2.3", hint="Type a tool, a setting or a question.",
               none="Nothing found.", failed="Search could not be loaded.", skip="Skip to content", nav="Docs navigation", original="Original post", enlarge="Enlarge", output="Output",
               tm="Apple, App Store and Mac are trademarks of Apple Inc., registered in the U.S. and other countries and regions."),
    "ko": dict(docs="문서", search="문서 검색", copy="복사", copied="복사함", selected="선택함", theme="밝은 화면과 어두운 화면 바꾸기", menu="메뉴 열기",
               outline="이 페이지에서", prev="이전", next="다음", edit="이 페이지 고치기", support="지원", privacy="개인정보 처리방침", other="English", otherlang="en",
               get="무료 다운로드", home="제품 소개", updated="2026년 11월 26일 고침", for_="Branchlane 2.3", hint="도구, 설정, 궁금한 것을 입력하세요.",
               none="찾은 내용이 없습니다.", failed="검색을 불러오지 못했습니다.", skip="본문으로", nav="문서 메뉴", original="블로그 원문", enlarge="크게 보기", output="출력",
               tm="Apple, App Store, Mac은 미국 및 기타 국가와 지역에 등록된 Apple Inc.의 상표입니다."),
}


def text_of(page, lang):
    return page[4] if lang == "en" else page[5]


def path_of(page, lang):
    return ("ko/" if lang == "ko" else "") + page[0] + "/" + (page[1] + "/" if page[1] else "")


# Code

def span(kind, text):
    return f'<span class="{kind}">{text}</span>'


RULES = {
    "json": r'(?P<k>"(?:\\.|[^"\\])*")(?=\s*:)|(?P<s>"(?:\\.|[^"\\])*")|(?P<n>\b-?\d+(?:\.\d+)?\b)|(?P<w>\b(?:true|false|null)\b)',
    "toml": r'(?P<w>^\[[^\]]+\])|(?P<s>"(?:\\.|[^"\\])*")|(?P<k>[A-Za-z_]+)(?=\s*=)|(?P<c>#.*$)',
    "bash": r"(?P<s>\"(?:\\.|[^\"\\])*\"|'[^']*')|(?P<c>(?<!\S)#.*$)|(?P<k>(?<=\s)--?[A-Za-z][\w-]*)|(?P<w>^(?:claude|curl|git|xattr|export|codex|jq|ssh-add|ssh-keygen|ssh-keyscan|ssh|xcode-select|echo|ollama|lms)(?![\w-]))",
}


def highlight(code, lang):
    if lang not in RULES:
        return html.escape(code, quote=False)
    out, at = [], 0
    for match in re.finditer(RULES[lang], code, re.M):
        out.append(html.escape(code[at:match.start()], quote=False))
        out.append(span(match.lastgroup, html.escape(match[0], quote=False)))
        at = match.end()
    return "".join(out) + html.escape(code[at:], quote=False)


def webp_size(path):
    data = path.read_bytes()[:40]
    kind = data[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if kind == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
    if kind == b"VP8 ":
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    raise ValueError(f"Not a WebP image: {path}")


def render(source, lang):
    words = T[lang]
    heads, ids, tabs = [], set(), [0]

    def code(match):
        attributes, body = match[1], html.unescape(match[2])
        name = re.search(r'data-file="([^"]+)"', attributes)
        language = re.search(r'data-lang="([^"]+)"', attributes)
        language = language[1] if language else "text"
        label = name[1] if name else {"bash": "Terminal" if lang == "en" else "터미널", "json": "JSON", "toml": "TOML", "output": words["output"]}.get(language, "")
        return (f'<div class="code"><div class="code-head"><span>{label}</span><button class="copy" type="button">{words["copy"]}</button></div>'
                f'<pre tabindex="0"><code>{highlight(body, language)}</code></pre></div>')

    def shot(match):
        """<shot src="docs/lines" alt="..." pins="x,y x,y" narrow>caption</shot>, a screenshot in screenshots/<lang>/."""
        attributes, caption = match[1], match[2].strip()
        src = re.search(r'src="([^"]+)"', attributes)[1]
        alt = re.search(r'alt="([^"]*)"', attributes)[1]
        pins = re.search(r'pins="([^"]+)"', attributes)
        file = f"screenshots/{lang}/{src}.webp"
        width, height = webp_size(ROOT / file)
        marks = "".join(f'<span class="pin" style="left:{x}%;top:{y}%" aria-hidden="true">{i}</span>'
                        for i, (x, y) in enumerate((pair.split(",") for pair in pins[1].split()), 1)) if pins else ""
        size = " narrow" if re.search(r"\bnarrow\b", attributes) else ""
        return (f'<figure class="shot{size}"><div class="frame"><img src="{{root}}{file}" width="{width}" height="{height}" alt="{alt}" loading="lazy" decoding="async">{marks}'
                f'<button class="zoom" type="button" aria-label="{words["enlarge"]}: {alt}"></button></div>'
                + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")

    def tabset(match):
        tabs[0] += 1
        items = re.findall(r'<tab name="([^"]+)">(.*?)</tab>', match[1], re.S)
        buttons = "".join(f'<button type="button" role="tab" id="t{tabs[0]}-{i}" aria-controls="p{tabs[0]}-{i}" data-tab="{html.escape(name)}" aria-selected="{"true" if i == 0 else "false"}">{name}</button>' for i, (name, _) in enumerate(items))
        panels = "".join(f'<div class="panel" role="tabpanel" id="p{tabs[0]}-{i}" aria-labelledby="t{tabs[0]}-{i}"{"" if i == 0 else " hidden"}>{body.strip()}</div>' for i, (_, body) in enumerate(items))
        return f'<div class="tabs"><div class="tablist" role="tablist">{buttons}</div>{panels}</div>'

    def heading(match):
        level, attributes, body = match[1], match[2], match[3]
        given = re.search(r'id="([^"]+)"', attributes)
        plain = html.unescape(re.sub(r'<span class="badge.*?</span>|<[^>]+>', "", body)).strip()
        slug = given[1] if given else re.sub(r"[^\w가-힣]+", "-", plain.lower()).strip("-")
        base, n = slug, 2
        while slug in ids:
            slug, n = f"{base}-{n}", n + 1
        ids.add(slug)
        heads.append((int(level), slug, plain))
        rest = re.sub(r'\s*id="[^"]+"', "", attributes)
        return f'<h{level} id="{slug}"{rest}>{body}<a class="anchor" href="#{slug}" aria-label="#{html.escape(plain)}">#</a></h{level}>'

    body = re.sub(r"<pre([^>]*)><code>(.*?)</code></pre>", code, source, flags=re.S)
    body = re.sub(r"<tabs>(.*?)</tabs>", tabset, body, flags=re.S)
    body = re.sub(r"<shot([^>]*)>(.*?)</shot>", shot, body, flags=re.S)
    body = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", heading, body, flags=re.S)
    return body, heads


def plain(fragment):
    fragment = re.sub(r'<div class="code-head">.*?</div>|<a class="anchor".*?</a>|<svg.*?</svg>|<span class="pin".*?</span>', "", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def sections(body, heads):
    """The text under each heading, for search."""
    marks = [(match.start(), match[1]) for match in re.finditer(r'<h[23] id="([^"]+)"', body)]
    yield "", plain(body[:marks[0][0]] if marks else body)
    for i, (start, slug) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        yield slug, plain(re.sub(r"^<h[23].*?</h[23]>", "", body[start:end], flags=re.S))


SEARCH = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="4.6"/><path d="m10.6 10.6 3.4 3.4"/></svg>'
SUN = '<svg class="sun" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="3.4"/><path d="M10 2.2v1.6M10 16.2v1.6M2.2 10h1.6M16.2 10h1.6M4.5 4.5l1.1 1.1M14.4 14.4l1.1 1.1M4.5 15.5l1.1-1.1M14.4 5.6l1.1-1.1"/></svg>'
MOON = '<svg class="moon" viewBox="0 0 20 20" aria-hidden="true"><path d="M16.6 12.1A7 7 0 0 1 7.9 3.4a7 7 0 1 0 8.7 8.7Z"/></svg>'
BURGER = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 6h14M3 10h14M3 14h14"/></svg>'


def build(lang):
    words, at = T[lang], 0 if lang == "en" else 1
    pages = [page for page in PAGES if text_of(page, lang)]
    outputs, index = {}, []
    for page in pages:
        area, folder, source, _, *_ = page
        title, summary = text_of(page, lang)
        path = path_of(page, lang)
        up = "../" * path.count("/")
        file = ROOT / "_docs" / lang / f"{source}.html"
        body, heads = render(file.read_text(), lang)
        body = body.replace("{root}", up).replace("{base}", up + ("ko/" if lang == "ko" else ""))
        other = "ko" if lang == "en" else "en"
        has_other = bool(text_of(page, other))
        other_path = path_of(page, other) if has_other else path_of(next(p for p in PAGES if p[0] == "developers"), other)
        key = f"{area}/{folder}"
        date, canonical = META.get(key, (words["updated"], SITE + path))

        mine = [p for p in pages if p[0] == area]
        groups = []
        for item in mine:
            if not groups or groups[-1][0] != item[3]:
                groups.append((item[3], []))
            groups[-1][1].append(item)
        nav = "".join(
            f'<div class="group"><p>{G[name][at]}</p><ul>' + "".join(
                f'<li><a href="{up}{path_of(p, lang)}"{" aria-current=" + chr(34) + "page" + chr(34) if p is page else ""}>{html.escape(text_of(p, lang)[0])}</a></li>' for p in items
            ) + "</ul></div>" for name, items in groups)
        areas = "".join(
            f'<a href="{up}{"ko/" if lang == "ko" else ""}{name}/"{" aria-current=" + chr(34) + "true" + chr(34) if name == area else ""}>{labels[at]}</a>'
            for name, labels in AREAS.items() if labels[at])
        outline = "".join(f'<li{" class=" + chr(34) + "sub" + chr(34) if level == 3 else ""}><a href="#{slug}">{html.escape(text)}</a></li>' for level, slug, text in heads)
        i = mine.index(page)
        before, after = mine[i - 1] if i else None, mine[i + 1] if i + 1 < len(mine) else None
        around = ""
        if before:
            around += f'<a class="back" href="{up}{path_of(before, lang)}"><small>{words["prev"]}</small><b>{html.escape(text_of(before, lang)[0])}</b></a>'
        if after:
            around += f'<a class="fwd" href="{up}{path_of(after, lang)}"><small>{words["next"]}</small><b>{html.escape(text_of(after, lang)[0])}</b></a>'
        moved = ""
        if not folder and area in MOVED:
            # Not a heading that this page itself still has.
            targets = {k: v for k, v in MOVED[area].items() if v}
            moved = f"<script>window.docsMoved={json.dumps(targets)}</script>\n"
        alternate = ""
        if has_other:
            alternate = "".join(f'<link rel="alternate" hreflang="{code}" href="{SITE}{path_of(page, l)}">\n' for code, l in (("en", "en"), ("ko", "ko"), ("x-default", "en")))
        source_note = f'<a href="{canonical}">{words["original"]}</a>' if key in META else f'<span>{words["for_"]}</span>'
        full_title = f"{title} - Branchlane {words['docs']}"
        outputs[path + "index.html"] = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(summary)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(summary)}">
<meta property="og:image" content="{SITE}screenshots/branchlane-graph.png">
<meta property="og:url" content="{SITE}{path}">
<link rel="canonical" href="{canonical}">
{alternate}<link rel="icon" href="{up}assets/app-icon.png">
<link rel="stylesheet" href="{up}assets/docs.css?v={VERSION}">
<script>try{{var t=localStorage.getItem('docs-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body data-base="{up}" data-area="{"ko/" if lang == "ko" else ""}{area}/" data-index="{up}assets/docs-{lang}.json?v={VERSION}" data-copy="{words['copy']}" data-copied="{words['copied']}" data-selected="{words['selected']}" data-hint="{words['hint']}" data-none="{words['none']}" data-failed="{words['failed']}" data-enlarge="{words['enlarge']}">
<a class="skip" href="#main">{words['skip']}</a>
<header class="bar"><div class="bar-in">
<button class="icon burger" type="button" aria-label="{words['menu']}" aria-expanded="false" aria-controls="side">{BURGER}</button>
<a class="brand" href="{up}{'ko/' if lang == 'ko' else ''}"><img src="{up}assets/app-icon.png" width="26" height="26" alt=""><span>Branchlane</span></a>
<nav class="areas" aria-label="{words['docs']}">{areas}</nav>
<div class="bar-end">
<button class="find" type="button" aria-label="{words['search']}">{SEARCH}<span>{words['search']}</span><kbd>⌘K</kbd></button>
<button class="icon theme" type="button" aria-label="{words['theme']}">{SUN}{MOON}</button>
<a class="text-link" href="{up}{other_path}" lang="{words['otherlang']}">{words['other']}</a>
<a class="get" href="{STORE}">{words['get']}</a>
</div></div></header>
<div class="scrim"></div>
<div class="shell">
<nav class="side" id="side" aria-label="{words['nav']}"><div class="side-areas">{areas}</div>{nav}</nav>
<main id="main"><article class="page">
<p class="crumb"><a href="{up}{'ko/' if lang == 'ko' else ''}{area}/">{AREAS[area][at]}</a><span aria-hidden="true">/</span><span>{G[page[3]][at]}</span></p>
<h1>{html.escape(title)}</h1>
<p class="lede">{html.escape(summary)}</p>
<div class="meta"><span>{date}</span>{source_note}</div>
<div class="text">
{body.strip()}
</div>
<nav class="next" aria-label="{words['prev']}, {words['next']}">{around}</nav>
<footer class="foot"><a href="{REPO}/edit/main/_docs/{lang}/{source}.html">{words['edit']}</a><a href="{REPO}/issues">{words['support']}</a><a href="{up}privacy/">{words['privacy']}</a><a href="{up}{'ko/' if lang == 'ko' else ''}">{words['home']}</a><p>{words['tm']}</p></footer>
</article></main>
{f'<aside class="outline"><p>{words["outline"]}</p><ul>{outline}</ul></aside>' if len(heads) > 1 else '<div></div>'}
</div>
<dialog aria-label="{words['search']}"><input type="search" placeholder="{words['search']}" aria-label="{words['search']}" autocomplete="off" spellcheck="false"><ul class="hits"><li class="none">{words['hint']}</li></ul></dialog>
{moved}<script src="{up}assets/docs.js?v={VERSION}"></script>
</body>
</html>
"""
        names = {slug: text for _, slug, text in heads}
        for slug, content in sections(body, heads):
            index.append({"u": path + (f"#{slug}" if slug else ""), "p": title, "h": names.get(slug, title), "t": (summary + " " + content if not slug else content)[:1200]})
    outputs[f"assets/docs-{lang}.json"] = json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n"
    return outputs


def sitemap():
    entries = [("", "ko/"), ("pricing/", "ko/pricing/"), ("privacy/", None), ("terms/", None)]
    entries += [(path_of(p, "en"), path_of(p, "ko")) if text_of(p, "en") else (path_of(p, "ko"), None) for p in PAGES if f"{p[0]}/{p[1]}" not in META]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for en, ko in entries:
        for loc in filter(lambda value: value is not None, (en, ko)):
            out.append(f"  <url>\n    <loc>{SITE}{loc}</loc>")
            if ko is not None:
                out += [f'    <xhtml:link rel="alternate" hreflang="{code}" href="{SITE}{target}"/>' for code, target in (("en", en), ("ko", ko), ("x-default", en))]
            out.append("  </url>")
    return "\n".join(out + ["</urlset>"]) + "\n"


def broken(outputs):
    ids = {path: set(re.findall(r'\bid="([^"]+)"', text)) for path, text in outputs.items() if path.endswith(".html")}
    problems = []
    for path, text in outputs.items():
        if not path.endswith(".html"):
            continue
        for link in re.findall(r'(?:href|src)="([^"]+)"', text):
            if re.match(r"[a-z]+:", link):
                continue
            target, _, fragment = html.unescape(link).partition("#")
            target = target.split("?")[0]
            full = (ROOT / path).parent / target if target else ROOT / path
            full = full.resolve()
            if target.endswith("/") or full.is_dir():
                full = full / "index.html"
            name = str(full.relative_to(ROOT))
            if name not in outputs and not full.exists():
                problems.append(f"{path}: {link}")
            elif fragment and fragment not in ids.get(name, {fragment}):
                problems.append(f"{path}: {link}")
    return problems


def main():
    outputs = {**build("en"), **build("ko"), "sitemap.xml": sitemap()}
    problems = broken(outputs)
    if "--check" in sys.argv:
        problems += [f"out of date: {p}" for p, text in outputs.items() if not (ROOT / p).exists() or (ROOT / p).read_text() != text]
    else:
        for path, text in outputs.items():
            file = ROOT / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text)
    print("\n".join(problems) or f"{len(outputs)} files")
    return 1 if problems else 0


sys.exit(main())
