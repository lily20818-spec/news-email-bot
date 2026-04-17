#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
抓 RSS 新聞 → 翻譯成中文 → 寄 Gmail（含除錯）
"""

import os
import smtplib
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage

# 👉 可改成你想要的新聞來源
FEED_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"


def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read()


def parse_titles(xml_data, limit=5):
    root = ET.fromstring(xml_data)
    titles = []
    for item in root.findall(".//item"):
        t = item.findtext("title")
        if t:
            titles.append(t.strip())
        if len(titles) >= limit:
            break
    return titles


# 🔥 用 Google 翻譯（免費，不用API）
def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&q=" + urllib.parse.quote(text)
        with urllib.request.urlopen(url) as res:
            result = eval(res.read().decode())
            return result[0][0][0]
    except:
        return text  # 翻譯失敗就維持原文


def send_email(titles):
    gmail = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    to = os.environ.get("NEWS_RECIPIENT")

    print("DEBUG:")
    print("EMAIL:", gmail)
    print("PASSWORD長度:", len(password) if password else 0)
    print("TO:", to)

    if not gmail or not password or not to:
        raise Exception("❌ 環境變數沒抓到！")

    # 👉 中文標題
    translated = [translate(t) for t in titles]

    content = "📢 今日新聞（中文）\n\n"
    for i, t in enumerate(translated, 1):
        content += f"{i}. {t}\n"

    msg = EmailMessage()
    msg["Subject"] = "📢 今日新聞（自動寄送）"
    msg["From"] = gmail
    msg["To"] = to
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail, password)
        smtp.send_message(msg)

    print("✅ Email sent!")


def main():
    data = fetch_feed(FEED_URL)
    titles = parse_titles(data)

    if not titles:
        print("❌ 沒抓到新聞")
        return

    send_email(titles)


if __name__ == "__main__":
    main()
