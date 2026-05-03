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
        <title>AITIFY | ASSET EXCHANGE V10</title>
        <style>
            :root { --gold: #FFD700; --green: #00ff00; --red: #ff3e3e; --bg: #000; --panel: #111; }
            body { background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; font-size: 12px; }
            
            /* EXCHANGE INTERFACE */
            .market-header { display: grid; grid-template-columns: 80px 2fr 120px 100px 150px 140px; padding: 12px 25px; background: #1a1a1a; color: #666; font-size: 10px; font-weight: bold; border-bottom: 1px solid #333; text-transform: uppercase; }
            
            .up-signal { color: var(--green); text-shadow: 0 0 10px rgba(0,255,0,0.3); }
            .down-signal { color: var(--red); text-shadow: 0 0 10px rgba(255,62,62,0.3); }
            
            #floor { overflow-y: auto; height: calc(100vh - 110px); }
            .trade-row { display: grid; grid-template-columns: 80px 2fr 120px 100px 150px 140px; align-items: center; padding: 15px 25px; border-bottom: 1px solid #222; font-family: 'Courier New', monospace; }
            .trade-row:hover { background: #0a0a0a; border-left: 4px solid var(--gold); }
            
            .price-ticker { font-size: 2em; font-weight: 900; text-align: right; }
            .status-tag { padding: 3px 7px; border-radius: 2px; font-weight: bold; font-size: 10px; text-transform: uppercase; border: 1px solid #333; }
            
            .execute-btn { background: #fff; color: #000; border: none; padding: 10px; font-weight: 900; cursor: pointer; width: 100%; border-radius: 2px; }
            .execute-btn:hover { background: var(--gold); }
            
            .duration-track { height: 2px; background: #222; margin-top: 6px; width: 100%; overflow: hidden; }
            .track-fill { height: 100%; background: var(--gold); transition: width 1s linear; }
        </style>
        <script>
            async function update() {
                const res = await fetch('/api/data');
                const data = await res.json();
                document.getElementById('floor').innerHTML = data.roster.map((i, idx) => {
                    const statusClass = i.is_up ? "up-signal" : "down-signal";
                    const arrow = i.is_up ? "▲" : "▼";
                    
                    return `<div class="trade-row">
                        <div style="color:#444;">#${1001+idx}</div>
                        <div>
                            <b style="color:#fff; font-size:1.1em;">${i.song}</b><br>
                            <span style="color:#666; font-size:9px;">CONTRACT: 4:00M</span>
                            <div class="duration-track"><div class="track-fill" style="width:${i.progress}%"></div></div>
                        </div>
                        <div><span class="status-tag ${statusClass}">${arrow} ${i.target_roi}% OFFER</span></div>
                        <div style="color:#666; text-align:center;">$${i.principal}.00</div>
                        <div class="price-ticker ${statusClass}">$${i.current_price}</div>
                        <div style="padding-left:20px;"><button class="execute-btn">LIMIT BUY</button></div>
                    </div>`;
                }).join('');
            }
            setInterval(update, 2000); window.onload = update;
        </script>
    </head>
    <body>
        <div style="padding: 15px 25px; border-bottom: 2px solid var(--gold); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight:900; font-size:1.5em; letter-spacing:3px;">AITIFY <span style="color:var(--gold)">EXCHANGE V10</span></span>
            <div style="text-align:right;"><span style="color:#666; font-size:10px;">CAPACITY RESERVE</span><br><b>$1,428,990.22</b></div>
        </div>
        <div class="market-header">
            <div>ID</div><div>MUSIC ASSET / DURATION</div><div>MARKET OFFER</div><div>PRINCIPAL</div><div>CURRENT PRICE</div><div>ACTION</div>
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
        # ASSET LOGIC
        principal = (sum(ord(char) for char in song_name) % 5) + 1
        
        # PREDETERMINED TARGET (Dictated by you)
        target_roi = random.choice([35, 85, 94, 100]) 
        final_price = principal * (1 + (target_roi / 100))
        
        # OSCILLATION ROLE: Price vibrates but stays below your predetermined close
        vibration = random.uniform(-0.15, 0.15)
        current_price = "{:.2f}".format(max(principal, final_price + vibration))
        
        roster.append({
            "song": song_name, "principal": principal, "target_roi": target_roi,
            "current_price": current_price, "progress": random.randint(10, 90),
            "is_up": vibration > 0
        })
    cur.close(); conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
