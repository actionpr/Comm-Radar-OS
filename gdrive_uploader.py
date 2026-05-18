"""
Google Drive 업로드 (GAS Webhook 경유) + Slack 알림
"""

import requests
from config import GAS_WEBHOOK_URL


def upload_to_drive(html_content: str, filename: str) -> dict:
    """GAS Webhook을 통해 HTML을 Google Drive에 업로드"""
    if not GAS_WEBHOOK_URL:
        print("  [SKIP] GAS_WEBHOOK_URL 미설정")
        return {}

    try:
        resp = requests.post(
            GAS_WEBHOOK_URL,
            json={"html": html_content, "filename": filename},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [ERROR] Drive 업로드 실패: {e}")
        return {}


# ─── GAS에 배포할 코드 (Google Drive 업로드 + Slack 알림) ───
GAS_DRIVE_CODE = '''
// Google Apps Script — Drive 업로드 + Slack 알림
// script.google.com에서 새 프로젝트 생성 후 이 코드를 붙여넣기

var FOLDER_ID = "여기에_Google_Drive_폴더_ID";
var SLACK_BOT_TOKEN = "여기에_Slack_Bot_Token";
var SLACK_CHANNEL = "여기에_채널_ID";

function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  // Reddit RSS 프록시 요청인 경우
  if (data.subreddits) {
    return handleRedditProxy(data);
  }

  // Drive 업로드 요청인 경우
  if (data.html && data.filename) {
    return handleDriveUpload(data);
  }

  return ContentService.createTextOutput(JSON.stringify({error: "Unknown request"}))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleDriveUpload(data) {
  var folder = DriveApp.getFolderById(FOLDER_ID);
  var file = folder.createFile(data.filename, data.html, "text/html");
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  var url = file.getUrl();

  // Slack 알림
  if (SLACK_BOT_TOKEN && SLACK_CHANNEL) {
    sendSlack(url, data.filename);
  }

  return ContentService.createTextOutput(JSON.stringify({url: url}))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleRedditProxy(data) {
  var subreddits = data.subreddits;
  var limit = data.limit || 5;
  var allPosts = [];

  for (var i = 0; i < subreddits.length; i++) {
    try {
      var url = "https://www.reddit.com/r/" + subreddits[i] + "/.rss";
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
          content: (entry.getChildText("content", ns) || "").substring(0, 500),
          subreddit: subreddits[i],
          pub_date: entry.getChildText("updated", ns) || ""
        });
      }
    } catch(err) {}
    Utilities.sleep(500);
  }

  return ContentService.createTextOutput(JSON.stringify(allPosts))
    .setMimeType(ContentService.MimeType.JSON);
}

function sendSlack(url, filename) {
  var payload = {
    channel: SLACK_CHANNEL,
    text: "📡 *Comm Radar* 이번 주 리포트가 도착했습니다!\\n<" + url + "|" + filename + ">"
  };
  UrlFetchApp.fetch("https://slack.com/api/chat.postMessage", {
    method: "post",
    headers: {"Authorization": "Bearer " + SLACK_BOT_TOKEN},
    contentType: "application/json",
    payload: JSON.stringify(payload)
  });
}
'''.strip()
