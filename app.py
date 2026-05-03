from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os

app = Flask(__name__)
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- [1] THE CLEAN PUBLIC EXCHANGE (V30) ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | 97.7 THE FLAME</title>
        <style>
            :root { --green: #00ff33; --blue: #0088ff; --gold: #ffcc00; --glass: rgba(255,255,255,0.03); }
            body { background: #000; color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            .radio-bar { background: #0a0a0a; border-bottom: 2px solid var(--green); padding: 25px 50px; display: grid; grid-template-columns: 110px 1fr; gap: 30px; align-items: center; }
            #floor { height: calc(100vh - 150px); overflow-y: auto; }
            .asset-row { display: grid; grid-template-columns: 80px 2fr 120px 180px 300px; padding: 25px 50px; border-bottom: 1px solid #111; align-items: center; }
            .ticker { font-size: 2.8em; color: var(--green); font-weight: 900; letter-spacing: -4px; }
            
            .trade-group { display: flex; gap: 10px; }
            .mbbo-btn { 
                flex: 1; border: 1px solid #333; background: #111; color: #fff; 
                padding: 10px 5px; font-size: 10px; font-weight: bold; cursor: pointer; text-transform: uppercase;
                transition: 0.2s;
            }
            .mbbo-btn:hover { border-color: #fff; }
            .mbbo-btn.static:active { background: var(--green); color: #000; box-shadow: 0 0 15px var(--green); }
            .mbbo-btn.forecast:active { background: var(--blue); color: #fff; box-shadow: 0 0 15px var(--blue); }
            .mbbo-btn.currency:active { background: var(--gold); color: #000; box-shadow: 0 0 15px var(--gold); }
            
            #cover { width: 100px; height: 100px; border: 1px solid var(--green); object-fit: cover; }
        </style>
        <script>
            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                        <div class="asset-row">
                            <div style="color:#444;">${1001 + idx}</div>
                            <div><b>${i.song}</b><br><span style="color:var(--green); font-size:9px;">MBBO ACTIVE</span></div>
                            <div style="color:#666;">$${i.principal}</div>
                            <div class="ticker" id="price-${idx}">$${i.current_price}</div>
                            <div class="trade-group">
                                <button class="mbbo-btn static" onclick="openTrade('${idx}', 'STATIC', '${i.song}', '${i.audio}', '${i.image}')">Static</button>
                                <button class="mbbo-btn forecast" onclick="openTrade('${idx}', 'FORECAST', '${i.song}', '${i.audio}', '${i.image}')">Forecast</button>
                                <button class="mbbo-btn currency" onclick="openTrade('${idx}', 'CURRENCY', '${i.song}', '${i.audio}', '${i.image}')">Currency</button>
                            </div>
                        </div> `).join('');
                }
            }

            function openTrade(idx, type, title, audio, img) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = type + " TRADE: " + title;
                document.getElementById('cover').src = img;
                player.src = audio;
                player.load(); player.play();
                alert(type + " Trade Executed. Market window open for duration of track.");
            }
            setInterval(sync, 4000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="radio-bar">
            <img id="cover" src="https://via.placeholder.com/100?text=AITIFY">
            <div>
                <span style="color:var(--green); font-size:10px; letter-spacing:5px;">AITIFY RAPID EXCHANGE</span><br>
                <b id="now-playing" style="font-size:2em;">SELECT MBBO PATHWAY</b><br>
                <audio id="master-player" controls style="width:100%; height:30px; margin-top:10px;"></audio>
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
    except: return jsonify({"roster": []})

@app.route('/mint-admin-portal')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head><title>AITIFY | STUDIO</title></head>
    <body style="background:#000; color:#0f3; padding:50px; font-family:monospace;">
        <div style="border:1px solid #0f3; padding:20px; max-width:500px; margin:auto;">
            <h1>MINT MBBO ASSET</h1>
            <form action="/stock_asset" method="post">
                <input type="text" name="title" placeholder="ASSET NAME" style="width:100%; margin-bottom:10px;"><br>
                <input type="text" name="artist" placeholder="ARTIST" style="width:100%; margin-bottom:10px;"><br>
                <input type="number" step="0.01" name="price" placeholder="MINT PRICE" style="width:100%; margin-bottom:10px;"><br>
                <input type="text" name="audio_url" placeholder="FIREBASE AUDIO URL" style="width:100%; margin-bottom:10px;"><br>
                <input type="text" name="image_url" placeholder="FIREBASE IMAGE URL" style="width:100%; margin-bottom:10px;"><br>
                <button type="submit" style="width:100%; padding:15px; background:#0f3; color:#000; font-weight:bold;">MINT TO FLOOR</button>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    title, artist, price = request.form.get('title'), request.form.get('artist'), request.form.get('price')
    audio, image = request.form.get('audio_url'), request.form.get('image_url')
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)", (f"{artist} - {title}", audio, image, price))
    conn.commit(); cur.close(); conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
