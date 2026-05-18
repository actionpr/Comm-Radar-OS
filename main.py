"""
Dock-In-sight — Main Pipeline
일일 커뮤니케이션 인텔리전스 파이프라인
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collectors.google_news import collect_all_news
from collectors.hackernews import collect_hackernews
from collectors.steam import collect_steam_trending
from collectors.reddit_gas import collect_reddit_posts
from collectors.threads import collect_all_threads
from dedup import filter_new_items
from analyzer.claude_analyst import (
    analyze_news_batch,
    analyze_hackernews,
    analyze_steam_trending,
    analyze_reddit_posts,
    generate_weekly_summary,
)
from report.generator import generate_report


def load_issue_number() -> int:
    """리포트 발행 번호 로드 (자동 증가)"""
    path = os.path.join(os.path.dirname(__file__), ".issue_number")
    try:
        with open(path) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 1


def save_issue_number(num: int):
    path = os.path.join(os.path.dirname(__file__), ".issue_number")
    with open(path, "w") as f:
        f.write(str(num))


def main():
    print("=" * 60)
    print("Dock-In-sight — 파이프라인 시작")
    print("=" * 60)

    issue_num = load_issue_number()
    print(f"\n Issue #{issue_num:03d}")

    # ── Step 1: 데이터 수집 ──
    print("\n" + "─" * 40)
    print("STEP 1: 데이터 수집")
    print("─" * 40)

    news_data = collect_all_news()
    hn_data = collect_hackernews()
    steam_data = collect_steam_trending()
    reddit_data = collect_reddit_posts()
    threads_data = collect_all_threads()

    total_collected = (
        sum(len(v) for v in news_data.values())
        + len(hn_data) + len(steam_data) + len(reddit_data) + len(threads_data)
    )
    print(f"\n 총 {total_collected}건 수집 완료")

    # ── Step 1.5: 중복 제거 ──
    print("\n" + "─" * 40)
    print("STEP 1.5: 중복 제거")
    print("─" * 40)

    for category in news_data:
        before = len(news_data[category])
        news_data[category] = filter_new_items(news_data[category], title_key="title")
        after = len(news_data[category])
        if before != after:
            print(f"  [{category}] {before} → {after} ({before - after}건 중복 제거)")

    hn_before = len(hn_data)
    hn_data = filter_new_items(hn_data, title_key="title")
    if hn_before != len(hn_data):
        print(f"  [HN] {hn_before} → {len(hn_data)} ({hn_before - len(hn_data)}건 중복 제거)")

    reddit_before = len(reddit_data)
    reddit_data = filter_new_items(reddit_data, title_key="title")
    if reddit_before != len(reddit_data):
        print(f"  [Reddit] {reddit_before} → {len(reddit_data)} ({reddit_before - len(reddit_data)}건 중복 제거)")

    threads_before = len(threads_data)
    threads_data = filter_new_items(threads_data, title_key="title")
    if threads_before != len(threads_data):
        print(f"  [Threads] {threads_before} → {len(threads_data)} ({threads_before - len(threads_data)}건 중복 제거)")

    new_total = sum(len(v) for v in news_data.values()) + len(hn_data) + len(reddit_data) + len(threads_data)
    print(f"\n 중복 제거 후 {new_total}건")

    # ── Step 2: AI 분석 ──
    print("\n" + "─" * 40)
    print("STEP 2: Claude AI 분석")
    print("─" * 40)

    news_insights = analyze_news_batch(news_data)
    hn_insights = analyze_hackernews(hn_data)
    steam_analysis = analyze_steam_trending(steam_data)
    reddit_insights = analyze_reddit_posts(reddit_data) if reddit_data else []

    print("\n✅ AI 분석 완료")

    # ── Step 3: 주간 요약 ──
    weekly_summary = generate_weekly_summary(news_insights, hn_insights, steam_analysis)
    print(f"\n📝 주간 요약:\n{weekly_summary}")

    # ── Step 4: HTML 리포트 생성 ──
    print("\n" + "─" * 40)
    print("STEP 3: HTML 리포트 생성")
    print("─" * 40)

    html = generate_report(
        weekly_summary=weekly_summary,
        news_insights=news_insights,
        hn_insights=hn_insights,
        steam_analysis=steam_analysis,
        steam_trending=steam_data,
        reddit_insights=reddit_insights,
        issue_number=issue_num,
    )

    # 리포트 파일 저장
    from datetime import datetime
    filename = f"comm-radar-{issue_num:03d}-{datetime.now().strftime('%Y%m%d')}.html"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ 리포트 저장: {filename}")

    # ── Step 5: 배포 (Google Drive + Slack) ──
    from config import GAS_WEBHOOK_URL
    if GAS_WEBHOOK_URL:
        print("\n" + "─" * 40)
        print("STEP 4: 배포")
        print("─" * 40)
        try:
            from gdrive_uploader import upload_to_drive
            result = upload_to_drive(html, filename)
            print(f"  ✓ Drive 업로드 완료: {result.get('url', 'N/A')}")
        except Exception as e:
            print(f"  [WARN] 배포 실패: {e}")
    else:
        print("\n⏭ GAS_WEBHOOK_URL 미설정 — 배포 건너뜀")

    # 발행 번호 증가
    save_issue_number(issue_num + 1)

    print("\n" + "=" * 60)
    print(f"✅ Comm Radar #{issue_num:03d} 파이프라인 완료!")
    print("=" * 60)

    return filepath


if __name__ == "__main__":
    main()
