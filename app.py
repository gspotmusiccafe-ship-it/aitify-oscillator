import os
import random
from flask import Flask, jsonify, request, make_response
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# --- THE BANKER'S BRAIN ---
SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "floor": 0.85, "ceiling": 2.50},
    {"id: 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "floor": 0.90, "ceiling": 3.00},
    {"id": 4, "title": "SILENT CRIES", "file": "SILENT CRIES NOBODY HEARS.mp3", "floor": 0.95, "ceiling": 5.00},
    {"id": 5, "title": "G-SPOT CLASSIC", "file": "G_SPOT_RECORDS_THEME.mp3", "floor": 1.20, "ceiling": 10.00},
]

# --- FIREBASE HANDSHAKE ---
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {'storageBucket': 'aititrade-radio-97.firebasestorage.app'})
bucket = storage.bucket()

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    # Force regulation from URL or defaults
    forecast = request.args.get('forecast', 75, type=int)
    close = request.args.get('close', 60, type=int)
    
    live_assets = []
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        live_assets.append({
            "id": song['id'], 
            "title": song['title'], 
            "current_price": market_price, 
            "current_pct": current_pct,
            "is_closed": current_pct >= close
        })
    
    # 🏦 THE BROWSER FIX: This header kills the "Same Shit" caching
    response = make_response(jsonify({"assets": live_assets, "regulator": {"forecast": forecast, "close": close}}))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    song_id = data.get('song_id', 0)
    song = next((s for s in SONG_ASSETS if s['id'] == song_id), SONG_ASSETS[0])
    blob = bucket.blob(song['file'])
    url = blob.generate_signed_url(expiration=3600)
    return jsonify({"status": "SUCCESS", "stream_url": url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
