"""
Reddit 수집기 (Google Apps Script 프록시 경유)
GitHub Actions IP에서 Reddit 직접 접근 차단되므로 GAS 프록시 사용
"""

import requests
from config import GAS_REDDIT_URL, REDDIT_SUBREDDITS


def collect_reddit_posts() -> list[dict]:
    """GAS 프록시를 통해 Reddit RSS 수집"""
    print("\n💬 Reddit 커뮤니티 수집 중...")

    if not GAS_REDDIT_URL:
        print("  [SKIP] GAS_REDDIT_URL 미설정 — Reddit 수집 건너뜀")
        return []

    try:
        resp = requests.post(
            GAS_REDDIT_URL,
            json={"subreddits": REDDIT_SUBREDDITS, "limit": 5},
            timeout=30,
        )
        resp.raise_for_status()
        posts = resp.json()

        result = []
        for post in posts:
            result.append({
                "title": post.get("title", ""),
                "subreddit": post.get("subreddit", ""),
                "link": post.get("link", ""),
                "content": post.get("content", "")[:500],  # 본문 500자 제한
                "pub_date": post.get("pub_date", ""),
            })

        print(f"  ✓ {len(result)}건 수집")
        return result

    except Exception as e:
        print(f"  [WARN] Reddit 수집 실패: {e}")
        return []


# ─── GAS에 배포할 코드 (별도 설정 필요) ───
GAS_CODE_TEMPLATE = '''
// Google Apps Script — Reddit RSS 프록시
// script.google.com에서 새 프로젝트 생성 후 이 코드를 붙여넣기

function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var subreddits = data.subreddits || ["gaming"];
  var limit = data.limit || 5;
  var allPosts = [];

  for (var i = 0; i < subreddits.length; i++) {
    var sub = subreddits[i];
    try {
      var url = "https://www.reddit.com/r/" + sub + "/.rss";
      var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
      var xml = XmlService.parse(response.getContentText());
      var root = xml.getRootElement();
      var ns = root.getNamespace();
      var entries = root.getChildren("entry", ns);

      for (var j = 0; j < Math.min(entries.length, limit); j++) {
        var entry = entries[j];
        allPosts.push({
          title: entry.getChildText("title", ns) || "",
          link: entry.getChild("link", ns) ? entry.getChild("link", ns).getAttribute("href").getValue() : "",
          content: entry.getChildText("content", ns) || "",
          subreddit: sub,
          pub_date: entry.getChildText("updated", ns) || ""
        });
      }
    } catch(err) {
      // 개별 서브레딧 실패 시 건너뜀
    }
    Utilities.sleep(500);
  }

  return ContentService.createTextOutput(JSON.stringify(allPosts))
    .setMimeType(ContentService.MimeType.JSON);
}
'''.strip()

if __name__ == "__main__":
    posts = collect_reddit_posts()
    for p in posts[:5]:
        print(f"  [r/{p['subreddit']}] {p['title']}")
