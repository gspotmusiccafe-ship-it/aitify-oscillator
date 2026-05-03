from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- [1] PRODUCTION MINT ROOM ---
@app.route('/mint')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | MINT ROOM</title>
        <style>
            :root { --green: #00ff33; }
            body { background: #010101; color: var(--green); font-family: 'IBM Plex Mono'; padding: 40px; }
            .station { border: 1px solid var(--green); padding: 30px; background: #0a0a0a; box-shadow: 0 0 20px rgba(0,255,51,0.2); }
            input { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 12px; margin-top: 15px; }
            .btn { background: var(--green); color: #000; border: none; padding: 20px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 20px; text-transform: uppercase; }
        </style>
    </head>
    <body>
        <a href="/" style="color:var(--green); text-decoration:none; font-size:12px;"><< LIVE EXCHANGE</a>
        <div class="station">
            <h2>MINT & BROADCAST</h2>
            <form action="/stock_asset" method="post" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="SONG TITLE" required>
                <input type="text" name="artist" placeholder="ARTIST NAME" required>
                <input type="number" step="0.01" name="price" placeholder="MINT PRICE" required>
                <div style="margin-top:20px;">AUDIO (.MP3): <input type="file" name="audio" required></div>
                <div style="margin-top:10px;">COVER (.JPG): <input type="file" name="image" required></div>
                <button type="submit" class="btn">COMMIT & BROADCAST LIVE</button>
            </form>
        </div>
    </body>
    </html>
    ''')

# --- [2] THE SYNCED STOCKING (DB + ASSETS) ---
@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    try:
        title, artist, price = request.form.get('title'), request.form.get('artist'), request.form.get('price')
        audio, image = request.files['audio'], request.files['image']
        # Use clean filenames to prevent radio breaks
        a_fn = secure_filename(f"{artist}_{title}.mp3")
        i_fn = secure_filename(f"{artist}_{title}.jpg")
        audio.save(os.path.join(app.config['UPLOAD_FOLDER'], a_fn))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], i_fn))
        
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("""
            INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) 
            VALUES (%s, %s, %s, %s)
        """, (f"{artist} - {title}", f"/static/uploads/{a_fn}", f"/static/uploads/{i_fn}", price))
        conn.commit(); cur.close(); conn.close()
        return redirect('/')
    except Exception as e:
        return f"SYNC ERROR: {str(e)}"

# --- [3] DUAL-FEED EXCHANGE ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | 97.7 THE FLAME</title>
        <style>
            :root { --green: #00ff33; --glass: rgba(255,255,255,0.03); }
            body { background: #000; color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            .radio-bar { background: #0a0a0a; border-bottom: 2px solid var(--green); padding: 25px 50px; display: grid; grid-template-columns: 100px 1fr 200px; gap: 30px; align-items: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 10; position: relative; }
            #floor { height: calc(100vh - 150px); overflow-y: auto; background: linear-gradient(180deg, #050505 0%, #000 100%); }
            .asset-row { display: grid; grid-template-columns: 80px 2fr 120px 180px 140px; padding: 25px 50px; border-bottom: 1px solid #111; cursor: pointer; transition: 0.2s; }
            .asset-row:hover { background: var(--glass); border-left: 4px solid var(--green); }
            .ticker { font-size: 2.8em; color: var(--green); font-weight: 900; letter-spacing: -3px; text-shadow: 0 0 10px rgba(0,255,51,0.3); }
            .btn { background: var(--green); color: #000; border: none; padding: 12px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
            audio::-webkit-media-controls-panel { background-color: #00ff33; }
        </style>
        <script>
            async function sync() {
                const res = await fetch('/api/data');
                const data = await res.json();
                if (data.roster) {
                    document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                        <div class="asset-row" onclick="broadcast('${i.song}', '${i.audio}', '${i.image}')">
                            <div style="color:#444;">${1001 + idx}</div>
                            <div><b style="font-size:1.3em;">${i.song}</b><br><span style="color:var(--green); font-size:9px; letter-spacing:2px;">ON-AIR ELIGIBLE</span></div>
                            <div style="color:#666; font-size:1.1em;">$${i.principal}</div>
                            <div class="ticker">$${i.current_price}</div>
                            <button class="btn" onclick="event.stopPropagation(); alert('Trade Logged to Ledger')">TRADE</button>
                        </div>
                    `).join('');
                }
            }
            function broadcast(title, audioSrc, img) {
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img || '';
                const player = document.getElementById('master-player');
                player.src = audioSrc;
                player.load();
                player.play().catch(e => console.log("User must click to play audio"));
            }
            setInterval(sync, 3000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="radio-bar">
            <img id="cover" style="width:100px; height:100px; border:1px solid var(--green); object-fit: cover;" src="https://via.placeholder.com/100?text=AITIFY">
            <div>
                <span style="color:var(--green); font-size:10px; letter-spacing:4px;">97.7 THE FLAME BROADCAST</span><br>
                <b id="now-playing" style="font-size:1.8em; color:#fff;">SELECT ASSET TO GO LIVE</b><br>
                <audio id="master-player" controls style="width:100%; height:35px; margin-top:10px;"></audio>
            </div>
            <button class="btn" style="height:60px; font-size:14px;" onclick="location.href='/mint'">OPEN MINT ROOM</button>
        </div>
        <div id="floor"></div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = []
        for r in cur.fetchall():
            p = float(r[3]) if r[3] else 1.00
            roster.append({
                "song": r[0].upper(), "audio": r[1], "image": r[2], 
                "principal": "{:.2f}".format(p),
                "current_price": "{:.2f}".format(p * 1.4 + random.uniform(-0.03, 0.03))
            })
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except Exception as e:
        return jsonify({"error": str(e), "roster": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
