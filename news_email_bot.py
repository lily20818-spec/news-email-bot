import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable
from zoneinfo import ZoneInfo

import feedparser
from dotenv import load_dotenv


DEFAULT_RSS_FEEDS = [
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "https://www.ft.com/markets?format=rss",
]


def parse_list(value: str | None, default: Iterable[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def fetch_news(feed_urls: list[str], max_items: int) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        source_title = feed.feed.get("title", url)

        for entry in feed.entries:
            items.append(
                {
                    "title": entry.get("title", "(無標題)"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": source_title,
                }
            )

    deduped: list[dict[str, str]] = []
    seen = set()
    for item in items:
        key = (item["title"], item["link"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped[:max_items]


def build_html(news_items: list[dict[str, str]], generated_at: str) -> str:
    if not news_items:
        return f"""
        <html><body>
            <h2>每日財經新聞摘要</h2>
            <p>目前沒有抓到新聞資料。</p>
            <p>產生時間：{generated_at}</p>
        </body></html>
        """

    rows = []
    for idx, item in enumerate(news_items, start=1):
        rows.append(
            f"""
            <li>
                <a href=\"{item['link']}\">{item['title']}</a><br/>
                <small>來源：{item['source']} | 發布時間：{item['published'] or '未知'}</small>
            </li>
            """
        )

    return f"""
    <html>
      <body style=\"font-family: Arial, sans-serif; line-height: 1.6;\">
        <h2>每日財經新聞摘要</h2>
        <p>以下是今天的重點新聞（最多 {len(news_items)} 則）：</p>
        <ol>
          {''.join(rows)}
        </ol>
        <hr/>
        <p style=\"color:#666; font-size:12px;\">產生時間：{generated_at}</p>
      </body>
    </html>
    """


def send_email(
    gmail_user: str,
    gmail_app_password: str,
    recipients: list[str],
    subject: str,
    html_content: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, recipients, msg.as_string())


def main() -> None:
    load_dotenv()

    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    recipients = parse_list(os.getenv("RECIPIENTS"), [])
    feed_urls = parse_list(os.getenv("RSS_FEEDS"), DEFAULT_RSS_FEEDS)
    max_items = int(os.getenv("MAX_ITEMS", "10"))
    subject = os.getenv("EMAIL_SUBJECT", "每日財經新聞摘要")
    tz_name = os.getenv("TIMEZONE", "Asia/Taipei")

    if not gmail_user or not gmail_app_password:
        raise ValueError("請設定 GMAIL_USER 與 GMAIL_APP_PASSWORD")
    if not recipients:
        raise ValueError("請設定至少一個 RECIPIENTS")

    generated_at = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S %Z")
    news_items = fetch_news(feed_urls, max_items=max_items)
    html_content = build_html(news_items, generated_at)

    send_email(gmail_user, gmail_app_password, recipients, subject, html_content)
    print(f"成功寄出 {len(news_items)} 則新聞給 {len(recipients)} 位收件人。")


if __name__ == "__main__":
    main()
