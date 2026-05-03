# News Email Bot（每日財經新聞寄送）

這是一個簡單的 Python 專案，可以：

1. 從多個財經新聞 RSS 自動抓取新聞。
2. 整理成 Email（HTML 格式）。
3. 透過 Gmail SMTP 自動寄送給指定收件人。

---

## 1) 專案結構

```bash
news-email-bot/
├─ news_email_bot.py      # 主程式：抓 RSS + 組信 + 寄信
├─ requirements.txt       # Python 套件需求
├─ .env.example           # 環境變數範例
├─ run_daily.sh           # 方便排程呼叫的 shell script
└─ README.md
```

---

## 2) 安裝方式

### Step A. 建立虛擬環境（建議）

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step B. 安裝套件

```bash
pip install -r requirements.txt
```

---

## 3) 設定環境變數

複製範例檔：

```bash
cp .env.example .env
```

然後編輯 `.env`：

- `GMAIL_USER`：Gmail 帳號
- `GMAIL_APP_PASSWORD`：Gmail 應用程式密碼（不是一般登入密碼）
- `RECIPIENTS`：收件人（逗號分隔）
- `RSS_FEEDS`：RSS 來源（逗號分隔）
- `MAX_ITEMS`：最多寄出幾則新聞
- `EMAIL_SUBJECT`：信件主旨
- `TIMEZONE`：例如 `Asia/Taipei`

> Gmail 建議使用「應用程式密碼（App Password）」，需先開啟 2-Step Verification。

---

## 4) 手動執行

```bash
python3 news_email_bot.py
```

若成功，會顯示：

```text
成功寄出 X 則新聞給 Y 位收件人。
```

---

## 5) 每天自動執行（cron）

先確認 `run_daily.sh` 可執行：

```bash
chmod +x run_daily.sh
```

打開 crontab：

```bash
crontab -e
```

加入（例如每天早上 7:30）：

```cron
30 7 * * * /bin/bash /你的路徑/news-email-bot/run_daily.sh >> /你的路徑/news-email-bot/cron.log 2>&1
```

---

## 6) 可自訂方向

- 新增/替換 RSS 來源。
- 改成純文字 Email。
- 將新聞存成檔案（CSV/Markdown）再附檔寄出。
- 改用排程工具（systemd timer、GitHub Actions、雲端排程）。

