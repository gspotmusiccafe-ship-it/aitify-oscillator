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
        <title>AITIFY | TERMINAL</title>
        <style>
            :root { --green: #00ff33; --blue: #00eeff; --gold: #ffaa00; --bg: #020202; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow-x: hidden; }
            
            .master-unit { 
                background: #000; border-bottom: 2px solid var(--green); padding: 15px 30px;
                display: flex; align-items: center; gap: 20px; position: sticky; top: 0; z-index: 1000;
            }
            #cover { width: 90px; height: 90px; border: 1px solid var(--green); object-fit: cover; filter: grayscale(50%); }
            
            .portal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 15px; padding: 30px; }
            .pace-card { 
                background: #080808; border: 1px solid #1a1a1a; padding: 20px; 
                display: grid; grid-template-columns: 1fr 180px; gap: 15px;
            }
            
            .ticker { font-size: 3.2em; font-weight: 900; color: var(--green); letter-spacing: -4px; line-height: 1; }
            .asset-name { font-size: 1.1em; color: #aaa; text-transform: uppercase; margin-bottom: 5px; }
            
            /* THE BLOOMBERG GRAPH */
            .spark-container { height: 60px; background: #000; border: 1px solid #111; position: relative; overflow: hidden; margin-top: 10px; }
            canvas { width: 100%; height: 100%; pointer-events: none; }
            
            .mbbo-dock { display: flex; flex-direction: column; gap: 8px; }
            .mbbo-btn { 
                padding: 12px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff;
                cursor: pointer; text-transform: uppercase; font-size: 10px; text-align: left;
            }
            .mbbo-btn:hover { border-color: #fff; }
            .mbbo-btn.static { border-left: 5px solid var(--green); }
            .mbbo-btn.forecast { border-left: 5px solid var(--blue); }
            .mbbo-btn.currency { border-left: 5px solid var(--gold); }
            
            .status-tag { font-size: 9px; color: var(--green); opacity: 0.6; }
        </style>
        <script>
            let charts = {};

            async function sync() {
                const res = await fetch('/api/data'); const data = await res.json();
                if (data.roster) {
                    const grid = document.getElementById('grid');
                    grid.innerHTML = data.roster.map((i, idx) => `
                        <div class="pace-card">
                            <div>
                                <div class="status-tag">PACECARD // PORTAL_ID_100${idx}</div>
                                <div class="asset-name">${i.song}</div>
                                <div class="ticker" id="price-${idx}">$${i.current_price}</div>
                                <div class="spark-container"><canvas id="chart-${idx}"></canvas></div>
                            </div>
                            <div class="mbbo-dock">
                                <button class="mbbo-btn static" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'STATIC')">MBBO: STATIC</button>
                                <button class="mbbo-btn forecast" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'FORECAST')">MBBO: TARGET</button>
                                <button class="mbbo-btn currency" onclick="execute('${i.audio}', '${i.image}', '${i.song}', 'CURRENCY')">MBBO: CURRENCY</button>
                            </div>
                        </div> `).join('');
                    
                    data.roster.forEach((i, idx) => updateChart(idx, i.current_price));
                }
            }

            function updateChart(idx, price) {
                const canvas = document.getElementById(`chart-${idx}`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 50) charts[idx].shift();
                
                ctx.clearRect(0,0, canvas.width, canvas.height);
                ctx.strokeStyle = '#00ff33'; ctx.lineWidth = 2;
                ctx.beginPath();
                const step = canvas.width / 50;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - 5) * 10); // Simple scaling
                    ctx.lineTo(i * step, y);
                });
                ctx.stroke();
            }

            function execute(audio, img, title, type) {
                const player = document.getElementById('master-player');
                document.getElementById('now-playing').innerText = type + " // " + title;
                document.getElementById('cover').src = img;
                player.src = audio;
                player.load();
                
                // FORCE RESUME AUDIO CONTEXT
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
                
                player.play().catch(e => {
                    alert("RADIO PORTAL STANDBY: Tap the Play button on the bar to ignite the stream.");
                });
            }
            setInterval(sync, 4000); window.onload = sync;
        </script>
    </head>
    <body>
        <div class="master-unit">
            <img id="cover" src="https://via.placeholder.com/100?text=AITIFY">
            <div style="flex-grow: 1;">
                <span class="status-tag">97.7 THE FLAME // GLOBAL SATELLITE FEED</span><br>
                <b id="now-playing" style="font-size:1.6em; text-transform:uppercase;">AWAITING BROKER SELECTION</b><br>
                <audio id="master-player" controls crossorigin="anonymous" style="width:100%; height:30px; margin-top:10px;"></audio>
            </div>
        </div>
        <div id="grid" class="portal-grid"></div>
    </body>
    </html>
    ''')

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL); cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url, unit_price FROM gsr_artist_roster ORDER BY id DESC LIMIT 50;")
        roster = [{"song": r[0].upper(), "audio": r[1], "image": r[2], "principal": "{:.2f}".format(float(r[3])), "current_price": "{:.2f}".format(float(r[3]) * 1.4 + random.uniform(-0.08, 0.08))} for r in cur.fetchall()]
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
