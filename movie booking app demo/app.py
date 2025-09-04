import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime, timedelta
import tempfile
import qrcode
from io import BytesIO

API_URL = "http://localhost:5000"
st.set_page_config(layout="wide", page_title="Cinema Booking Modern App")

@st.cache_data(ttl=600)
def fetch_locations():
    try:
        response = requests.get(f"{API_URL}/locations", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Failed to fetch locations")
        return []

@st.cache_data(ttl=600)
def fetch_movies():
    try:
        response = requests.get(f"{API_URL}/movies", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Failed to fetch movies")
        return {}

@st.cache_data(ttl=300)
def fetch_theatres(location):
    try:
        response = requests.get(f"{API_URL}/theatres/{location}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Failed to fetch theatres")
        return {}

@st.cache_data(ttl=180)
def fetch_showtimes(theatre_id, movie_id=None):
    try:
        params = {'movie_id': movie_id} if movie_id else {}
        response = requests.get(f"{API_URL}/showtimes/{theatre_id}", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Failed to fetch showtimes")
        return []

@st.cache_data(ttl=60)
def fetch_seatmap(showtime_id, booking_date=None):
    try:
        params = {'date': booking_date} if booking_date else {}
        response = requests.get(f"{API_URL}/seatmap/{showtime_id}", params=params, timeout=3)
        if response.status_code != 200:
            status_code = str(response.status_code)[:10]
            st.error(f"API Error: {status_code}")
            return []
        return response.json()
    except requests.exceptions.JSONDecodeError:
        st.error("Invalid response from server")
        return []
    except Exception as e:
        error_msg = str(e).replace('\n', ' ').replace('\r', ' ')[:100]
        st.error(f"Network error: {error_msg}")
        return []

def generate_ticket_pdf(ticket_data):
    """Generate a PDF ticket with QR code and cinema icon"""
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        filename = f"CineBook_Ticket_{ticket_data['booking_id']}.pdf"
        pdf_path = os.path.join(downloads_path, filename)
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Generate QR Code
        qr_data = f"CineBook|{ticket_data['booking_id']}|{ticket_data['movie']}|{ticket_data['theatre']}|{ticket_data['date']}|{ticket_data['showtime']}|{','.join(ticket_data['seats'])}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to BytesIO
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Header with cinema icon
        c.setFont("Helvetica-Bold", 28)
        c.drawString(50, height-70, "🎬 CineBook")
        c.setFont("Helvetica", 16)
        c.drawString(50, height-95, "Premium Cinema Experience")
        
        # Draw QR Code
        c.drawImage(ImageReader(qr_buffer), width-150, height-150, 100, 100)
        c.setFont("Helvetica", 8)
        c.drawString(width-150, height-160, "Scan for verification")
        
        # Ticket details
        c.setFont("Helvetica-Bold", 12)
        y_pos = height - 180
        
        details = [
            f"🎫 Booking ID: {ticket_data['booking_id']}",
            f"🎬 Movie: {ticket_data['movie']}",
            f"🏭 Theatre: {ticket_data['theatre']}",
            f"📅 Date: {ticket_data['date']}",
            f"⏰ Show Time: {ticket_data['showtime']}",
            f"📺 Technology: {ticket_data['technology']}",
            f"🪑 Seats: {', '.join(ticket_data['seats'])}",
            f"💰 Price per Seat: ₹{ticket_data.get('price_per_seat', 200)}",
            f"💵 Total Amount: ₹{ticket_data.get('total_price', 200)}"
        ]
        
        for detail in details:
            c.drawString(50, y_pos, detail)
            y_pos -= 25
        
        # Footer
        c.setFont("Helvetica", 10)
        c.drawString(50, 80, "🍿 Thank you for booking with CineBook! Enjoy your movie!")
        c.drawString(50, 65, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        return pdf_path
        
    except Exception as e:
        st.error(f"Failed to generate ticket: {str(e)}")
        return None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', sans-serif;
    animation: backgroundShift 10s ease-in-out infinite;
}

@keyframes backgroundShift {
    0%, 100% { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    50% { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: calc(200px + 100%) 0; }
}

.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
    animation: fadeInUp 0.8s ease-out;
}

header[data-testid="stHeader"] { height: 0px !important; }
footer { visibility: hidden !important; }

.stSelectbox > div > div {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 15px !important;
    border: 2px solid rgba(255,255,255,0.3) !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease !important;
}

.stSelectbox > div > div:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.main-header {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(25px);
    border-radius: 25px;
    padding: 25px;
    margin-bottom: 20px;
    border: 2px solid rgba(255,255,255,0.3);
    animation: fadeInUp 0.6s ease-out;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -200px;
    width: 200px;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shimmer 3s infinite;
}

.movie-card {
    background: rgba(255,255,255,0.98);
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    backdrop-filter: blur(15px);
    border: 2px solid rgba(255,255,255,0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
}

.movie-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.movie-card:hover::before {
    transform: scaleX(1);
}

.movie-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    border-color: rgba(255,255,255,0.5);
}

.theatre-section {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    border: 2px solid rgba(255,255,255,0.3);
    animation: fadeInUp 0.8s ease-out;
    transition: all 0.3s ease;
}

.theatre-section:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 50px rgba(0,0,0,0.15);
}

.showtime-card {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 18px;
    padding: 18px;
    margin: 8px;
    color: white;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,0.2);
}

.showtime-card::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: all 0.5s ease;
}

