"""
backend/seed.py - Seed Script with Authentic India-Centric Transport Data
Populates SQLite database with:
- Seeded admin (admin@transport.com / admin123)
- Seeded Indian users (rahul@example.com, priya@example.com, amit@example.com, etc.)
- 15+ login audit logs (both success and failed)
- 60+ authentic Indian domestic & international trips (Flights, Trains, Buses, Cabs, Bikes)
- Direct India -> London flights (Air India, British Airways, Emirates, Virgin Atlantic, IndiGo)
- Indian Railway Vande Bharat, Rajdhani, Shatabdi expresses
- State & private Volvo buses (KSRTC, MSRTC Shivneri, Zingbus, IntrCity, NueGo)
- Urban cabs (Uber Premier, Ola Prime, BluSmart EV) and micromobility bikes (Yulu, Rapido, Bounce)
- All fares strictly in Indian Rupees (INR / ₹)
"""

import sys
import os
from datetime import datetime, timedelta, timezone
import bcrypt

# Ensure root directory is on the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.models import User, LoginLog, Trip, Booking


def hash_pw(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_database():
    print("Dropping existing tables and recreating schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        print("1. Seeding User Accounts...")
        admin_user = User(
            name="System Administrator",
            email="admin@transport.com",
            password_hash=hash_pw("admin123"),
            role="admin",
            created_at=now - timedelta(days=30)
        )
        rahul = User(
            name="Rahul Sharma",
            email="rahul@example.com",
            password_hash=hash_pw("user123"),
            role="user",
            created_at=now - timedelta(days=20)
        )
        priya = User(
            name="Priya Patel",
            email="priya@example.com",
            password_hash=hash_pw("user123"),
            role="user",
            created_at=now - timedelta(days=15)
        )
        amit = User(
            name="Amit Verma",
            email="amit@example.com",
            password_hash=hash_pw("user123"),
            role="user",
            created_at=now - timedelta(days=10)
        )
        sneha = User(
            name="Sneha Reddy",
            email="sneha@example.com",
            password_hash=hash_pw("user123"),
            role="user",
            created_at=now - timedelta(days=5)
        )

        db.add_all([admin_user, rahul, priya, amit, sneha])
        db.commit()

        print("2. Seeding Security Audit Logs (login_logs)...")
        sample_logs = [
            LoginLog(user_id=admin_user.id, email_tried="admin@transport.com", login_time=now - timedelta(hours=48), ip_address="103.21.124.50", status="success"),
            LoginLog(user_id=None, email_tried="admin@transport.com", login_time=now - timedelta(hours=36), ip_address="49.37.155.10", status="failed"),
            LoginLog(user_id=rahul.id, email_tried="rahul@example.com", login_time=now - timedelta(hours=30), ip_address="106.195.34.82", status="success"),
            LoginLog(user_id=None, email_tried="unknown_user@evil.org", login_time=now - timedelta(hours=26), ip_address="185.220.101.5", status="failed"),
            LoginLog(user_id=None, email_tried="priya@example.com", login_time=now - timedelta(hours=22), ip_address="157.48.201.14", status="failed"),
            LoginLog(user_id=priya.id, email_tried="priya@example.com", login_time=now - timedelta(hours=21, minutes=58), ip_address="157.48.201.14", status="success"),
            LoginLog(user_id=amit.id, email_tried="amit@example.com", login_time=now - timedelta(hours=18), ip_address="122.161.45.90", status="success"),
            LoginLog(user_id=None, email_tried="root@admin.com", login_time=now - timedelta(hours=14), ip_address="203.0.113.88", status="failed"),
            LoginLog(user_id=sneha.id, email_tried="sneha@example.com", login_time=now - timedelta(hours=10), ip_address="117.211.89.33", status="success"),
            LoginLog(user_id=None, email_tried="sneha@example.com", login_time=now - timedelta(hours=9), ip_address="117.211.89.99", status="failed"),
            LoginLog(user_id=admin_user.id, email_tried="admin@transport.com", login_time=now - timedelta(hours=4), ip_address="103.21.124.50", status="success"),
            LoginLog(user_id=rahul.id, email_tried="rahul@example.com", login_time=now - timedelta(hours=2), ip_address="106.195.34.82", status="success"),
            LoginLog(user_id=None, email_tried="finance@transport.in", login_time=now - timedelta(minutes=45), ip_address="49.37.155.10", status="failed"),
            LoginLog(user_id=priya.id, email_tried="priya@example.com", login_time=now - timedelta(minutes=20), ip_address="157.48.201.14", status="success"),
            LoginLog(user_id=admin_user.id, email_tried="admin@transport.com", login_time=now - timedelta(minutes=5), ip_address="127.0.0.1", status="success"),
        ]
        db.add_all(sample_logs)
        db.commit()

        print("3. Seeding 60+ Authentic India-Centric Trips...")
        today = now.replace(minute=0, second=0, microsecond=0)

        trips_data = [
            # =========================================================================
            # FLIGHTS: International from India (Delhi, Mumbai to London, Dubai, etc.)
            # =========================================================================
            ("flight", "Air India AI 161 (Boeing 777)", "Delhi", "London", today + timedelta(hours=5, minutes=15), today + timedelta(hours=14, minutes=45), 58400.0, 240, 192),
            ("flight", "British Airways BA 142 (Boeing 787-9)", "Delhi", "London", today + timedelta(hours=9, minutes=30), today + timedelta(hours=18, minutes=45), 64900.0, 214, 168),
            ("flight", "Virgin Atlantic VS 301 (Airbus A350)", "Delhi", "London", today + timedelta(hours=13, minutes=40), today + timedelta(hours=22, minutes=50), 61200.0, 235, 180),
            ("flight", "Emirates EK 511 via Dubai (Airbus A380)", "Delhi", "London", today + timedelta(hours=10, minutes=45), today + timedelta(hours=21, minutes=30), 52300.0, 280, 215),
            ("flight", "IndiGo 6E 101 via Istanbul (Codeshare)", "Delhi", "London", today + timedelta(hours=6, minutes=0), today + timedelta(hours=16, minutes=30), 44800.0, 186, 140),
            ("flight", "Air India AI 129 (Boeing 777-300ER)", "Mumbai", "London", today + timedelta(hours=6, minutes=45), today + timedelta(hours=16, minutes=20), 59800.0, 240, 185),
            ("flight", "British Airways BA 138 (Boeing 777)", "Mumbai", "London", today + timedelta(hours=14, minutes=20), today + timedelta(hours=23, minutes=50), 66500.0, 220, 172),
            ("flight", "Qatar Airways QR 557 via Doha", "Mumbai", "London", today + timedelta(days=1, hours=4, minutes=30), today + timedelta(days=1, hours=15, minutes=15), 54100.0, 250, 198),
            ("flight", "Emirates EK 513 (Boeing 777)", "Delhi", "Dubai", today + timedelta(hours=4, minutes=15), today + timedelta(hours=7, minutes=50), 24500.0, 260, 210),
            ("flight", "IndiGo 6E 1461 (Airbus A321neo)", "Delhi", "Dubai", today + timedelta(hours=17, minutes=30), today + timedelta(hours=21, minutes=10), 18900.0, 222, 175),
            ("flight", "Singapore Airlines SQ 423 (Airbus A380)", "Mumbai", "Singapore", today + timedelta(days=1, hours=11, minutes=40), today + timedelta(days=1, hours=19, minutes=40), 34200.0, 280, 230),

            # FLIGHTS: Domestic Indian Metro Connections
            ("flight", "IndiGo 6E 2045", "Delhi", "Mumbai", today + timedelta(hours=2), today + timedelta(hours=4, minutes=15), 4850.0, 180, 142),
            ("flight", "Air India AI 865", "Delhi", "Mumbai", today + timedelta(hours=8), today + timedelta(hours=10, minutes=15), 5400.0, 180, 110),
            ("flight", "Vistara UK 995", "Delhi", "Mumbai", today + timedelta(hours=14, minutes=30), today + timedelta(hours=16, minutes=45), 6100.0, 164, 95),
            ("flight", "Akasa Air QP 1109", "Delhi", "Mumbai", today + timedelta(hours=18), today + timedelta(hours=20, minutes=15), 4450.0, 189, 138),
            ("flight", "IndiGo 6E 5326", "Mumbai", "Goa", today + timedelta(hours=3, minutes=30), today + timedelta(hours=4, minutes=45), 3600.0, 180, 72),
            ("flight", "Akasa Air QP 1332", "Mumbai", "Goa", today + timedelta(hours=15, minutes=40), today + timedelta(hours=16, minutes=55), 3150.0, 189, 115),
            ("flight", "IndiGo 6E 2132", "Bengaluru", "Delhi", today + timedelta(hours=7, minutes=15), today + timedelta(hours=10, minutes=5), 5950.0, 180, 88),
            ("flight", "Air India Express IX 974", "Bengaluru", "Mumbai", today + timedelta(hours=13, minutes=10), today + timedelta(hours=14, minutes=55), 4100.0, 180, 126),
            ("flight", "Vistara UK 817", "Delhi", "Bengaluru", today + timedelta(hours=16), today + timedelta(hours=18, minutes=50), 6400.0, 164, 104),
            ("flight", "IndiGo 6E 6114", "Hyderabad", "Goa", today + timedelta(days=1, hours=9, minutes=45), today + timedelta(days=1, hours=11, minutes=10), 3800.0, 180, 135),
            ("flight", "Air India AI 440", "Chennai", "Delhi", today + timedelta(days=1, hours=6, minutes=30), today + timedelta(days=1, hours=9, minutes=20), 5750.0, 180, 145),

            # =========================================================================
            # TRAINS: Indian Railways (IRCTC Vande Bharat, Rajdhani, Shatabdi Expresses)
            # =========================================================================
            ("train", "Vande Bharat Express (Train #22436)", "Delhi", "Varanasi", today + timedelta(hours=3), today + timedelta(hours=11), 1750.0, 300, 240),
            ("train", "Vande Bharat Express (Train #22439)", "Delhi", "Katra", today + timedelta(hours=6), today + timedelta(hours=14), 1630.0, 300, 210),
            ("train", "Mumbai Rajdhani Express (Train #12952)", "Delhi", "Mumbai", today + timedelta(hours=16, minutes=55), today + timedelta(hours=32, minutes=35), 2950.0, 280, 195),
            ("train", "Vande Bharat Express (Train #20901)", "Mumbai", "Ahmedabad", today + timedelta(hours=6, minutes=10), today + timedelta(hours=11, minutes=35), 1420.0, 300, 225),
            ("train", "Vande Bharat Express (Train #20608)", "Bengaluru", "Chennai", today + timedelta(hours=5, minutes=45), today + timedelta(hours=10, minutes=10), 1020.0, 300, 250),
            ("train", "Gatimaan Express (Train #12050)", "Delhi", "Agra", today + timedelta(hours=8, minutes=10), today + timedelta(hours=9, minutes=50), 860.0, 260, 180),
            ("train", "Swarna Shatabdi (Train #12029)", "Delhi", "Amritsar", today + timedelta(hours=7, minutes=20), today + timedelta(hours=13, minutes=30), 1180.0, 280, 190),
            ("train", "Tejas Express (Train #22119)", "Mumbai", "Goa", today + timedelta(hours=5, minutes=50), today + timedelta(hours=14), 1580.0, 260, 145),
            ("train", "Vande Bharat Express (Train #20704)", "Bengaluru", "Hyderabad", today + timedelta(hours=14, minutes=45), today + timedelta(hours=23), 1540.0, 300, 175),
            ("train", "Howrah Rajdhani Express (Train #12301)", "Kolkata", "Delhi", today + timedelta(hours=16, minutes=50), today + timedelta(hours=34, minutes=5), 3100.0, 280, 160),

            # =========================================================================
            # BUSES: Indian Intercity Volvo & Electric Luxury Coaches
            # =========================================================================
            ("bus", "KSRTC Airavat Club Class Multi-Axle", "Bengaluru", "Hyderabad", today + timedelta(hours=9), today + timedelta(hours=18), 1250.0, 48, 32),
            ("bus", "MSRTC Shivneri AC Volvo", "Mumbai", "Pune", today + timedelta(hours=2), today + timedelta(hours=5, minutes=30), 520.0, 45, 28),
            ("bus", "Zingbus Electric AC Sleeper", "Delhi", "Jaipur", today + timedelta(hours=6, minutes=30), today + timedelta(hours=12, minutes=15), 680.0, 36, 19),
            ("bus", "IntrCity SmartBus Volvo Sleeper", "Delhi", "Manali", today + timedelta(hours=18, minutes=30), today + timedelta(hours=32), 1450.0, 38, 22),
            ("bus", "KSRTC Flybus Multi-Axle", "Chennai", "Bengaluru", today + timedelta(hours=14), today + timedelta(hours=20, minutes=30), 790.0, 48, 35),
            ("bus", "VRL Travels Multi-Axle I-Shift", "Bengaluru", "Goa", today + timedelta(hours=20), today + timedelta(hours=31, minutes=30), 1350.0, 40, 24),
            ("bus", "TSRTC Garuda Plus AC", "Hyderabad", "Vijayawada", today + timedelta(hours=6), today + timedelta(hours=11, minutes=30), 620.0, 46, 30),
            ("bus", "SRS Travels Scania AC", "Ahmedabad", "Mumbai", today + timedelta(hours=22), today + timedelta(hours=31), 980.0, 44, 27),
            ("bus", "NueGo Electric AC Luxury Bus", "Pune", "Goa", today + timedelta(hours=21), today + timedelta(hours=30, minutes=45), 1100.0, 42, 29),
            ("bus", "NueGo Intercity Electric Coach", "Delhi", "Chandigarh", today + timedelta(hours=8), today + timedelta(hours=12, minutes=45), 550.0, 45, 34),

            # =========================================================================
            # CABS: Urban, Airport & Outstation Cabs (Ola, Uber, BluSmart EV)
            # =========================================================================
            ("cab", "Uber Premier Sedan", "Mumbai Airport", "South Mumbai (Colaba)", today + timedelta(hours=1), today + timedelta(hours=2, minutes=15), 950.0, 4, 4),
            ("cab", "BluSmart EV Sedan", "Bengaluru Airport", "Whitefield", today + timedelta(hours=1, minutes=30), today + timedelta(hours=2, minutes=45), 1450.0, 4, 4),
            ("cab", "Meru Premium Cab", "Delhi IGI Airport", "Connaught Place", today + timedelta(hours=2), today + timedelta(hours=3), 780.0, 4, 4),
            ("cab", "BluSmart All-Electric Cab", "Delhi IGI Airport", "Gurgaon Cyber City", today + timedelta(hours=1), today + timedelta(hours=1, minutes=40), 650.0, 4, 4),
            ("cab", "MakeMyTrip Prime Outstation", "Pune", "Mumbai", today + timedelta(hours=3), today + timedelta(hours=6, minutes=30), 2800.0, 4, 4),
            ("cab", "Ola Prime Sedan", "Chennai Airport", "OMR IT Corridor", today + timedelta(hours=2, minutes=30), today + timedelta(hours=3, minutes=30), 620.0, 4, 4),
            ("cab", "Uber Premier XL", "Hyderabad Airport", "Hitec City", today + timedelta(hours=2), today + timedelta(hours=3), 980.0, 6, 6),
            ("cab", "Goa Miles Airport Taxi", "Goa Mopa Airport", "Baga Beach", today + timedelta(hours=1), today + timedelta(hours=2, minutes=15), 1600.0, 4, 4),
            ("cab", "City Yellow-Blue AC Cab", "Kolkata Airport", "Salt Lake Sector V", today + timedelta(hours=3), today + timedelta(hours=3, minutes=45), 450.0, 4, 4),
            ("cab", "Ola Prime SUV", "Ahmedabad Airport", "Gandhinagar GIFT City", today + timedelta(hours=4), today + timedelta(hours=4, minutes=50), 750.0, 6, 6),

            # =========================================================================
            # BIKES: Smart EV, Bike Taxis & Tourist Rentals (Yulu, Rapido, Royal Enfield)
            # =========================================================================
            ("bike", "Yulu Miracle EV Smart Bike", "Indiranagar", "Koramangala (Bengaluru)", today + timedelta(minutes=30), today + timedelta(hours=1, minutes=15), 45.0, 15, 12),
            ("bike", "Rapido Electric Bike Taxi", "Cyber City", "DLF Phase 5 (Gurgaon)", today + timedelta(hours=1), today + timedelta(hours=1, minutes=35), 55.0, 20, 16),
            ("bike", "Yulu Move EV", "Connaught Place", "India Gate (Delhi)", today + timedelta(hours=2), today + timedelta(hours=2, minutes=45), 35.0, 25, 21),
            ("bike", "Bounce City Cruiser e-Bike", "Marine Drive", "Colaba Causeway (Mumbai)", today + timedelta(hours=2, minutes=30), today + timedelta(hours=3, minutes=20), 60.0, 18, 14),
            ("bike", "Royal Enfield Hunter 350 Rental", "Calangute Beach", "Anjuna Beach (Goa)", today + timedelta(hours=3), today + timedelta(hours=12), 750.0, 10, 8),
            ("bike", "Honda Activa 6G Beach Scooter", "Baga Beach", "Fort Aguada (Goa)", today + timedelta(hours=2), today + timedelta(hours=10), 450.0, 15, 11),
            ("bike", "Rapido Speed Bike Taxi", "Hitec City", "Madhapur Metro (Hyderabad)", today + timedelta(hours=1, minutes=15), today + timedelta(hours=1, minutes=40), 40.0, 22, 18),
            ("bike", "Yulu Wynn Urban Commuter", "T. Nagar", "Marina Beach (Chennai)", today + timedelta(hours=3), today + timedelta(hours=3, minutes=45), 50.0, 20, 15),
            ("bike", "MetroSmart Green Bike", "Sector 17", "Sukhna Lake (Chandigarh)", today + timedelta(hours=4), today + timedelta(hours=4, minutes=45), 30.0, 30, 26),
            ("bike", "Royal Enfield Himalayan 450", "Old Manali", "Solang Valley (Himachal)", today + timedelta(hours=4), today + timedelta(hours=12), 1200.0, 8, 6),
        ]

        trip_objects = []
        for t in trips_data:
            trip_obj = Trip(
                transport_type=t[0],
                operator=t[1],
                origin=t[2],
                destination=t[3],
                departure_time=t[4],
                arrival_time=t[5],
                price=t[6],
                seats_total=t[7],
                seats_available=t[8]
            )
            trip_objects.append(trip_obj)

        db.add_all(trip_objects)
        db.commit()

        print("4. Seeding Sample Indian Bookings...")
        sample_bookings = [
            Booking(
                user_id=rahul.id,
                trip_id=trip_objects[0].id,  # Air India to London
                passenger_names="Rahul Sharma, Ananya Sharma",
                seats_booked=2,
                total_price=trip_objects[0].price * 2,
                status="confirmed",
                booked_at=now - timedelta(days=2)
            ),
            Booking(
                user_id=priya.id,
                trip_id=trip_objects[21].id,  # Vande Bharat to Varanasi
                passenger_names="Priya Patel",
                seats_booked=1,
                total_price=trip_objects[21].price * 1,
                status="confirmed",
                booked_at=now - timedelta(days=1, hours=5)
            ),
            Booking(
                user_id=amit.id,
                trip_id=trip_objects[31].id,  # KSRTC Volvo to Hyderabad
                passenger_names="Amit Verma, Pooja Verma",
                seats_booked=2,
                total_price=trip_objects[31].price * 2,
                status="confirmed",
                booked_at=now - timedelta(hours=16)
            ),
            Booking(
                user_id=sneha.id,
                trip_id=trip_objects[41].id,  # Uber Premier Mumbai
                passenger_names="Sneha Reddy",
                seats_booked=1,
                total_price=trip_objects[41].price * 1,
                status="confirmed",
                booked_at=now - timedelta(hours=8)
            ),
            Booking(
                user_id=rahul.id,
                trip_id=trip_objects[51].id,  # Yulu EV Bengaluru
                passenger_names="Rahul Sharma",
                seats_booked=1,
                total_price=trip_objects[51].price * 1,
                status="confirmed",
                booked_at=now - timedelta(hours=3)
            ),
            Booking(
                user_id=priya.id,
                trip_id=trip_objects[11].id,  # IndiGo Delhi to Mumbai
                passenger_names="Priya Patel",
                seats_booked=1,
                total_price=trip_objects[11].price * 1,
                status="cancelled",
                booked_at=now - timedelta(days=3)
            ),
            Booking(
                user_id=amit.id,
                trip_id=trip_objects[23].id,  # Vande Bharat Mumbai to Ahmedabad
                passenger_names="Amit Verma",
                seats_booked=1,
                total_price=trip_objects[23].price * 1,
                status="confirmed",
                booked_at=now - timedelta(hours=1)
            ),
        ]
        db.add_all(sample_bookings)
        db.commit()

        print("\nDatabase successfully seeded with authentic Indian data!")
        print(f"Users created: {db.query(User).count()}")
        print(f"Login logs created: {db.query(LoginLog).count()}")
        print(f"Trips created: {db.query(Trip).count()} across 5 transport modes")
        print(f"Bookings created: {db.query(Booking).count()}")
        print("\n--- CREDENTIALS ---")
        print("Admin account:  admin@transport.com / admin123  (Role: admin)")
        print("User account:   rahul@example.com   / user123   (Role: user)")
        print("User account:   priya@example.com   / user123   (Role: user)")
        print("-------------------\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
