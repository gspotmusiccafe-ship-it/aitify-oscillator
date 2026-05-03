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
        <title>AITIFY | BIG BOY TERMINAL V35</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --red: #ff3300; --bg: #020202; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            
            .terminal-container { display: grid; grid-template-columns: 400px 1fr; height: 100vh; gap: 2px; background: #111; }
            
            /* MASTER BROADCAST (LEFT) */
            .monitor { background: #000; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--green); object-fit: cover; margin-bottom: 15px; box-shadow: 0 0 20px rgba(0,255,51,0.2); }
            
            /* THE TRADING FLOOR (RIGHT) */
            .trading-floor { background: #000; overflow-y: auto; padding: 20px; }
            .pace-card { 
                background: #080808; border: 1px solid #1a1a1a; padding: 25px; 
                display: grid; grid-template-columns: 1fr 220px; gap: 30px; margin-bottom: 15px; min-height: 350px;
            }
            
            /* FILLING THE VOID: OSCILLATOR */
            .ticker-section { display: flex; flex-direction: column; justify-content: space-between; }
            .ticker-price { font-size: 4.5em; font-weight: 900; color: var(--green); letter-spacing: -5px; line-height: 1; }
            .void-filler-graph { flex-grow: 1; background: #050505; border: 1px solid #111; margin-top: 20px; position: relative; }
            canvas { width: 100%; height: 100%; }

            /* BLOOMBERG BUTTON DOCK */
            .mbbo-dock { display: flex; flex-direction: column; gap: 10px; justify-content: center; }
            .mbbo-btn { 
                padding: 18px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; border-left: 6px solid #444;
            }
            .mbbo-btn.static:hover { border-left-color: var(--green); background: #0a110a; }
            .mbbo-btn.forecast:hover { border-left-color: var(--blue); background: #0a0e11; }
            .mbbo-btn.currency:hover { border-left-color: var(--gold); background: #110e0a; }
            
            audio { width: 100%; height: 35px; filter: invert(1); margin-top: auto; }
        </style>
        <script>
            let charts = {};

            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const floor = document.getElementById('floor');
                    if (floor.children.length !== data.roster.length) {
                        floor.innerHTML = data.roster.map((i, idx) => `
                            <div class="pace-card">
                                <div class="ticker-section">
                                    <div style="font-size:10px; color:var(--green); letter-spacing:3px;">ASSET_ID: 100${idx} // ${i.song}</div>
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div class="void-filler-graph"><canvas id="canvas-${idx}"></canvas></div>
                                </div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn static" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                    <button class="mbbo-btn forecast" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'TARGET')">TARGET MBBO</button>
                                    <button class="mbbo-btn currency" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'CURRENCY')">FOREX MBBO</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updatePace(idx, i.current_price));
                }
            }

            function updatePace(idx, price) {
                const pEl = document.getElementById(`price-${idx}`);
                if (pEl) pEl.innerText = `$${price}`;
                
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                
                let lastP = charts[idx][charts[idx].length - 1] || price;
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 60) charts[idx].shift();

                ctx.clearRect(0,0, canvas.width, canvas.height);
                ctx.lineWidth = 3;
                ctx.strokeStyle = parseFloat(price) >= parseFloat(lastP) ? '#00ff33' : '#ff3300'; // RED FOR LOSSES
                
                ctx.beginPath();
                const step = canvas.width / 60;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-1)) * 50);
                    ctx.lineTo(i * step, y);
                });
                ctx.stroke();
            }

            function ignite(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                player.src = audio; player.load();
                player.play().catch(() => { alert("IGNITION DELAY: Tap the Play button below."); });
            }

            setInterval(sync, 3000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY+TERMINAL">
                <div id="now-playing" style="font-size:1.4em; text-transform:uppercase; margin-top:10px; color:#aaa;">STANDBY</div>
                <audio id="master-player" controls crossorigin="anonymous"></audio>
            </div>
            <div class="trading-floor" id="floor"></div>
        </div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.15, 0.15))} for r in cur.fetchall()]
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
