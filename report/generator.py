"""
Comm Radar — HTML 리포트 생성기
매주 자동 생성되는 커뮤니케이션 인텔리전스 리포트
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
    """전체 HTML 리포트 생성"""

    now = datetime.now()
    date_str = now.strftime("%Y년 %m월 %d일")
    week_str = now.strftime("%Y-W%W")

    # ── 섹션별 HTML 생성 ──
    hero_html = _build_hero(weekly_summary, date_str, issue_number)
    news_html = _build_news_section(news_insights)
    hn_html = _build_hn_section(hn_insights)
    steam_html = _build_steam_section(steam_analysis, steam_trending)
    reddit_html = _build_reddit_section(reddit_insights) if reddit_insights else ""

    # ── 통계 ──
    stats = {
        "뉴스": len(news_insights),
        "테크 담론": len(hn_insights),
        "게임 트렌드": len(steam_trending),
        "커뮤니티": len(reddit_insights) if reddit_insights else 0,
    }

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comm Radar #{issue_number:03d} — {date_str}</title>
{_css()}
</head>
<body>
<div class="container">
{hero_html}
{_build_stats_bar(stats)}

<nav class="tab-nav">
  <button class="tab-btn active" data-tab="news">📰 뉴스 인사이트</button>
  <button class="tab-btn" data-tab="tech">🔶 테크 담론</button>
  <button class="tab-btn" data-tab="steam">🎮 게임 트렌드</button>
  {"<button class='tab-btn' data-tab='community'>💬 커뮤니티</button>" if reddit_insights else ""}
</nav>

<div class="tab-content active" id="tab-news">{news_html}</div>
<div class="tab-content" id="tab-tech">{hn_html}</div>
<div class="tab-content" id="tab-steam">{steam_html}</div>
{"<div class='tab-content' id='tab-community'>" + reddit_html + "</div>" if reddit_insights else ""}

<footer class="footer">
  <p>Comm Radar #{issue_number:03d} · {date_str} · Bagelcode Communication Intelligence OS</p>
  <p class="footer-sub">Powered by Claude API · 자동 생성 리포트</p>
</footer>
</div>
{_js()}
</body>
</html>"""


def _build_hero(summary: str, date_str: str, issue_number: int) -> str:
    lines = summary.strip().split("\n") if summary else ["📊 이번 주 리포트를 확인하세요."]
    items_html = "\n".join(f'<div class="hero-item">{line.strip()}</div>' for line in lines if line.strip())
    return f"""
<header class="hero">
  <div class="hero-badge">ISSUE #{issue_number:03d}</div>
  <h1 class="hero-title">📡 Comm Radar</h1>
  <p class="hero-subtitle">Weekly Communication Intelligence · {date_str}</p>
  <div class="hero-summary">{items_html}</div>
</header>"""


def _build_stats_bar(stats: dict) -> str:
    items = "".join(
        f'<div class="stat"><span class="stat-num">{v}</span><span class="stat-label">{k}</span></div>'
        for k, v in stats.items() if v > 0
    )
    return f'<div class="stats-bar">{items}</div>'


def _build_news_section(insights: list[dict]) -> str:
    if not insights:
        return '<div class="empty">뉴스 데이터가 없습니다.</div>'

    cards = []
    for item in insights:
        rel_class = item.get("relevance", "medium")
        type_badge = item.get("type", "참고")
        type_colors = {
            "PR기회": "#10b981", "경쟁동향": "#f59e0b",
            "시장트렌드": "#3b82f6", "리스크": "#ef4444", "참고": "#6b7280",
            "실리콘밸리": "#6366f1", "글로벌게임사": "#f59e0b",
            "국내IT": "#10b981", "에이전트문화": "#f43f5e",
        }
        color = type_colors.get(type_badge, "#6b7280")
        url = item.get("url", "")
        source_html = f'<a href="{url}" target="_blank" rel="noopener" style="color:#6b7280;text-decoration:none;border-bottom:1px dotted #999">{item.get("title", "")}</a>' if url else item.get("title", "")
        cards.append(f"""
<div class="card card-{rel_class}">
  <div class="card-header">
    <span class="badge" style="background:{color}">{type_badge}</span>
    <span class="relevance-dot rel-{rel_class}"></span>
  </div>
  <h3 class="card-title">{source_html}</h3>
  <p class="card-insight">{item.get('insight', '')}</p>
  <div class="card-action">→ {item.get('action', '')}</div>
</div>""")
    return f'<div class="card-grid">{"".join(cards)}</div>'


