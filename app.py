@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        # Using a more flexible query to avoid column errors
        cur.execute("SELECT song_title, audio_url, image_url FROM gsr_artist_roster LIMIT 50;")
        rows = cur.fetchall()
        roster = []
        for r in rows:
            principal = (sum(ord(c) for c in r[0]) % 5) + 1
            roster.append({
                "song": r[0],
                "principal": principal,
                "target_roi": random.choice([35, 50, 80, 100]),
                "current_price": "{:.2f}".format(principal * 1.5), # Standard vibration
                "audio": r[1] if r[1] else "",
                "image": r[2] if r[2] else ""
            })
        cur.close(); conn.close()
        return jsonify({"roster": roster})
    except Exception as e:
        return jsonify({"error": str(e), "roster": []}) # Prevents the terminal from freezing
