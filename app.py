import os
import random
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# --- BANKER'S CONTROL PANEL ---
BANKER_FORECAST = 75  
BANKER_CLOSE = 60     
# ------------------------------

SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "floor": 0.85, "ceiling": 2.50},
    {"id": 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "floor": 0.90, "ceiling": 3.00},
    {"id": 4, "title": "SILENT CRIES", "file": "SILENT CRIES NOBODY HEARS.mp3", "floor": 0.95, "ceiling": 5.00},
    {"id": 5, "title": "G-SPOT CLASSIC", "file": "G_SPOT_RECORDS_THEME.mp3", "floor": 1.20, "ceiling": 10.00},
]

if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {'storageBucket': 'aititrade-radio-97.firebasestorage.app'})
bucket = storage.bucket()

@app.route('/')
def mbbo_terminal():
    forecast = request.args.get('forecast', BANKER_FORECAST, type=int)
    close = request.args.get('close', BANKER_CLOSE, type=int)
    ticker_html = "<body style='background:black;color:#00ff00;font-family:monospace;padding:20px;'>"
    ticker_html += f"<h1 style='color:white;'>97.7 THE FLAME | REGULATOR: {forecast}% / {close}%</h1><hr>"
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        is_closed = current_pct >= close
        color = "#ff00ff" if is_closed else "#00ff00"
        ticker_html += f"<div style='border:2px solid {color};padding:15px;margin-bottom:10px;background:#111;'>"
        ticker_html += f"<b style='color:white;'>{song['title']}</b> | MKT: {current_pct}% (${market_price})<br>"
        ticker_html += f"<span style='color:{color}; font-weight:bold;'>[{'MARKET CLOSED' if is_closed else 'OPEN'}]</span>"
        ticker_html += f" <small style='color:#666;'> (Target: {forecast}% | Banker Close: {close}%)</small></div>"
    return ticker_html + "</body>"

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    forecast = request.args.get('forecast', BANKER_FORECAST, type=int)
    close = request.args.get('close', BANKER_CLOSE, type=int)
    live_assets = []
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        live_assets.append({
            "id": song['id'], "title": song['title'], "floor": song['floor'],
            "current_price": market_price, "current_pct": current_pct,
            "is_closed": current_pct >= close, "is_target_hit": current_pct >= forecast
        })
    return jsonify({"assets": live_assets, "regulator": {"forecast": forecast, "close": close}})

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    song_id = data.get('song_id', 0)
    song = next((s for s in SONG_ASSETS if s['id'] == song_id), SONG_ASSETS[0])
    blob = bucket.blob(song['file'])
    url = blob.generate_signed_url(expiration=3600)
    return jsonify({"status": "TRADED", "asset": song['title'], "stream_url": url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
