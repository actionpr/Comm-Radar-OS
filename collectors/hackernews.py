"""
Hacker News 수집기
상위 스토리 중 AI/게임/자동화 관련 항목 필터링
"""

import requests
import time
from config import (
    HN_TOP_STORIES_URL, HN_ITEM_URL,
    HN_MAX_FETCH, HN_RELEVANT_KEYWORDS, MAX_HN_ITEMS,
)


def fetch_top_stories() -> list[int]:
    """HN 상위 스토리 ID 목록"""
    try:
        resp = requests.get(HN_TOP_STORIES_URL, timeout=10)
        resp.raise_for_status()
        return resp.json()[:HN_MAX_FETCH]
    except Exception as e:
        print(f"  [WARN] HN 스토리 목록 실패: {e}")
        return []


def fetch_item(item_id: int) -> dict | None:
    """개별 스토리 상세 정보"""
    try:
        resp = requests.get(HN_ITEM_URL.format(item_id), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def is_relevant(item: dict) -> bool:
    """베이글코드 관심 분야와 관련 있는지 키워드 매칭"""
    text = f"{item.get('title', '')} {item.get('text', '')}".lower()
    return any(kw in text for kw in HN_RELEVANT_KEYWORDS)


def collect_hackernews() -> list[dict]:
    """관련 있는 HN 스토리 수집"""
    print("\n🔶 Hacker News 수집 중...")
    story_ids = fetch_top_stories()
    relevant = []

    for sid in story_ids:
        item = fetch_item(sid)
        if not item or item.get("type") != "story":
            continue

        if is_relevant(item):
            relevant.append({
                "title": item.get("title", ""),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "by": item.get("by", ""),
                "hn_id": sid,
            })

        if len(relevant) >= MAX_HN_ITEMS:
            break
        time.sleep(0.2)  # API 예의

    # 점수순 정렬
    relevant.sort(key=lambda x: x["score"], reverse=True)
    print(f"  ✓ {len(relevant)}건 수집 (상위 {HN_MAX_FETCH}개 중 필터링)")
    return relevant


if __name__ == "__main__":
    items = collect_hackernews()
    for item in items:
        print(f"  [{item['score']}↑] {item['title']}")
