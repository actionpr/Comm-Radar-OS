"""
Comm Radar — Configuration
커뮤니케이션 인텔리전스 OS 설정값
"""

import os

# ─── Claude API (AIProxy 경유) ───
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # AIProxy 토큰
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "")  # AIProxy 엔드포인트

# ─── Google News RSS 키워드 ───
# 각 카테고리별 검색 키워드 (Google News RSS에서 사용)
NEWS_KEYWORDS = {
    "AI_게임": [
        "AI game development",
        "AI agent gaming",
        "generative AI games",
        "AI NPC",
    ],
    "소셜카지노": [
        "social casino games",
        "social casino market",
        "free-to-play casino",
    ],
    "AI_에이전트": [
        "AI agent workflow",
        "AI agent enterprise",
        "agentic AI",
        "AI automation workplace",
    ],
    "게임산업": [
        "indie game trending",
        "mobile game revenue",
        "game industry layoffs",
        "game studio acquisition",
    ],
}

# ─── Hacker News ───
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_MAX_FETCH = 50  # 상위 50개 중 관련 있는 것만 필터
HN_RELEVANT_KEYWORDS = [
    "ai", "agent", "llm", "claude", "openai", "game", "gaming",
    "automation", "workflow", "startup", "casino", "mobile",
    "anthropic", "generative", "copilot", "chatgpt",
]

# ─── SteamSpy ───
STEAMSPY_API_URL = "https://steamspy.com/api.php"
STEAM_TOP_N = 10  # Trending 표시 개수

# ─── Threads 모니터링 계정 ───
THREADS_ACCOUNTS = [
    "choi.openai",      # AI 기술 최신 소식
]
THREADS_RSS_BASE = "https://threads-rss.com/user/"

# ─── Reddit (GAS 프록시) ───
GAS_REDDIT_URL = os.environ.get("GAS_REDDIT_URL", "")
REDDIT_SUBREDDITS = [
    "gaming",
    "truegaming",
    "gamingsuggestions",
    "artificialintelligence",
    "singularity",
]

# ─── 리포트 ───
REPORT_TITLE = "Comm Radar"
REPORT_SUBTITLE = "Weekly Communication Intelligence Report"
MAX_NEWS_PER_CATEGORY = 5
MAX_HN_ITEMS = 8
MAX_STEAM_TRENDING = 10

# ─── 배포 ───
GAS_WEBHOOK_URL = os.environ.get("GAS_WEBHOOK_URL", "")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "")

# ─── 베이글코드 컨텍스트 (Claude 분석에 사용) ───
BAGELCODE_CONTEXT = """
[회사 개요]
베이글코드(Bagelcode)는 2012년 설립된 글로벌 게임 스타트업으로,
북미 소셜 카지노 시장에서 주력 사업을 운영 중이다.
한국·이스라엘·우크라이나·베트남에 글로벌 거점을 두고 있으며,
싱가포르 법인 Highspire를 통해 사업을 확장하고 있다.

[AI 전환 전략 (AX)]
베이글코드는 AI를 단순 도구가 아닌 '협업 파트너'로 정의한다.
김준영 대표(AI 및 조직문화 총괄)는 "인간의 세계와 AI의 세계가 있고,
계약을 통해 협업한다"는 철학을 가지고 있다.
전사적으로 'Agent-Driven' 조직문화를 추진 중이며,
AI 도전은 기술이 아닌 리더십에서 시작된다는 것이 핵심이다.

[핵심 제품/프로젝트]
- GameBakery.ai: 멀티에이전트 AI 게임 개발 엔진
- 소셜 카지노 게임 포트폴리오 (북미 시장 중심)

[조직 문화 핵심가치]
지적 정직성, 궁극적 오너십, 지수적 실험, 임팩트 증폭

[커뮤니케이션 관점의 핵심 키워드]
에이전트 디렉터, 데이터 위의 에이전트, 도메인 가속, 3인 맥스, 압도적 시행
""".strip()
