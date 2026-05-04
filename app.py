from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import psycopg2, random, os

app = Flask(__name__)
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>MUSIC MONEY MARKET | V54</title>
        <style>
            :root { --emerald: #50C878; --red: #ff3300; --bg: #000; --glass: rgba(255,255,255,0.03); }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
            
            /* GLASS OVERLAY FOR INITIAL KICK */
            #ignition-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 9999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(20px); }
            .kick-btn { padding: 30px 60px; background: none; border: 1px solid var(--emerald); color: var(--emerald); font-weight: 900; letter-spacing: 5px; cursor: pointer; text-transform: uppercase; font-size: 1.2em; box-shadow: 0 0 30px rgba(80,200,120,0.2); }

            .terminal-container { display: grid; grid-template-columns: 1fr; height: 100vh; }
            @media (min-width: 1024px) { .terminal-container { grid-template-columns: 420px 1fr; } }

            /* BROADCAST MONITOR */
            .monitor { background: #000; padding: 20px; display: flex; flex-direction: column; border-bottom: 1px solid #222; position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(10px); }
            #cover { width: 100px; height: 100px; border: 1px solid var(--emerald); object-fit: cover; margin-right: 20px; box-shadow: 0 0 20px rgba(80,200,120,0.1); }
            .monitor-top { display: flex; align-items: center; margin-bottom: 15px; }
            
            .on-air-tag { background: rgba(255,0,0,0.1); color: #ff3300; padding: 2px 10px; font-weight: 900; border: 1px solid #ff3300; font-size: 0.7em; animation: blink 1.5s infinite; visibility: hidden; }
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

            /* TRADING FLOOR */
            .trading-floor { padding: 20px; background: #020202; }
            .pace-card { background: #080808; border: 1px solid #1a1a1a; padding: 25px; display: flex; flex-direction: column; margin-bottom: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.8); border-radius: 4px; }
            
            .card-header { display: flex; flex-direction: column; margin-bottom: 20px; border-bottom: 1px solid #222; padding-bottom: 15px; }
            .ticker-price { font-size: 6em; font-weight: 900; color: var(--emerald); letter-spacing: -8px; line-height: 0.8; }
            @media (min-width: 768px) { .ticker-price { font-size: 9em; letter-spacing: -14px; } }
            
            /* KINETIC OSCILLATOR */
            .oscillator-void { 
                width: 100%; height: 250px; background: #000; border: 1px solid #111; position: relative; margin-bottom: 25px; overflow: hidden;
                background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 20px 20px;
            }
            canvas { width: 100%; height: 100%; }

            /* GLASS COMMAND DOCK */
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
            .mbbo-btn { 
                padding: 18px 5px; font-weight: 900; border: 1px solid #333; background: var(--glass); color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 9px; backdrop-filter: blur(5px); transition: 0.2s;
            }
            .mbbo-btn:active { background: var(--emerald); color: #000; }
            
            audio { width: 100%; height: 40px; filter: invert(1) hue-rotate(90deg); margin-top: 10px; opacity: 0.5; }
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
                                <div style="font-size:9px; color:#444; letter-spacing:4px; margin-bottom:10px;">MMM_NETWORK_HQ // ${i.song}</div>
                                <div class="card-header">
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                                        <div id="vel-${idx}" style="font-size:2em; font-weight:bold;">--</div>
                                        <div style="font-size:0.7em; color:#333;">KINETIC_PULSE_0-100</div>
                                    </div>
                                </div>
                                <div class="oscillator-void"><canvas id="canvas-${idx}"></canvas></div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">STATIC</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">TARGET</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">CURRENCY</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updateKineticPulse(idx, i.current_price));
                }
            }

            function updateKineticPulse(idx, price) {
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 100) charts[idx].shift();

                document.getElementById(`price-${idx}`).innerText = `$${price}`;
                const vEl = document.getElementById(`vel-${idx}`);
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? '#50C878' : '#ff3300';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '80, 200, 120' : '255, 51, 0';
                
                // FORCE OSCILLATION BETWEEN 0% AND 100% OF VOID
                const min = Math.min(...charts[idx]) - 0.10;
                const max = Math.max(...charts[idx]) + 0.10;
                const range = max - min;

                ctx.strokeStyle = `rgb(${rgb})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                const step = canvas.width / 100;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - (((p - min) / range) * canvas.height);
                    if(i === 0) ctx.moveTo(i * step, y); else ctx.lineTo(i * step, y);
                });
                ctx.stroke();
            }

            function ignite(audio, img, title) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                player.src = audio; player.load(); player.play();
            }
            
            function systemsEngage() {
                const p = document.getElementById('master-player');
                p.play().then(() => { 
                    p.pause(); 
                    document.getElementById('ignition-overlay').style.display = "none";
                    document.getElementById('on-air').style.visibility = "visible";
                    sync();
                });
            }
            setInterval(sync, 3000);
        </script>
    </head>
    <body>
        <div id="ignition-overlay">
            <button class="kick-btn" onclick="systemsEngage()">SYSTEMS_ENGAGE</button>
        </div>
        <div class="terminal-container">
            <div class="monitor">
                <div class="monitor-top">
                    <img id="cover" src="https://via.placeholder.com/100?text=SIGNAL">
                    <div>
                        <div id="on-air" class="on-air-tag">ON AIR</div>
                        <div id="now-playing" style="font-size:0.9em; text-transform:uppercase; margin-top:5px; color:#555;">SIGNAL_STANDBY</div>
                    </div>
                </div>
                <audio id="master-player" controls crossorigin="anonymous"></audio>
            </div>
            <div class="trading-floor" id="floor"></div>
        </div>
    </body>
    </html>
    ''')

# ... ALL OTHER ROUTES (api, mint, stock_asset) REMAIN IDENTICAL TO V53 ...
@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.95, 0.95))} for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except: return jsonify({"roster": []})

@app.route('/mint-admin-portal')
def minting_suite():
    return render_template_string('''
    <body style="background: #000; color: #fff; font-family: monospace; padding: 20px;">
        <div style="border: 1px solid #333; padding: 30px; max-width: 500px; margin: auto;">
            <h2>MARKET_MINT</h2>
            <form action="/stock_asset" method="post">
                <input name="title" placeholder="TITLE" style="width:100%; margin-bottom:10px; background:#111; color:#0f3; border:1px solid #333; padding:10px;">
                <input name="artist" placeholder="ARTIST" style="width:100%; margin-bottom:10px; background:#111; color:#0f3; border:1px solid #333; padding:10px;">
                <input name="price" type="number" step="0.01" placeholder="PRICE" style="width:100%; margin-bottom:10px; background:#111; color:#0f3; border:1px solid #333; padding:10px;">
                <input name="audio_url" placeholder="AUDIO URL" style="width:100%; margin-bottom:10px; background:#111; color:#0f3; border:1px solid #333; padding:10px;">
                <input name="image_url" placeholder="IMAGE URL" style="width:100%; margin-bottom:10px; background:#111; color:#0f3; border:1px solid #333; padding:10px;">
                <button type="submit" style="width:100%; padding:15px; background:#0f3; color:#000; border:none; font-weight:bold;">MINT</button>
            </form>
        </div>
    </body>
    ''')

@app.route('/stock_asset', methods=['POST'])
def stock_asset():
    try:
        title, artist, price_val, audio_url, image_url = request.form.get('title'), request.form.get('artist'), request.form.get('price'), request.form.get('audio_url'), request.form.get('image_url')
        unit_price = float(price_val) if price_val else 0.0
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("INSERT INTO gsr_artist_roster (song_title, audio_url, image_url, unit_price) VALUES (%s, %s, %s, %s)", (f"{artist} - {title}", audio_url, image_url, unit_price))
        conn.commit(); cur.close(); conn.close()
        return redirect('/')
    except Exception as e: return f"ERROR: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
