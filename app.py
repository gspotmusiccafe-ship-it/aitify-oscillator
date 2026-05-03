from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os

app = Flask(__name__)
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | TRADING PORTAL</title>
        <style>
            :root { --green: #00ff33; --blue: #0088ff; --gold: #ffcc00; --bg: #050505; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; }
            
            /* TOP BROADCAST UNIT */
            .master-unit { 
                background: #000; border-bottom: 3px solid var(--green); padding: 20px 40px;
                display: flex; align-items: center; gap: 30px; position: sticky; top: 0; z-index: 100;
            }
            #cover { width: 120px; height: 120px; border: 2px solid var(--green); object-fit: cover; background: #111; }
            
            /* PACECARD GRID */
            .portal-grid { 
                display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); 
                gap: 20px; padding: 40px; 
            }
            .pace-card { 
                background: #0a0a0a; border: 1px solid #222; padding: 25px; 
                border-top: 4px solid var(--green); transition: 0.3s;
            }
            .pace-card:hover { border-color: var(--green); box-shadow: 0 0 20px rgba(0,255,51,0.1); }
            
            .ticker { font-size: 3.5em; font-weight: 900; color: var(--green); letter-spacing: -3px; margin: 10px 0; }
            .asset-name { font-size: 1.4em; text-transform: uppercase; border-bottom: 1px solid #222; padding-bottom: 10px; }
            
            /* BLOOMBERG MBBO BUTTONS */
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px; }
            .mbbo-btn { 
                padding: 15px 5px; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; font-size: 11px;
                background: #111; color: #666; border: 1px solid #333;
            }
            .mbbo-btn.static:hover { background: var(--green); color: #000; border-color: var(--green); }
            .mbbo-btn.forecast:hover { background: var(--blue); color: #fff; border-color: var(--blue); }
            .mbbo-btn.currency:hover { background: var(--gold); color: #000; border-color: var(--gold); }
            
            .status-tag { font-size: 10px; color: var(--green); letter-spacing: 2px; }
        </style>
        <script>
            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const grid = document.getElementById('grid');
                    grid.innerHTML = data.roster.map((i, idx) => `
                        <div class="pace-card">
                            <div class="status-tag">PACECARD PORTAL // 100${idx}</div>
                            <div class="asset-name">${i.song}</div>
                            <div class="ticker" id="price-${idx}">$${i.current_price}</div>
                            <div style="color:#666; font-size:12px;">MINT PRICE: $${i.principal}</div>
                            
                            <div class="mbbo-dock">
                                <button class="mbbo-btn static" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">Static</button>
                                <button class="mbbo-btn forecast" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'FORECAST')">Forecast</button>
                                <button class="mbbo-btn currency" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'CURRENCY')">Currency</button>
                            </div>
                        </div> `).join('');
                }
            }

            function execute(audio, img, title, type) {
                const player = document.getElementById('master-player');
                const cover = document.getElementById('cover');
                const display = document.getElementById('now-playing');
                
                // FORCE SYNC
                display.innerText = type + " EXECUTION: " + title;
                cover.src = img;
                player.src = audio;
                
                // RE-MAP AND FIRE
                player.load();
                var playPromise = player.play();
                
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.log("Playback failed. User must interact.");
                        alert("PORTAL LOCKED: Click the Play Button on the Radio Bar to finalize the Trade.");
                    });
                }
            }
            setInterval(sync, 4000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="master-unit">
            <img id="cover" src="https://via.placeholder.com/120?text=AITIFY">
            <div style="flex-grow: 1;">
                <span class="status-tag">97.7 THE FLAME // SATELLITE FEED</span><br>
                <b id="now-playing" style="font-size:2.2em; text-transform:uppercase;">READY FOR BROKER INPUT</b><br>
                <audio id="master-player" controls crossorigin="anonymous" style="width:100%; height:40px; margin-top:15px;"></audio>
            </div>
        </div>
        <div id="grid" class="portal-grid"></div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "principal": "{:.2f}".format(float(r[3])), "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.06, 0.06))} for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except: return jsonify({"roster": []})

@app.route('/mint-admin-portal')
def minting_suite():
    return render_template_string('''
    <body style="background:#000; color:#0f3; padding:50px; font-family:monospace;">
        <div style="border:1px solid #0f3; padding:20px; max-width:500px; margin:auto;">
            <h1>PACECARD MINTING</h1>
            <form action="/stock_asset" method="post">
                <input name="title" placeholder="SONG TITLE" style="width:100%; margin-bottom:10px;"><br>
                <input name="artist" placeholder="ARTIST" style="width:100%; margin-bottom:10px;"><br>
                <input name="price" type="number" step="0.01" placeholder="MINT PRICE" style="width:100%; margin-bottom:10px;"><br>
                <input name="audio_url" placeholder="FIREBASE AUDIO URL" style="width:100%; margin-bottom:10px;"><br>
                <input name="image_url" placeholder="FIREBASE IMAGE URL" style="width:100%; margin-bottom:10px;"><br>
                <button type="submit" style="width:100%; padding:20px; background:#0f3; color:#000; font-weight:bold;">PUSH TO EXCHANGE</button>
            </form>
        </div>
    </body>
    ''')

@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    t, a, p, au, im = request.form.get('title'), request.form.get('artist'), request.form.get('price'), request.form.get('audio_url'), request.form.get('image_url')
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)", (f"{a} - {t}", au, im, p))
    conn.commit(); cur.close(); conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
