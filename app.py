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
        <title>AITIFY | KRAKEN TERMINAL V43</title>
        <style>
            :root { --emerald: #50C878; --red: #ff3300; --bg: #050505; --panel: #0d0d0d; }
            body { background: var(--bg); color: #fff; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; height: 100vh; }
            .terminal-container { display: grid; grid-template-columns: 400px 1fr; height: 100vh; background: #1a1a1a; }
            .monitor { background: #000; padding: 25px; display: flex; flex-direction: column; border-right: 1px solid #222; }
            #cover { width: 100%; aspect-ratio: 1; border: 1px solid #333; object-fit: cover; margin-bottom: 20px; }
            .ignite-btn { background: var(--emerald); color: #000; border: none; padding: 18px; font-weight: 900; cursor: pointer; text-transform: uppercase; margin-bottom: 20px; }
            .trading-floor { background: #020202; overflow-y: auto; padding: 40px; }
            .pace-card { 
                background: var(--panel); border: 1px solid #1a1a1a; padding: 35px; 
                display: flex; flex-direction: column; margin-bottom: 40px; min-height: 680px;
                box-shadow: 0 30px 60px rgba(0,0,0,0.7);
            }
            .card-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 25px; border-bottom: 1px solid #222; padding-bottom: 15px; }
            .ticker-price { font-size: 8em; font-weight: 900; color: var(--emerald); letter-spacing: -10px; line-height: 0.8; }
            .velocity-ticker { font-size: 3em; font-weight: bold; }
            .void-filler-graph { width: 100%; height: 380px; background: #000; border: 1px solid #111; position: relative; margin-bottom: 30px; }
            canvas { width: 100%; height: 100%; }
            .mbbo-dock { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            .mbbo-btn { padding: 22px; font-weight: bold; border: 1px solid #333; background: #000; color: #fff; cursor: pointer; text-transform: uppercase; font-size: 11px; border-top: 5px solid #444; }
            .mbbo-btn:hover { border-top-color: var(--emerald); background: #111; }
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
                                <div style="font-size:9px; color:#444; letter-spacing:4px; margin-bottom:10px;">SIGNAL_STATION_97.7 // ${i.song}</div>
                                <div class="card-header">
                                    <div class="ticker-price" id="price-${idx}">$${i.current_price}</div>
                                    <div id="vel-${idx}" class="velocity-ticker">--</div>
                                </div>
                                <div class="void-filler-graph"><canvas id="canvas-${idx}"></canvas></div>
                                <div class="mbbo-dock">
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">STATIC MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">TARGET MBBO</button>
                                    <button class="mbbo-btn" onclick="ignite('${i.audio}', '${i.image}', '${i.song}')">CURRENCY MBBO</button>
                                </div>
                            </div> `).join('');
                    }
                    data.roster.forEach((i, idx) => updateKrakenPulse(idx, i.current_price));
                }
            }
            function updateKrakenPulse(idx, price) {
                const canvas = document.getElementById(`canvas-${idx}`);
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                if (!charts[idx]) charts[idx] = [];
                let lastP = charts[idx][charts[idx].length - 1] || price;
                let diff = (parseFloat(price) - parseFloat(lastP)).toFixed(2);
                charts[idx].push(parseFloat(price));
                if (charts[idx].length > 400) charts[idx].shift();
                document.getElementById(`price-${idx}`).innerText = `$${price}`;
                document.getElementById(`price-${idx}`).style.color = diff >= 0 ? 'var(--emerald)' : 'var(--red)';
                const vEl = document.getElementById(`vel-${idx}`);
                vEl.innerText = (diff >= 0 ? '▲ ' : '▼ ') + Math.abs(diff);
                vEl.style.color = diff >= 0 ? 'var(--emerald)' : 'var(--red)';
                ctx.clearRect(0,0, canvas.width, canvas.height);
                const rgb = diff >= 0 ? '80, 200, 120' : '255, 51, 0';
                let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
                grad.addColorStop(0, `rgba(${rgb}, 0.2)`);
                grad.addColorStop(1, `rgba(${rgb}, 0)`);
                ctx.fillStyle = grad;
                ctx.strokeStyle = `rgb(${rgb})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                const step = canvas.width / 400;
                charts[idx].forEach((p, i) => {
                    const y = canvas.height - ((p - (price-0.2)) * 600);
                    if(i === 0) ctx.moveTo(i * step, y);
                    else ctx.lineTo(i * step, y);
                });
                ctx.stroke();
                ctx.lineTo(charts[idx].length * step, canvas.height);
                ctx.lineTo(0, canvas.height); ctx.fill();
            }
            function ignite(audio, img, title) {
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

# ... rest of routes (api, mint, stock_asset) same as V42 ...
