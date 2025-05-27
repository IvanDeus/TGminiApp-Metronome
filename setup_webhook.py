import json
import requests
from app_cfg import TELEGRAM_BOT_TOKEN, WEBHOOK_URL

def set_telegram_webhook(token, url, max_connections=18, drop_pending_updates=True):
    telegram_api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    payload = {
        'url': url,
        'max_connections': max_connections,
        'drop_pending_updates': drop_pending_updates
    }
    response = requests.post(telegram_api_url, data=payload)
    return response.json()

if __name__ == "__main__":
    webhook_path = "/whook"  # Adjust this path if needed
    # Construct full webhook URL if not already defined
    if not WEBHOOK_URL:
        public_domain = input("Enter your public domain (e.g. https://yourdomain.com ): ").strip()
        webhook_url = f"{public_domain}{webhook_path}"
    else:
        webhook_url = f"{WEBHOOK_URL}{webhook_path}"
    print(f"\nSetting webhook to: {webhook_url}")

    result = set_telegram_webhook(
        token=TELEGRAM_BOT_TOKEN,
        url=webhook_url,
        max_connections=18,
        drop_pending_updates=True
    )
    if result.get('ok'):
        print("\n✅ Webhook set successfully!")
        print("Telegram response:", json.dumps(result, indent=2))
    else:
        print("\n❌ Failed to set webhook.")
        print("Error:", result.get('description', 'Unknown error'))
