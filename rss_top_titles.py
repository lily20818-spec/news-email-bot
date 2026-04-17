#!/usr/bin/env python3
"""每日自動寄送中文財經新聞（多來源備援）"""

from __future__ import annotations

import os
import smtplib
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage


# ✅ 多個RSS來源（避免404）
RSS_FEEDS = [
    "https://news.cnyes.com/rss/news/cat/headline",  # 鉅亨網（推薦）
    "https://news.cnyes.com/rss/news/cat/tw_stock",  # 台股
    "https://feeds.bbci.co.uk/zhongwen/trad/business/rss.xml",  # BBC中文
]

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465


# 👉 抓RSS
def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "news-bot/1.0"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()


# 👉 解析標題
def parse_titles(feed_data: bytes, limit: int = 5) -> list[str]:
    root = ET.fromstring(feed_data)
    titles = []

    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            titles.append(title.strip())
        if len(titles) >= limit:
            break

    return titles


# 👉 自動找可用RSS（避免壞掉）
def get_news(limit=5):
    for url in RSS_FEEDS:
        try:
            data = fetch_feed(url)
            titles = parse_titles(data, limit)
            if titles:
                return titles, url
        except Exception:
            continue
    return [], "無可用來源"


# 👉 寄信
def send_email(titles, source_url):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("NEWS_RECIPIENT")

    if not all([gmail_address, gmail_app_password, recipient]):
        raise RuntimeError("缺少 Gmail 設定")

    msg = EmailMessage()
    msg["Subject"] = "📊 今日全球財經新聞"
    msg["From"] = gmail_address
    msg["To"] = recipient

    content = f"""📊 今日精選財經新聞

來源：{source_url}

"""

    for i, title in enumerate(titles, 1):
        content += f"{i}. {title}\n"

    content += "\n———\nAI 自動新聞系統 🤖"

    msg.set_content(content)

    with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as smtp:
        smtp.login(gmail_address, gmail_app_password)
        smtp.send_message(msg)


# 👉 主程式
def main():
    titles, source = get_news()

    if not titles:
        print("❌ 沒抓到新聞")
        return

    print("抓到新聞：")
    for t in titles:
        print(t)

    send_email(titles, source)
    print("✅ 已寄出 Email")


if __name__ == "__main__":
    main()