def _build_hn_section(insights: list[dict]) -> str:
    if not insights:
        return '<div class="empty">Hacker News 데이터가 없습니다.</div>'

    rows = []
    for item in insights:
        buzz = item.get("buzz_level", "💡")
        url = item.get("url", "")
        title_html = f'<a href="{url}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted #555">{item.get("title", "")}</a>' if url else item.get("title", "")
        rows.append(f"""
<div class="hn-item">
  <span class="hn-buzz">{buzz}</span>
  <div class="hn-content">
    <div class="hn-title">{title_html}</div>
    <div class="hn-summary">{item.get('summary', '')}</div>
    <div class="hn-insight">{item.get('insight', '')}</div>
  </div>
</div>""")
    return f'<div class="hn-list">{"".join(rows)}</div>'


def _build_steam_section(analysis: dict, trending: list[dict]) -> str:
    parts = []

    if isinstance(analysis, dict) and analysis.get("trend_summary"):
        genres = ", ".join(analysis.get("hot_genres", []))
        parts.append(f"""
<div class="steam-summary">
  <h3>🔥 이번 주 게임 트렌드</h3>
  <p>{analysis['trend_summary']}</p>
  <div class="hot-genres">주목 장르: <strong>{genres}</strong></div>
</div>""")

    if trending:
        rows = []
        for i, g in enumerate(trending, 1):
            top_tags = ", ".join(list(g.get("tags", {}).keys())[:3])
            rows.append(f"""
<tr>
  <td class="rank">{i}</td>
  <td class="game-name">{g['name']}</td>
  <td>{g['bayesian_rate']}%</td>
  <td>{g['owners_mid']:,}</td>
  <td class="tags">{top_tags}</td>
  <td class="score">{g['trending_score']}</td>
</tr>""")
        parts.append(f"""
<div class="steam-table-wrap">
  <table class="steam-table">
    <thead><tr>
      <th>#</th><th>게임</th><th>긍정률</th><th>소유자</th><th>태그</th><th>점수</th>
    </tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</div>""")

    # AI 분석 게임별 인사이트
    if isinstance(analysis, dict) and analysis.get("games"):
        game_cards = []
        for g in analysis["games"]:
            game_cards.append(f"""
<div class="game-card">
  <strong>{g.get('name', '')}</strong>
  <p>{g.get('one_liner', '')}</p>
  <div class="why-notable">📌 {g.get('why_notable', '')}</div>
</div>""")
        parts.append(f'<div class="game-grid">{"".join(game_cards)}</div>')

    return "".join(parts) if parts else '<div class="empty">Steam 데이터가 없습니다.</div>'


def _build_reddit_section(insights: list[dict]) -> str:
    if not insights:
        return '<div class="empty">Reddit 데이터가 없습니다.</div>'

    cards = []
    for item in insights:
        cards.append(f"""
<div class="reddit-card">
  <div class="reddit-sub">r/{item.get('subreddit', '')}</div>
  <h4>{item.get('title', '')}</h4>
  <p class="reddit-summary">{item.get('summary', '')}</p>
  <div class="reddit-insight">{item.get('insight', '')}</div>
</div>""")
    return f'<div class="reddit-grid">{"".join(cards)}</div>'


