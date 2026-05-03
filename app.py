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
        <title>AITIFY | TERMINAL BLOOMBERG V11</title>
        <style>
            :root { --bloomberg-green: #00ff33; --bloomberg-red: #ff003c; --glass: rgba(255, 255, 255, 0.03); --glass-border: rgba(255, 255, 255, 0.1); }
            body { background: #020202; color: #e0e0e0; font-family: 'IBM Plex Mono', 'Courier New', monospace; margin: 0; overflow: hidden; font-size: 11px; }
            
            /* BLOOMBERG TERMINAL GLASS HEADER */
            .terminal-header { background: #0a0a0a; border-bottom: 1px solid var(--bloomberg-green); padding: 12px 25px; display: flex; justify-content: space-between; align-items: center; }
            .market-status { color: var(--bloomberg-green); font-weight: bold; letter-spacing: 2px; }

            /* GLASS GRID SYSTEM */
            .market-grid-header { display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; padding: 10px 25px; background: rgba(0, 255, 51, 0.05); color: var(--bloomberg-green); font-size: 9px; border-bottom: 1px solid var(--glass-border); }
            
            #floor { overflow-y: auto; height: calc(100vh - 100px); }
            .asset-row { display: grid; grid-template-columns: 70px 2fr 130px 100px 160px 140px; align-items: center; padding: 12px 25px; border-bottom: 1px solid var(--glass-border); background: var(--glass); transition: 0.2s; }
            .asset-row:hover { background: rgba(255, 255, 255, 0.06); border-left: 2px solid var(--bloomberg-green); }

            /* VIBRATION & SIGNAL */
            .signal-up { color: var(--bloomberg-green); text-shadow: 0 0 8px rgba(0, 255, 51, 0.4); }
            .signal-down { color: var(--bloomberg-red); text-shadow: 0 0 8px rgba(255, 0, 60, 0.4); }
            
            .price-display { font-size: 2.4em; font-weight: 900; text-align: right; letter-spacing: -2px; }
            .offer-badge { border: 1px solid currentColor; padding: 2px 6px; font-weight: bold; border-radius: 2px; font-size: 10px; background: rgba(0,0,0,0.3); }

            /* GLASS LIMIT BUTTON */
            .glass-btn { background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid var(--glass-border); padding: 10px; font-weight: bold; cursor: pointer; backdrop-filter: blur(5px); border-radius: 3px; text-transform: uppercase; width: 100%; transition: all 0.3s; }
            .glass-btn:hover { background: var(--bloomberg-green); color: #000; border-color: var(--bloomberg-green); box-shadow: 0 0 15px var(--bloomberg-green); }

            .contract-bar { height: 1px; background: #222; margin-top: 8px; width: 100%; }
            .contract-fill { height: 100%; background: var(--bloomberg-green); transition: width 1s linear; }
        </style>
        <script>
            async function update() {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => {
                    const status = i.is_up ? "signal-up" : "signal-down";
                    return `<div class="asset-row">
                        <div style="color:#555;">${1001+idx}</div>
                        <div>
                            <b style="color:#fff; font-size:1.2em; letter-spacing:1px;">${i.song.toUpperCase()}</b><br>
                            <div class="contract-bar"><div class="contract-fill" style="width:${i.progress}%"></div></div>
                        </div>
                        <div><span class="offer-badge ${status}">${i.is_up ? '▲' : '▼'} ${i.target_roi}% MBBO</span></div>
                        <div style="color:#888; text-align:center;">$${i.principal}.00</div>
                        <div class="price-display ${status}">$${i.current_price}</div>
                        <div style="padding-left:20px;"><button class="glass-btn">LIMIT BUY</button></div>
                    </div>`;
                }).join('');
            }
            setInterval(update, 2000); window.onload = update;
        </script>
    </head>
    <body>
        <div class="terminal-header">
            <span style="font-weight:900; font-size:1.6em; letter-spacing:4px;">AITIFY <span style="color:var(--bloomberg-green)">TERMINAL</span></span>
            <div style="text-align:right;">
                <span style="color:#666; font-size:9px;">CAPACITY RESERVE</span><br>
                <b class="market-status">$1,428,990.22</b>
            </div>
        </div>
        <div class="market-grid-header">
            <div>INDEX</div><div>ASSET / CONTRACT DURATION</div><div>MARKET OFFER</div><div>PRINCIPAL</div><div>CURRENT PRICE</div><div>EXECUTION</div>
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
        vibration = random.uniform(-0.12, 0.12)
        current_price = "{:.2f}".format(max(principal, final_price + vibration))
        roster.append({
            "song": song_name, "principal": principal, "target_roi": target_roi,
            "current_price": current_price, "progress": random.randint(5, 95),
            "is_up": vibration > 0
        })
    cur.close(); conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
