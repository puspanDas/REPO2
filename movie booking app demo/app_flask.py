from flask import Flask, request, jsonify, send_from_directory
import redis
from flask_cors import CORS
import random
import os
from functools import lru_cache
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Optimized Redis connection with connection pooling
pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True, max_connections=20)
r = redis.Redis(connection_pool=pool)

LOCATIONS = ["Kolkata", "Delhi", "Mumbai", "Bangalore"]

THEATRES = {
    "1": {"name": "INOX: South City", "location": "Kolkata"},
    "2": {"name": "PVR: Diamond Plaza", "location": "Kolkata"},
    "3": {"name": "Cinepolis: Lake Mall", "location": "Kolkata"},
    "4": {"name": "INOX: Quest Mall", "location": "Kolkata"},
    "5": {"name": "Cinepolis: Acropolis Mall", "location": "Kolkata"},
    "6": {"name": "INOX: Nehru Place", "location": "Delhi"},
    "7": {"name": "PVR: DLF Promenade", "location": "Delhi"},
    "8": {"name": "Cinepolis: Select Citywalk", "location": "Delhi"},
    "9": {"name": "INOX: R City Mall", "location": "Mumbai"},
    "10": {"name": "PVR: Phoenix Marketcity", "location": "Mumbai"},
    "11": {"name": "Cinepolis: Andheri West", "location": "Mumbai"},
    "12": {"name": "INOX: Orion Mall", "location": "Bangalore"},
    "13": {"name": "PVR: Forum Mall", "location": "Bangalore"},
    "14": {"name": "Cinepolis: ETA Mall", "location": "Bangalore"}
}

MOVIES = {
    "201": {"name": "Param Sundari", "genres": "Comedy/Drama/Romantic", "rating": "164.8K Likes", "poster_url": "static/param_sundari.jpg"},
    "202": {"name": "Vash Level 2", "genres": "Supernatural/Thriller", "rating": "8.7/10 936 Votes", "poster_url": "static/vash_level_2.jpg"},
    "203": {"name": "Dhumketu", "genres": "Drama/Family", "rating": "7.3/10 15.3K Votes", "poster_url": "static/dhumketu.jpg"},
    "204": {"name": "War 2", "genres": "Action/Thriller", "rating": "7.8/10 160.9K Votes", "poster_url": "static/war2.jpg"},
    "205": {"name": "Mahavatar Narsimha", "genres": "Action/Animation/Drama", "rating": "9.6/10 289.6K Votes", "poster_url": "static/mahavatar_narsimha.jpg"}
}

TECH_TYPES = ['ATMOS', 'LASER', 'INSIGNIA', 'DOLBY 7.1']
SHOWTIME_SLOTS = [
    "09:10 AM", "10:00 AM", "11:00 AM", "12:05 PM", "01:50 PM", "03:10 PM", "04:45 PM",
    "05:45 PM", "07:40 PM", "08:40 PM", "10:35 PM", "11:35 PM"
]

# Generate showtimes
SHOWTIMES = []
showtime_id = 1
for tid in THEATRES:
    for mid in MOVIES:
        for idx, slot in enumerate(SHOWTIME_SLOTS):
            SHOWTIMES.append({
                "id": str(showtime_id),
                "theatre_id": tid,
                "movie_id": mid,
                "time": slot,
                "technology": TECH_TYPES[idx % len(TECH_TYPES)],
                "cancellable": ((idx % 4) < 3),
            })
            showtime_id += 1

def initialize_data():
    """Initialize Redis data"""
    for tid, tdat in THEATRES.items():
        r.hset(f"theatre:{tid}", mapping=tdat)
    for mid, mdat in MOVIES.items():
        r.hset(f"movie:{mid}", mapping=mdat)
    for st in SHOWTIMES:
        r.hset(f"showtime:{st['id']}", mapping={
            "movie_id": st["movie_id"],
            "theatre_id": st["theatre_id"],
            "time": st["time"],
            "technology": st["technology"],
            "cancellable": "yes" if st["cancellable"] else "no"
        })
        r.delete(f"showtime:{st['id']}:booked")

initialize_data()

@app.route('/locations')
@lru_cache(maxsize=1)
def get_locations():
    """Get all available locations"""
    return jsonify(LOCATIONS)

