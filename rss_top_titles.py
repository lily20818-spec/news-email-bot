#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import smtplib
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage
import requests

FEED_URL = "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"


def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read()


def parse_titles(xml_data, limit=10):
    root = ET.fromstring(xml_data)
    titles = []
    for item in root.findall(".//item"):
        t = item.findtext("title")
        if t:
            titles.append(t.strip())
        if len(titles) >= limit:
            break
    return titles


# 🔥 AI整理（核心）
def summarize_with_ai(text):
    api_key = os.environ.get("OPENAI_API_KEY")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
請把以下新聞整理成每日財經重點：

格式如下：
📰 今日財經重點

🌏 宏觀經濟
👉 解讀

📊 股市
👉 解讀

🏢 企業
👉 解讀

🌍 國際
👉 解讀

💰 利率
👉 解讀

🪙 加密貨幣
👉 解讀

要求：
- 使用繁體中文
- 像投資人看的摘要
- 精簡但有重點

新聞如下：
{text}
"""

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


def send_email(content):
    gmail = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    to = os.environ.get("NEWS_RECIPIENT")

    msg = EmailMessage()
    msg["Subject"] = "📰 今日財經重點（自動寄送）"
    msg["From"] = gmail
    msg["To"] = to
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail, password)
        smtp.send_message(msg)


def main():
    data = fetch_feed(FEED_URL)
    titles = parse_titles(data)

    text = "\n".join(titles)
    summary = summarize_with_ai(text)

    send_email(summary)


if __name__ == "__main__":
    main()
