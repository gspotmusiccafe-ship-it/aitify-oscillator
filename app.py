# Updated Asset List with your Firebase filenames
SONG_ASSETS = [
    {"id": 0, "title": "BETTER THAN GOOD", "file": "BETTER THAN GOOD (1).mp3", "price": 1.05},
    {"id": 1, "title": "I'M NOT HER", "file": "I'M NOT HER.mp3", "price": 0.98},
    {"id": 2, "title": "LOVE MAKE OVER", "file": "LOVE MAKE OVER.mp3", "price": 1.12},
    {"id": 3, "title": "TIMES UP", "file": "TIMES UP.mp3", "price": 0.85},
    # The Oscillator will now track these prices in real-time
]

@app.route('/')
def health_check():
    # This turns your white page into a live ticker
    ticker_html = "<h1>97.7 THE FLAME | LIVE MARKET</h1>"
    for song in SONG_ASSETS:
        ticker_html += f"<p>{song['title']}: ${song['price']} <span style='color:green;'>▲</span></p>"
    return ticker_html
