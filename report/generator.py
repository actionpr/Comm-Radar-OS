"""
Comm Radar v2 — Editorial Report Generator
4-Desk newspaper layout: Market / Indie / Contents / Culture
Light theme, serif typography, no emoji
"""

from datetime import datetime


def generate_report(
    weekly_summary: str,
    news_insights: list[dict],
    hn_insights: list[dict],
    steam_analysis: dict,
    steam_trending: list[dict],
    reddit_insights: list[dict] = None,
    issue_number: int = 1,
) -> str:
    """Generate the full HTML editorial report."""

    now = datetime.now()
    date_str = now.strftime("%Y.%m.%d")
    date_full = now.strftime("%Y년 %m월 %d일")
    day_names = ["월", "화", "수", "목", "금", "토", "일"]
    day_str = day_names[now.weekday()]

    # Split news into main desk vs gossip sidebar
    market_items = [n for n in news_insights if n.get("type") != "참고"]
    gossip_items = [n for n in news_insights if n.get("type") == "참고"]
    if not gossip_items:
        gossip_items = [n for n in news_insights if n.get("relevance") == "low"]
        market_items = [n for n in news_insights if n.get("relevance") != "low"]

    # Build sections
    masthead = _build_masthead(date_str, day_str, issue_number)
    lede = _build_lede(weekly_summary, date_full)
    market_html = _build_market_desk(market_items)
    indie_html = _build_indie_desk(steam_analysis, steam_trending)
    contents_html = _build_contents_desk(hn_insights)
    culture_html = _build_culture_desk(reddit_insights)
    gossip_html = _build_gossip_sidebar(gossip_items)
    footer_html = _build_footer(issue_number, date_full)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comm Radar #{issue_number:03d} — {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Serif+KR:wght@400;700;900&display=swap" rel="stylesheet">
{_css()}
</head>
<body>
<div class="page">

{masthead}
{lede}

<div class="content-grid">
  <main class="desks">
    {market_html}
    {indie_html}
    {contents_html}
    {culture_html}
  </main>
  <aside class="sidebar">
    {gossip_html}
  </aside>
</div>

{footer_html}

</div>
</body>
</html>"""


# ── Masthead ──

def _build_masthead(date_str: str, day_str: str, issue_number: int) -> str:
    return f"""
<header class="masthead">
  <div class="masthead-rule"></div>
  <div class="masthead-meta">{date_str} {day_str}요일</div>
  <h1 class="masthead-title">COMM RADAR</h1>
  <div class="masthead-sub">Bagelcode Communication Intelligence</div>
  <div class="masthead-issue">No. {issue_number:03d}</div>
  <div class="masthead-rule"></div>
</header>"""


# ── Lede / Summary ──

def _build_lede(summary: str, date_full: str) -> str:
    if not summary:
        return ""
    lines = [l.strip() for l in summary.strip().split("\n") if l.strip()]
    # Strip leading emoji from each line
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        # Remove leading emoji characters
        while stripped and (not stripped[0].isalpha() and not stripped[0].isdigit()
                           and stripped[0] not in "([\"'"):
            if ord(stripped[0]) > 127:
                stripped = stripped[1:].lstrip()
            else:
                break
        cleaned.append(stripped if stripped else line)
    items_html = "".join(f'<li>{c}</li>' for c in cleaned if c)
    return f"""
<section class="lede">
  <div class="lede-label">Weekly Briefing</div>
  <ul class="lede-list">{items_html}</ul>
