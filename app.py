import os
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)

# 1. THE 12-SONG INVENTORY (Direct from your aititrade-radio-97 bucket)
SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "price": 1.00},
    {"id": 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "price": 1.00},
    {"id": 2, "title": "LOVE MAKE OVER", "file": "LOVE MAKE OVER.mp3", "price": 1.00},
    {"id": 3, "title": "TIMES UP", "file": "TIMES UP.mp3", "price": 1.00},
    # We will add the other 8 as you verify the filenames
]

# 2. FIREBASE HANDSHAKE
# Note: We'll use an Env Var for the key to keep it secure
if not firebase_admin._apps:
    # This looks for a file we will upload to Render Secrets later
    cred = credentials.Certificate("/etc/secrets/firebase-key.json") 
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'aititrade-radio-97.firebasestorage.app'
    })

bucket = storage.bucket()

@app.route('/')
def health_check():
    return "97.7 THE FLAME | OSCILLATOR ONLINE"

# 3. THE TRADE TRIGGER (The "Cut & Restart")
@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.json
    song_id = data.get('song_id', 0)
    song = SONG_ASSETS[song_id]
    
    # Generate the link for the player to restart at 0:00
    blob = bucket.blob(song['file'])
    url = blob.generate_signed_url(expiration=3600)
    
    return jsonify({
        "status": "TRADED",
        "song": song['title'],
        "stream_url": url,
        "msg": "Restarting stream for buyer..."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
