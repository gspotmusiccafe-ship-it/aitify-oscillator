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

# --- FIREBASE HANDSHAKE ---
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {'storageBucket': 'aititrade-radio-97.firebasestorage.app'})
bucket = storage.bucket()

@app.route('/')
def home():
    return """
    <body style="background:#000; color:#0f0; font-family:monospace; padding:50px;">
        <h1 style="color:#f0f; border-bottom:2px solid #222; padding-bottom:10px;">97.7 THE FLAME | REGULATOR ACTIVE</h1>
        <div style="margin-top:20px; font-size:18px;">
            <p>> SYSTEM: ONLINE</p>
            <p>> KINETIC FEED: ACTIVE</p>
            <p>> DATA SOURCE: <a href="/api/market-data" style="color:#0f0;">/api/market-data</a></p>
        </div>
    </body>
    """

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    live_assets = []
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        live_assets.append({
            "id": song['id'], "title": song['title'], 
            "current_price": price, "current_pct": current_pct,
            "is_closed": current_pct >= 60
        })
    response = make_response(jsonify({"assets": live_assets}))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    song_id = request.json.get('song_id', 0)
    song = next((s for s in SONG_ASSETS if s['id'] == song_id), SONG_ASSETS[0])
    url = bucket.blob(song['file']).generate_signed_url(expiration=3600)
    return jsonify({"stream_url": url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
