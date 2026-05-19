"""
Claude API 분석기
수집된 데이터를 베이글코드 커뮤니케이션 관점에서 분석
"""

import json
import requests as http_client
from config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, BAGELCODE_CONTEXT


def call_claude(prompt: str, system: str = "") -> str:
    """Claude API 호출 — AIProxy Passthrough 방식"""
    if ANTHROPIC_BASE_URL:
        url = f"{ANTHROPIC_BASE_URL.rstrip('/')}/v1/messages"
        headers = {
            "Authorization": f"Bearer {ANTHROPIC_API_KEY}",
            "Content-Type": "application/json",
        }
    else:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": CLAUDE_MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    else:
        body["system"] = _default_system()

    try:
        resp = http_client.post(url, headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    except Exception as e:
        print(f"  [ERROR] Claude API 호출 실패: {e}")
        return ""


def _default_system() -> str:
    return f"""당신은 베이글코드(Bagelcode)의 커뮤니케이션 인텔리전스 분석가입니다.
수집된 뉴스와 트렌드를 분석하여, 커뮤니케이션 디렉터가 즉시 활용할 수 있는 인사이트를 도출합니다.

{BAGELCODE_CONTEXT}

분석 원칙:
1. 모든 정보를 베이글코드의 사업·전략·문화와 연결하여 해석
2. PR 기회, 포지셔닝 참고, 리스크 모니터링 관점으로 분류
3. 구체적이고 실행 가능한 인사이트 우선
4. 반드시 한국어로 작성"""


def _parse_json(text: str):
    """Claude 응답에서 JSON을 안전하게 추출"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(cleaned)


def analyze_news_batch(news_by_category: dict) -> list[dict]:
    """
    카테고리별 뉴스를 분석하여 인사이트 도출
    URL을 보존하여 리포트에서 클릭 가능하게 함
    """
    print("\n  뉴스 AI 분석 중...")

    all_items = []
    for category, items in news_by_category.items():
        for item in items:
            all_items.append({
                "category": category,
                "title": item["title"],
                "source": item.get("source", ""),
                "url": item.get("link", ""),
            })

    if not all_items:
        print("  [INFO] 분석할 뉴스가 없습니다 (수집 0건)")
        return []

    # URL 매핑 테이블 (제목 → URL)
    url_map = {}
    for item in all_items:
        url_map[item["title"].strip()] = item["url"]
        short_key = item["title"].strip()[:40].lower()
        url_map[short_key] = item["url"]

    news_text = "\n".join(
        f"[{item['category']}] {item['title']} (출처: {item['source']})"
        for item in all_items
    )

    prompt = f"""다음은 이번 주 수집된 뉴스 헤드라인입니다:

{news_text}

각 뉴스를 분석하여 아래 JSON 배열로 반환하세요.
중요도가 높은 순서로 최대 8개만 선별하세요.

반드시 아래 JSON 형식만 출력하고, 다른 텍스트는 포함하지 마세요:

[
  {{
    "title": "뉴스 제목 (원문 그대로)",
    "category": "카테고리",
    "relevance": "high|medium|low",
    "type": "PR기회|경쟁동향|시장트렌드|리스크|참고",
    "insight": "베이글코드 관점의 분석 인사이트 (2~3문장)",
    "action": "커뮤니케이션 디렉터가 취할 수 있는 구체적 액션 (1문장)"
  }}
]"""

    result_text = call_claude(prompt)

    try:
        results = _parse_json(result_text)
        # URL 복원
        for item in results:
            title = item.get("title", "").strip()
            url = url_map.get(title, "")
            if not url:
                short_key = title[:40].lower()
                url = url_map.get(short_key, "")
            item["url"] = url
        return results
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  [WARN] 뉴스 분석 JSON 파싱 실패: {e}")
        return []


def analyze_hackernews(hn_items: list[dict]) -> list[dict]:
    """Hacker News 스토리 분석"""
    print("  Hacker News AI 분석 중...")

    if not hn_items:
        print("  [INFO] 분석할 HN 항목이 없습니다")
        return []

    # URL 매핑 테이블
    url_map = {}
    for item in hn_items:
        url_map[item["title"].strip()] = item.get("url", "")
        short_key = item["title"].strip()[:40].lower()
        url_map[short_key] = item.get("url", "")

    hn_text = "\n".join(
        f"- {item['title']} (Score: {item['score']}, Comments: {item['comments']})"
        for item in hn_items
    )

    prompt = f"""다음은 Hacker News 상위 스토리 중 AI/게임/자동화 관련 항목입니다:

{hn_text}

각 항목을 베이글코드 관점에서 분석하여 아래 JSON 배열로 반환하세요.
가장 관련성 높은 5개만 선별하세요.

반드시 아래 JSON 형식만 출력하고, 다른 텍스트는 포함하지 마세요:

[
  {{
    "title": "스토리 제목 (원문 그대로)",
    "buzz_level": "high|medium|low",
    "summary": "한 줄 요약 (한국어)",
    "insight": "베이글코드와의 연결점 또는 시사점 (한국어, 2문장)"
  }}
]"""

    result_text = call_claude(prompt)

    try:
        results = _parse_json(result_text)
        # URL 복원
        for item in results:
            title = item.get("title", "").strip()
            url = url_map.get(title, "")
            if not url:
                short_key = title[:40].lower()
                url = url_map.get(short_key, "")
            item["url"] = url
        return results
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  [WARN] HN 분석 JSON 파싱 실패: {e}")
        return []


def analyze_steam_trending(trending: list[dict]) -> dict:
    """Steam 트렌딩 게임 분석"""
    print("  Steam 트렌드 AI 분석 중...")

    if not trending:
        print("  [INFO] 분석할 Steam 항목이 없습니다")
        return {}

    steam_text = "\n".join(
        f"- {g['name']} (긍정률: {g['bayesian_rate']}%, 소유자: {g['owners_mid']:,}, "
        f"태그: {', '.join(list(g.get('tags', {}).keys())[:5])})"
        for g in trending[:10]
    )

    prompt = f"""다음은 Steam에서 이번 주 주목할 만한 인디/중소 게임입니다:

{steam_text}

게임 시장 트렌드 관점에서 분석하여 아래 JSON 형식으로 반환하세요.
반드시 아래 JSON 형식만 출력하고, 다른 텍스트는 포함하지 마세요:

{{
  "trend_summary": "이번 주 게임 트렌드 핵심 요약 (3문장, 한국어)",
  "hot_genres": ["주목 장르 1", "주목 장르 2", "주목 장르 3"],
  "games": [
    {{
      "name": "게임명",
      "one_liner": "한 줄 설명",
      "why_notable": "주목 이유 (1문장)"
    }}
  ]
}}"""

    result_text = call_claude(prompt)

    try:
        return _parse_json(result_text)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  [WARN] Steam 분석 JSON 파싱 실패: {e}")
        return {}


def generate_weekly_summary(news_insights: list, hn_insights: list, steam_analysis: dict) -> str:
    """주간 종합 요약 생성 (리포트 Lede 섹션용)"""
    print("  주간 종합 요약 생성 중...")

    context_parts = []

    if news_insights:
        top_news = [n.get("insight", "") for n in news_insights[:3]]
        context_parts.append("주요 뉴스 인사이트:\n" + "\n".join(f"- {n}" for n in top_news))

    if hn_insights:
        top_hn = [h.get("summary", "") for h in hn_insights[:3]]
        context_parts.append("테크 커뮤니티 화제:\n" + "\n".join(f"- {h}" for h in top_hn))

    if steam_analysis and isinstance(steam_analysis, dict):
        context_parts.append(f"게임 트렌드: {steam_analysis.get('trend_summary', '')}")

    if not context_parts:
        return "이번 주 수집된 데이터가 부족하여 요약을 생성하지 못했습니다."

    prompt = f"""다음은 이번 주 수집·분석된 커뮤니케이션 인텔리전스입니다:

{chr(10).join(context_parts)}

위 내용을 종합하여, 베이글코드 커뮤니케이션 디렉터가 이번 주 알아야 할 핵심 3가지를
간결하게 요약하세요 (총 150자 이내, 한국어).
각 항목은 줄바꿈으로 구분하세요.
이모지는 사용하지 마세요.
추가 설명 없이 요약만 출력하세요."""

    return call_claude(prompt)


def analyze_reddit_posts(posts: list[dict]) -> list[dict]:
    """Reddit 포스트 분석"""
    print("  Reddit 커뮤니티 AI 분석 중...")

    if not posts:
        print("  [INFO] 분석할 Reddit 항목이 없습니다")
        return []

    posts_text = "\n".join(
        f"[r/{p['subreddit']}] {p['title']}\n내용 일부: {p.get('content', '')[:200]}"
        for p in posts[:10]
    )

    prompt = f"""다음은 Reddit 게임/AI 커뮤니티의 최신 포스트입니다:

{posts_text}

유저 커뮤니티의 목소리에서 신작 기획 힌트나 시장 트렌드를 추출하세요.
업계 뉴스/기업 논란 등 유저 목소리가 아닌 포스트는 제외하세요.

반드시 아래 JSON 배열 형식만 출력하고, 다른 텍스트는 포함하지 마세요:

[
  {{
    "subreddit": "서브레딧명",
    "title": "포스트 제목",
    "summary": "유저 목소리 요약 (1줄, 한국어)",
    "insight": "신작 기획 힌트 또는 트렌드 시사점 (1문장, 한국어)"
  }}
]"""

    result_text = call_claude(prompt)

    try:
        return _parse_json(result_text)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  [WARN] Reddit 분석 JSON 파싱 실패: {e}")
        return []
