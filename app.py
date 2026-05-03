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
        <title>AITIFY | TRADING TERMINAL</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --bg: #050505; --panel: #0a0a0a; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            
            /* COMMAND CENTER LAYOUT */
            .terminal-container { display: grid; grid-template-columns: 450px 1fr; height: 100vh; gap: 2px; background: #1a1a1a; }
            
            /* LEFT PANEL: BROADCAST MONITOR */
            .broadcast-monitor { background: #000; padding: 30px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--green); object-fit: cover; margin-bottom: 20px; box-shadow: 0 0 30px rgba(0,255,51,0.1); }
            .on-air-status { color: var(--green); font-size: 10px; letter-spacing: 4px; margin-bottom: 5px; }
            #now-playing { font-size: 2em; line-height: 1.1; margin-bottom: 20px; text-transform: uppercase; }
            
            /* RIGHT PANEL: TRADING FLOOR */
            .trading-floor { background: #050505; overflow-y: auto; padding: 20px; }
            .pace-card { 
                background: var(--panel); border: 1px solid #1a1a1a; padding: 15px; margin-bottom: 10px;
                display: grid; grid-template-columns: 1fr 150px; align-items: center; gap: 20px;
            }
            .ticker { font-size: 2.5em; font-weight: 900; color: var(--green); letter-spacing: -3px; }
            
            /* BLOOMBERG BUTTONS */
            .mbbo-dock { display: flex; flex-direction: column; gap: 5px; }
            .mbbo-btn { 
                padding: 10px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 9px; border-left: 4px solid #444; text-align: left;
            }
            .mbbo-btn.static:hover { border-left-color: var(--green); background: #111; }
            .mbbo-btn.forecast:hover { border-left-color: var(--blue); background: #111; }
            .mbbo-btn.currency:hover { border-left-color: var(--gold); background: #111; }

            /* MASTER AUDIO UNIT */
            .audio-unit { margin-top: auto; border-top: 1px solid #222; padding-top: 20px; }
            audio { width: 100%; height: 35px; filter: invert(1); }
        </style>
        <script>
            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const floor = document.getElementById('floor');
                    floor.innerHTML = data.roster.map((i, idx) => `
                        <div class="pace-card">
                            <div>
                                <div style="font-size:9px; color:#444;">ASSET_ID: 100${idx}</div>
                                <div style="font-size:1.1em; color:#ddd;">${i.song}</div>
                                <div class="ticker" id="price-${idx}">$${i.current_price}</div>
                            </div>
                            <div class="mbbo-dock">
                                <button class="mbbo-btn static" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                <button class="mbbo-btn forecast" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'TARGET')">TARGET MBBO</button>
                                <button class="mbbo-btn currency" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'CURRENCY')">FOREX MBBO</button>
                            </div>
                        </div> `).join('');
                }
            }

            function ignite(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('mode').innerText = type + " EXECUTION ACTIVE";
                document.getElementById('cover').src = img;
                
                // AUDIO SYNC
                player.src = audio;
                player.load();
                
                // BYPASS BROWSER SILENCE
                const playPromise = player.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => {
                        console.log("Waiting for user trigger...");
                        document.getElementById('mode').innerText = "PORTAL STANDBY - CLICK PLAY TO IGNITE";
                    });
                }
            }
            setInterval(sync, 4000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="broadcast-monitor">
                <div class="on-air-status">97.7 THE FLAME // LIVE</div>
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY+TERMINAL">
                <div id="mode" style="font-size:10px; color:var(--gold); margin-bottom:5px;">AWAITING PORTAL ENTRY...</div>
                <div id="now-playing">STANDBY FOR BROADCAST</div>
                
                <div class="audio-unit">
                    <audio id="master-player" controls crossorigin="anonymous"></audio>
                    <p style="font-size:9px; color:#444; margin-top:10px;">ENCRYPTED SATELLITE FEED // FIREBASE STORAGE CLOUD</p>
                </div>
            </div>
            
            <div class="trading-floor" id="floor">
                </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "principal": "{:.2f}".format(float(r[3])), "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.08, 0.08))} for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except: return jsonify({"roster": []})

@app.route('/mint-admin-portal')
def minting_suite():
    return render_template_string('''<body style="background:#000; color:#0f3; padding:50px;"><form action="/stock_asset" method="post"><input name="title" placeholder="SONG TITLE"><input name="artist" placeholder="ARTIST"><input name="price" type="number" step="0.01" placeholder="PRICE"><input name="audio_url" placeholder="FIREBASE AUDIO"><input name="image_url" placeholder="IMAGE URL"><button type="submit">MINT</button></form></body>''')

@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    t, a, p, au, im = request.form.get('title'), request.form.get('artist'), request.form.get('price'), request.form.get('audio_url'), request.form.get('image_url')
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)", (f"{a} - {t}", au, im, p))
    conn.commit(); cur.close(); conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
