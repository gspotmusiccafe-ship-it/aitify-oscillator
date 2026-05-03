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
        <title>AITIFY | GLASS TERMINAL V39</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --red: #ff3300; --bg: #050505; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            
            .terminal-container { display: grid; grid-template-columns: 420px 1fr; height: 100vh; gap: 2px; background: #111; }
            
            /* MONITOR PANEL */
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; border-right: 2px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--green); object-fit: cover; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0,255,51,0.2); }
            
            .ignite-btn { background: var(--green); color: #000; border: none; padding: 15px; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-bottom: 20px; box-shadow: 0 0 15px var(--green); }

            /* TRADING FLOOR */
            .trading-floor { background: #080808; overflow-y: auto; padding: 30px; }
            .pace-card { 
                background: rgba(20,20,20,0.8); border: 1px solid #333; border-radius: 8px; padding: 30px; 
                display: grid; grid-template-columns: 1fr 240px; gap: 30px; margin-bottom: 20px; min-height: 480px;
                backdrop-filter: blur(10px); box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
            }
            
            .ticker-price { font-size: 6.5em; font-weight: 900; color: var(--green); letter-spacing: -8px; line-height: 0.8; margin-bottom: 15px; }
            
            /* AREA CHART VOID */
            .void-filler-graph { flex-grow: 1; background: #000; border: 1px solid #222; position: relative; overflow: hidden; border-radius: 4px; }
            .velocity-tag { position: absolute; top: 15px; right: 20px; background: rgba(0,0,0,0.9); padding: 10px 20px; border: 1px solid #444; z-index: 100; font-size: 2em; font-weight: bold; }
            canvas { width: 100%; height: 100%; }

            /* MBBO COMMAND DOCK */
            .mbbo-dock { display: flex; flex-direction: column; gap: 12px; justify-content: center; }
            .mbbo-btn { 
                padding: 20px; font-weight: bold; border: 1px solid #444; background: #111; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; border-left: 8px solid #666;
                transition: 0.2s;
            }
            .mbbo-btn.static:hover { border-left-color: var(--green); background: #0a150a; box-shadow: 0 0 15px rgba(0,255,51,0.2); }
            .mbbo-btn.forecast:hover { border-left-color: var(--blue); background: #0a0e15; }
            .mbbo-btn.currency:hover { border-left-color: var(--gold); background: #15110a; }
            
            audio { width: 100%; height: 45px; filter: invert(1); margin-top: auto; }
        </style>
        <script>
            let charts = {};
            let audioUnlocked = false;

            function unlockAudio() {
                const player = document.getElementById('master-player');
                player.play().then(() => {
                    player.pause();
                    audioUnlocked = true;
                    document.getElementById('ignite').style.display = 'none';
                    document.getElementById('now-playing').innerText = "SATELLITE SYNCED";
                });
            }

            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const floor = document.getElementById('floor');
                    if (floor.children.length !== data.roster.length) {
                        floor.innerHTML = data.roster.map((i, idx) => `
                            <div class="pace-card" id="card-${idx}">
                                <div class="ticker-section" style="display:flex; flex-direction:column;">
                                    <div style="font-size:10px; color:#666; letter-spacing:4px; margin-bottom:5px;">FEED_ID_97.7 // ${i.song}</div>
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div class="void-filler-graph">
                                        <div id="vel-${idx}" class="velocity-tag">--</div>
                                        <canvas id="canvas-${idx}"></canvas>
                                    </div>
                                </div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn static" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                    <button class="mbbo-btn forecast" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'TARGET')">TARGET MBBO</button>
                                    <button class="mbbo-btn currency" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'FOREX')">CURRENCY MBBO</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updateArea(idx, i.current_price));
                }
            }

            function updateArea(idx, price) {
                const pEl = document.getElementById(`price-${idx}`);
                const vEl = document.getElementById(`vel-${idx}`);
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!pEl || !vEl || !canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 150) charts[idx].shift();

                pEl.innerText = `$${price}`;
                pEl.style.color = diff >= 0 ? 'var(--green)' : 'var(--red)';
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? 'var(--green)' : 'var(--red)';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '0, 255, 51' : '255, 51, 0';
                
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, `rgba(${rgb}, 0.5)`);
                grad.addColorStop(1, `rgba(${rgb}, 0)`);
                
                ctx.fillStyle = grad;
                ctx.strokeStyle = `rgb(${rgb})`;
                ctx.lineWidth = 3;
                
                ctx.beginPath();
                const step = canvas.width / 150;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.2)) * 600);
                    if(i === 0) ctx.moveTo(i * step, y);
                    else ctx.lineTo(i * step, y);
                });
                ctx.stroke();
                ctx.lineTo(charts[idx].length * step, canvas.height);
                ctx.lineTo(0, canvas.height);
                ctx.fill();
            }

            function ignite(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                player.src = audio; 
                player.load();
                player.play();
            }
            setInterval(sync, 2000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <button id="ignite" class="ignite-btn" onclick="unlockAudio()">IGNITE SATELLITE FEED</button>
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY">
                <div id="now-playing" style="font-size:1.3em; text-transform:uppercase; margin-top:10px; color:#444;">WAITING FOR IGNITION</div>
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.50, 0.50))} for r in cur.fetchall()]
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
