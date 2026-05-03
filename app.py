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
        <title>AITIFY | GLOBAL ASSET EXCHANGE V8</title>
        <style>
            :root { --gold: #FFD700; --green: #00ff00; --red: #ff3e3e; --bg: #000; --gray: #1a1a1a; }
            body { background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; font-size: 12px; }
            
            /* EXCHANGE HEADERS */
            .market-header { display: grid; grid-template-columns: 60px 2fr 100px 100px 120px 140px; padding: 10px 25px; background: var(--gray); color: #666; font-weight: bold; border-bottom: 1px solid #333; text-transform: uppercase; letter-spacing: 1px; font-size: 10px; }
            
            /* VIBRATION & MOVEMENT */
            .up-signal { color: var(--green); text-shadow: 0 0 5px rgba(0,255,0,0.5); }
            .down-signal { color: var(--red); text-shadow: 0 0 5px rgba(255,62,62,0.5); }
            .arrow { font-size: 14px; margin-right: 5px; display: inline-block; }
            
            #floor { overflow-y: auto; height: calc(100vh - 100px); scrollbar-width: thin; scrollbar-color: #333 #000; }
            .trade-row { display: grid; grid-template-columns: 60px 2fr 100px 100px 120px 140px; align-items: center; padding: 15px 25px; border-bottom: 1px solid #111; font-family: 'Courier New', monospace; }
            .trade-row:hover { background: #0a0a0a; border-left: 3px solid var(--gold); }
            
            .price-ticker { font-size: 1.8em; font-weight: 900; text-align: right; letter-spacing: -1px; }
            .points-badge { padding: 2px 6px; border-radius: 2px; font-weight: bold; font-size: 10px; }
            .bg-green { background: rgba(0, 255, 0, 0.1); border: 1px solid var(--green); }
            .bg-red { background: rgba(255, 62, 62, 0.1); border: 1px solid var(--red); }

            /* BUTTONS */
            .execute-btn { background: #fff; color: #000; border: none; padding: 8px 12px; font-weight: 900; cursor: pointer; border-radius: 2px; width: 100%; transition: 0.2s; }
            .execute-btn:hover { background: var(--gold); }
        </style>
        <script>
            async function update() {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => {
                    const isUp = i.is_up;
                    const statusClass = isUp ? "up-signal" : "down-signal";
                    const badgeClass = isUp ? "bg-green" : "bg-red";
                    const arrow = isUp ? "▲" : "▼";
                    
                    return `<div class="trade-row">
                        <div style="color:#444;">${1001+idx}</div>
                        <div><b style="color:#fff; font-size:1.1em;">${i.song}</b></div>
                        <div class="${statusClass}"><span class="points-badge ${badgeClass}">${arrow} ${i.points}</span></div>
                        <div style="color:#666; text-align:center;">${i.vol}k VOL</div>
                        <div class="price-ticker ${statusClass}">$${i.vibrated}</div>
                        <div style="padding-left:20px;"><button class="execute-btn">LIMIT BUY</button></div>
                    </div>`;
                }).join('');
            }
            setInterval(update, 2000); window.onload = update;
        </script>
    </head>
    <body>
        <div style="padding: 15px 25px; border-bottom: 2px solid var(--gold); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight:900; font-size:1.5em; letter-spacing:2px;">AITIFY <span style="color:var(--gold)">EXCHANGE</span></span>
            <div style="text-align:right;"><span style="color:#666; font-size:10px;">MARKET CAP</span><br><b>$1,428,990.22</b></div>
        </div>
        <div class="market-header">
            <div>ID</div><div>ASSET PAIR</div><div>SPREAD</div><div>VOLUME</div><div>MARKET PRICE</div><div>ACTION</div>
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
        points = random.randint(10, 99)
        buy_in = (sum(ord(char) for char in song_name) % 5) + 1
        roster.append({
            "song": song_name, "buy_in": buy_in, "points": points, "vol": random.randint(100, 999),
            "vibrated": round(buy_in + (points/100), 2), "is_up": random.choice([True, False])
        })
    cur.close(); conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
