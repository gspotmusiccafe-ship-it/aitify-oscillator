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
        <title>AITIFY | PRECISION TERMINAL V37</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --red: #ff3300; --bg: #010101; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            .terminal-container { display: grid; grid-template-columns: 450px 1fr; height: 100vh; gap: 1px; background: #222; }
            
            /* BROADCAST MONITOR */
            .monitor { background: #000; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--green); object-fit: cover; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0,255,51,0.3); }
            
            /* TRADING FLOOR */
            .trading-floor { background: #000; overflow-y: auto; padding: 20px; }
            .pace-card { 
                background: #080808; border: 1px solid #1a1a1a; padding: 20px; 
                display: grid; grid-template-columns: 1fr 240px; gap: 20px; margin-bottom: 15px; min-height: 420px;
            }
            
            .ticker-price { font-size: 6em; font-weight: 900; color: var(--green); letter-spacing: -7px; line-height: 0.8; margin-bottom: 15px; }
            
            /* THE PRECISION OSCILLATOR */
            .void-filler-graph { flex-grow: 1; background: #000; border: 1px solid #111; position: relative; overflow: hidden; }
            .velocity-panel { position: absolute; top: 15px; right: 20px; background: rgba(0,0,0,0.8); padding: 5px 15px; border: 1px solid #333; z-index: 10; font-size: 1.5em; font-weight: bold; }
            canvas { width: 100%; height: 100%; }

            /* TRIPLE MBBO DOCK */
            .mbbo-dock { display: flex; flex-direction: column; gap: 8px; justify-content: center; }
            .mbbo-btn { 
                padding: 16px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; border-left: 6px solid #444;
            }
            .mbbo-btn.static:hover { border-left-color: var(--green); background: #0a110a; }
            .mbbo-btn.forecast:hover { border-left-color: var(--blue); background: #0a0e11; }
            .mbbo-btn.currency:hover { border-left-color: var(--gold); background: #110e0a; }
            
            audio { width: 100%; height: 40px; filter: invert(1); margin-top: auto; }
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
                                <div class="ticker-section" style="display:flex; flex-direction:column;">
                                    <div style="font-size:9px; color:var(--green); letter-spacing:4px; margin-bottom:5px;">TERMINAL FEED // ${i.song}</div>
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div class="void-filler-graph">
                                        <div id="vel-${idx}" class="velocity-panel">--</div>
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
                    data.roster.forEach((i, idx) => updatePulse(idx, i.current_price));
                }
            }

            function updatePulse(idx, price) {
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
                ctx.lineWidth = 1; // PIXEL PRECISION
                ctx.strokeStyle = diff >= 0 ? '#00ff33' : '#ff3300';
                ctx.beginPath();
                const step = canvas.width / 150;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.2)) * 500);
                    ctx.lineTo(i * step, y);
                });
                ctx.stroke();
            }

            function ignite(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                
                player.src = audio; 
                player.load();
                
                // KICK THE AUDIO CONTEXT
                const playPromise = player.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => {
                        console.log("Portal standby... user interaction required.");
                    });
                }
            }
            setInterval(sync, 2000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY">
                <div id="now-playing" style="font-size:1.2em; text-transform:uppercase; margin-top:10px; color:#666;">READY TO TRADE</div>
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.40, 0.40))} for r in cur.fetchall()]
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
