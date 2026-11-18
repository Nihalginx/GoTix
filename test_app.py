"""
test_app.py - End-to-End System Verification Test Script
Tests all REST API endpoints, Indian transport search, Rupee pricing,
database transactions, audit logging, and frontend file serving.
"""

import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import SessionLocal
from backend.models import User, LoginLog, Trip, Booking

client = TestClient(app)

def run_tests():
    print("========================================")
    print("STARTING TICKET BOOKING TEST SUITE")
    print("========================================")

    # 1. Test HTML routes for all 11 frontend pages
    print("\n--- 1. Testing Frontend Page Serving (11 Pages) ---")
    pages = [
        "/",
        "/search.html",
        "/login.html",
        "/booking.html",
        "/ticket.html",
        "/my-bookings.html",
        "/admin/dashboard.html",
        "/admin/users.html",
        "/admin/login-logs.html",
        "/admin/trips.html",
        "/admin/bookings.html",
    ]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200, f"Failed serving {page}: {res.status_code}"
        print(f" [PASS] Served: {page} (200 OK)")

    # 2. Test Customer Registration
    print("\n--- 2. Testing Customer Registration ---")
    test_email = "testrunner_in@example.com"
    reg_payload = {
        "name": "Karan Malhotra",
        "email": test_email,
        "password": "password123"
    }
    db = SessionLocal()
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    res = client.post("/api/register", json=reg_payload)
    assert res.status_code == 201, f"Registration failed: {res.text}"
    user_data = res.json()
    assert "token" in user_data
    assert "password_hash" not in user_data["user"]
    print(" [PASS] User registered successfully with token (password_hash safely omitted).")

    # 3. Test Failed Login & Audit Trail
    print("\n--- 3. Testing Failed Login & Audit Trail ---")
    fail_res = client.post("/api/login", json={"email": test_email, "password": "wrongpassword"})
    assert fail_res.status_code == 401
    print(" [PASS] Failed login returned 401 Unauthorized.")

    db = SessionLocal()
    latest_fail_log = db.query(LoginLog).filter(
        LoginLog.email_tried == test_email,
        LoginLog.status == "failed"
    ).order_by(LoginLog.id.desc()).first()
    assert latest_fail_log is not None
    print(f" [PASS] Failed login logged to database (Log ID #{latest_fail_log.id}, status={latest_fail_log.status}).")
    db.close()

    # 4. Test Successful Login
    print("\n--- 4. Testing Successful Login ---")
    success_res = client.post("/api/login", json={"email": test_email, "password": "password123"})
    assert success_res.status_code == 200
    token = success_res.json()["token"]
    user_headers = {"Authorization": f"Bearer {token}"}
    print(" [PASS] Successful login returned session token.")

    # 5. Test India to London Flight Search
    print("\n--- 5. Testing Flights from India to London ---")
    trips_res = client.get("/api/trips?type=flight&origin=Delhi&destination=London")
    assert trips_res.status_code == 200
    london_flights = trips_res.json()["trips"]
    assert len(london_flights) > 0, "No flights found from Delhi to London!"
    print(f" [PASS] Found {len(london_flights)} direct/connecting flights from Delhi to London:")
    for f in london_flights[:3]:
        print(f"        * {f['operator']} | Fare: ₹{f['price']:,.2f} | Seats: {f['seats_available']}")

    # 6. Test Atomic Booking & Seat Decrement
    print("\n--- 6. Testing Atomic Booking & Seat Decrement ---")
    target_trip = london_flights[0]
    trip_id = target_trip["id"]
    initial_seats = target_trip["seats_available"]

    booking_payload = {
        "trip_id": trip_id,
        "passenger_names": "Karan Malhotra, Simran Malhotra",
        "seats_booked": 2
    }
    book_res = client.post("/api/bookings", json=booking_payload, headers=user_headers)
    assert book_res.status_code == 201, f"Booking creation failed: {book_res.text}"
    booking_id = book_res.json()["booking"]["id"]
    print(f" [PASS] Created Booking #{booking_id} for 2 seats (Total: ₹{book_res.json()['booking']['total_price']:,.2f}).")

    trip_check = client.get(f"/api/trips/{trip_id}").json()["trip"]
    assert trip_check["seats_available"] == initial_seats - 2
    print(f" [PASS] trips.seats_available atomically decremented: {initial_seats} -> {trip_check['seats_available']}")

    # 7. Test My Bookings & Ticket Details
    print("\n--- 7. Testing My Bookings & Ticket Confirmation ---")
    my_res = client.get("/api/my-bookings", headers=user_headers)
    assert my_res.status_code == 200
    my_bookings = my_res.json()["bookings"]
    assert any(b["id"] == booking_id for b in my_bookings)
    print(f" [PASS] GET /api/my-bookings listed Booking #{booking_id}.")

    # 8. Test Booking Cancellation & Seat Restoration
    print("\n--- 8. Testing Booking Cancellation & Seat Restoration ---")
    cancel_res = client.post(f"/api/bookings/{booking_id}/cancel", headers=user_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["booking"]["status"] == "cancelled"

    trip_after_cancel = client.get(f"/api/trips/{trip_id}").json()["trip"]
    assert trip_after_cancel["seats_available"] == initial_seats
    print(f" [PASS] trips.seats_available atomically restored: {trip_check['seats_available']} -> {trip_after_cancel['seats_available']}")

    # 9. Test Admin Authentication & Role Protection
    print("\n--- 9. Testing Admin Authentication & Role Protection ---")
    forbidden_res = client.get("/api/admin/stats", headers=user_headers)
    assert forbidden_res.status_code == 403
    print(" [PASS] Regular user blocked from admin endpoint (403 Forbidden).")

    admin_login = client.post("/api/login", json={"email": "admin@transport.com", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(" [PASS] Admin logged in successfully with admin token.")

    # 10. Test Admin Monitor Endpoints with Rupee Revenue
    print("\n--- 10. Testing Admin Monitor Endpoints ---")
    stats_res = client.get("/api/admin/stats", headers=admin_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_users" in stats
    assert "total_bookings" in stats
    assert "bookings_per_transport_type" in stats
    print(f" [PASS] GET /api/admin/stats returned total_users={stats['total_users']}, bookings={stats['total_bookings']}, revenue=₹{stats['revenue']:,.2f}.")

    users_res = client.get("/api/admin/users?page=1&limit=5", headers=admin_headers)
    assert users_res.status_code == 200
    print(f" [PASS] GET /api/admin/users returned {len(users_res.json()['users'])} users safely.")

    sync_res = client.post("/api/admin/sync-trips", headers=admin_headers)
    assert sync_res.status_code == 200
    sync_data = sync_res.json()
    assert "synced_conditions" in sync_data
    print(f" [PASS] POST /api/admin/sync-trips synced via {sync_data['source']}.")

    print("\n========================================")
    print("ALL TESTS PASSED! 100% OK")
    print("========================================")

if __name__ == "__main__":
    run_tests()
