import logging
from flask import Flask, render_template, request, jsonify
from app_cfg import TELEGRAM_BOT_TOKEN, DEBUG, bot_lport
from tinydb import TinyDB, Query
import hashlib
import hmac
import json

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize TinyDB
db = TinyDB('users_db.json')
User = Query()

ERROR_MESSAGES = {
    'no_tg': 'This app only works inside Telegram.'
}

def verify_telegram_data(data):
    """
    Verify Telegram init data signature
    https://core.telegram.org/bots/webapps #validating-data
    """
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    received_hash = data.get("hash", "")
    data.pop("hash", None)
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == received_hash

@app.route('/')
def index():
    return render_template(
        'metr.html',
        ERROR_MESSAGES=ERROR_MESSAGES,
        photo_url=request.args.get('photo_url', '')
    )

@app.route('/init_telegram', methods=['POST'])
def init_telegram():
    raw_data = request.form.get('initData', '')
    try:
        data_dict = dict(x.split("=", 1) for x in raw_data.split("&"))
        if not verify_telegram_data(data_dict):
            return jsonify({"error": "Invalid signature"}), 401

        user_data = json.loads(data_dict['user'])

        user_id = user_data['id']
        first_name = user_data.get('first_name', 'Unknown')
        username = user_data.get('username', '')
        photo_url = user_data.get('photo_url', '')

        # Update or insert user
        user_query = User.user_id == user_id
        existing_user = db.search(user_query)

        if not existing_user:
            db.insert({
                'user_id': user_id,
                'telegram_id': user_id,
                'is_bot': user_data.get('is_bot', False),
                'first_name': first_name,
                'last_name': user_data.get('last_name', ''),
                'username': username,
                'language_code': user_data.get('language_code', 'en'),
                'is_premium': user_data.get('is_premium', False),
                'photo_url': photo_url,
                'bpm': 90,
                'is_subbed': 0
            })
        else:
            db.update({
                'first_name': first_name,
                'username': username,
                'photo_url': photo_url
            }, user_query)

        return jsonify({
            'user_id': user_id,
            'first_name': first_name,
            'username': username,
            'photo_url': photo_url
        })

    except Exception as e:
        print("Error parsing initData:", e)
        return jsonify({"error": "Invalid initData"}), 400

if __name__ == '__main__':
    logging.basicConfig(filename=logfpath, level=logging.INFO)
    app.run(host='127.0.0.1', port=bot_lport, debug=DEBUG)
