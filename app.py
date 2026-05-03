from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- [1] THE CLOSED DOOR: PRIVATE MINTING PORTAL ---
@app.route('/mint-admin-portal')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | ADMIN</title>
        <style>
            :root { --green: #00ff33; }
            body { background: #010101; color: var(--green); font-family: 'IBM Plex Mono'; padding: 40px; }
            .station { border: 1px solid var(--green); padding: 30px; background: #0a0a0a; box-shadow: 0 0 30px rgba(0,255,51,0.4); max-width: 500px; margin: auto; }
            input { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 12px; margin-top: 15px; box-sizing: border-box; }
            .btn { background: var(--green); color: #000; border: none; padding: 20px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 20px; text-transform: uppercase; }
        </style>
    </head>
    <body>
        <div class="station">
            <h1 style="text-align:center; letter-spacing:3px;">PRIVATE MINT</h1>
            <p style="font-size:10px; text-align:center; opacity:0.6;">ADMIN ACCESS ONLY | G. SMOOTH</p>
            <form action="/stock_asset" method="post" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="SONG TITLE" required>
                <input type="text" name="artist" placeholder="ARTIST NAME" required>
                <input type="number" step="0.01" name="price" placeholder="MINT PRICE" required>
                <div style="margin-top:20px; font-size:12px;">MP3: <input type="file" name="audio" accept="audio/*" required></div>
                <div style="margin-top:10px; font-size:12px;">JPG: <input type="file" name="image" accept="image/*" required></div>
                <button type="submit" class="btn">DEPLOY TO FLAME</button>
            </form>
        </div>
    </body>
    </html>
    ''')

# --- [2] THE ASSET SYNC ENGINE ---
@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    try:
        title, artist, price = request.form.get('title'), request.form.get('artist'), request.form.get('price')
        audio, image = request.files['audio'], request.files['image']
        a_fn, i_fn = secure_filename(f"{artist}_{title}.mp3"), secure_filename(f"{artist}_{title}.jpg")
        audio.save(os.path.join(app.config['UPLOAD_FOLDER'], a_fn))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], i_fn))
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)",
                    (f"{artist} - {title}", f"/static/uploads/{a_fn}", f"/static/uploads/{i_fn}", price))
        conn.commit(); cur.close(); conn.close()
        return redirect('/')
    except Exception as e: return f"SYNC ERROR: {str(e)}"

# --- [3] THE PUBLIC EXCHANGE (CLEAN & SYNCHRONIZED) ---
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
            .radio-bar { background: #0a0a0a; border-bottom: 2px solid var(--green); padding: 25px 50px; display: grid; grid-template-columns: 110px 1fr; gap: 30px; align-items: center; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
            #floor { height: calc(100vh - 150px); overflow-y: auto; background: #000; }
            .asset-row { display: grid; grid-template-columns: 80px 2fr 120px 180px 140px; padding: 25px 50px; border-bottom: 1px solid #111; cursor: pointer; transition: 0.1s; }
            .asset-row:hover { background: var(--glass); border-left: 5px solid var(--green); }
            .ticker { font-size: 3em; color: var(--green); font-weight: 900; letter-spacing: -4px; text-shadow: 0 0 10px rgba(0,255,51,0.2); }
            .trade-btn { background: var(--green); color: #000; border: none; padding: 12px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
            #cover { width: 100px; height: 100px; border: 1px solid var(--green); object-fit: cover; background: #111; }
        </style>
        <script>
            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                        <div class="asset-row" onclick="broadcast('${i.song}', '${i.audio}', '${i.image}')">
                            <div style="color:#444;">${1001 + idx}</div>
                            <div><b style="font-size:1.4em;">${i.song}</b><br><span style="color:var(--green); font-size:9px; letter-spacing:2px;">ON-AIR ELIGIBLE</span></div>
                            <div style="color:#666; font-size:1.2em;">$${i.principal}</div>
                            <div class="ticker">$${i.current_price}</div>
                            <button class="trade-btn" onclick="event.stopPropagation(); alert('Trade Sent to Ledger')">TRADE</button>
                        </div> `).join('');
                }
            }
            function broadcast(title, audioSrc, img) {
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                const p = document.getElementById('master-player'); p.src = audioSrc; p.load(); p.play();
            }
            setInterval(sync, 3000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="radio-bar">
            <img id="cover" src="https://via.placeholder.com/100?text=AITIFY">
            <div>
                <span style="color:var(--green); font-size:10px; letter-spacing:5px;">97.7 THE FLAME BROADCAST</span><br>
                <b id="now-playing" style="font-size:2em; color:#fff;">SELECT ASSET TO GO LIVE</b><br>
                <audio id="master-player" controls style="width:100%; height:35px; margin-top:10px; opacity:0.9;"></audio>
            </div>
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "principal": "{:.2f}".format(float(r[3])), "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.04, 0.04))} for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except Exception as e: return jsonify({"error": str(e), "roster": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
