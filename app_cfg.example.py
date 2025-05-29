# app_cfg.example.py - Example configuration for your Flask application

# Telegram Bot Token (get it from @BotFather)
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
# Webhook URL (must be public, e.g., ngrok or real server)
WEBHOOK_URL = "https://myapp.com/"
# Telegram Channel ID (from RawDataBot or similar)
CHANNEL_ID = "-100YourChannelIDHere"
# Logging settings
LOGFPATH = "/var/log/TGminiApp-Metronome.log"
# DB name
DATABASE = 'users_db.sqlite'
# Local port for webhook
BOT_LPORT = 6543

# Application Settings
DEBUG = False
