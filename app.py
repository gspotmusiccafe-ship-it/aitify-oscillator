# Add this route to the bottom of app.py, before 'if __name__ == "__main__":'

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    # Capture current Banker settings
    forecast = request.args.get('forecast', BANKER_FORECAST, type=int)
    close = request.args.get('close', BANKER_CLOSE, type=int)
    
    live_assets = []
    for song in SONG_ASSETS:
        # Replicate the Banker's 0-100% bounce
        current_pct = random.randint(0, 100)
        market_price = round(song['floor'] + (song['ceiling'] - song['floor']) * (current_pct / 100), 2)
        
        live_assets.append({
            "id": song['id'],
            "title": song['title'],
            "floor": song['floor'],
            "current_price": market_price,
            "current_pct": current_pct,
            "is_closed": current_pct >= close,
            "is_target_hit": current_pct >= forecast
        })
        
    return jsonify({
        "assets": live_assets,
        "regulator": {"forecast": forecast, "close": close}
    })
