from flask import Flask, render_template_string, jsonify
import psycopg2, random, os

app = Flask(__name__)

# YOUR SECURE NEON CONNECTION
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | TERMINAL V16</title>
        <style>
            :root { --bloomberg-green: #00ff33; --glass: rgba(255, 255, 255, 0.05); --glass-border: rgba(255, 255, 255, 0.1); }
            body { background: #010101; color: #e0e0e0; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            .radio-unit { background: #0a0a0a; border-bottom: 1px solid var(--bloomberg-green); padding: 20px 40px; display: grid; grid-template-columns: 120px 1fr 200px; align-items: center; gap: 30px; }
            .album-art { width: 100px; height: 100px; border: 1px solid var(--bloomberg-green); background: #111; object-fit: cover; }
            #floor { overflow-y: auto; height: calc(100vh - 145px); }
            .asset-row { display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; align-items: center; padding: 15px 40px; border-bottom: 1px solid var(--glass-border); cursor: pointer; }
            .price-ticker { font-size: 2.2em; font-weight: 900; color: var(--bloomberg-green); letter-spacing: -2px; }
            .trade-btn { background: var(--bloomberg-green); color: #000; border: none; padding: 10px; font-weight: bold; cursor: pointer; width: 100%; }
        </style>
        <script>
            const urlParams = new URLSearchParams(window.location.search);
            const activeBroker = urlParams.get('broker') || 'HOUSE';

            function loadAsset(song, audio, img) {
                document.getElementById('current-song').innerText = song;
                document.getElementById('main-art').src = img || 'https://via.placeholder.com/100?text=AITIFY';
                const p = document.getElementById('main-player');
                p.src = audio; p.play();
            }

            async function update() {
                const res = await fetch('/api/data');
                const data = await res.json();
                if (data.error) { console.error(data.error); return; }
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                    <div class="asset-row" onclick="loadAsset('${i.song}', '${i.audio}', '${i.image}')">
                        <div style="color:#444;">${1001+idx}</div>
                        <div><b style="color:#fff;">${i.song.toUpperCase()}</b><br><span style="color:var(--bloomberg-green); font-size:8px;">CONTRACT ACTIVE</span></div>
                        <div style="color:var(--bloomberg-green); font-size:9px; border:1px solid; text-align:center;">${i.target_roi}% MBBO</div>
                        <div style="color:#666; text-align:center;">$${i.principal}.00</div>
                        <div class="price-ticker">$${i.current_price}</div>
                        <div style="padding-left:20px;"><button class="trade-btn" onclick="alert('Trade logged for Broker: ' + activeBroker)">TRADE NOW</button></div>
                    </div>
                `).join('');
            }
            setInterval(update, 3000); window.onload = update;
        </script>
    </head>
    <body>
        <div class="radio-unit">
            <img id="main-art" class="album-art" src="https://via.placeholder.com/100?text=AITIFY" alt="Art">
            <div>
                <span style="color:var(--bloomberg-green); font-size:9px; letter-spacing:3px;">ACTIVE BROKER: ${activeBroker}</span><br>
                <b id="current-song" style="font-size:1.8em; color:#fff;">SELECT ASSET</b><br>
                <audio id="main-player" controls style="height:30px; filter: invert(100%); opacity:0.8;"></audio>
            </div>
            <button class="trade-btn" style="height:50px; font-size:14px;" onclick="alert('Trade Sent')">TRADE NOW</button>
        </div>
        <div id="floor"></div>
    </body>
    </html>
    """)

@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT song_title, audio_url, image_url FROM gsr_artist_roster LIMIT 50;")
        rows = cur.fetchall()
        roster = []
        for r in rows:
            principal = (sum(ord(c) for c in r[0]) % 5) + 1
            target_roi = random.choice([35, 50, 80, 95]) # MFP (Forecast)
            roster.append({
                "song": r[0], "principal": principal, "target_roi": target_roi,
                "current_price": "{:.2f}".format(principal * 1.4),
                "audio": r[1] if r[1] else "", "image": r[2] if r[2] else ""
            })
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except Exception as e:
        return jsonify({"error": str(e), "roster": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
