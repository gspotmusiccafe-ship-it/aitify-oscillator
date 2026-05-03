# --- THE MINTING SUITE (ADMIN ONLY) ---
@app.route('/mint')
def minting_suite():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AITIFY | MINTING SUITE</title>
        <style>
            :root { --bloomberg-green: #00ff33; --glass: rgba(0, 255, 51, 0.05); }
            body { background: #010101; color: var(--bloomberg-green); font-family: 'IBM Plex Mono'; padding: 40px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .station { border: 1px solid var(--bloomberg-green); padding: 20px; background: #0a0a0a; }
            textarea, input { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 10px; margin-top: 10px; }
            .action-btn { background: var(--bloomberg-green); color: #000; border: none; padding: 10px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>AITIFY PRODUCTION ROOM</h1>
        <div class="grid">
            <div class="station">
                <h3>[1] LYRIC GENERATOR</h3>
                <input type="text" id="prompt" placeholder="Enter Vibe (e.g. Luxury Trap, 90s R&B)">
                <button class="action-btn" onclick="alert('Generating Lyrics...')">GENERATE TEXT</button>
                <textarea rows="5" placeholder="Lyrics will appear here..."></textarea>
            </div>
            
            <div class="station">
                <h3>[2] IMAGE GENERATOR</h3>
                <input type="text" placeholder="Visual Prompt">
                <button class="action-btn" onclick="alert('Rendering Art...')">MINT COVER ART</button>
                <div style="height:100px; background:#111; margin-top:10px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; font-size:10px;">PREVIEW BOX</div>
            </div>

            <div class="station" style="grid-column: span 2;">
                <h3>[3] FINAL MINT & DEPLOY</h3>
                <form action="/stock_asset" method="post" enctype="multipart/form-data" style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <input type="text" name="title" placeholder="ASSET TITLE" required>
                    <input type="number" step="0.01" name="price" placeholder="UNIT PRICE ($1-$5)" required>
                    <input type="file" name="audio" accept="audio/*" required>
                    <input type="file" name="image" accept="image/*" required>
                    <button type="submit" class="action-btn" style="grid-column: span 2; height: 60px; font-size: 1.2em;">COMMIT TO EXCHANGE</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    ''')
