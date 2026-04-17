#!/usr/bin/env python3
"""Fetch an RSS feed, print the top five titles, and email them via Gmail."""

from __future__ import annotations

import os
import smtplib
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from email.message import EmailMessage


DEFAULT_FEED_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "rss-top-titles/1.0"},
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

    missing = [
        name
        for name, value in (
            ("GMAIL_ADDRESS", gmail_address),
            ("GMAIL_APP_PASSWORD", gmail_app_password),
            ("NEWS_RECIPIENT", recipient),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = "Top 5 RSS News Titles"
    message["From"] = gmail_address
    message["To"] = recipient
    message.set_content(f"Top 5 titles from {feed_url}:\n\n{format_titles(titles)}")

    with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT, timeout=15) as smtp:
        smtp.login(gmail_address, gmail_app_password)
        smtp.send_message(message)


def main() -> int:
    feed_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FEED_URL

    try:
        feed_data = fetch_feed(feed_url)
        titles = parse_titles(feed_data)
    except urllib.error.URLError as exc:
        print(f"Failed to fetch RSS feed: {exc}", file=sys.stderr)
        return 1
    except ET.ParseError as exc:
        print(f"Failed to parse RSS feed: {exc}", file=sys.stderr)
        return 1

    if not titles:
        print("No titles found.")
        return 0

    print(format_titles(titles))

    try:
        send_email(titles, feed_url)
    except (RuntimeError, OSError, smtplib.SMTPException) as exc:
        print(f"Failed to send email: {exc}", file=sys.stderr)
        return 1

    print("Email sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