</section>"""


# ── Market Desk ──

def _build_market_desk(items: list[dict]) -> str:
    if not items:
        return _empty_desk("Market", "수집된 시장 뉴스가 없습니다.")

    cards = []
    for item in items:
        rel = item.get("relevance", "medium")
        type_tag = item.get("type", "")
        url = item.get("url", "")
        title = item.get("title", "")
        title_html = (
            f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
            if url else title
        )
        cards.append(f"""
    <article class="desk-article">
      <div class="article-meta">
        <span class="article-tag tag-{rel}">{type_tag}</span>
      </div>
      <h3 class="article-title">{title_html}</h3>
      <p class="article-body">{item.get('insight', '')}</p>
      <p class="article-action">{item.get('action', '')}</p>
    </article>""")

    return _desk_wrapper("Market", "시장 · 경쟁 · PR", "".join(cards))


# ── Indie Desk (Steam) ──

def _build_indie_desk(analysis: dict, trending: list[dict]) -> str:
    parts = []

    if isinstance(analysis, dict) and analysis.get("trend_summary"):
        genres = ", ".join(analysis.get("hot_genres", []))
        parts.append(f"""
    <div class="indie-summary">
      <p>{analysis['trend_summary']}</p>
      <p class="genre-line">Trending Genres &mdash; <strong>{genres}</strong></p>
    </div>""")

    if trending:
        rows = []
        for i, g in enumerate(trending, 1):
            top_tags = ", ".join(list(g.get("tags", {}).keys())[:3])
            rows.append(f"""
      <tr>
        <td class="col-rank">{i}</td>
        <td class="col-name">{g['name']}</td>
        <td>{g['bayesian_rate']}%</td>
        <td>{g['owners_mid']:,}</td>
        <td class="col-tags">{top_tags}</td>
        <td class="col-score">{g['trending_score']}</td>
      </tr>""")
        parts.append(f"""
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr>
          <th>#</th><th>Title</th><th>Positive</th><th>Owners</th><th>Tags</th><th>Score</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>""")

    if isinstance(analysis, dict) and analysis.get("games"):
        game_items = []
        for g in analysis["games"]:
            game_items.append(f"""
      <div class="game-brief">
        <strong>{g.get('name', '')}</strong>
        <span class="game-liner">{g.get('one_liner', '')}</span>
        <span class="game-note">{g.get('why_notable', '')}</span>
      </div>""")
        parts.append(f'<div class="game-briefs">{"".join(game_items)}</div>')

    body = "".join(parts) if parts else '<p class="empty-note">Steam 데이터가 없습니다.</p>'
    return _desk_wrapper("Indie", "인디 게임 · 트렌드", body)


# ── Contents Desk (Hacker News) ──

def _build_contents_desk(items: list[dict]) -> str:
    if not items:
        return _empty_desk("Contents", "Hacker News 데이터가 없습니다.")

    rows = []
    for item in items:
        url = item.get("url", "")
        title = item.get("title", "")
        title_html = (
            f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
            if url else title
        )
        rows.append(f"""
    <article class="hn-row">
      <div class="hn-title">{title_html}</div>
      <p class="hn-summary">{item.get('summary', '')}</p>
      <p class="hn-insight">{item.get('insight', '')}</p>
    </article>""")

    return _desk_wrapper("Contents", "테크 담론 · 개발자 커뮤니티", "".join(rows))


# ── Culture Desk (Reddit) ──

def _build_culture_desk(items: list[dict]) -> str:
    if not items:
        return _empty_desk("Culture", "커뮤니티 데이터가 없습니다.")

    rows = []
    for item in items:
        rows.append(f"""
    <article class="culture-row">
      <span class="culture-sub">r/{item.get('subreddit', '')}</span>
      <h4>{item.get('title', '')}</h4>
      <p class="culture-summary">{item.get('summary', '')}</p>
      <p class="culture-insight">{item.get('insight', '')}</p>
    </article>""")

    return _desk_wrapper("Culture", "유저 · 커뮤니티 · 여론", "".join(rows))


# ── Gossip Sidebar ──

def _build_gossip_sidebar(items: list[dict]) -> str:
    if not items:
        return """
<div class="gossip">
  <div class="gossip-header">Gossip</div>
  <p class="gossip-empty">이번 호에는 가십이 없습니다.</p>
</div>"""

    entries = []
    for item in items:
        url = item.get("url", "")
        title = item.get("title", "")
        title_html = (
            f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
            if url else title
        )
        entries.append(f"""
    <div class="gossip-item">
      <div class="gossip-title">{title_html}</div>
      <p class="gossip-note">{item.get('insight', '')}</p>
    </div>""")

    return f"""
<div class="gossip">
  <div class="gossip-header">Gossip</div>
  {"".join(entries)}
</div>"""


# ── Footer ──

def _build_footer(issue_number: int, date_full: str) -> str:
    return f"""
<footer class="editorial-footer">
  <div class="selection-note">
    <div class="note-label">Selection Note</div>
    <p>
      본 리포트는 Comm Radar OS가 Google News, Hacker News, Steam, Reddit에서
      자동 수집한 데이터를 Claude API로 분석하여 생성합니다.
      베이글코드 커뮤니케이션 전략에 유의미한 시그널을 우선 선별하며,
      각 기사의 원문은 제목 링크를 통해 확인할 수 있습니다.
    </p>
  </div>
  <div class="footer-bar">
    <span>Comm Radar No.{issue_number:03d} / {date_full}</span>
    <span class="footer-sep">&middot;</span>
    <a href="https://bagelcode.com" target="_blank" rel="noopener">bagelcode.com</a>
  </div>
</footer>"""


