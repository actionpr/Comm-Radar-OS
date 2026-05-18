"""
Dock-In-sight — Main Pipeline
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


def load_issue_number():
    path = os.path.join(os.path.dirname(__file__), ".issue_number")
    try:
        with open(path) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 1


def save_issue_number(num):
    path = os.path.join(os.path.dirname(__file__), ".issue_number")
    with open(path, "w") as f:
        f.write(str(num))


def send_slack_notification(issue_num, filepath):
    import requests
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        print("  [SKIP] SLACK_WEBHOOK_URL not set")
        return
    try:
        message = {
            "text": f"Dock-In-sight #{issue_num:03d} daily report generated.\nFile: {filepath}"
        }
        requests.post(webhook_url, json=message, timeout=10)
        print("  Slack notification sent")
    except Exception as ex:
        print(f"  [WARN] Slack failed: {ex}")


def main():
    print("=" * 60)
    print("Dock-In-sight pipeline start")
    print("=" * 60)

    issue_num = load_issue_number()
    print(f"\nIssue #{issue_num:03d}")

    print("\nSTEP 1: Collect data")
    news_data = collect_all_news()
    hn_data = collect_hackernews()
    steam_data = collect_steam_trending()
    reddit_data = collect_reddit_posts()
    threads_data = collect_all_threads()

    total = sum(len(v) for v in news_data.values()) + len(hn_data) + len(steam_data) + len(reddit_data) + len(threads_data)
    print(f"Collected {total} items")

    print("\nSTEP 1.5: Dedup")
    for category in news_data:
        before = len(news_data[category])
        news_data[category] = filter_new_items(news_data[category], title_key="title")
        after = len(news_data[category])
        if before != after:
            print(f"  [{category}] {before} -> {after}")

    hn_data = filter_new_items(hn_data, title_key="title")
    reddit_data = filter_new_items(reddit_data, title_key="title")
    threads_data = filter_new_items(threads_data, title_key="title")

    print("\nSTEP 2: AI analysis")
    news_insights = analyze_news_batch(news_data)
    hn_insights = analyze_hackernews(hn_data)
    steam_analysis = analyze_steam_trending(steam_data)
    reddit_insights = analyze_reddit_posts(reddit_data) if reddit_data else []

    weekly_summary = generate_weekly_summary(news_insights, hn_insights, steam_analysis)

    print("\nSTEP 3: Generate report")
    html = generate_report(
        weekly_summary=weekly_summary,
        news_insights=news_insights,
        hn_insights=hn_insights,
        steam_analysis=steam_analysis,
        steam_trending=steam_data,
        reddit_insights=reddit_insights,
        issue_number=issue_num,
    )

    from datetime import datetime
    filename = f"dock-in-sight-{issue_num:03d}-{datetime.now().strftime('%Y%m%d')}.html"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Report saved: {filename}")

    print("\nSTEP 4: Notify")
    send_slack_notification(issue_num, filepath)

    save_issue_number(issue_num + 1)
    print(f"\nDock-In-sight #{issue_num:03d} complete!")

    return filepath


if __name__ == "__main__":
    main()
