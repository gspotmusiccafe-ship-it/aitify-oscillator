from flask import Flask, render_template_string, jsonify, request, redirect
import psycopg2, random, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# CONFIG FOR FILE STORAGE
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# YOUR SECURE NEON CONNECTION
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- [1] PRODUCTION ROOM (LYRICS, IMAGE, & MINT) ---
@app.route('/mint')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | MINTING SUITE</title>
        <style>
            :root { --bloomberg-green: #00ff33; --glass: rgba(0, 255, 51, 0.05); }
            body { background: #010101; color: var(--bloomberg-green); font-family: 'IBM Plex Mono'; padding: 40px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .station { border: 1px solid var(--bloomberg-green); padding: 20px; background: #0a0a0a; box-shadow: 0 0 15px rgba(0,255,51,0.1); }
            textarea, input { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 10px; margin-top: 10px; font-family: inherit; }
            .action-btn { background: var(--bloomberg-green); color: #000; border: none; padding: 10px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; text-transform: uppercase; }
            h1 { letter-spacing: 5px; border-bottom: 1px solid var(--bloomberg-green); padding-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>AITIFY PRODUCTION ROOM</h1>
        <div class="grid">
            <div class="station">
                <h3>[1] LYRIC GENERATOR</h3>
                <input type="text" id="prompt" placeholder="Enter Vibe (e.g. Luxury Trap, 90s R&B)">
                <button class="action-btn" onclick="alert('Syncing with AI Engine...')">GENERATE TEXT</button>
                <textarea rows="5" placeholder="Lyrics will appear here..."></textarea>
            </div>
            
            <div class="station">
                <h3>[2] IMAGE GENERATOR</h3>
                <input type="text" placeholder="Visual Prompt">
                <button class="action-btn" onclick="alert('Rendering Cover Art...')">MINT ART</button>
                <div style="height:100px; background:#111; margin-top:10px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; font-size:10px; color:#444;">PREVIEW_RENDER_WAITING</div>
            </div>

            <div class="station" style="grid-column: span 2;">
                <h3>[3] FINAL MINT & STOCK THE MARKET</h3>
                <form action="/stock_asset" method="post" enctype="multipart/form-data" style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <input type="text" name="title" placeholder="SONG TITLE" required>
                    <input type="text" name="artist" placeholder="ARTIST NAME" required>
                    <input type="number" step="0.01" name="price" placeholder="PRICE ($1-$5)" required>
                    <input type="text" name="genre" placeholder="GENRE">
                    <div style="font-size:10px;">AUDIO (.MP3)<input type="file" name="audio" accept="audio/*" required></div>
                    <div style="font-size:10px;">COVER (.JPG)<input type="file" name="image" accept="image/*" required></div>
                    <button type="submit" class="action-btn" style="grid-column: span 2; height: 60px; font-size: 1.2em;">COMMIT ASSET TO EXCHANGE</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    ''')

# --- [2] ADMIN ACTION (STOCKING THE DB) ---
@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    title = request.form.get('title')
    artist = request.form.get('artist')
    price = request.form.get('price')
    audio_file = request.files['audio']
    image_file = request.files['image']
    
    audio_fn = secure_filename(f"{title}_{artist}.mp3")
    image_fn = secure_filename(f"{title}_{artist}.jpg")
    
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_fn))
    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_fn))
    
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("""
        INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price, status)
        VALUES (%s, %s, %s, %s, 'LIVE')
    """, (f"{artist} - {title}", f"/static/uploads/{audio_fn}", f"/static/uploads/{image_fn}", price))
    conn.commit(); cur.close(); conn.close()
    return redirect('/')

# --- [3] PUBLIC TRADING FLOOR (BROADCAST TERMINAL) ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | TERMINAL V18</title>
        <style>
            :root { --bloomberg-green: #00ff33; --glass: rgba(255, 255, 255, 0.05); --glass-border: rgba(255, 255, 255, 0.1); }
            body { background: #010101; color: #e0e0e0; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            .radio-unit { background: #0a0a0a; border-bottom: 1px solid var(--bloomberg-green); padding: 20px 40px; display: grid; grid-template-columns: 120px 1fr 200px; align-items: center; gap: 30px; }
            .album-art { width: 100px; height: 100px; border: 1px solid var(--bloomberg-green); background: #111; object-fit: cover; }
            #floor { overflow-y: auto; height: calc(100vh - 145px); }
            .asset-row { display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; align-items: center; padding: 15px 40px; border-bottom: 1px solid var(--glass-border); cursor: pointer; }
            .price-ticker { font-size: 2.2em; font-weight: 900; color: var(--bloomberg-green); letter-spacing: -2px; }
            .trade-btn { background: var(--bloomberg-green); color: #000; border: none; padding: 10px; font-weight: bold; cursor: pointer; width: 100%; text-transform: uppercase; }
        </style>
        <script>
            const urlParams = new URLSearchParams(window.location.search);
            const activeBroker = urlParams.get('broker') || 'HOUSE';

            window.onload = function() {
                document.getElementById('broker-display').innerText = activeBroker;
                updateMarket();
            };

            function loadAsset(song, audio, img) {
                document.getElementById('current-song').innerText = song;
                document.getElementById('main-art').src = img || 'https://via.placeholder.com/100?text=AITIFY';
                const p = document.getElementById('main-player');
                p.src = audio; p.play();
            }

            async function updateMarket() {
                const res = await fetch('/api/data');
                const data = await res.json();
                if (data.error) return;
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                    <div class="asset-row" onclick="loadAsset('${i.song}', '${i.audio}', '${i.image}')">
                        <div style="color:#444;">${1001+idx}</div>
                        <div><b style="color:#fff;">${i.song.toUpperCase()}</b><br><span style="color:var(--bloomberg-green); font-size:8px;">CONTRACT ACTIVE</span></div>
                        <div style="color:var(--bloomberg-green); font-size:9px; border:1px solid; text-align:center;">${i.target_roi}% MBBO</div>
                        <div style="color:#666; text-align:center;">$${i.principal}.00</div>
                        <div class="price-ticker">$${i.current_price}</div>
                        <div style="padding-left:20px;"><button class="trade-btn" onclick="event.stopPropagation(); alert('Trade Sent via: ' + activeBroker)">TRADE NOW</button></div>
                    </div>
                `).join('');
            }
            setInterval(updateMarket, 3000);
        </script>
    </head>
    <body>
        <div class="radio-unit">
            <img id="main-art" class="album-art" src="https://via.placeholder.com/100?text=AITIFY" alt="Art">
            <div>
                <span style="color:var(--bloomberg-green); font-size:9px; letter-spacing:3px;">ACTIVE BROKER: <span id="broker-display"></span></span><br>
                <b id="current-song" style="font-size:1.8em; color:#fff;">SELECT ASSET TO BROADCAST</b><br>
                <audio id="main-player" controls style="height:30px; filter: invert(100%); opacity:0.8;"></audio>
            </div>
            <button class="trade-btn" style="height:50px; font-size:14px;" onclick="location.href='/mint'">OPEN PRODUCTION ROOM</button>
        </div>
        <div id="floor"></div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster LIMIT 50;")
        rows = cur.fetchall()
        roster = []
        for r in rows:
            principal = float(r[3]) if r[3] else 1.00
            target_roi = random.choice([35, 50, 80, 95])
            roster.append({
                "song": r[0], "principal": principal, "target_roi": target_roi,
                "current_price": "{:.2f}".format(principal * 1.4 + random.uniform(-0.1, 0.1)),
                "audio": r[1] if r[1] else "", "image": r[2] if r[2] else ""
            })
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except Exception as e:
        return jsonify({"error": str(e), "roster": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