@app.route('/theatres/<location>')
def get_theatres(location):
    """Get theatres for a specific location"""
    result = {tid: t["name"] for tid, t in THEATRES.items() if t["location"].lower() == location.lower()}
    return jsonify(result)

@app.route('/movies')
@lru_cache(maxsize=1)
def get_movies():
    """Get all available movies"""
    return jsonify(MOVIES)

def get_pricing(show_time):
    """Calculate pricing based on show timing"""
    try:
        # Extract hour from time string (e.g., "09:10 AM" -> 9)
        time_part = show_time.split()[0]  # "09:10"
        hour = int(time_part.split(':')[0])  # 9
        is_pm = 'PM' in show_time
        
        if is_pm and hour != 12:
            hour += 12
        elif not is_pm and hour == 12:
            hour = 0
            
        # Pricing logic
        if 6 <= hour < 12:  # Morning (6 AM - 12 PM)
            return 200  # Average price
        elif 12 <= hour < 18:  # Afternoon (12 PM - 6 PM) 
            return 300  # High price
        else:  # Night (6 PM - 6 AM)
            return 150  # Low price
            
    except:
        return 200  # Default price

@app.route('/showtimes/<theatre_id>')
def get_showtimes(theatre_id):
    """Get showtimes for a specific theatre and optionally movie"""
    mid = request.args.get('movie_id')
    
    # Pre-filter and optimize lookup
    filtered_shows = [st for st in SHOWTIMES if st["theatre_id"] == theatre_id and (not mid or st["movie_id"] == mid)]
    
    out = []
    for st in filtered_shows:
        m = MOVIES[st["movie_id"]]
        price = get_pricing(st["time"])
        out.append({
            "showtime_id": st["id"],
            "movie_id": st["movie_id"],
            "movie_name": m["name"],
            "genres": m["genres"],
            "rating": m["rating"],
            "time": st["time"],
            "technology": st["technology"],
            "cancellable": st["cancellable"],
            "price": price
        })
    return jsonify(out)

@app.route('/seatmap/<showtime_id>')
def seatmap_for_showtime(showtime_id):
    """Get seat map for a specific showtime and date"""
    try:
        booking_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Optimized seat map generation
        rows = "ABCDEFGHIJKLMN"
        blocks_ranges = [
            list(range(20, 24)),     # left block: 20-23
            list(range(12, 20)),     # center_left: 12-19  
            list(range(2, 12)),      # center_right: 2-11
            list(range(0, 2)) + list(range(24, 28))  # right: 0-1, 24-27
        ]
        
        # Date-specific booking key
        booked_key = f'showtime:{showtime_id}:booked:{booking_date}'
        
        # Single Redis call to get booked seats
        booked = set(r.smembers(booked_key))
        
        # Initialize if empty (reduced pre-booking for faster load)
        if not booked:
            all_seats = [f"{row}{n:02d}" for row in rows for block_range in blocks_ranges for n in block_range]
            prebook = random.sample(all_seats, int(0.15 * len(all_seats)))  # Reduced to 15%
            if prebook:
                r.sadd(booked_key, *prebook)
                booked = set(prebook)
        
        # Build optimized seat map
        seat_map = []
        for row in rows:
            blocks = []
            for block_range in blocks_ranges:
                block = [{"label": f"{row}{n:02d}", "booked": f"{row}{n:02d}" in booked} for n in block_range]
                blocks.append(block)
            seat_map.append({"row": row, "blocks": blocks})
        
        return jsonify(seat_map)
    
    except Exception as e:
        print(f"Error in seatmap_for_showtime: {e}")
        return jsonify([])

@app.route('/book', methods=['POST'])
def book_seat():
    """Book a specific seat for a showtime and date"""
    data = request.json
    showtime_id = data.get('showtime_id')
    seat = data.get('seat')
    booking_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if not showtime_id or not seat:
        return jsonify({'error': 'Missing showtime_id or seat'}), 400
    
    # Date-specific booking key
    seat_set_name = f"showtime:{showtime_id}:booked:{booking_date}"
    
    # Check if seat is already booked
    if r.sismember(seat_set_name, seat):
        return jsonify({'error': 'Seat already booked'}), 409
    
    # Book the seat
    r.sadd(seat_set_name, seat)
    return jsonify({'message': f'Seat {seat} successfully booked for showtime {showtime_id} on {booking_date}.'})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

if __name__ == '__main__':
    app.run(port=5000, threaded=True, debug=False)