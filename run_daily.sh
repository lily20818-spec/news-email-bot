#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 news_email_bot.py