.showtime-card:hover::before {
    width: 300px;
    height: 300px;
}

.showtime-card:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 15px 40px rgba(79,172,254,0.4);
    border-color: rgba(255,255,255,0.4);
}

.seat-section {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 25px;
    padding: 25px;
    margin: 20px 0;
    color: white;
    animation: fadeInUp 1s ease-out;
    position: relative;
    overflow: hidden;
}

.seat-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

.seat-box {
    display: inline-block;
    width: 38px;
    height: 38px;
    text-align: center;
    line-height: 38px;
    margin: 4px;
    border-radius: 10px;
    border: 2px solid #fff;
    background: rgba(255,255,255,0.95);
    font-weight: 700;
    font-size: 12px;
    color: #333;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    position: relative;
}

.seat-box:hover {
    transform: scale(1.1) rotate(5deg);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

.seat-box.booked {
    background: #ff4757 !important;
    color: white !important;
    border-color: #ff3742;
    cursor: not-allowed;
    animation: pulse 2s infinite;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 15px 30px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 6px 20px rgba(79,172,254,0.4) !important;
    position: relative !important;
    overflow: hidden !important;
}

div[data-testid="stButton"] > button::before {
    content: '' !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    width: 0 !important;
    height: 0 !important;
    background: rgba(255,255,255,0.2) !important;
    border-radius: 50% !important;
    transform: translate(-50%, -50%) !important;
    transition: all 0.5s ease !important;
}

div[data-testid="stButton"] > button:hover::before {
    width: 300px !important;
    height: 300px !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 12px 35px rgba(79,172,254,0.5) !important;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.25);
    padding: 12px 16px;
    border-radius: 25px;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.3s ease;
    border: 2px solid rgba(255,255,255,0.2);
}

