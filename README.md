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
tar -xzf release-name.tar.gz

### Step 2: Create Environment & Install Dependencies
pip install gunicorn
pip install Flask
