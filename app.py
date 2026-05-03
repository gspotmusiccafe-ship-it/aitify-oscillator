from flask import Flask, render_template_string, jsonify
import psycopg2, random, os

app = Flask(__name__)
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | BROADCAST TERMINAL V13</title>
        <style>
            :root { --bloomberg-green: #00ff33; --glass: rgba(255, 255, 255, 0.05); --glass-border: rgba(255, 255, 255, 0.1); }
            body { background: #010101; color: #e0e0e0; font-family: 'IBM Plex Mono', monospace; margin: 0; overflow: hidden; }
            
            /* MASTER RADIO UNIT */
            .radio-unit { background: #0a0a0a; border-bottom: 1px solid var(--bloomberg-green); padding: 20px 40px; display: grid; grid-template-columns: 120px 1fr 200px; align-items: center; gap: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            .album-art { width: 100px; height: 100px; border: 1px solid var(--bloomberg-green); background: #111; border-radius: 4px; object-fit: cover; box-shadow: 0 0 15px rgba(0, 255, 51, 0.2); }
            
            .now-playing-info { display: flex; flex-direction: column; gap: 5px; }
            .trade-btn-main { background: var(--bloomberg-green); color: #000; border: none; padding: 12px 25px; font-weight: 900; border-radius: 3px; cursor: pointer; text-transform: uppercase; letter-spacing: 2px; animation: pulse-glow 2s infinite; }
            
            @keyframes pulse-glow {
                0% { box-shadow: 0 0 5px var(--bloomberg-green); }
                50% { box-shadow: 0 0 25px var(--bloomberg-green); }
                100% { box-shadow: 0 0 5px var(--bloomberg-green); }
            }

            #floor { overflow-y: auto; height: calc(100vh - 145px); }
            .asset-row { display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; align-items: center; padding: 15px 40px; border-bottom: 1px solid var(--glass-border); background: var(--glass); }
            .price-ticker { font-size: 2.2em; font-weight: 900; color: var(--bloomberg-green); letter-spacing: -2px; }

            /* GLASS CONTROLS */
            .glass-input { background: rgba(0,0,0,0.5); border: 1px solid var(--glass-border); color: var(--bloomberg-green); padding: 5px; font-family: inherit; font-size: 10px; width: 100%; margin-top: 5px; }
        </style>
        <script>
            function updatePlayer(songName, imgUrl) {
                document.getElementById('current-song').innerText = songName;
                document.getElementById('main-art').src = imgUrl;
            }

            async function updateMarket() {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => `
                    <div class="asset-row">
                        <div style="color:#444;">${1001+idx}</div>
                        <div><b style="color:#fff; font-size:1.1em;">${i.song.toUpperCase()}</b><br><span style="color:var(--bloomberg-green); font-size:8px;">4:00M CONTRACT</span></div>
                        <div><span style="border:1px solid var(--bloomberg-green); color:var(--bloomberg-green); padding:2px 5px; font-size:9px;">${i.target_roi}% MBBO</span></div>
                        <div style="color:#666; text-align:center;">$${i.principal}.00</div>
                        <div class="price-ticker">$${i.current_price}</div>
                        <div style="padding-left:20px;"><button class="trade-btn-main" style="font-size:9px; padding:8px 12px; animation:none;">TRADE NOW</button></div>
                    </div>
                `).join('');
            }
            setInterval(updateMarket, 2000); window.onload = updateMarket;
        </script>
    </head>
    <body>
        <div class="radio-unit">
            <img id="main-art" class="album-art" src="https://via.placeholder.com/100?text=AITIFY+IMG" alt="Art">
            <div class="now-playing-info">
                <span style="color:var(--bloomberg-green); font-size:9px; letter-spacing:3px;">BROADCASTING LIVE: 97.7 THE FLAME</span>
                <b id="current-song" style="font-size:1.8em; letter-spacing:1px; color:#fff;">SELECT ASSET TO BROADCAST</b>
                <div style="display:flex; gap:10px; align-items:center;">
                    <audio controls style="height:30px; filter: invert(100%); opacity:0.8;">
                        <source src="" type="audio/mpeg">
                    </audio>
                    <span style="color:#444; font-size:10px;">| MBBO LIQUIDITY: $522/1K</span>
                </div>
            </div>
            <button class="trade-btn-main" onclick="alert('Trade Order Sent to Queue')">TRADE NOW</button>
        </div>

        <div class="market-grid-header" style="display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; padding: 10px 40px; background: rgba(0, 255, 51, 0.05); color: var(--bloomberg-green); font-size: 9px; border-bottom: 1px solid var(--glass-border);">
            <div>INDEX</div><div>ASSET CONTRACT</div><div>MARKET OFFER</div><div>PRINCIPAL</div><div>CURRENT PRICE</div><div>EXECUTION</div>
        </div>
        <div id="floor"></div>
    </body>
    </html>
    """)

@app.route('/api/data')
def get_data():
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    cur.execute("SELECT song_title FROM gsr_artist_roster LIMIT 50;")
    roster = []
    for r in cur.fetchall():
        song_name = r[0]
        principal = (sum(ord(char) for char in song_name) % 5) + 1
        target_roi = random.choice([35, 50, 80, 100])
        final_price = principal * (1 + (target_roi / 100))
        current_price = "{:.2f}".format(max(principal, final_price + random.uniform(-0.1, 0.1)))
        roster.append({"song": song_name, "principal": principal, "target_roi": target_roi, "current_price": current_price})
    cur.close(); conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
