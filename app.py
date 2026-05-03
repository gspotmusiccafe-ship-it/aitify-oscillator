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
        <title>AITIFY | TERMINAL V34</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --red: #ff3300; --bg: #020202; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            
            /* TRADING HUB LAYOUT */
            .terminal-container { display: grid; grid-template-columns: 550px 1fr; height: 100vh; gap: 1px; background: #111; }
            
            /* MASTER MONITOR (LEFT) */
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; position: relative; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 16/9; border: 1px solid #222; object-fit: cover; margin-bottom: 15px; filter: contrast(1.2) brightness(0.8); }
            
            /* GAINS & LOSSES OSCILLATOR */
            .oscillator-vault { flex-grow: 1; background: #050505; border: 1px solid #111; position: relative; overflow: hidden; margin-bottom: 20px; }
            canvas#master-pulse { width: 100%; height: 100%; }
            .vibration-data { position: absolute; top: 10px; right: 10px; text-align: right; font-weight: bold; }
            .gain { color: var(--green); } .loss { color: var(--red); }
            
            /* PACECARDS (RIGHT) */
            .trading-floor { background: #000; overflow-y: auto; padding: 20px; }
            .pace-card { 
                background: #080808; border-bottom: 1px solid #1a1a1a; padding: 20px; 
                display: grid; grid-template-columns: 1fr 180px; align-items: center; margin-bottom: 5px;
            }
            .ticker-price { font-size: 2.8em; font-weight: 900; color: var(--green); letter-spacing: -3px; }
            
            .mbbo-btn { 
                padding: 12px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 10px; border-left: 5px solid #444; margin-bottom: 4px;
            }
            .mbbo-btn:hover { background: #111; border-left-color: #fff; }
            
            audio { width: 100%; height: 35px; filter: invert(1) hue-rotate(90deg); margin-top: 10px; }
        </style>
        <script>
            let pulseData = [];
            
            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const floor = document.getElementById('floor');
                    floor.innerHTML = data.roster.map((i, idx) => `
                        <div class="pace-card">
                            <div>
                                <div style="font-size:9px; color:#444;">ASSET_STATION: 97.7</div>
                                <div style="color:#aaa;">${i.song}</div>
                                <div class="ticker-price">$${i.current_price}</div>
                            </div>
                            <div style="display:flex; flex-direction:column;">
                                <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">STATIC MBBO</button>
                                <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}', 'FOREX')">CURRENCY MBBO</button>
                            </div>
                        </div> `).join('');
                }
            }

            function ignite(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = title;
                document.getElementById('cover').src = img;
                player.src = audio; player.load();
                
                const playPromise = player.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => { document.getElementById('now-playing').innerText = "CLICK PLAY TO IGNITE FEED"; });
                }
                startOscillator();
            }

            function startOscillator() {
                const canvas = document.getElementById('master-pulse');
                const ctx = canvas.getContext('2d');
                function draw() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.strokeStyle = '#00ff33'; ctx.lineWidth = 2;
                    ctx.beginPath();
                    pulseData.push(Math.random() * 50 + 25);
                    if(pulseData.length > 100) pulseData.shift();
                    
                    pulseData.forEach((val, i) => {
                        ctx.lineTo(i * (canvas.width/100), canvas.height - val);
                    });
                    ctx.stroke();
                    
                    const roi = (Math.random() * 2.5).toFixed(2);
                    document.getElementById('roi-display').innerHTML = `<span class="gain">+${roi}% VELOCITY</span>`;
                    requestAnimationFrame(draw);
                }
                draw();
            }

            setInterval(sync, 4000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="terminal-container">
            <div class="monitor">
                <div style="font-size:10px; color:var(--green); letter-spacing:5px; margin-bottom:10px;">97.7 THE FLAME // SATELLITE MONITOR</div>
                <img id="cover" src="https://via.placeholder.com/600x400?text=AITIFY+WAITING+FOR+FEED">
                
                <div class="oscillator-vault">
                    <div class="vibration-data" id="roi-display"></div>
                    <canvas id="master-pulse"></canvas>
                </div>

                <div id="now-playing" style="font-size:1.8em; text-transform:uppercase; margin-bottom:10px;">STANDBY</div>
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
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.08, 0.08))} for r in cur.fetchall()]
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
