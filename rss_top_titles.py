#!/usr/bin/env python3
"""抓取中文財經 RSS，寄送前五則新聞到 Gmail"""

from __future__ import annotations

import os
import smtplib
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage


# 👉 改成中文財經（鉅亨網）
DEFAULT_FEED_URL = "https://news.cnyes.com/rss/news"

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "rss-news-bot/1.0"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()


def parse_titles(feed_data: bytes, limit: int = 5) -> list[str]:
    root = ET.fromstring(feed_data)
    titles: list[str] = []

    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            titles.append(title.strip())
        if len(titles) == limit:
            break

    return titles


def format_titles(titles: list[str]) -> str:
    return "\n".join(f"{index}. {title}" for index, title in enumerate(titles, start=1))


def send_email(titles: list[str], feed_url: str) -> None:
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("NEWS_RECIPIENT")

    if not all([gmail_address, gmail_app_password, recipient]):
        raise RuntimeError("請確認已設定 GMAIL_ADDRESS / GMAIL_APP_PASSWORD / NEWS_RECIPIENT")

    message = EmailMessage()
    message["Subject"] = "📊 今日全球財經新聞（自動寄送）"
    message["From"] = gmail_address
    message["To"] = recipient

    # 👉 中文信件內容
    content = f"""📊 今日精選財經新聞

來源：{feed_url}

{format_titles(titles)}

———
此郵件由你的 AI 自動新聞系統發送 🤖
"""

    message.set_content(content)

    with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT, timeout=15) as smtp:
        smtp.login(gmail_address, gmail_app_password)
        smtp.send_message(message)


def main() -> int:
    feed_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FEED_URL

    try:
        feed_data = fetch_feed(feed_url)
        titles = parse_titles(feed_data)
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1

    if not titles:
        print("沒有抓到新聞")
        return 0

    print(format_titles(titles))

    try:
        send_email(titles, feed_url)
    except Exception as exc:
        print(f"寄信失敗：{exc}", file=sys.stderr)
        return 1

    print("✅ 已成功寄出 Email")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
