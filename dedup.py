"""
Dock-In-sight — 중복 방지 모듈
이전에 수집한 기사를 추적하여 매일 새로운 기사만 리포트에 포함
"""

import json
import hashlib
import os
from datetime import datetime, timedelta

SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_articles.json")
RETENTION_DAYS = 14  # 14일 지난 기록은 자동 삭제


def _load_seen() -> dict:
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_seen(seen: dict):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def _hash(title: str) -> str:
    """제목 기반 해시 생성"""
    cleaned = title.strip().lower()[:80]
    return hashlib.md5(cleaned.encode()).hexdigest()[:12]


def filter_new_items(items: list[dict], title_key: str = "title") -> list[dict]:
    """이미 본 기사를 제외하고 새 기사만 반환"""
    seen = _load_seen()
    today = datetime.now().strftime("%Y-%m-%d")

    # 오래된 기록 정리 (14일 초과)
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d")
    seen = {k: v for k, v in seen.items() if v >= cutoff}

    new_items = []
    for item in items:
        h = _hash(item.get(title_key, ""))
        if h not in seen:
            seen[h] = today
            new_items.append(item)

    _save_seen(seen)
    return new_items


def mark_as_seen(items: list[dict], title_key: str = "title"):
    """분석 완료된 아이템을 seen으로 마킹"""
    seen = _load_seen()
    today = datetime.now().strftime("%Y-%m-%d")
    for item in items:
        h = _hash(item.get(title_key, ""))
        seen[h] = today
    _save_seen(seen)
