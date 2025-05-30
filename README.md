## TGminiApp-Metronome
# Telegram Mini App: Simple Metronome

A simple metronome mini app that runs inside **Telegram WebApp** environment using **Flask backend** and **SQLite** for storing user BPM preferences.

> Works only inside Telegram and requires HTTPS access.

---

## ✅ Features

- Runs in Telegram via WebApp
- Fetches Telegram user info
- Saves/loads BPM settings from SQLite
- Audio click metronome with adjustable tempo
- Works securely over HTTPS

---

## 📦 Requirements

### 💻 Local Development Tools

- Python 3.8+
- gunicorn
- Flask
- SQLite
- telebot
- Telegram account with bot created via BotFather

### ⚙️ Server Setup (for production)

- Linux (Ubuntu/Redhat) server
- Nginx
- Certbot (Let’s Encrypt SSL)
- Domain name with DNS configured

---

## 🛠️ Installation Instructions

### Step 1: Clone the repo
Download release file and unpack:
`tar -xzf release-name.tar.gz`

### Step 2: Create Environment & Install Dependencies
`pip install gunicorn
pip install Flask
pip install telebot`

### Step 3: Set Up Your Telegram Bot
3.1 Open Telegram and search for @BotFather
3.2 Run /newbot and follow the instructions
3.3 Save the token provided — this is your BOT_TOKEN

### Step 4: Configure app_cfg.py
Copy app_cfg.example.py to app_cfg.py and add your actual data: TELEGRAM_BOT_TOKEN, WEBHOOK_URL, log file and local port for webhook

### Step 5: Set Up Webhook 

python setup_webhook.py

### Step 6: Run Flask App

python run-my-app.py start

### Step 7: Expose App Publicly 
Use Nginx + Let's Encrypt (Recommended for Production)
