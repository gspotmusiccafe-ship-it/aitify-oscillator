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
        <title>AITIFY | 97.7 THE FLAME OSCILLATOR V7</title>
        <style>
            :root { --gold: #FFD700; --green: #00ff00; --red: #ff3e3e; --bg: #000; }
            body { background: #000; color: #fff; font-family: 'Roboto Mono', monospace; margin: 0; overflow: hidden; font-size: 11px; }
            
            /* STOCK ARROW VIBRATION */
            .vibrate-green { color: var(--green); text-shadow: 0 0 12px var(--green); font-weight: 900; }
            .vibrate-red { color: var(--red); text-shadow: 0 0 12px var(--red); font-weight: 900; }
            .arrow-up { font-size: 1.4em; color: var(--green); display: inline-block; animation: bounce-up 0.5s infinite alternate; }
            .arrow-down { font-size: 1.4em; color: var(--red); display: inline-block; animation: bounce-down 0.5s infinite alternate; }
            
            @keyframes bounce-up { from { transform: translateY(0); } to { transform: translateY(-3px); } }
            @keyframes bounce-down { from { transform: translateY(0); } to { transform: translateY(3px); } }

            .ticker-wrap { background: #050505; border-bottom: 2px solid var(--gold); padding: 12px 0; overflow: hidden; white-space: nowrap; }
            .ticker { display: inline-block; animation: ticker-move 140s linear infinite; }
            @keyframes ticker-move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
            
            .terminal-grid { display: grid; grid-template-columns: 240px 1fr 340px; height: calc(100vh - 45px); }
            #floor { overflow-y: auto; background: #000; scroll-behavior: smooth; }
            .asset-row { display: grid; grid-template-columns: 60px 1.8fr 120px 80px 120px 140px; align-items: center; padding: 20px 25px; border-bottom: 1px solid #111; transition: background 0.3s; }
            .asset-row:hover { background: #080808; }
            .price-cell { font-family: 'Courier New', monospace; font-size: 2.2em; font-weight: 900; text-align: right; }
            .execute-btn { background: linear-gradient(145deg, #222, #000); color: var(--gold); border: 1px solid var(--gold); padding: 10px 15px; font-weight: 900; cursor: pointer; border-radius: 4px; font-size: 10px; text-transform: uppercase; }
        </style>
        <script>
            async function update() {
                try {
                    const res = await fetch('/api/data');
                    const data = await res.json();
                    
                    document.getElementById('floor').innerHTML = data.roster.map((i, idx) => {
                        const isUp = i.is_up;
                        const statusClass = isUp ? "vibrate-green" : "vibrate-red";
                        const arrow = isUp ? '<span class="arrow-up">▲</span>' : '<span class="arrow-down">▼</span>';
                        const sign = isUp ? "+" : "-";
                        
                        return `<div class="asset-row">
                            <div style="color:#444;">${1001+idx}</div>
                            <div>
                                <b style="color:#fff; font-size:1.2em;">${i.song}</b><br>
                                <span class="${statusClass}" style="letter-spacing:1px;">${arrow} ${sign}${i.points} POINTS</span>
                            </div>
                            <div style="text-align:center; color:#222; font-size:1.5em;">| | | |</div>
                            <div style="text-align:center; color:#666;">4:00M</div>
                            <div class="price-cell ${statusClass}">$${i.vibrated}</div>
                            <div style="text-align:right;"><button class="execute-btn">EXECUTE $${i.buy_in}.00</button></div>
                        </div>`;
                    }).join('');
                } catch (e) { console.error("Market Signal Interrupted"); }
            }
            setInterval(update, 2500); window.onload = update;
        </script>
    </head>
    <body>
        <div class="ticker-wrap"><div class="ticker" id="ticker" style="color:var(--gold); font-size:1.5em; font-weight:900;">AITIFY | TRADING FLOOR ACTIVE | V7</div></div>
        <div class="terminal-grid">
            <div style="background: #050505; border-right: 1px solid #222; padding: 20px;">
                <p style="color:var(--gold); font-size:9px; letter-spacing:2px;">OPERATIONS</p>
                <button style="width:100%; background:#111; border:1px solid #333; color:var(--gold); padding:12px; font-size:10px; text-align:left; font-weight:900;">97.7 THE FLAME</button>
            </div>
            <div id="floor"></div>
            <div style="padding:25px; background:#050505; border-left:1px solid var(--gold);">
                <div style="border:1px solid #222; padding:20px; background:#000;"><span style="color:var(--gold); font-size:9px;">TREASURY RESERVE</span><br><span style="font-size:2em; font-weight:900;">$1,428,990.22</span></div>
            </div>
        </div>
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
        points = random.randint(15, 95)
        buy_in = (sum(ord(char) for char in song_name) % 5) + 1
        roster.append({
            "song": song_name, 
            "buy_in": buy_in, 
            "points": points,
            "vibrated": round(buy_in + (points/100), 2), 
            "is_up": random.choice([True, False])
        })
    cur.close(); conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