.legend-item:hover {
    transform: translateY(-2px);
    background: rgba(255,255,255,0.35);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.price-badge {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 16px;
    display: inline-block;
    margin: 8px 0;
    animation: pulse 2s infinite;
    box-shadow: 0 4px 15px rgba(238,90,36,0.3);
}

.loading {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

.interactive-hover {
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.interactive-hover:hover {
    transform: translateY(-2px);
    filter: brightness(1.1);
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "clicked_movie" not in st.session_state: st.session_state["clicked_movie"] = None
if "inline_seatmap_id" not in st.session_state: st.session_state["inline_seatmap_id"] = None
if "inline_theatre_name" not in st.session_state: st.session_state["inline_theatre_name"] = ""
if "booking_success" not in st.session_state: st.session_state["booking_success"] = False
if "booking_message" not in st.session_state: st.session_state["booking_message"] = ""
if "seat_selected" not in st.session_state: st.session_state["seat_selected"] = set()
if "selected_date" not in st.session_state: st.session_state["selected_date"] = datetime.now().date()

# Location and Movie Selection
locations = fetch_locations()
movies_data = fetch_movies()
if not locations or not movies_data: st.stop()

# Date and Location Selection
col_city, col_date = st.columns(2)
with col_city:
    location = st.selectbox("📍 City", options=locations)
with col_date:
    # Generate next 5 days
    today = datetime.now().date()
    date_options = [(today + timedelta(days=i)) for i in range(5)]
    date_labels = []
    for i, date in enumerate(date_options):
        if i == 0:
            date_labels.append(f"Today ({date.strftime('%b %d')})")
        elif i == 1:
            date_labels.append(f"Tomorrow ({date.strftime('%b %d')})")
        else:
            date_labels.append(date.strftime('%a, %b %d'))
    
    selected_date_idx = st.selectbox("📅 Select Date", range(len(date_labels)), format_func=lambda x: date_labels[x])
    st.session_state["selected_date"] = date_options[selected_date_idx]

theatres = fetch_theatres(location)
if not theatres:
    st.error("No theatres found for this city.")
    st.stop()

# Header
st.markdown("""
<div class='main-header'>
    <h1 style='color:white; font-size:3rem; font-weight:800; margin:0; text-align:center; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
        <i class='fas fa-film'></i> CineBook
    </h1>
    <p style='color:rgba(255,255,255,0.9); text-align:center; margin:15px 0 0 0; font-size:1.2rem; font-weight:500;'>
        <i class='fas fa-ticket-alt'></i> Book your favorite movies with ease
    </p>
    <div style='text-align:center; margin-top:15px;'>
        <span style='background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:20px; font-size:14px; font-weight:600;'>
            <i class='fas fa-star'></i> Premium Cinema Experience
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Movie Grid
st.markdown("""
<div style='text-align:center; margin:30px 0 25px 0;'>
    <h2 style='color:white; font-weight:700; font-size:2.2rem; margin:0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
        <i class='fas fa-popcorn'></i> Now Showing
    </h2>
    <p style='color:rgba(255,255,255,0.8); margin:10px 0 0 0; font-size:1.1rem;'>
        Choose from our latest blockbusters
    </p>
</div>
""", unsafe_allow_html=True)
poster_cols = st.columns(len(movies_data))
for idx, (mid, m) in enumerate(movies_data.items()):
    with poster_cols[idx]:
        poster_url = m.get("poster_url")
        if poster_url and not poster_url.startswith("http"):
            poster_url = f"{API_URL}/{poster_url}"
        
        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
        
        if st.button("", key=f"poster_{mid}", help=m["name"]):
            st.session_state["clicked_movie"] = mid
            st.session_state["inline_seatmap_id"] = None
            st.session_state["inline_theatre_name"] = ""
            st.session_state["seat_selected"] = set()
            st.session_state["booking_success"] = False
            st.session_state["booking_message"] = ""
            st.rerun()
        
        st.image(poster_url, width=140)
        st.markdown(f"<h4 style='margin:10px 0 5px 0; color:#333; font-weight:600;'>{m['name']}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px; color:#666; margin:0;'>{m['genres']}</p>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:linear-gradient(135deg,#ff6b6b,#ee5a24); color:white; padding:4px 8px; border-radius:12px; font-size:11px; font-weight:600; display:inline-block; margin-top:8px;'>⭐ {m['rating']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Booking Success Message
if st.session_state["booking_success"]:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#667eea,#764ba2); border-radius:20px; 
                padding:30px; margin:20px 0; text-align:center; color:white;
                box-shadow:0 10px 30px rgba(0,0,0,0.2);'>
        <h2 style='margin:0 0 15px 0; font-size:2rem;'>🎉 Booking Successful!</h2>
        <p style='font-size:16px; margin:0; opacity:0.9;'>{st.session_state["booking_message"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🏠 Back to Movies", key="back_to_home_btn", use_container_width=True):
            st.session_state["booking_success"] = False
            st.session_state["booking_message"] = ""
            st.session_state["clicked_movie"] = None
            st.session_state["inline_seatmap_id"] = None
            st.session_state["seat_selected"] = set()
            st.rerun()
    with col_b:
        if st.button("✅ Continue Booking", type="primary", key="close_popup_btn", use_container_width=True):
            st.session_state["booking_success"] = False
            st.session_state["booking_message"] = ""
            st.session_state["inline_seatmap_id"] = None
            st.session_state["seat_selected"] = set()
            st.rerun()
    st.stop()

# Movie Selection and Showtimes
selected_movie = st.session_state.get("clicked_movie")
if selected_movie:
    movie_name = movies_data[selected_movie]["name"]
    col_header, col_home = st.columns([4,1])
    with col_header:
        st.header(f"Showtimes for {movie_name}")
    with col_home:
        # Show selected date
        selected_date_str = st.session_state["selected_date"].strftime('%A, %B %d, %Y')
        st.markdown(f"<p style='color:#666; margin:0;'>📅 {selected_date_str}</p>", unsafe_allow_html=True)
        
        if st.button("🏠 Back to Movies", key="home_btn"):
            st.session_state["clicked_movie"] = None
            st.session_state["inline_seatmap_id"] = None
            st.session_state["seat_selected"] = set()
            st.rerun()
    
    for tid, tname in theatres.items():
        showtimes = fetch_showtimes(tid, selected_movie)
        if not showtimes: continue
        
        st.markdown("<div class='theatre-section'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#333; font-weight:600; margin:0 0 20px 0;'>🎭 {tname}</h3>", unsafe_allow_html=True)
        
        pill_cols = st.columns(len(showtimes))
        for idx, show in enumerate(showtimes):
            with pill_cols[idx]:
                cancellable_icon = "✅" if show["cancellable"] else "❌"
                price = show.get('price', 200)
                st.markdown(f"""
                <div class='showtime-card'>
                    <div style='position:relative; z-index:2;'>
                        <div style='font-size:20px; font-weight:800; margin-bottom:8px;'>
                            <i class='fas fa-clock'></i> {show['time']}
                        </div>
                        <div class='price-badge' style='margin:8px 0;'>
                            <i class='fas fa-rupee-sign'></i>{price}
                        </div>
                        <div style='font-size:13px; font-weight:600; margin:8px 0; opacity:0.95;'>
                            <i class='fas fa-tv'></i> {show['technology']}
                        </div>
                        <div style='font-size:11px; opacity:0.9; margin-top:8px;'>
                            {cancellable_icon} {"Cancellable" if show["cancellable"] else "Non-cancellable"}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎫 Book Now", key=f"show_{show['showtime_id']}", use_container_width=True):
                    st.session_state["inline_seatmap_id"] = show["showtime_id"]
                    st.session_state["inline_theatre_name"] = tname
                    st.session_state["seat_selected"] = set()
                    st.session_state["booking_success"] = False
                    st.session_state["booking_message"] = ""
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Seat Selection
        if st.session_state["inline_seatmap_id"]:
            seatmap_to_show = st.session_state["inline_seatmap_id"]
            this_shows = [s for s in showtimes if s["showtime_id"] == seatmap_to_show]
            
            if this_shows:
                st.markdown(f"""
                <div class='seat-section'>
                    <h3 style='color:white; font-weight:600; margin:0 0 25px 0; text-align:center;'>
                        🎪 Select Your Seats - {st.session_state['inline_theatre_name']}
                    </h3>
                """, unsafe_allow_html=True)
                
                booking_date = st.session_state["selected_date"].strftime('%Y-%m-%d')
                seat_map = fetch_seatmap(seatmap_to_show, booking_date)
                if seat_map:
                    for rowObj in seat_map:
                        row_label = rowObj['row']
                        blocks = rowObj['blocks']
                        
                        total_seats = sum(len(block) for block in blocks)
                        row_cols = st.columns([1] + [1] * total_seats)
                        
                        with row_cols[0]:
                            st.markdown(f"<div style='font-weight:600;color:white;font-size:14px;text-align:center;padding-top:8px;'>{row_label}</div>", unsafe_allow_html=True)
                        
                        col_idx = 1
                        for block in blocks:
                            for seat in block:
                                if col_idx < len(row_cols):
                                    with row_cols[col_idx]:
                                        if not seat['label']:
                                            st.markdown("<div style='height:33px;'></div>", unsafe_allow_html=True)
                                        elif seat['booked']:
                                            st.markdown(f"<div class='seat-box booked'>{seat['label']}</div>", unsafe_allow_html=True)
                                        else:
                                            btn_key = f"{row_label}_{seat['label']}_{seatmap_to_show}_select"
                                            selected_now = seat['label'] in st.session_state["seat_selected"]
                                            
                                            if st.button(seat['label'], key=btn_key, 
                                                       help=f"Seat {seat['label']} - {'Selected' if selected_now else 'Available'}"):
                                                if not selected_now:
                                                    st.session_state["seat_selected"].add(seat['label'])
                                                else:
                                                    st.session_state["seat_selected"].remove(seat['label'])
                                                st.rerun()
                                    col_idx += 1

                    # Legend
                    st.markdown("<div style='margin:25px 0 20px 0;'></div>", unsafe_allow_html=True)
                    legend_cols = st.columns(3)
                    with legend_cols[0]:
                        st.markdown("""
                        <div class='legend-item'>
                            <div style='width:20px;height:20px;background:rgba(255,255,255,0.9);border:2px solid #fff;border-radius:4px;'></div>
                            <span>Available</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with legend_cols[1]:
                        st.markdown("""
                        <div class='legend-item'>
                            <div style='width:20px;height:20px;background:#ff4757;border:2px solid #ff3742;border-radius:4px;'></div>
                            <span>Booked</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with legend_cols[2]:
                        st.markdown("""
                        <div class='legend-item'>
                            <div style='width:20px;height:20px;background:linear-gradient(135deg,#ff6b6b,#ee5a24);border:2px solid #ee5a24;border-radius:4px;'></div>
                            <span>Selected</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Booking
                    if st.session_state["seat_selected"]:
                        st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
                        # Calculate pricing for selected seats
                        selected_seats = sorted(st.session_state['seat_selected'])
                        price_per_seat = this_shows[0].get('price', 200) if this_shows else 200
                        total_price = price_per_seat * len(selected_seats)
                        
                        st.markdown(f"""
                        <div style='background:rgba(255,255,255,0.25); border-radius:20px; padding:20px; margin:20px 0; border:2px solid rgba(255,255,255,0.3); backdrop-filter:blur(10px);'>
                            <h4 style='color:white; margin:0 0 15px 0; font-size:1.3rem; font-weight:700;'>
                                <i class='fas fa-chair'></i> Selected Seats
                            </h4>
                            <div style='background:rgba(255,255,255,0.2); padding:12px; border-radius:15px; margin:10px 0;'>
                                <p style='color:white; font-size:18px; font-weight:700; margin:0; text-align:center;'>
                                    {', '.join(selected_seats)}
                                </p>
                            </div>
                            <div style='border-top:2px solid rgba(255,255,255,0.3); margin:15px 0; padding-top:15px;'>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin:8px 0;'>
                                    <span style='color:rgba(255,255,255,0.9); font-weight:600;'>
                                        <i class='fas fa-tag'></i> Price per seat:
                                    </span>
                                    <span style='color:white; font-weight:700; font-size:16px;'>₹{price_per_seat}</span>
                                </div>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin:12px 0; padding:12px; background:rgba(255,255,255,0.2); border-radius:12px;'>
                                    <span style='color:white; font-weight:700; font-size:18px;'>
                                        <i class='fas fa-calculator'></i> Total Amount:
                                    </span>
                                    <span style='color:#FFD700; font-weight:800; font-size:22px; text-shadow:2px 2px 4px rgba(0,0,0,0.3);'>
                                        ₹{total_price}
                                    </span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 Confirm Booking", type="primary", key="confirm_booking_button", use_container_width=True):
                            with st.spinner('🎫 Processing booking...'):
                                seats = list(st.session_state["seat_selected"])
                            successes = []
                            fails = []
                            
                            for seat in seats:
                                try:
                                    resp = requests.post(f"{API_URL}/book", json={
                                        "showtime_id": seatmap_to_show,
                                        "seat": seat,
                                        "date": booking_date
                                    }, timeout=5)
                                    if resp.status_code == 200:
                                        result = resp.json()
                                        if "message" in result:
                                            successes.append(seat)
                                        else:
                                            fails.append((seat, result.get('error', 'Unknown error')))
                                    else:
                                        fails.append((seat, f"HTTP {resp.status_code}"))
                                except Exception as e:
                                    fails.append((seat, str(e)))
                            
                            if successes:
                                # Generate and download ticket
                                # Calculate total price
                                price_per_seat = this_shows[0].get('price', 200)
                                total_price = price_per_seat * len(successes)
                                
                                ticket_data = {
                                    'movie': movie_name,
                                    'theatre': st.session_state['inline_theatre_name'],
                                    'seats': successes,
                                    'showtime': this_shows[0]['time'],
                                    'technology': this_shows[0]['technology'],
                                    'date': st.session_state["selected_date"].strftime('%Y-%m-%d'),
                                    'booking_id': f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                    'price_per_seat': price_per_seat,
                                    'total_price': total_price
                                }
                                
                                pdf_path = generate_ticket_pdf(ticket_data)
                                
                                msg = f"Successfully booked seats: {', '.join(successes)}"
                                st.session_state["booking_success"] = True
                                st.session_state["booking_message"] = msg + f"\n\nTicket saved to: {pdf_path}"
                                st.session_state["seat_selected"] = set()
                                st.rerun()
                            
                            if fails:
                                for seat, error_msg in fails:
                                    st.error(f"Failed to book {seat}: {error_msg}")
                    else:
                        st.markdown("""
                        <div style='background:rgba(255,255,255,0.1); border-radius:15px; padding:15px; margin:20px 0; text-align:center;'>
                            <p style='color:rgba(255,255,255,0.8); margin:0; font-size:14px;'>
                                💡 Click seats to select them, then book multiple seats at once!
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)