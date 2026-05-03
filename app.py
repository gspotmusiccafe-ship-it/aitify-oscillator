from flask import Flask, render_template_string, jsonify
import psycopg2, random, os

app = Flask(__name__)

# Link to your Neon Database
DB_URL = "postgresql://neondb_owner:npg_49bsxXGdfouV@ep-calm-sun-a4s6bd19-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | 97.7 THE FLAME OSCILLATOR V5</title>
        <style>
            :root { --gold: #FFD700; --green: #00ff00; --red: #ff3e3e; --bg: #000; }
            body { background: #000; color: #fff; font-family: 'Roboto Mono', monospace; margin: 0; overflow: hidden; font-size: 11px; }
            
            @keyframes pulse-green { 0% { color: #004400; } 50% { color: #00ff00; text-shadow: 0 0 15px #00ff00; } 100% { color: #004400; } }
            @keyframes pulse-red { 0% { color: #440000; } 50% { color: #ff3e3e; text-shadow: 0 0 15px #ff3e3e; } 100% { color: #440000; } }
            .vibrate-green { animation: pulse-green 1s infinite; font-weight: 900; }
            .vibrate-red { animation: pulse-red 1s infinite; font-weight: 900; }

            .ticker-wrap { background: #050505; border-bottom: 2px solid var(--gold); padding: 12px 0; overflow: hidden; white-space: nowrap; }
            .ticker { display: inline-block; animation: ticker-move 140s linear infinite; font-weight: 900; }
            @keyframes ticker-move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
            
            .terminal-grid { display: grid; grid-template-columns: 240px 1fr 340px; height: calc(100vh - 45px); }
            .genre-remote { background: #050505; border-right: 1px solid #222; padding: 20px; }
            .genre-btn { width: 100%; background: #111; border: 1px solid #333; color: #888; padding: 12px; margin-bottom: 8px; text-align: left; cursor: pointer; font-size: 10px; border-radius: 4px; }
            
            #floor { overflow-y: auto; background: #000; }
            .asset-row { display: grid; grid-template-columns: 60px 1.5fr 150px 80px 120px 140px; align-items: center; padding: 18px 25px; border-bottom: 1px solid #111; }
            .price-cell { font-family: 'Courier New', monospace; font-size: 2.2em; font-weight: 900; text-align: right; }
            .execute-btn { background: linear-gradient(145deg, #222, #000); color: var(--gold); border: 1px solid var(--gold); padding: 10px 15px; font-weight: 900; cursor: pointer; border-radius: 50px; text-transform: uppercase; font-size: 10px; }
        </style>
        <script>
            const audio = new Audio();
            function executeTrade(song, url) {
                document.getElementById('now-playing').innerText = song;
                audio.src = url; audio.play();
            }
            async function update() {
                try {
                    const res = await fetch('/api/data');
                    const data = await res.json();
                    let tickerHtml = "";
                    data.roster.forEach(i => {
                        const style = i.is_up ? "vibrate-green" : "vibrate-red";
                        tickerHtml += `<span style="color:var(--gold); margin-right:60px; font-size:1.5em;">${i.song} <span class="${style}">${i.is_up?'▲':'▼'} ${i.roi}%</span></span>`;
                    });
                    document.getElementById('ticker').innerHTML = tickerHtml;
                    document.getElementById('floor').innerHTML = data.roster.map((i, idx) => {
                        const style = i.is_up ? "vibrate-green" : "vibrate-red";
                        return `<div class="asset-row">
                            <div style="color:#444;">${1001+idx}</div>
                            <div><b style="color:#fff;">${i.song}</b><br><span class="${style}" style="font-size: 9px; letter-spacing:2px; font-weight:bold;">OSCILLATING LIVE</span></div>
                            <div style="height:30px; border-bottom: 1px solid #222;"></div>
                            <div style="text-align:center; color:#666;">4:00M</div>
                            <div class="price-cell ${style}">$${i.vibrated}</div>
                            <div style="text-align:right;"><button class="execute-btn" onclick="executeTrade('${i.song}', '${i.audio_url}')">BUY $${i.buy_in}.00</button></div>
                        </div>`;
                    }).join('');
                } catch(e) { console.log("Signal Lost..."); }
            }
            setInterval(update, 3000); window.onload = update;
        </script>
    </head>
    <body>
        <div class="ticker-wrap"><div class="ticker" id="ticker">AITIFY | SIGNAL ESTABLISHED V5...</div></div>
        <div class="terminal-grid">
            <div class="genre-remote">
                <p style="color:var(--gold); font-size:9px; margin-bottom:15px;">ASSET CLASSES</p>
                <button class="genre-btn">97.7 THE FLAME (AUTO)</button>
            </div>
            <div id="floor"></div>
            <div class="sidebar" style="padding:25px; background:#050505; border-left:1px solid var(--gold);">
                <div style="border:1px solid #222; padding:20px; background:#000;"><span style="color:var(--gold); font-size:9px;">AITIFY TREASURY</span><br><span style="font-size:2em; font-weight:900;">$1,428,990.22</span></div>
                <div style="margin-top:20px; text-align:center; border:1px solid #222; padding:20px; background:#080808; border-radius:12px;">
                    <b style="color:var(--red); font-size:10px; letter-spacing:2px;">LIVE ON AIR</b>
                    <p id="now-playing" style="color:var(--gold); font-size:14px; font-weight:900; margin:10px 0;">STATION STANDBY</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/api/data')
def get_data():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT song_title FROM gsr_artist_roster LIMIT 50;")
    roster = []
    for r in cur.fetchall():
        song_name = r[0]
        fixed_buy_in = (sum(ord(char) for char in song_name) % 5) + 1
        url = "https://firebasestorage.googleapis.com/v0/b/aititrade-radio-97.firebasestorage.app/o/I_GOT_WHAT_YOU_NEED.mp3?alt=media"
        roster.append({"song": song_name, "buy_in": fixed_buy_in, "vibrated": round(fixed_buy_in + random.uniform(-0.5, 1.2), 2), "is_up": random.choice([True, False]), "roi": random.randint(65, 95), "audio_url": url})
    cur.close()
    conn.close()
    return jsonify({"roster": roster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
