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
        <title>AITIFY | PRECISION TERMINAL V41</title>
        <style>
            :root { --emerald: #50C878; --red: #ff3300; --bg: #020202; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            .terminal-container { display: grid; grid-template-columns: 400px 1fr; height: 100vh; background: #111; }
            
            /* MONITOR LEFT */
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid var(--emerald); object-fit: cover; margin-bottom: 20px; box-shadow: 0 0 20px rgba(80,200,120,0.2); }
            .ignite-btn { background: var(--emerald); color: #000; border: none; padding: 18px; font-weight: 900; cursor: pointer; text-transform: uppercase; margin-bottom: 20px; box-shadow: 0 0 15px var(--emerald); }

            /* TRADING FLOOR RIGHT */
            .trading-floor { background: #050505; overflow-y: auto; padding: 30px; }
            .pace-card { 
                background: #080808; border: 1px solid #1a1a1a; padding: 30px; 
                display: flex; flex-direction: column; margin-bottom: 30px; min-height: 600px;
            }
            
            .ticker-price { font-size: 8em; font-weight: 900; color: var(--emerald); letter-spacing: -12px; line-height: 0.7; margin-bottom: 20px; }
            
            /* STRETCHED OSCILLATOR */
            .void-filler-graph { width: 100%; height: 300px; background: #000; border: 1px solid #111; position: relative; margin-bottom: 25px; }
            .velocity-tag { position: absolute; top: 15px; right: 20px; background: rgba(0,0,0,0.8); padding: 5px 15px; border: 1px solid #333; z-index: 10; font-size: 2.5em; font-weight: bold; }
            canvas { width: 100%; height: 100%; }

            /* BUTTONS UNDER OSCILLATOR */
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            .mbbo-btn { 
                padding: 22px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; border-top: 5px solid #444; text-align: center;
            }
            .mbbo-btn:hover { background: #111; border-top-color: #fff; }
            
            audio { width: 100%; height: 40px; filter: invert(1) hue-rotate(90deg); margin-top: auto; }
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
                                <div style="font-size:10px; color:#444; letter-spacing:5px;">SATELLITE_SIGNAL // ${i.song}</div>
                                <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                <div class="void-filler-graph">
                                    <div id="vel-${idx}" class="velocity-tag">--</div>
                                    <canvas id="canvas-${idx}"></canvas>
                                </div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'TARGET')">TARGET MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'FOREX')">CURRENCY MBBO</button>
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
                if (charts[idx].length > 300) charts[idx].shift();

                document.getElementById(`price-${idx}`).innerText = `$${price}`;
                document.getElementById(`price-${idx}`).style.color = diff >= 0 ? '#50C878' : '#ff3300';
                
                const vEl = document.getElementById(`vel-${idx}`);
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? '#50C878' : '#ff3300';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '80, 200, 120' : '255, 51, 0';
                
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, `rgba(${rgb}, 0.5)`);
                grad.addColorStop(1, `rgba(${rgb}, 0)`);
                
                ctx.fillStyle = grad;
                ctx.strokeStyle = `rgb(${rgb})`;
                ctx.lineWidth = 1; // HIGH TECH PRECISION
                
                ctx.beginPath();
                const step = canvas.width / 300;
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
                player.src = audio; player.load(); player.play();
            }
            
            function unlock() {
                document.getElementById('master-player').play().then(() => {
                    document.getElementById('master-player').pause();
                    document.getElementById('ignite').innerText = "SATELLITE SYNCED";
                });
            }

            setInterval(sync, 2000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <button id="ignite" class="ignite-btn" onclick="unlock()">IGNITE EMERALD FEED</button>
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY">
                <div id="now-playing" style="font-size:1.2em; text-transform:uppercase; margin-top:10px; color:#444;">SIGNAL STANDBY</div>
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.60, 0.60))} for r in cur.fetchall()]
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
