# Updated API to calculate and serve Broker Spread Earnings
@app.route('/api/broker_stats/<broker_id>')
def broker_stats(broker_id):
    conn = psycopg2.connect(DB_URL); cur = conn.cursor()
    # Summing the spread from the tiered settlement logic
    cur.execute("""
        SELECT SUM(principal * (forecast_roi - settled_roi) / 100) 
        FROM rapid_trade_queue 
        WHERE broker_id = %s AND status = 'SETTLED'
    """, (broker_id,))
    total_earned = cur.fetchone()[0] or 0.00
    
    can_withdraw = total_earned >= 50.00
    return jsonify({
        "broker": broker_id,
        "total_earned": "{:.2f}".format(total_earned),
        "withdrawal_status": "READY" if can_withdraw else "LOCKED (MIN $50)"
    })
