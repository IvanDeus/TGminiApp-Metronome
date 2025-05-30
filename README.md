## TGminiApp-Metronome
# Telegram Mini App: Simple Metronome

A simple metronome mini app that runs inside **Telegram WebApp** environment using **Flask backend** and **SQLite** for storing user BPM preferences.

> Works only inside Telegram and requires HTTPS access.

---

## ✅ Features

- Runs in Telegram via WebApp
- Fetches Telegram user info
- Saves/loads BPM settings from SQLite
- Audio click metronome with easily adjustable tempo
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

- Linux (Ubuntu/RedHat or similar) server
- Nginx
- Domain name with DNS configured

---

## 🛠️ Installation Instructions

### Step 1: Get the App

Download release file and unpack:

`tar -xzf release-name.tar.gz`

### Step 2: Create Environment & Install Dependencies

Depending on your OS, install Python 3 main package and then run those:

`pip install gunicorn`

`pip install Flask`

`pip install telebot`

### Step 3: Set Up Your Telegram Bot

3.1. Open Telegram and search for @BotFather

3.2. Run /newbot and follow the instructions

3.3. Save the token provided — this is your TELEGRAM_BOT_TOKEN

### Step 4: Configure App

Copy app_cfg.example.py to app_cfg.py:

`cp app_cfg.example.py app_cfg.py`

And add your actual data, like: TELEGRAM_BOT_TOKEN, Webhook URL, log file and local port for webhook

### Step 5: Set Up Webhook 

This will connect your Telegram bot to your App:

`python setup_webhook.py`

### Step 6: Run Flask App

To start the App in the background run: 

`python run-my-app.py start`

This step will also initialize the SQLite database

### Step 7: Expose App Publicly 

Use Nginx (Recommended for Production) + SSL Certificate from Certbot/acme.sh "Let's Encrypt" or any other provider.


