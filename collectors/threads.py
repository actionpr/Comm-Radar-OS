"""
Threads 수집기
threads-rss.com 브릿지를 통해 특정 계정의 최신 포스트 수집
"""

import xml.etree.ElementTree as ET
import requests
import time
from config import THREADS_ACCOUNTS, THREADS_RSS_BASE


def fetch_threads_posts(username: str, max_results: int = 10) -> list[dict]:
    """Threads 계정의 최신 포스트를 RSS로 수집"""
    url = f"{THREADS_RSS_BASE}{username}"

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DockInSight/1.0)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Threads 수집 실패 (@{username}): {e}")
        return []

    items = []
    try:
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item")[:max_results]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            description = item.findtext("description", "")

            items.append({
                "title": title[:200] if title else description[:200],
                "link": link,
                "content": description[:500],
                "pub_date": pub_date,
                "source": f"Threads @{username}",
                "username": username,
            })
    except ET.ParseError as e:
        print(f"  [WARN] Threads XML 파싱 실패 (@{username}): {e}")

    return items


def collect_all_threads() -> list[dict]:
    """모든 모니터링 계정에서 포스트 수집"""
    print("\n Threads 수집 중...")
    all_posts = []

    for username in THREADS_ACCOUNTS:
        print(f"  @{username} 수집...")
        posts = fetch_threads_posts(username)
        all_posts.extend(posts)
        time.sleep(1)

    print(f"  {len(all_posts)}건 수집")
    return all_posts


if __name__ == "__main__":
    posts = collect_all_threads()
    for p in posts[:5]:
        print(f"  [@{p['username']}] {p['title'][:80]}")
