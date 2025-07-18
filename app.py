import logging
import traceback
from flask import Flask, render_template, request, jsonify, g
from app_cfg import TELEGRAM_BOT_TOKEN, DEBUG, BOT_LPORT, LOGFPATH, DATABASE
import hashlib
import hmac
import json
import sqlite3
import os
import telebot
from urllib.parse import unquote, parse_qs, unquote_plus
# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Database init
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, '_sqlite_db'):
        g._sqlite_db = sqlite3.connect(DATABASE)
        g._sqlite_db.row_factory = sqlite3.Row
    return g._sqlite_db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_sqlite_db', None)
    if db is not None:
        db.close()
        #app.logger.debug("Closed SQLite connection.")
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
# Integrity check 
def verify_telegram_data(data):
    """
    Verify Telegram init data signature
    https://core.telegram.org/bots/webapps #validating-data
    """
    received_hash = data.pop("hash", "")
    data_check_arr = []
    for key in sorted(data.keys()):
        value = data[key]
        if isinstance(value, str) and '=' in value:
            value = value.replace('=', r'\=')
        data_check_arr.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_arr)
    secret_key = hmac.new("WebAppData".encode(), TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    #app.logger.info("Received hash: %s", received_hash)
    #app.logger.info("Calculated hash: %s", calculated_hash)
    #app.logger.info("Data check string:\n%s", data_check_string)
    return calculated_hash == received_hash
# Main web page
@app.route('/')
def index():
    return render_template('load.html')
# Get initial user data from app
@app.route('/init_telegram', methods=['POST'])
def init_telegram():
    raw_data = request.form.get('initData', '')
    #app.logger.info("Raw initData received: %s", raw_data)
    #app.logger.info("Unquoted initData: %s", unquote_plus(raw_data))    
    if not raw_data:
        return jsonify({"error": "Missing initData"}), 400
    try:
        parsed_data = parse_qs(raw_data)
        data_dict = {k: v[0] for k, v in parsed_data.items()}
        if not verify_telegram_data(data_dict):
            return jsonify({"error": "Invalid signature"}), 401
        if 'user' not in data_dict:
            return jsonify({"error": "Missing user in initData"}), 400
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
        # Get BPM before returning
        cur.execute("SELECT bpm FROM telegram_users WHERE user_id = ?", (user_id,))
        bpm = cur.fetchone()['bpm']
        return jsonify({
            'user_id': user_id,
            'first_name': first_name,
            'username': username,
            'photo_url': photo_url,
            'bpm': bpm
        })
    except json.JSONDecodeError as je:
        app.logger.error("JSON decode error: %s", str(je))
        return jsonify({"error": "Invalid user JSON"}), 400
    except sqlite3.Error as se:
        app.logger.error("Database error: %s", str(se))
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        app.logger.error("Error processing initData: %s", str(e))
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
# handle updates 
@app.route('/update_user_prefs', methods=['POST'])
def update_user_prefs():
    user_id = request.form.get('user_id')
    bpm = request.form.get('bpm')
    if not user_id or not bpm:
        app.logger.warning("Missing user_id or bpm in update_user_prefs request.")
        return jsonify({"error": "Missing user_id or bpm"}), 400
    try:
        user_id = int(user_id)
        bpm = int(bpm)
    except ValueError:
        app.logger.warning(f"Invalid user_id or bpm format: user_id={user_id}, bpm={bpm}")
        return jsonify({"error": "Invalid user_id or bpm format"}), 400
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "UPDATE telegram_users SET bpm = ? WHERE user_id = ?",
            (bpm, user_id)
        )
        db.commit()
        #app.logger.info(f"User {user_id} BPM updated to {bpm}.")
        return jsonify({"success": True}), 200
    except sqlite3.Error as se:
        app.logger.error(f"Database error updating user {user_id} prefs: {str(se)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in update_user_prefs for user {user_id}: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
# Telegram BOT here
def tgmessage_user(telegram_id, message):
    try:
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        sent_message = bot.send_message(
            telegram_id, 
            message, 
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        #app.logger.info(f"Message sent to {telegram_id}: {message[:50]}...") 
        return True
    except telebot.apihelper.ApiTelegramException as api_error:
        if api_error.error_code == 403:
            app.logger.warning(f"User {telegram_id} blocked the bot or can't receive messages")
        else:
            app.logger.error(f"Telegram API error sending to {telegram_id}: {str(api_error)}")
        return False
    except Exception as e:
        app.logger.error(f"Error sending Telegram message to {telegram_id}: {str(e)}")
        app.logger.error(traceback.format_exc())
        return False
# Telegram Bot Webhook
@app.route('/whook', methods=['POST'])
def telegram_webhook():
    db = None
    try:
        update = request.get_json()
        if not update:
            app.logger.warning("No data received in webhook")
            return jsonify({'status': 'No data'}), 400
        db = get_db()
        cur = db.cursor()
        # Process message or callback query
        if 'message' in update:
            msg = update['message']
            chat_id = msg['from']['id']
            text = msg.get('text', '')
            user_id = msg['from']['id']
            language_code = msg['from'].get('language_code', 'en')
            # Check if user exists in database
            cur.execute("SELECT * FROM telegram_users WHERE user_id = ?", (user_id,))
            user = cur.fetchone()
            if text == '/start':
                if user:
                    welcome_msg = f"Welcome back, {user['first_name']}!"
                else:
                    welcome_msg = "Welcome! Please use our web app to get started."
                tgmessage_user(chat_id, welcome_msg)
            else:
                tgmessage_user(chat_id, "Please use our web interface for full functionality.")
        elif 'callback_query' in update:
            callback = update['callback_query']
            chat_id = callback['from']['id']
            data = callback.get('data', '')
            tgmessage_user(chat_id, f"Action received: {data}")
        return '', 204
    except sqlite3.Error as se:
        app.logger.error(f"Database error in webhook: {str(se)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    except Exception as e:
        app.logger.error(f"Error in webhook: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if db:
            db.close()
# Run flask web app      
if __name__ == '__main__':
    # Only initialize DB if the file doesn't exist
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')
    #logging.basicConfig(filename=LOGFPATH, level=logging.INFO)
    app.run(host='127.0.0.1', port=BOT_LPORT, debug=DEBUG)