def _css() -> str:
    return """<style>
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #242836;
  --border: #2d3248;
  --text: #e4e7ef;
  --text-dim: #8b90a5;
  --accent: #6366f1;
  --accent2: #818cf8;
  --green: #10b981;
  --amber: #f59e0b;
  --red: #ef4444;
  --blue: #3b82f6;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: 'Pretendard', -apple-system, system-ui, sans-serif; line-height: 1.6; }
.container { max-width: 960px; margin: 0 auto; padding: 24px 16px; }

/* Hero */
.hero { text-align: center; padding: 48px 24px 32px; margin-bottom: 24px;
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(16,185,129,0.1));
  border-radius: 16px; border: 1px solid var(--border); }
.hero-badge { display: inline-block; background: var(--accent); color: #fff; font-size: 11px; font-weight: 700;
  padding: 4px 12px; border-radius: 99px; letter-spacing: 1px; margin-bottom: 12px; }
.hero-title { font-size: 32px; font-weight: 800; margin-bottom: 4px; }
.hero-subtitle { color: var(--text-dim); font-size: 14px; margin-bottom: 20px; }
.hero-summary { text-align: left; max-width: 640px; margin: 0 auto; }
.hero-item { padding: 8px 0; font-size: 15px; border-bottom: 1px solid var(--border); }
.hero-item:last-child { border: none; }

/* Stats */
.stats-bar { display: flex; gap: 12px; margin-bottom: 24px; }
.stat { flex: 1; background: var(--surface); border-radius: 12px; padding: 16px; text-align: center;
  border: 1px solid var(--border); }
.stat-num { display: block; font-size: 28px; font-weight: 800; color: var(--accent2); }
.stat-label { font-size: 12px; color: var(--text-dim); }

/* Tabs */
.tab-nav { display: flex; gap: 4px; margin-bottom: 20px; background: var(--surface); border-radius: 12px;
  padding: 4px; border: 1px solid var(--border); overflow-x: auto; }
.tab-btn { flex: 1; padding: 10px 16px; background: none; border: none; color: var(--text-dim);
  font-size: 13px; font-weight: 600; cursor: pointer; border-radius: 8px; transition: all .2s;
  white-space: nowrap; }
.tab-btn.active { background: var(--accent); color: #fff; }
.tab-content { display: none; }
.tab-content.active { display: block; }

/* News Cards */
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.card { background: var(--surface); border-radius: 12px; padding: 20px;
  border: 1px solid var(--border); transition: transform .2s; }
.card:hover { transform: translateY(-2px); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.badge { color: #fff; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; }
.relevance-dot { width: 8px; height: 8px; border-radius: 50%; }
.rel-high { background: var(--green); }
.rel-medium { background: var(--amber); }
.rel-low { background: var(--text-dim); }
.card-title { font-size: 15px; font-weight: 700; margin-bottom: 8px; line-height: 1.4; }
.card-insight { font-size: 13px; color: var(--text-dim); margin-bottom: 10px; }
.card-action { font-size: 12px; color: var(--accent2); font-weight: 600; }

/* HN */
.hn-list { display: flex; flex-direction: column; gap: 12px; }
.hn-item { display: flex; gap: 14px; background: var(--surface); border-radius: 12px; padding: 16px;
  border: 1px solid var(--border); }
.hn-buzz { font-size: 24px; flex-shrink: 0; }
.hn-title { font-weight: 700; font-size: 14px; margin-bottom: 4px; }
.hn-summary { font-size: 13px; color: var(--text-dim); margin-bottom: 4px; }
.hn-insight { font-size: 12px; color: var(--accent2); }

/* Steam */
.steam-summary { background: var(--surface); border-radius: 12px; padding: 20px; margin-bottom: 16px;
  border: 1px solid var(--border); }
.steam-summary h3 { margin-bottom: 8px; }
.hot-genres { margin-top: 10px; font-size: 13px; color: var(--amber); }
.steam-table-wrap { overflow-x: auto; margin-bottom: 16px; }
.steam-table { width: 100%; border-collapse: collapse; background: var(--surface);
  border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
.steam-table th { background: var(--surface2); padding: 10px 14px; font-size: 12px;
  color: var(--text-dim); text-align: left; font-weight: 600; }
.steam-table td { padding: 10px 14px; font-size: 13px; border-top: 1px solid var(--border); }
.steam-table .rank { font-weight: 800; color: var(--accent2); }
.steam-table .game-name { font-weight: 600; }
.steam-table .tags { color: var(--text-dim); font-size: 12px; }
.steam-table .score { font-weight: 700; color: var(--green); }
.game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.game-card { background: var(--surface); border-radius: 10px; padding: 16px;
  border: 1px solid var(--border); }
.game-card strong { font-size: 14px; }
.game-card p { font-size: 12px; color: var(--text-dim); margin: 4px 0; }
.why-notable { font-size: 11px; color: var(--amber); }

/* Reddit */
.reddit-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.reddit-card { background: var(--surface); border-radius: 12px; padding: 18px;
  border: 1px solid var(--border); }
.reddit-sub { font-size: 11px; color: var(--accent2); font-weight: 700; margin-bottom: 6px; }
.reddit-card h4 { font-size: 14px; margin-bottom: 6px; }
.reddit-summary { font-size: 13px; color: var(--text-dim); margin-bottom: 6px; }
.reddit-insight { font-size: 12px; color: var(--green); }

/* Footer */
.footer { text-align: center; padding: 32px 0 16px; color: var(--text-dim); font-size: 12px; }
.footer-sub { margin-top: 4px; opacity: 0.6; }
.empty { text-align: center; padding: 40px; color: var(--text-dim); }

@media (max-width: 640px) {
  .stats-bar { flex-wrap: wrap; }
  .stat { min-width: calc(50% - 8px); }
  .card-grid, .game-grid, .reddit-grid { grid-template-columns: 1fr; }
  .hero-title { font-size: 24px; }
}
</style>"""


def _js() -> str:
    return """<script>
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});
</script>"""
