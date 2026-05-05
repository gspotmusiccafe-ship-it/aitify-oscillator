import os
import random
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# --- BANKER'S CONTROL PANEL ---
# You can change these two numbers anytime to shift the entire market logic
BANKER_FORECAST = 75  # The "Vision" target shown to the market
BANKER_CLOSE = 60     # The "Execution" point where you pull the trigger
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
    # Adding a dynamic query check: 
    # Use ?forecast=80&close=50 in the URL to override the Banker Panel instantly
    forecast = request.args.get('forecast', BANKER_FORECAST, type=int)
    close = request.args.get('close', BANKER_CLOSE, type=int)

    ticker_html = "<body style='background:black;color:#00ff00;font-family:monospace;padding:20px;'>"
    ticker_html += f"<h1 style='color:white;'>97.7 THE FLAME | REGULATOR: {forecast}% / {close}%</h1><hr>"
    
    for song in SONG_ASSETS:
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        
        is_closed = current_pct >= close
        status = "TARGET HIT" if current_pct >= forecast else "FORECASTING"
        signal = "MARKET CLOSED" if is_closed else "OPEN"
        
        color = "#ff00ff" if is_closed else "#00ff00"
        
        ticker_html += f"""
        <div style='border:2px solid {color};padding:15px;margin-bottom:10px;background:#111;'>
            <b style='color:white;'>{song['title']}</b> | MKT: {current_pct}% (${market_price})<br>
            <span style='color:{color}; font-weight:bold;'>[{signal}]</span> 
            <small style='color:#666;'> (Target: {forecast}% | Banker Close: {close}%)</small>
        </div>
        """
    return ticker_html + "</body>"

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    # Power Move: This endpoint now accepts custom close instructions
    data = request.json
    song_id = data.get('song_id', 0)
    banker_override = data.get('close_at', BANKER_CLOSE)
    
    song = next((s for s in SONG_ASSETS if s['id'] == song_id), SONG_ASSETS[0])
    blob = bucket.blob(song['file'])
    url = blob.generate_signed_url(expiration=3600)
    
    return jsonify({
        "status": "TRADED",
        "asset": song['title'],
        "stream_url": url,
        "banker_instruction": f"CLOSE_AT_{banker_override}_PERCENT"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
