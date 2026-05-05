@app.route('/')
def home():
    # 🏦 THE BANKER'S STATUS BOARD
    return """
    <body style="background:#000; color:#0f0; font-family:monospace; padding:50px;">
        <h1 style="color:#f0f; border-bottom:2px solid #222; padding-bottom:10px;">97.7 THE FLAME | REGULATOR ACTIVE</h1>
        <div style="margin-top:20px; font-size:18px;">
            <p>> SYSTEM: ONLINE</p>
            <p>> KINETIC FEED: ACTIVE</p>
            <p>> DATA SOURCE: <a href="/api/market-data" style="color:#0f0;">/api/market-data</a></p>
        </div>
        <div style="margin-top:50px; color:#444; font-size:10px;">
            AITITRADE DEX ENGINE v2.0 | MUSIC MEETS WALL STREET
        </div>
    </body>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
