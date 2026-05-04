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
        <title>MUSIC MONEY MARKET | V55</title>
        <style>
            :root { --emerald: #50C878; --red: #ff3300; --bg: #000; --glass: rgba(255,255,255,0.05); }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
            
            /* HIGH-END APP STARTUP */
            #ignition-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(30px); }
            .kick-btn { padding: 40px 80px; background: var(--glass); border: 2px solid var(--emerald); color: var(--emerald); font-weight: 900; letter-spacing: 8px; cursor: pointer; text-transform: uppercase; font-size: 1.4em; box-shadow: 0 0 50px rgba(80,200,120,0.3); backdrop-filter: blur(10px); }
            .kick-btn:active { transform: scale(0.95); background: var(--emerald); color: #000; }

            .terminal-container { display: flex; flex-direction: column; }
            
            /* MOBILE BROADCAST BAR */
            .monitor { background: rgba(0,0,0,0.9); padding: 15px; display: flex; align-items: center; border-bottom: 1px solid #222; position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(15px); }
            #cover { width: 60px; height: 60px; border: 1px solid var(--emerald); object-fit: cover; margin-right: 15px; }
            .on-air-tag { color: #ff3300; font-weight: 900; font-size: 0.7em; border: 1px solid #ff3300; padding: 2px 8px; visibility: hidden; animation: blink 1s infinite; }
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }

            /* TRADING FLOOR */
            .trading-floor { padding: 20px; background: #020202; }
            .pace-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 25px; display: flex; flex-direction: column; margin-bottom: 40px; box-shadow: 0 30px 60px rgba(0,0,0,0.9); }
            
            .ticker-price { font-size: 7em; font-weight: 900; color: var(--emerald); letter-spacing: -10px; line-height: 0.7; margin-bottom: 15px; }
            
            /* KINETIC OSCILLATOR VOID */
            .oscillator-void { 
                width: 100%; height: 280px; background: #000; border: 1px solid #111; position: relative; margin-bottom: 25px; overflow: hidden;
                background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
                background-size: 40px 40px;
            }
            canvas { width: 100%; height: 100%; }

            /* GLASS COMMAND DOCK */
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            .mbbo-btn { 
                padding: 22px 5px; font-weight: 900; border: 1px solid #333; background: var(--glass); color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 10px; backdrop-filter: blur(5px);
            }
            .mbbo-btn:active { background: var(--emerald); color: #000; }
            
            audio { display: none; }
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
                                <div style="font-size:9px; color:#444; letter-spacing:5px; margin-bottom:12px;">MMM_NETWORK_HQ // ${i.song}</div>
                                <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
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
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 100) charts[idx].shift();

                document.getElementById(`price-${idx}`).innerText = `$${price}`;
                
                // TRUE 0-100% BOUNCE LOGIC
                const min = Math.min(...charts[idx]) - 0.05;
                const max = Math.max(...charts[idx]) + 0.05;
                const range = max - min;

                ctx.clearRect(0,0, canvas.width, canvas.height);
                ctx.strokeStyle = '#50C878';
                ctx.lineWidth = 3;
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
            <h1 style="color:var(--emerald); letter-spacing:15px; margin-bottom:50px;">MUSIC MONEY MARKET</h1>
            <button class="kick-btn" onclick="systemsEngage()">SYSTEMS_ENGAGE</button>
        </div>
        <div class="terminal-container">
            <div class="monitor">
                <img id="cover" src="https://via.placeholder.com/600?text=SIGNAL">
                <div style="flex-grow:1;">
                    <div id="on-air" class="on-air-tag">ON AIR</div>
                    <div id="now-playing" style="font-size:0.9em; text-transform:uppercase; margin-top:5px; color:#555;">SIGNAL_STANDBY</div>
                </div>
                <audio id="master-player" controls crossorigin="anonymous"></audio>
            </div>
            <div class="trading-floor" id="floor"></div>
        </div>
    </body>
    </html>
    ''')

# API, MINT, AND STOCK_ASSET ROUTES REMAIN THE SAME...
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
    return render_template_string('''<body style="background:#000; color:#fff; font-family:monospace; padding:50px;"><form action="/stock_asset" method="post"><input name="title" placeholder="TITLE"><input name="artist" placeholder="ARTIST"><input name="price" type="number" step="0.01" placeholder="PRICE"><input name="audio_url" placeholder="AUDIO URL"><input name="image_url" placeholder="IMAGE URL"><button type="submit">MINT</button></form></body>''')

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
