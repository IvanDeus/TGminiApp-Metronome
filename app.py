import logging
from flask import Flask, render_template, request, jsonify
from app_cfg import TELEGRAM_BOT_TOKEN, DEBUG, bot_lport
import hashlib
import hmac
import json
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database initialization
DATABASE = 'users_db.sqlite'

def get_db():
    db = getattr(app, '_database', None)
    if db is None:
        db = app._database = sqlite3.connect(DATABASE)
        # Enable foreign key support (optional)
        db.execute('PRAGMA foreign_keys = ON')
        db.row_factory = sqlite3.Row  # Access rows as dictionaries
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(app, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')
        language_code = user_data.get('language_code', 'en')
        is_premium = user_data.get('is_premium', False)
        photo_url = user_data.get('photo_url', '')

        db = get_db()
        cur = db.cursor()

        # Check if user exists
        cur.execute("SELECT * FROM telegram_users WHERE user_id = ?", (user_id,))
        existing_user = cur.fetchone()

        if not existing_user:
            cur.execute("""
                INSERT INTO telegram_users (
                    user_id, telegram_id, is_bot, first_name, last_name, username,
                    language_code, is_premium, photo_url, bpm, is_subbed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_id, user_data.get('is_bot', False),
                first_name, last_name, username,
                language_code, is_premium, photo_url,
                90, 0
            ))
        else:
            cur.execute("""
                UPDATE telegram_users SET
                    first_name = ?,
                    username = ?,
                    photo_url = ?
                WHERE user_id = ?
            """, (first_name, username, photo_url, user_id))

        db.commit()

        return jsonify({
            'user_id': user_id,
            'first_name': first_name,
            'username': username,
            'photo_url': photo_url
        })

    except Exception as e:
        db.rollback()
        print("Error parsing initData:", e)
        return jsonify({"error": "Invalid initData"}), 400


if __name__ == '__main__':
    # Initialize DB schema if needed
    init_db()  # Run once to create tables
    logging.basicConfig(filename=logfpath, level=logging.INFO)
    app.run(host='127.0.0.1', port=bot_lport, debug=DEBUG)
