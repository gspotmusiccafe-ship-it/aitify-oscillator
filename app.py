import os
import json
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# 1. THE FULL 12-TRACK ROSTER
SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "price": 1.05},
    {"id": 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "price": 0.98},
    {"id": 2, "title": "LOVE MAKE OVER", "file": "LOVE MAKE OVER.mp3", "price": 1.12},
    {"id": 3, "title": "TIMES UP", "file": "TIMES UP.mp3", "price": 0.85},
    {"id": 4, "title": "SILENT CRIES", "file": "SILENT CRIES NOBODY HEARS.mp3", "price": 1.20},
    {"id": 5, "title": "G-SPOT CLASSIC", "file": "G_SPOT_RECORDS_THEME.mp3", "price": 2.50},
    {"id": 6, "title": "NAWFSIDE KING", "file": "NAWFSIDE_KING.mp3", "price": 1.10},
    {"id": 7, "title": "BLUE FLAME SOUL", "file": "BLUE_FLAME_SOUL.mp3", "price": 0.95},
    {"id": 8, "title": "SONGETRY VOL 1", "file": "SONGETRY_1.mp3", "price": 1.30},
    {"id": 9, "title": "SHANAE BUTTA", "file": "MS_BUTTA_VIBE.mp3", "price": 1.15},
    {"id": 10, "title": "BLACK NEON", "file": "BLACK_NEON_SAINTS.mp3", "price": 1.02},
    {"id": 11, "title": "SHOWTOWN THEME", "file": "SHOWTOWN_NEWS.mp3", "price": 0.90}
]

# 2. FIREBASE HANDSHAKE
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'aititrade-radio-97.firebasestorage.app'
    })

bucket = storage.bucket()

# 3. THE LIVE MARKET TICKER
@app.route('/')
def health_check():
    ticker_html = "<body style='background:black;color:#00ff00;font-family:monospace;padding:20px;'>"
    ticker_html += "<h1 style='color:white;'>97.7 THE FLAME | LIVE MUSIC MARKET</h1><hr>"
    ticker_html += "<div style='display:grid;grid-template-columns: 1fr 1fr;gap:10px;'>"
    for song in SONG_ASSETS:
        ticker_html += f"<div style='border:1px solid #333;padding:10px;'>{song['title']}: <span style='color:cyan;'>${song['price']}</span></div>"
    ticker_html += "</div></body>"
    return ticker_html

# 4. THE TRADE EXECUTION (The "Bastard" Hook)
@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    song_id = data.get('song_id', 0)
    
    # Secure validation
    if song_id >= len(SONG_ASSETS):
        return jsonify({"error": "Asset not found"}), 404
        
    song = SONG_ASSETS[song_id]
    blob = bucket.blob(song['file'])
    
    # Generate the 1-hour "Trade Access" URL
    url = blob.generate_signed_url(expiration=3600)
    
    return jsonify({
        "status": "TRADED",
        "song": song['title'],
        "stream_url": url,
        "market_impact": "BULLISH"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
