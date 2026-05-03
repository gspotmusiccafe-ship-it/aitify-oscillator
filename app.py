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
        <title>AITIFY | BIG BOY TERMINAL V36</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --red: #ff3300; --bg: #020202; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            .terminal-container { display: grid; grid-template-columns: 450px 1fr; height: 100vh; gap: 2px; background: #111; }
            .monitor { background: #000; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--green); object-fit: cover; margin-bottom: 15px; }
            .trading-floor { background: #000; overflow-y: auto; padding: 20px; }
            .pace-card { 
                background: #080808; border: 1px solid #1a1a1a; padding: 25px; 
                display: grid; grid-template-columns: 1fr 220px; gap: 30px; margin-bottom: 15px; min-height: 400px;
            }
            .ticker-section { display: flex; flex-direction: column; }
            .ticker-price { font-size: 5.5em; font-weight: 900; color: var(--green); letter-spacing: -6px; line-height: 0.8; margin-bottom: 15px; }
            .void-filler-graph { flex-grow: 1; background: #000; border: 1px solid #111; position: relative; min-height: 200px; }
            .velocity-tag { position: absolute; top: 15px; right: 20px; font-weight: bold; font-size: 1.8em; z-index: 10; font-family: 'Courier New'; }
            canvas { width: 100%; height: 100%; }
            .mbbo-dock { display: flex; flex-direction: column; gap: 10px; justify-content: center; }
            .mbbo-btn { padding: 20px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff; cursor: pointer; text-transform: uppercase; font-size: 12px; border-left: 8px solid #444; }
            .mbbo-btn.static:hover { border-left-color: var(--green); background: #0a110a; }
            .mbbo-btn.currency:hover { border-left-color: var(--gold); background: #110e0a; }
            audio { width: 100%; height: 45px; filter: invert(1); margin-top: auto; }
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
                                    <div style="font-size:10px; color:var(--green); letter-spacing:3px;">SATELLITE FEED // ${i.song}</div>
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div class="void-filler-graph">
                                        <div id="vel-${idx}" class="velocity-tag">--</div>
                                        <canvas id="canvas-${idx}"></canvas>
                                    </div>
                                </div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn static" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                    <button class="mbbo-btn currency" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'FOREX')">CURRENCY MBBO</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updatePace(idx, i.current_price));
                }
            }
            function updatePace(idx, price) {
                const pEl = document.getElementById(`price-${idx}`);
                const vEl = document.getElementById(`vel-${idx}`);
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!pEl || !vEl || !canvas) return;
                
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 100) charts[idx].shift();

                pEl.innerText = `$${price}`;
                pEl.style.color = diff >= 0 ? 'var(--green)' : 'var(--red)';
                
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? 'var(--green)' : 'var(--red)';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                ctx.lineWidth = 5;
                ctx.strokeStyle = diff >= 0 ? '#00ff33' : '#ff3300';
                ctx.beginPath();
                const step = canvas.width / 100;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.3)) * 300);
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
                player.play().catch(e => console.log("Ignition failed, checking stream..."));
            }
            setInterval(sync, 2000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY">
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.30, 0.30))} for r in cur.fetchall()]
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
