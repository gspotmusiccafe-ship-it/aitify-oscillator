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
        <title>MUSIC MONEY MARKET | V53</title>
        <style>
            :root { --emerald: #50C878; --red: #ff3300; --bg: #010101; --glass: rgba(255,255,255,0.05); }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            .terminal-container { display: grid; grid-template-columns: 420px 1fr; height: 100vh; background: #111; }
            
            /* BROADCAST MONITOR */
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; border-right: 2px solid #222; position: relative; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--emerald); object-fit: cover; margin-bottom: 20px; box-shadow: 0 0 40px rgba(80,200,120,0.1); }
            
            .ignite-btn { 
                background: var(--glass); color: var(--emerald); border: 1px solid var(--emerald); padding: 20px; 
                font-weight: 900; cursor: pointer; text-transform: uppercase; letter-spacing: 3px; 
                backdrop-filter: blur(10px); transition: 0.2s; box-shadow: 0 0 15px rgba(80,200,120,0.1);
            }
            .ignite-btn:hover { background: var(--emerald); color: #000; box-shadow: 0 0 30px var(--emerald); }
            .ignite-btn:active { transform: scale(0.98); }

            .on-air-signal { display: none; position: absolute; top: 15px; right: 15px; background: rgba(255,0,0,0.2); color: #ff3300; padding: 5px 15px; font-weight: 900; font-size: 0.8em; border: 1px solid #ff3300; animation: blink 1.5s infinite; text-shadow: 0 0 10px #ff3300; }
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

            /* TRADING FLOOR */
            .trading-floor { background: #030303; overflow-y: auto; padding: 40px; }
            .pace-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 40px; display: flex; flex-direction: column; margin-bottom: 50px; min-height: 750px; box-shadow: 0 50px 100px rgba(0,0,0,0.8); }
            
            .card-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 30px; border-bottom: 1px solid #222; padding-bottom: 25px; }
            .ticker-price { font-size: 10em; font-weight: 900; color: var(--emerald); letter-spacing: -18px; line-height: 0.6; }
            .velocity-widget { font-size: 4em; font-weight: bold; font-family: 'Courier New'; }
            
            /* PRECISION OSCILLATOR */
            .void-filler-graph { 
                width: 100%; height: 450px; background: #000; border: 1px solid #111; position: relative; margin-bottom: 35px; overflow: hidden;
                background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 25px 25px;
            }
            canvas { width: 100%; height: 100%; }

            /* GLASS COMMAND DOCK */
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
            .mbbo-btn { 
                padding: 25px; font-weight: 900; border: 1px solid #333; background: var(--glass); color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; backdrop-filter: blur(5px);
                transition: 0.2s; border-radius: 2px;
            }
            .mbbo-btn:hover { border-color: var(--emerald); color: var(--emerald); box-shadow: 0 0 20px rgba(80,200,120,0.1); }
            .mbbo-btn:active { background: #111; }
            
            audio { width: 100%; height: 45px; filter: invert(1) hue-rotate(90deg); margin-top: auto; opacity: 0.3; }
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
                                <div style="font-size:10px; color:#333; letter-spacing:8px; margin-bottom:12px;">MMM_NETWORK_SIGNAL // ${i.song}</div>
                                <div class="card-header">
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div id="vel-${idx}" class="velocity-widget">--</div>
                                </div>
                                <div class="void-filler-graph"><canvas id="canvas-${idx}"></canvas></div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">STATIC MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">TARGET MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">CURRENCY MBBO</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updatePulse(idx, i.current_price));
                }
            }

            function updatePulse(idx, price) {
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 3000) charts[idx].shift();

                document.getElementById(`price-${idx}`).innerText = `$${price}`;
                document.getElementById(`price-${idx}`).style.color = diff >= 0 ? '#50C878' : '#ff3300';
                document.getElementById(`vel-${idx}`).innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                document.getElementById(`vel-${idx}`).style.color = diff >= 0 ? '#50C878' : '#ff3300';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '80, 200, 120' : '255, 51, 0';
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, `rgba(${rgb}, 0.3)`); grad.addColorStop(1, `rgba(${rgb}, 0)`);
                ctx.fillStyle = grad; ctx.strokeStyle = `rgb(${rgb})`; ctx.lineWidth = 0.5;
                ctx.beginPath();
                const step = canvas.width / 3000;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.25)) * 1000);
                    if(i === 0) ctx.moveTo(i * step, y); else ctx.lineTo(i * step, y);
                });
                ctx.stroke(); ctx.lineTo(charts[idx].length * step, canvas.height); ctx.lineTo(0, canvas.height); ctx.fill();
            }

            function ignite(audio, img, title) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                player.src = audio; player.load(); player.play();
            }
            
            function broadcast() {
                const p = document.getElementById('master-player');
                // Force unmuting and playing
                p.play().then(() => { 
                    p.pause(); 
                    document.getElementById('ignite').innerText = "SYSTEMS LIVE"; 
                    document.getElementById('ignite').style.borderColor = "#ff3300";
                    document.getElementById('ignite').style.color = "#ff3300";
                    document.getElementById('on-air').style.display = "block";
                });
            }
            setInterval(sync, 2000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <div id="on-air" class="on-air-signal">ON AIR</div>
                <button id="ignite" class="ignite-btn" onclick="broadcast()">BROADCAST LIVE</button>
                <img id="cover" src="https://via.placeholder.com/400?text=SIGNAL+OFFLINE">
                <div id="now-playing" style="font-size:1.1em; text-transform:uppercase; margin-top:10px; color:#444;">WAITING FOR SIGNAL</div>
                <audio id="master-player" controls crossorigin="anonymous"></audio>
            </div>
            <div class="trading-floor" id="floor"></div>
        </div>
    </body>
    </html>
    ''')

# Minter & Data routes remain consistent with V52
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
    <body style="background: #030303; color: #fff; font-family: 'IBM Plex Mono', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
        <div style="background: rgba(8,8,8,0.95); border: 1px solid #333; padding: 60px; width: 700px; box-shadow: 0 50px 120px rgba(0,0,0,0.9); backdrop-filter: blur(15px);">
            <h2 style="color: #50C878; margin-bottom: 40px; letter-spacing: 8px; text-align: center;">MARKET_ASSET_MINT</h2>
            <form action="/stock_asset" method="post">
                <input name="title" style="width:100%; padding:22px; margin-bottom:25px; background:#000; border:1px solid #444; color:#50C878; font-size:1.3em;" placeholder="SONG TITLE" required>
                <input name="artist" style="width:100%; padding:22px; margin-bottom:25px; background:#000; border:1px solid #444; color:#50C878; font-size:1.3em;" placeholder="ARTIST" required>
                <input name="price" type="number" step="0.01" style="width:100%; padding:22px; margin-bottom:25px; background:#000; border:1px solid #444; color:#50C878; font-size:1.3em;" placeholder="BASE PRICE ($)" required>
                <input name="audio_url" style="width:100%; padding:22px; margin-bottom:25px; background:#000; border:1px solid #444; color:#50C878; font-size:1.3em;" placeholder="FIREBASE AUDIO URL" required>
                <input name="image_url" style="width:100%; padding:22px; margin-bottom:25px; background:#000; border:1px solid #444; color:#50C878; font-size:1.3em;" placeholder="IMAGE ASSET URL" required>
                <button type="submit" style="width:100%; padding:28px; background:#50C878; border:none; color:#000; font-weight:900; cursor:pointer; text-transform:uppercase; font-size:1.2em; letter-spacing:4px;">MINT ASSET</button>
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
    except Exception as e: return f"MINTING ERROR: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
