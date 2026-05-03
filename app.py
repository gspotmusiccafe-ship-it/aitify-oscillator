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
        <title>AITIFY | EMERALD TERMINAL V40</title>
        <style>
            :root { 
                --emerald: #50C878; 
                --emerald-glow: rgba(80, 200, 120, 0.3);
                --red: #ff3300; 
                --bg: #030303; 
            }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            
            .terminal-container { display: grid; grid-template-columns: 420px 1fr; height: 100vh; gap: 2px; background: #1a1a1a; }
            
            /* MONITOR PANEL */
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; border-right: 2px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 2px solid var(--emerald); object-fit: cover; margin-bottom: 20px; box-shadow: 0 0 30px var(--emerald-glow); }
            
            .ignite-btn { 
                background: var(--emerald); color: #000; border: none; padding: 18px; 
                font-weight: 900; cursor: pointer; text-transform: uppercase; 
                margin-bottom: 20px; box-shadow: 0 0 25px var(--emerald);
                letter-spacing: 2px;
            }

            /* TRADING FLOOR */
            .trading-floor { background: #050505; overflow-y: auto; padding: 30px; }
            .pace-card { 
                background: linear-gradient(145deg, #0a0a0a, #050505); 
                border: 1px solid #222; border-radius: 4px; padding: 30px; 
                display: grid; grid-template-columns: 1fr 240px; gap: 30px; margin-bottom: 25px; min-height: 500px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
            }
            
            .ticker-price { font-size: 7em; font-weight: 900; color: var(--emerald); letter-spacing: -10px; line-height: 0.75; margin-bottom: 20px; }
            
            /* AREA CHART VOID */
            .void-filler-graph { flex-grow: 1; background: #000; border: 1px solid #111; position: relative; overflow: hidden; }
            .velocity-tag { position: absolute; top: 15px; right: 20px; background: rgba(0,0,0,0.9); padding: 10px 20px; border: 1px solid #333; z-index: 100; font-size: 2.2em; font-weight: bold; }
            canvas { width: 100%; height: 100%; }

            /* MBBO COMMAND DOCK */
            .mbbo-dock { display: flex; flex-direction: column; gap: 12px; justify-content: center; }
            .mbbo-btn { 
                padding: 22px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 11px; border-left: 10px solid #444;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .mbbo-btn.static:hover { border-left-color: var(--emerald); background: #0d1a10; box-shadow: 0 0 20px var(--emerald-glow); }
            .mbbo-btn.forecast:hover { border-left-color: #00eeff; background: #0d151a; }
            .mbbo-btn.currency:hover { border-left-color: #ffaa00; background: #1a150d; }
            
            audio { width: 100%; height: 45px; filter: invert(1) hue-rotate(90deg); margin-top: auto; }
        </style>
        <script>
            let charts = {};
            let audioUnlocked = false;

            function unlockAudio() {
                const player = document.getElementById('master-player');
                // Trigger a short playback to satisfy browser security
                player.play().then(() => {
                    player.pause();
                    audioUnlocked = true;
                    document.getElementById('ignite').innerText = "SATELLITE SYNCED";
                    document.getElementById('ignite').style.background = "#111";
                    document.getElementById('ignite').style.color = "#50C878";
                    document.getElementById('ignite').style.boxShadow = "none";
                    document.getElementById('now-playing').innerText = "READY FOR SIGNAL";
                });
            }

            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const floor = document.getElementById('floor');
                    if (floor.children.length !== data.roster.length) {
                        floor.innerHTML = data.roster.map((i, idx) => `
                            <div class="pace-card">
                                <div class="ticker-section" style="display:flex; flex-direction:column;">
                                    <div style="font-size:10px; color:#444; letter-spacing:5px; margin-bottom:8px;">SIGNAL_97.7 // ${i.song}</div>
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
                    data.roster.forEach((i, idx) => updateEmeraldArea(idx, i.current_price));
                }
            }

            function updateEmeraldArea(idx, price) {
                const pEl = document.getElementById(`price-${idx}`);
                const vEl = document.getElementById(`vel-${idx}`);
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!pEl || !vEl || !canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 180) charts[idx].shift();

                pEl.innerText = `$${price}`;
                pEl.style.color = diff >= 0 ? '#50C878' : '#ff3300';
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? '#50C878' : '#ff3300';

                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '80, 200, 120' : '255, 51, 0';
                
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, `rgba(${rgb}, 0.6)`);
                grad.addColorStop(1, `rgba(${rgb}, 0)`);
                
                ctx.fillStyle = grad;
                ctx.strokeStyle = `rgb(${rgb})`;
                ctx.lineWidth = 2;
                
                ctx.beginPath();
                const step = canvas.width / 180;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.25)) * 400);
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
                <button id="ignite" class="ignite-btn" onclick="unlockAudio()">IGNITE EMERALD FEED</button>
                <img id="cover" src="https://via.placeholder.com/400?text=AITIFY">
                <div id="now-playing" style="font-size:1.3em; text-transform:uppercase; margin-top:10px; color:#333;">SIGNAL STANDBY</div>
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
        roster = [{"song" : r[0].upper(), "audio" : r[1], "image" : r[2], "current_price" : "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.60, 0.60))} for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"roster" : roster})
    except: return jsonify({"roster" : []})

# REST OF THE CODE FOR MINTING REMAINS THE SAME
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
