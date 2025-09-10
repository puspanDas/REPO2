import unittest
import requests
import json
import os
from datetime import datetime

class TestCineBookAPI(unittest.TestCase):
    """Test cases for CineBook movie booking application"""
    
    BASE_URL = "http://localhost:5000"
    
    def setUp(self):
        """Setup test environment"""
        self.test_showtime_id = "1"
        self.test_seat = "A01"
        self.test_date = datetime.now().strftime('%Y-%m-%d')
    
    # API Endpoint Tests
    def test_get_locations(self):
        """Test fetching locations"""
        response = requests.get(f"{self.BASE_URL}/locations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("Kolkata", data)
    
    def test_get_movies(self):
        """Test fetching movies"""
        response = requests.get(f"{self.BASE_URL}/movies")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)
    
    def test_get_theatres(self):
        """Test fetching theatres by location"""
        response = requests.get(f"{self.BASE_URL}/theatres/Kolkata")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)
    
    def test_get_showtimes(self):
        """Test fetching showtimes"""
        response = requests.get(f"{self.BASE_URL}/showtimes/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("price", data[0])
            self.assertIn("showtime_id", data[0])
    
    def test_get_seatmap(self):
        """Test fetching seat map"""
        response = requests.get(f"{self.BASE_URL}/seatmap/{self.test_showtime_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    # Booking Tests
    def test_book_seat_success(self):
        """Test successful seat booking"""
        payload = {
            "showtime_id": self.test_showtime_id,
            "seat": f"Z{datetime.now().strftime('%H%M%S')}",  # Unique seat
            "date": self.test_date
        }
        response = requests.post(f"{self.BASE_URL}/book", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
    
    def test_book_duplicate_seat(self):
        """Test booking already booked seat"""
        seat = f"DUP{datetime.now().strftime('%S')}"
        payload = {
            "showtime_id": self.test_showtime_id,
            "seat": seat,
            "date": self.test_date
        }
        # Book first time
        requests.post(f"{self.BASE_URL}/book", json=payload)
        # Try booking again
        response = requests.post(f"{self.BASE_URL}/book", json=payload)
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertIn("error", data)
    
    def test_book_invalid_data(self):
        """Test booking with invalid data"""
        payload = {"showtime_id": ""}
        response = requests.post(f"{self.BASE_URL}/book", json=payload)
        self.assertEqual(response.status_code, 400)

class TestPricingLogic(unittest.TestCase):
    """Test pricing calculations"""
    
    def test_morning_pricing(self):
        """Test morning show pricing"""
        response = requests.get("http://localhost:5000/showtimes/1")
        data = response.json()
        morning_shows = [s for s in data if "AM" in s["time"] and int(s["time"].split(":")[0]) < 12]
        if morning_shows:
            self.assertEqual(morning_shows[0]["price"], 200)
    
    def test_afternoon_pricing(self):
        """Test afternoon show pricing"""
        response = requests.get("http://localhost:5000/showtimes/1")
        data = response.json()
        afternoon_shows = [s for s in data if "PM" in s["time"] and int(s["time"].split(":")[0]) <= 6]
        if afternoon_shows:
            self.assertEqual(afternoon_shows[0]["price"], 300)
    
    def test_night_pricing(self):
        """Test night show pricing"""
        response = requests.get("http://localhost:5000/showtimes/1")
        data = response.json()
        night_shows = [s for s in data if "PM" in s["time"] and int(s["time"].split(":")[0]) > 6]
        if night_shows:
            self.assertEqual(night_shows[0]["price"], 150)

class TestAdvanceBooking(unittest.TestCase):
    """Test advance booking functionality"""
    
    def test_date_specific_booking(self):
        """Test booking for specific dates"""
        from datetime import timedelta
        future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        payload = {
            "showtime_id": "1",
            "seat": f"ADV{datetime.now().strftime('%H%M%S')}",
            "date": future_date
        }
        response = requests.post("http://localhost:5000/book", json=payload)
        self.assertEqual(response.status_code, 200)

class TestUIComponents(unittest.TestCase):
    """Test UI functionality"""
    
    def test_pdf_generation(self):
        """Test PDF ticket generation"""
        try:
            from app import generate_ticket_pdf
            
            ticket_data = {
                'movie': 'Test Movie',
                'theatre': 'Test Theatre',
                'seats': ['A01', 'A02'],
                'showtime': '07:00 PM',
                'technology': 'ATMOS',
                'date': '2024-01-01',
                'booking_id': 'TEST123',
                'price_per_seat': 200,
                'total_price': 400
            }
            
            pdf_path = generate_ticket_pdf(ticket_data)
            self.assertIsNotNone(pdf_path)
            self.assertTrue(os.path.exists(pdf_path))
            
            # Cleanup
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except ImportError:
            self.skipTest("Streamlit app not available for PDF generation test")

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def test_invalid_theatre_id(self):
        """Test invalid theatre ID"""
        response = requests.get("http://localhost:5000/showtimes/999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)
    
    def test_invalid_location(self):
        """Test invalid location"""
        response = requests.get("http://localhost:5000/theatres/InvalidCity")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)
    
    def test_server_connectivity(self):
        """Test server connectivity"""
        try:
            response = requests.get("http://localhost:5000/locations", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.fail("Server not accessible")

if __name__ == '__main__':
    # Test Suite Configuration
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestCineBookAPI))
    test_suite.addTest(unittest.makeSuite(TestPricingLogic))
    test_suite.addTest(unittest.makeSuite(TestAdvanceBooking))
    test_suite.addTest(unittest.makeSuite(TestUIComponents))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print(f"SUCCESS RATE: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")