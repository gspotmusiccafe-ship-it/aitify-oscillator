import os
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# 1. THE 12-SONG INVENTORY (Direct from your aititrade-radio-97 bucket)
SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "price": 1.05},
    {"id": 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "price": 0.98},
    {"id": 2, "title": "LOVE MAKE OVER", "file": "LOVE MAKE OVER.mp3", "price": 1.12},
    {"id": 3, "title": "TIMES UP", "file": "TIMES UP.mp3", "price": 0.85},
]

# 2. FIREBASE HANDSHAKE
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'aititrade-radio-97.firebasestorage.app'
    })

bucket = storage.bucket()

# 3. THE LIVE TICKER VIEW
@app.route('/')
def health_check():
    ticker_html = "<body style='background:black;color:#00ff00;font-family:monospace;padding:20px;'>"
    ticker_html += "<h1>97.7 THE FLAME | LIVE MARKET</h1><hr>"
    for song in SONG_ASSETS:
        ticker_html += f"<p style='font-size:1.5rem;'>{song['title']}: ${song['price']} <span style='color:green;'>▲</span></p>"
    ticker_html += "</body>"
    return ticker_html

# 4. THE TRADE TRIGGER
@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    song_id = data.get('song_id', 0)
    song = SONG_ASSETS[song_id]
    blob = bucket.blob(song['file'])
    url = blob.generate_signed_url(expiration=3600)
    return jsonify({"status": "TRADED", "song": song['title'], "stream_url": url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
