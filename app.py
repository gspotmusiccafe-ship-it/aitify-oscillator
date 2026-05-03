from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# STORAGE CONFIG
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SECURE NEON CONNECTION
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- [1] THE MINTING SUITE (ADMIN ONLY) ---
@app.route('/mint')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | MINTING SUITE</title>
        <style>
            :root { --bloomberg-green: #00ff33; }
            body { background: #010101; color: var(--bloomberg-green); font-family: 'IBM Plex Mono'; padding: 40px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .station { border: 1px solid var(--bloomberg-green); padding: 20px; background: #0a0a0a; box-shadow: 0 0 15px rgba(0,255,51,0.1); }
            input, textarea { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 10px; margin-top: 10px; font-family: inherit; }
            .action-btn { background: var(--bloomberg-green); color: #000; border: none; padding: 15px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; text-transform: uppercase; }
            .nav-link { color: var(--bloomberg-green); text-decoration: none; font-size: 10px; margin-bottom: 20px; display: block; letter-spacing: 2px; }
        </style>
    </head>
    <body>
        <a href="/" class="nav-link"><< BACK TO TRADING FLOOR</a>
        <h1 style="letter-spacing: 5px;">AITIFY PRODUCTION ROOM</h1>
        <div class="grid">
            <div class="station">
                <h3>[1] GENERATION ENGINE</h3>
                <input type="text" placeholder="ENTER LYRIC OR IMAGE PROMPT">
                <button class="action-btn" onclick="alert('Minting Assets...')">GENERATE</button>
                <textarea rows="4" placeholder="AI OUTPUT WILL APPEAR HERE"></textarea>
            </div>
            <div class="station">
                <h3>[2] STOCK THE EXCHANGE</h3>
                <form action="/stock_asset" method="post" enctype="multipart/form-data">
                    <input type="text" name="title" placeholder="SONG TITLE" required>
                    <input type="text" name="artist" placeholder="ARTIST" required>
                    <input type="number" step="0.01" name="price" placeholder="PRICE ($1-$5)" required>
                    <div style="font-size:10px; margin-top:10px;">AUDIO (.MP3): <input type="file" name="audio" required></div>
                    <div style="font-size:10px; margin-top:10px;">COVER (.JPG): <input type="file" name="image" required></div>
                    <button type="submit" class="action-btn">COMMIT TO FLOOR</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    ''')

# --- [2] STOCKING ACTION (NEON INJECTION) ---
@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    title = request.form.get('title')
    artist = request.form.get('artist')
    price = request.form.get('price')
    audio = request.files['audio']
    image = request.files['image']
    
    a_fn = secure_filename(f"{artist}_{title}.mp3")
    i_fn = secure_filename(f"{artist}_{title}.jpg")
    audio.save(os.path.join(app.config['UPLOAD_FOLDER'], a_fn))
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], i_fn))
    
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)",
                (f"{artist} - {title}", f"/static/uploads/{a_fn}", f"/static/uploads/{i_fn}", price))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('index'))

# --- [3] TRADING FLOOR (TERMINAL) ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | TERMINAL V19</title>
        <style>
            :root { --bloomberg-green: #00ff33; }
            body { background: #010101; color: #e0e0e0; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            .header { background: #0a0a0a; border-bottom: 1px solid var(--bloomberg-green); padding: 20px 40px; display: grid; grid-template-columns: 120px 1fr 220px; align-items: center; gap: 30px; }
            .art-box { width: 100px; height: 100px; border: 1px solid var(--bloomberg-green); background: #111; object-fit: cover; }
            #floor { overflow-y: auto; height: calc(100vh - 145px); }
            .row { display: grid; grid-template-columns: 70px 2fr 100px 150px 120px; padding: 15px 40px; border-bottom: 1px solid #222; cursor: pointer; }
            .price { font-size: 2em; color: var(--bloomberg-green); font-weight: 900; letter-spacing: -2px; }
            .btn { background: var(--bloomberg-green); color: #000; border: none; padding: 10px; font-weight: bold; cursor: pointer; width: 100%; text-transform: uppercase; }
        </style>
        <script>
            async function update() {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('floor').innerHTML = data.roster.map(i => `
                    <div class="row" onclick="play('${i.song}', '${i.audio}', '${i.image}')">
                        <div style="color:#444;">1001</div>
                        <div><b>${i.song.toUpperCase()}</b><br><span style="font-size:9px; color:var(--bloomberg-green);">CONTRACT ACTIVE</span></div>
                        <div style="color:#666; text-align:center;">$${i.principal}</div>
                        <div class="price">$${i.current_price}</div>
                        <button class="btn" onclick="event.stopPropagation(); alert('Trade Processed')">TRADE</button>
                    </div>
                `).join('');
            }
            function play(s, a, i) {
                document.getElementById('title').innerText = s;
                document.getElementById('art').src = i || '';
                const p = document.getElementById('player'); p.src = a; p.play();
            }
            setInterval(update, 3000); window.onload = update;
        </script>
    </head>
    <body>
        <div class="header">
            <img id="art" class="art-box" src="https://via.placeholder.com/100?text=AITIFY">
            <div>
                <b id="title" style="font-size:1.5em; color:#fff;">SELECT ASSET TO BROADCAST</b><br>
                <audio id="player" controls style="filter: invert(100%); height: 30px; margin-top: 10px; opacity: 0.8;"></audio>
            </div>
            <button class="btn" style="height: 60px;" onclick="location.href='/mint'">OPEN PRODUCTION ROOM</button>
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
        roster = []
        for r in cur.fetchall():
            p = float(r[3]) if r[3] else 1.00
            roster.append({"song": r[0], "audio": r[1], "image": r[2], "principal": p, "current_price": "{:.2f}".format(p * 1.4 + random.uniform(-0.05, 0.05))})
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except: return jsonify({"roster": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
