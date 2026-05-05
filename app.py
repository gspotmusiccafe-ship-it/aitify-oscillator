import os
import random
from flask import Flask, jsonify, request, make_response
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# --- THE BANKER'S ASSETS ---
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

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    close_trigger = request.args.get('close', 60, type=int)
    
    live_assets = []
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        live_assets.append({
            "id": song['id'], 
            "title": song['title'], 
            "current_price": market_price, 
            "current_pct": current_pct,
            "is_closed": current_pct >= close_trigger
        })
    
    # 🏦 KILL CACHE: Force the browser to show NEW data every 5 seconds
    response = make_response(jsonify({"assets": live_assets}))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    song_id = request.json.get('song_id', 0)
    song = next((s for s in SONG_ASSETS if s['id'] == song_id), SONG_ASSETS[0])
    url = bucket.blob(song['file']).generate_signed_url(expiration=3600)
    return jsonify({"stream_url": url})
@app.route('/')
def home():
    # This gives the browser something to look at so you don't get a 404
    return "<h1>97.7 THE FLAME | REGULATOR ACTIVE</h1><p>The DEX is pulling data from /api/market-data</p>"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
