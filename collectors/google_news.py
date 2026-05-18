"""
Google News RSS 수집기
키워드별 최신 뉴스를 RSS 피드로 수집
"""

import xml.etree.ElementTree as ET
import requests
import time
import re
from urllib.parse import quote
from config import NEWS_KEYWORDS, MAX_NEWS_PER_CATEGORY


def fetch_google_news(keyword: str, max_results: int = 5) -> list[dict]:
    """Google News RSS에서 키워드 기반 뉴스 수집"""
    encoded = quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CommRadar/1.0)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Google News 수집 실패 ({keyword}): {e}")
        return []

    items = []
    try:
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item")[:max_results]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")
            # 제목에서 소스 분리 (Google News 형식: "제목 - 소스")
            clean_title = re.sub(r"\s*-\s*[^-]+$", "", title) if " - " in title else title
            items.append({
                "title": clean_title.strip(),
                "link": link,
                "source": source,
                "pub_date": pub_date,
                "keyword": keyword,
            })
    except ET.ParseError as e:
        print(f"  [WARN] XML 파싱 실패 ({keyword}): {e}")

    return items


def collect_all_news() -> dict[str, list[dict]]:
    """모든 카테고리의 뉴스를 수집"""
    all_news = {}

    for category, keywords in NEWS_KEYWORDS.items():
        print(f"\n📰 [{category}] 뉴스 수집 중...")
        category_items = []
        seen_titles = set()

        for kw in keywords:
            print(f"  → '{kw}' 검색...")
            items = fetch_google_news(kw, max_results=MAX_NEWS_PER_CATEGORY)
            for item in items:
                # 중복 제거 (제목 기준)
                title_key = item["title"].lower()[:50]
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    category_items.append(item)
            time.sleep(1)  # rate limit 방지

        all_news[category] = category_items[:MAX_NEWS_PER_CATEGORY * 2]
        print(f"  ✓ {len(all_news[category])}건 수집")

    return all_news


if __name__ == "__main__":
    news = collect_all_news()
    for cat, items in news.items():
        print(f"\n=== {cat} ({len(items)}건) ===")
        for item in items[:3]:
            print(f"  - {item['title']} [{item['source']}]")
