"""
SteamSpy 수집기
최근 인기 게임 및 트렌드 데이터 수집
"""

import requests
import time
import math
from config import STEAMSPY_API_URL, STEAM_TOP_N


def fetch_top_2weeks() -> dict:
    """최근 2주 인기 게임"""
    try:
        resp = requests.get(
            STEAMSPY_API_URL,
            params={"request": "top100in2weeks"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] SteamSpy Top 2W 실패: {e}")
        return {}


def bayesian_score(positive: int, negative: int, prior_ratio: float = 75.0, prior_weight: int = 100) -> float:
    """베이지안 보정 긍정률"""
    total = positive + negative
    if total == 0:
        return prior_ratio
    return (positive + prior_weight * (prior_ratio / 100)) / (total + prior_weight) * 100


def compute_trending_score(game: dict) -> float:
    """복합 트렌딩 점수 계산"""
    pos = game.get("positive", 0)
    neg = game.get("negative", 0)
    total_reviews = pos + neg

    if total_reviews < 50:
        return 0

    # ① 베이지안 긍정률
    bay_score = bayesian_score(pos, neg)

    # ② 리뷰수 가산
    review_bonus = min(math.log10(max(total_reviews, 1)) * 5, 20)

    # ③ 소규모 가산 (owners 파싱)
    owners_mid = parse_owners_mid(game.get("owners", "0 .. 0"))
    if owners_mid < 300_000:
        size_bonus = 15
    elif owners_mid < 1_000_000:
        size_bonus = 8
    else:
        size_bonus = 0

    return bay_score + review_bonus + size_bonus


def parse_owners_mid(owners_str: str) -> int:
    """SteamSpy owners 문자열 → 중간값"""
    try:
        parts = owners_str.replace(",", "").split(" .. ")
        low = int(parts[0].strip())
        high = int(parts[1].strip()) if len(parts) > 1 else low
        return (low + high) // 2
    except (ValueError, IndexError):
        return 0


def collect_steam_trending() -> list[dict]:
    """인기 게임 중 트렌딩 상위 N개 추출"""
    print("\n🎮 Steam 트렌드 수집 중...")
    raw = fetch_top_2weeks()

    games = []
    for appid, data in raw.items():
        owners_mid = parse_owners_mid(data.get("owners", "0 .. 0"))
        pos = data.get("positive", 0)
        neg = data.get("negative", 0)
        total = pos + neg

        # 필터: 소유자 5만~500만, 리뷰 50개 이상
        if 50_000 <= owners_mid <= 5_000_000 and total >= 50:
            score = compute_trending_score(data)
            games.append({
                "appid": appid,
                "name": data.get("name", "Unknown"),
                "owners_mid": owners_mid,
                "positive": pos,
                "negative": neg,
                "total_reviews": total,
                "positive_rate": round(pos / total * 100, 1) if total > 0 else 0,
                "bayesian_rate": round(bayesian_score(pos, neg), 1),
                "trending_score": round(score, 1),
                "tags": data.get("tags", {}),
            })

    games.sort(key=lambda x: x["trending_score"], reverse=True)
    result = games[:STEAM_TOP_N]
    print(f"  ✓ {len(result)}개 트렌딩 게임 선별 (전체 {len(games)}개 중)")
    return result


if __name__ == "__main__":
    trending = collect_steam_trending()
    for i, g in enumerate(trending, 1):
        print(f"  {i}. {g['name']} (Score: {g['trending_score']}, Rate: {g['bayesian_rate']}%)")