# ── Helpers ──

def _desk_wrapper(name: str, subtitle: str, body: str) -> str:
    slug = name.lower()
    return f"""
<section class="desk desk-{slug}">
  <div class="desk-header desk-header-{slug}">
    <span class="desk-name">{name}</span>
    <span class="desk-sub">{subtitle}</span>
  </div>
  <div class="desk-body">
    {body}
  </div>
</section>"""


def _empty_desk(name: str, message: str) -> str:
    return _desk_wrapper(name, "", f'<p class="empty-note">{message}</p>')


# ── CSS ──

def _css() -> str:
    return """<style>
:root {
  --bg: #FDFBF7;
  --surface: #FFFFFF;
  --border: #D4C5B0;
  --border-light: #E8E0D4;
  --text: #2B2B2B;
  --text-dim: #6B6B6B;
  --text-muted: #999;
  --navy: #1B2A4A;
  --gold: #8B6914;
  --gold-light: #C4A24E;
  --desk-market: #1B2A4A;
  --desk-indie: #4A6741;
  --desk-contents: #6B4226;
  --desk-culture: #5A3E6B;
  --tag-high: #1B2A4A;
  --tag-medium: #8B6914;
  --tag-low: #999;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Lora', 'Noto Serif KR', Georgia, 'Times New Roman', serif;
  line-height: 1.75;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

a {
  color: var(--navy);
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  transition: border-color 0.2s;
}
a:hover { border-color: var(--navy); }

.page {
  max-width: 980px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* ── Masthead ── */
.masthead {
  text-align: center;
  margin-bottom: 32px;
}
.masthead-rule {
  height: 2px;
  background: var(--text);
  margin: 8px 0;
}
.masthead-rule:first-child { height: 4px; }
.masthead-meta {
  font-size: 12px;
  letter-spacing: 2px;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-top: 12px;
}
.masthead-title {
  font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
  font-size: 48px;
  font-weight: 900;
  letter-spacing: 6px;
  color: var(--navy);
  margin: 4px 0;
}
.masthead-sub {
  font-size: 13px;
  letter-spacing: 3px;
  color: var(--text-dim);
  text-transform: uppercase;
}
.masthead-issue {
  font-size: 11px;
  letter-spacing: 4px;
  color: var(--gold);
  margin-top: 8px;
  font-weight: 700;
}

/* ── Lede ── */
.lede {
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 20px 0;
  margin-bottom: 28px;
}
.lede-label {
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 700;
  margin-bottom: 10px;
}
.lede-list {
  list-style: none;
  padding: 0;
}
.lede-list li {
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
  font-size: 15px;
  color: var(--text);
}
.lede-list li::before {
  content: '';
  position: absolute;
  left: 0; top: 14px;
  width: 6px; height: 6px;
  background: var(--gold);
  border-radius: 50%;
}

/* ── Content Grid ── */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 32px;
  align-items: start;
}
.desks { min-width: 0; }

/* ── Desk Sections ── */
.desk {
  margin-bottom: 32px;
}
.desk-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 8px 14px;
  margin-bottom: 16px;
  border-left: 4px solid;
}
.desk-header-market { border-color: var(--desk-market); background: rgba(27,42,74,0.04); }
.desk-header-indie { border-color: var(--desk-indie); background: rgba(74,103,65,0.04); }
.desk-header-contents { border-color: var(--desk-contents); background: rgba(107,66,38,0.04); }
.desk-header-culture { border-color: var(--desk-culture); background: rgba(90,62,107,0.04); }

.desk-name {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.desk-header-market .desk-name { color: var(--desk-market); }
.desk-header-indie .desk-name { color: var(--desk-indie); }
.desk-header-contents .desk-name { color: var(--desk-contents); }
.desk-header-culture .desk-name { color: var(--desk-culture); }

.desk-sub {
  font-size: 12px;
  color: var(--text-dim);
  letter-spacing: 1px;
}
.desk-body { padding: 0 4px; }

/* ── Market Articles ── */
.desk-article {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-light);
}
.desk-article:last-child { border-bottom: none; }
.article-meta { margin-bottom: 6px; }
.article-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 2px;
}
.tag-high { background: var(--tag-high); color: #fff; }
.tag-medium { background: var(--tag-medium); color: #fff; }
.tag-low { background: var(--tag-low); color: #fff; }
.article-title {
  font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 6px;
}
.article-title a { border-bottom-color: var(--border-light); }
.article-title a:hover { border-bottom-color: var(--navy); }
.article-body {
  font-size: 14px;
  color: var(--text-dim);
  line-height: 1.7;
  margin-bottom: 6px;
}
.article-action {
  font-size: 13px;
  color: var(--gold);
  font-weight: 600;
  font-style: italic;
}

/* ── Indie (Steam) ── */
.indie-summary {
  padding: 14px 0;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 14px;
}
.indie-summary p { font-size: 14px; color: var(--text-dim); }
.genre-line {
  margin-top: 8px;
  font-size: 12px;
  color: var(--desk-indie);
  letter-spacing: 0.5px;
}
.table-wrap { overflow-x: auto; margin-bottom: 16px; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  text-align: left;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-dim);
  padding: 8px 10px;
  border-bottom: 2px solid var(--border);
}
.data-table td {
  padding: 7px 10px;
  border-bottom: 1px solid var(--border-light);
}
.col-rank { font-weight: 700; color: var(--desk-indie); width: 32px; }
.col-name { font-weight: 600; }
.col-tags { color: var(--text-dim); font-size: 12px; }
.col-score { font-weight: 700; color: var(--desk-indie); }

.game-briefs { padding-top: 8px; }
.game-brief {
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}
.game-brief:last-child { border-bottom: none; }
.game-brief strong { display: block; font-size: 14px; margin-bottom: 2px; }
.game-liner { color: var(--text-dim); }
.game-note { display: block; color: var(--gold); font-style: italic; font-size: 12px; margin-top: 2px; }

/* ── Contents (HN) ── */
.hn-row {
  padding: 14px 0;
  border-bottom: 1px solid var(--border-light);
}
.hn-row:last-child { border-bottom: none; }
.hn-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}
.hn-title a { border-bottom-color: var(--border-light); }
.hn-title a:hover { border-bottom-color: var(--desk-contents); }
.hn-summary { font-size: 13px; color: var(--text-dim); margin-bottom: 4px; }
.hn-insight { font-size: 12px; color: var(--desk-contents); font-style: italic; }

/* ── Culture (Reddit) ── */
.culture-row {
  padding: 14px 0;
  border-bottom: 1px solid var(--border-light);
}
.culture-row:last-child { border-bottom: none; }
.culture-sub {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--desk-culture);
  text-transform: uppercase;
}
.culture-row h4 {
  font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
  font-size: 15px;
  font-weight: 700;
  margin: 4px 0;
}
.culture-summary { font-size: 13px; color: var(--text-dim); }
.culture-insight { font-size: 12px; color: var(--desk-culture); font-style: italic; margin-top: 4px; }

/* ── Gossip Sidebar ── */
.sidebar { position: sticky; top: 24px; }
.gossip {
  border: 1px solid var(--border);
  padding: 20px;
}
.gossip-header {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  padding-bottom: 10px;
  border-bottom: 2px solid var(--gold);
  margin-bottom: 14px;
}
.gossip-item {
  padding: 10px 0;
  border-bottom: 1px solid var(--border-light);
}
.gossip-item:last-child { border-bottom: none; }
.gossip-title {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 4px;
}
.gossip-title a { border-bottom-color: var(--border-light); }
.gossip-title a:hover { border-bottom-color: var(--gold); }
.gossip-note { font-size: 12px; color: var(--text-dim); line-height: 1.5; }
.gossip-empty { font-size: 13px; color: var(--text-muted); font-style: italic; }

/* ── Footer ── */
.editorial-footer {
  margin-top: 40px;
  border-top: 2px solid var(--text);
  padding-top: 20px;
}
.selection-note {
  margin-bottom: 20px;
}
.note-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 6px;
}
.selection-note p {
  font-size: 13px;
  color: var(--text-dim);
  line-height: 1.7;
}
.footer-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}
.footer-sep { color: var(--border); }
.footer-bar a {
  color: var(--navy);
  font-weight: 600;
  border-bottom: 1px solid var(--border);
}

.empty-note {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-style: italic;
  font-size: 14px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .sidebar { position: static; }
  .masthead-title { font-size: 32px; letter-spacing: 3px; }
  .desk-name { font-size: 16px; }
}

@media print {
  body { font-size: 12px; }
  .page { max-width: 100%; padding: 0; }
  .content-grid { grid-template-columns: 1fr 220px; }
  a { border-bottom: none; color: var(--text); }
  .sidebar { position: static; }
}
</style>"""
