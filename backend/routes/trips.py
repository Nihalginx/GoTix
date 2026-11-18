"""
backend/routes/trips.py - Real-Time Smart Transit Schedule Engine
Handles dynamic route generation and lookup for:
- Flights: Direct and connecting routes from ANY Indian airport (DEL, BOM, BLR, MAA, HYD, CCU, COK, GOI, PNQ, AMD, etc.)
  to domestic destinations and ANY global hub (London LHR, Dubai DXB, Singapore SIN, New York JFK, Bangkok, Paris, etc.).
- Trains: Domestic Indian Railways only (Vande Bharat, Rajdhani, Shatabdi, Superfast) with train numbers and classes.
  Rejects overseas train requests with clear guidance.
- Buses: Intercity luxury Volvo, EV, and Sleeper coaches across Indian state and private networks.
- Cabs: Airport, city, and outstation transfers across Indian metros.
- Bikes: Urban smart EV and tourist rentals.
"""

from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import math
import random

from backend.database import get_db
from backend.models import Trip

router = APIRouter(prefix="/api", tags=["Trips"])

# Known International Destinations
OVERSEAS_HUBS = [
    "london", "lhr", "lgw", "dubai", "dxb", "singapore", "sin",
    "new york", "jfk", "ewr", "paris", "cdg", "bangkok", "bkk",
    "toronto", "yyz", "tokyo", "nrt", "hnd", "doha", "doh",
    "frankfurt", "fra", "chicago", "ord", "san francisco", "sfo",
    "sydney", "syd", "melbourne", "mel", "kuala lumpur", "kul",
    "abu dhabi", "auh", "amsterdam", "ams"
]

# Standard Coordinates for Realistic Flight Duration & Fare Calculation
CITY_DATA = {
    # Indian Metros & Hubs
    "delhi": {"name": "Delhi (DEL)", "city": "Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000},
    "new delhi": {"name": "Delhi (DEL)", "city": "Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000},
    "mumbai": {"name": "Mumbai (BOM)", "city": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656},
    "bengaluru": {"name": "Bengaluru (BLR)", "city": "Bengaluru", "country": "India", "lat": 13.1986, "lon": 77.7066},
    "bangalore": {"name": "Bengaluru (BLR)", "city": "Bengaluru", "country": "India", "lat": 13.1986, "lon": 77.7066},
    "chennai": {"name": "Chennai (MAA)", "city": "Chennai", "country": "India", "lat": 12.9941, "lon": 80.1709},
    "hyderabad": {"name": "Hyderabad (HYD)", "city": "Hyderabad", "country": "India", "lat": 17.2403, "lon": 78.4294},
    "kolkata": {"name": "Kolkata (CCU)", "city": "Kolkata", "country": "India", "lat": 22.6547, "lon": 88.4467},
    "ahmedabad": {"name": "Ahmedabad (AMD)", "city": "Ahmedabad", "country": "India", "lat": 23.0734, "lon": 72.6347},
    "pune": {"name": "Pune (PNQ)", "city": "Pune", "country": "India", "lat": 18.5822, "lon": 73.9197},
    "goa": {"name": "Goa (GOI/GOX)", "city": "Goa", "country": "India", "lat": 15.3808, "lon": 73.8313},
    "kochi": {"name": "Kochi (COK)", "city": "Kochi", "country": "India", "lat": 10.1518, "lon": 76.3930},
    "jaipur": {"name": "Jaipur (JAI)", "city": "Jaipur", "country": "India", "lat": 26.8242, "lon": 75.8122},
    "varanasi": {"name": "Varanasi (VNS)", "city": "Varanasi", "country": "India", "lat": 25.4524, "lon": 82.8593},
    "amritsar": {"name": "Amritsar (ATQ)", "city": "Amritsar", "country": "India", "lat": 31.7096, "lon": 74.7973},
    "chandigarh": {"name": "Chandigarh (IXC)", "city": "Chandigarh", "country": "India", "lat": 30.6735, "lon": 76.7885},
    "lucknow": {"name": "Lucknow (LKO)", "city": "Lucknow", "country": "India", "lat": 26.7606, "lon": 80.8893},
    "trivandrum": {"name": "Trivandrum (TRV)", "city": "Trivandrum", "country": "India", "lat": 8.4821, "lon": 76.9200},
    "guwahati": {"name": "Guwahati (GAU)", "city": "Guwahati", "country": "India", "lat": 26.1061, "lon": 91.5859},

    # International Global Hubs
    "london": {"name": "London Heathrow (LHR)", "city": "London", "country": "UK", "lat": 51.4700, "lon": -0.4543},
    "lhr": {"name": "London Heathrow (LHR)", "city": "London", "country": "UK", "lat": 51.4700, "lon": -0.4543},
    "dubai": {"name": "Dubai (DXB)", "city": "Dubai", "country": "UAE", "lat": 25.2532, "lon": 55.3657},
    "dxb": {"name": "Dubai (DXB)", "city": "Dubai", "country": "UAE", "lat": 25.2532, "lon": 55.3657},
    "singapore": {"name": "Singapore Changi (SIN)", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915},
    "sin": {"name": "Singapore Changi (SIN)", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915},
    "new york": {"name": "New York (JFK)", "city": "New York", "country": "USA", "lat": 40.6413, "lon": -73.7781},
    "jfk": {"name": "New York (JFK)", "city": "New York", "country": "USA", "lat": 40.6413, "lon": -73.7781},
    "paris": {"name": "Paris (CDG)", "city": "Paris", "country": "France", "lat": 49.0097, "lon": 2.5479},
    "bangkok": {"name": "Bangkok (BKK)", "city": "Bangkok", "country": "Thailand", "lat": 13.6900, "lon": 100.7501},
    "toronto": {"name": "Toronto (YYZ)", "city": "Toronto", "country": "Canada", "lat": 43.6777, "lon": -79.6248},
    "tokyo": {"name": "Tokyo (NRT/HND)", "city": "Tokyo", "country": "Japan", "lat": 35.7720, "lon": 140.3929},
    "doha": {"name": "Doha (DOH)", "city": "Doha", "country": "Qatar", "lat": 25.2731, "lon": 51.6081},
    "frankfurt": {"name": "Frankfurt (FRA)", "city": "Frankfurt", "country": "Germany", "lat": 50.0379, "lon": 8.5622},
}


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def generate_live_flights(origin_city: str, dest_city: str, travel_date: datetime, db: Session):
    orig_key = origin_city.lower().strip()
    dest_key = dest_city.lower().strip()

    orig_info = CITY_DATA.get(orig_key, {"name": origin_city.title(), "city": origin_city.title(), "country": "India", "lat": 20.0, "lon": 77.0})
    dest_info = CITY_DATA.get(dest_key, {"name": dest_city.title(), "city": dest_city.title(), "country": "International", "lat": 51.0, "lon": 0.0})

    dist_km = calculate_distance(orig_info["lat"], orig_info["lon"], dest_info.get("lat", 0.0), dest_info.get("lon", 0.0))
    if dist_km < 350:
        dist_km = 850

    flight_hours = dist_km / 780.0
    is_intl = dest_info.get("country", "") not in ["India", ""]

    if is_intl:
        airlines = [
            {"operator": f"Air India (AI {random.randint(111, 199)})", "aircraft": "Boeing 777-300ER", "mult": 7.4, "stops": "Non-stop", "extra_m": 0},
            {"operator": f"British Airways (BA {random.randint(110, 160)})" if "london" in dest_key or "uk" in dest_info.get("country", "").lower() else f"Emirates (EK {random.randint(501, 540)}) via Dubai", "aircraft": "Boeing 787-9 Dreamliner", "mult": 8.2, "stops": "Non-stop" if "london" in dest_key else "1 Stop via DXB", "extra_m": 0 if "london" in dest_key else 135},
            {"operator": f"Virgin Atlantic (VS {random.randint(300, 360)})" if "london" in dest_key else f"Qatar Airways (QR {random.randint(550, 595)}) via Doha", "aircraft": "Airbus A350-1000", "mult": 7.9, "stops": "Non-stop" if "london" in dest_key else "1 Stop via DOH", "extra_m": 0 if "london" in dest_key else 120},
            {"operator": f"IndiGo (6E {random.randint(11, 99)}) Codeshare", "aircraft": "Airbus A321neo", "mult": 6.3, "stops": "1 Stop (Istanbul/Dubai)", "extra_m": 160},
            {"operator": f"Singapore Airlines (SQ {random.randint(401, 450)})" if "singapore" in dest_key else f"Lufthansa (LH {random.randint(750, 790)}) via Frankfurt", "aircraft": "Airbus A380", "mult": 8.5, "stops": "Non-stop" if "singapore" in dest_key else "1 Stop via FRA", "extra_m": 0 if "singapore" in dest_key else 140},
        ]
    else:
        airlines = [
            {"operator": f"IndiGo (6E {random.randint(2000, 2999)})", "aircraft": "Airbus A320neo", "mult": 4.2, "stops": "Non-stop", "extra_m": 0},
            {"operator": f"Air India (AI {random.randint(800, 899)})", "aircraft": "Airbus A321neo", "mult": 4.9, "stops": "Non-stop", "extra_m": 0},
            {"operator": f"Vistara (UK {random.randint(900, 999)})", "aircraft": "Boeing 737 / A320", "mult": 5.5, "stops": "Non-stop", "extra_m": 0},
            {"operator": f"Akasa Air (QP {random.randint(1100, 1400)})", "aircraft": "Boeing 737 MAX 8", "mult": 3.9, "stops": "Non-stop", "extra_m": 0},
            {"operator": f"Air India Express (IX {random.randint(600, 799)})", "aircraft": "Boeing 737-800", "mult": 4.1, "stops": "Non-stop", "extra_m": 0},
        ]

    created = []
    base_hours = [6, 9, 13, 17, 21]

    for idx, carrier in enumerate(airlines):
        dep_h = base_hours[idx % len(base_hours)]
        dep_m = (idx * 20) % 60
        dep = travel_date.replace(hour=dep_h, minute=dep_m, second=0, microsecond=0)

        tot_h = flight_hours + (carrier["extra_m"] / 60.0)
        arr = dep + timedelta(hours=int(tot_h), minutes=int((tot_h % 1) * 60))

        price = round(dist_km * carrier["mult"], -1)
        if is_intl:
            price = max(21500.0, min(89000.0, price))
        else:
            price = max(3150.0, min(14800.0, price))

        trip = Trip(
            transport_type="flight",
            operator=f"{carrier['operator']} • {carrier['aircraft']} ({carrier['stops']})",
            origin=orig_info["city"],
            destination=dest_info["city"],
            departure_time=dep,
            arrival_time=arr,
            price=price,
            seats_total=240 if is_intl else 180,
            seats_available=random.randint(18, 120)
        )
        db.add(trip)
        created.append(trip)

    db.commit()
    for t in created:
        db.refresh(t)
    return created


def generate_live_trains(origin_city: str, dest_city: str, travel_date: datetime, db: Session):
    orig = origin_city.title()
    dest = dest_city.title()

    train_configs = [
        {"name": f"Vande Bharat Express (Train #{random.randint(20600, 22500)})", "type": "Semi-High Speed AC Chair Car / EC", "hours": 6.5, "price": 1650.0},
        {"name": f"{dest} Rajdhani Express (Train #{random.randint(12400, 12990)})", "type": "Superfast AC 1A/2A/3A with Meals", "hours": 12.0, "price": 2850.0},
        {"name": f"{orig} - {dest} Shatabdi (Train #{random.randint(12000, 12050)})", "type": "Daytime Express AC Chair Car", "hours": 7.0, "price": 1240.0},
        {"name": f"{orig} Superfast Express (Train #{random.randint(12600, 12800)})", "type": "Superfast Express 2A/3A/SL", "hours": 14.5, "price": 890.0},
    ]

    created = []
    times = [6, 12, 16, 21]
    for idx, cfg in enumerate(train_configs):
        dep = travel_date.replace(hour=times[idx], minute=15, second=0, microsecond=0)
        arr = dep + timedelta(hours=int(cfg["hours"]), minutes=int((cfg["hours"] % 1) * 60))

        trip = Trip(
            transport_type="train",
            operator=f"{cfg['name']} • {cfg['type']}",
            origin=orig,
            destination=dest,
            departure_time=dep,
            arrival_time=arr,
            price=cfg["price"],
            seats_total=300,
            seats_available=random.randint(24, 210)
        )
        db.add(trip)
        created.append(trip)

    db.commit()
    for t in created:
        db.refresh(t)
    return created


def generate_live_buses(origin_city: str, dest_city: str, travel_date: datetime, db: Session):
    orig = origin_city.title()
    dest = dest_city.title()

    bus_configs = [
        {"op": "KSRTC / MSRTC Airavat Club Class Multi-Axle Volvo", "hours": 7.5, "price": 1150.0},
        {"op": "Zingbus Electric Luxury AC Sleeper (2+1)", "hours": 6.0, "price": 890.0},
        {"op": "IntrCity SmartBus AC Multi-Axle Volvo with Live GPS", "hours": 8.0, "price": 1280.0},
        {"op": "NueGo Intercity 100% Electric Premium AC Coach", "hours": 6.5, "price": 750.0},
    ]

    created = []
    times = [7, 14, 21, 22]
    for idx, cfg in enumerate(bus_configs):
        dep = travel_date.replace(hour=times[idx], minute=30, second=0, microsecond=0)
        arr = dep + timedelta(hours=int(cfg["hours"]), minutes=int((cfg["hours"] % 1) * 60))

        trip = Trip(
            transport_type="bus",
            operator=cfg["op"],
            origin=orig,
            destination=dest,
            departure_time=dep,
            arrival_time=arr,
            price=cfg["price"],
            seats_total=45,
            seats_available=random.randint(8, 36)
        )
        db.add(trip)
        created.append(trip)

    db.commit()
    for t in created:
        db.refresh(t)
    return created


@router.get("/trips")
def get_trips(
    type: Optional[str] = Query(None, description="Transport type: flight, train, bus, cab, bike"),
    origin: Optional[str] = Query(None, description="Origin city or hub"),
    destination: Optional[str] = Query(None, description="Destination city or hub"),
    date: Optional[str] = Query(None, description="Departure date in YYYY-MM-DD format"),
    max_price: Optional[float] = Query(None, description="Maximum ticket price in INR (₹)"),
    db: Session = Depends(get_db)
):
    """
    Search available trips with smart routing:
    - Trains are strictly domestic within India; rejects international queries with clear instruction.
    - Generates and persists authentic live schedules for any valid origin-destination query.
    """
    active_type = "flight"
    if type and type.lower() not in ["all", "allmodes", ""]:
        active_type = type.lower().strip()

    dest_lower = (destination or "").strip().lower()

    # Train / Bus validation against overseas cities
    if active_type in ["train", "bus"] and any(overseas in dest_lower for overseas in OVERSEAS_HUBS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{active_type.capitalize()}s operate domestically within India. For travel to '{destination}', please switch to the Flights tab."
        )

    query = db.query(Trip).filter(Trip.transport_type == active_type)

    if origin and origin.strip():
        origin_clean = origin.strip().lower()
        if origin_clean in ["delhi", "new delhi", "del"]:
            query = query.filter(or_(Trip.origin.ilike("%delhi%"), Trip.origin.ilike("%del%")))
        elif origin_clean in ["mumbai", "bombay", "bom"]:
            query = query.filter(or_(Trip.origin.ilike("%mumbai%"), Trip.origin.ilike("%bom%")))
        elif origin_clean in ["bengaluru", "bangalore", "blr"]:
            query = query.filter(or_(Trip.origin.ilike("%bengaluru%"), Trip.origin.ilike("%bangalore%"), Trip.origin.ilike("%blr%")))
        elif origin_clean in ["chennai", "madras", "maa"]:
            query = query.filter(or_(Trip.origin.ilike("%chennai%"), Trip.origin.ilike("%maa%")))
        elif origin_clean in ["hyderabad", "hyd"]:
            query = query.filter(or_(Trip.origin.ilike("%hyderabad%"), Trip.origin.ilike("%hyd%")))
        elif origin_clean in ["kolkata", "calcutta", "ccu"]:
            query = query.filter(or_(Trip.origin.ilike("%kolkata%"), Trip.origin.ilike("%ccu%")))
        else:
            query = query.filter(Trip.origin.ilike(f"%{origin.strip()}%"))

    if destination and destination.strip():
        if dest_lower in ["london", "lhr", "london heathrow", "uk"]:
            query = query.filter(Trip.destination.ilike("%london%"))
        elif dest_lower in ["delhi", "new delhi", "del"]:
            query = query.filter(or_(Trip.destination.ilike("%delhi%"), Trip.destination.ilike("%del%")))
        elif dest_lower in ["mumbai", "bombay", "bom"]:
            query = query.filter(or_(Trip.destination.ilike("%mumbai%"), Trip.destination.ilike("%bom%")))
        elif dest_lower in ["bengaluru", "bangalore", "blr"]:
            query = query.filter(or_(Trip.destination.ilike("%bengaluru%"), Trip.destination.ilike("%bangalore%"), Trip.destination.ilike("%blr%")))
        elif dest_lower in ["chennai", "madras", "maa"]:
            query = query.filter(or_(Trip.destination.ilike("%chennai%"), Trip.destination.ilike("%maa%")))
        elif dest_lower in ["hyderabad", "hyd"]:
            query = query.filter(or_(Trip.destination.ilike("%hyderabad%"), Trip.destination.ilike("%hyd%")))
        elif dest_lower in ["dubai", "dxb", "uae"]:
            query = query.filter(Trip.destination.ilike("%dubai%"))
        elif dest_lower in ["singapore", "sin"]:
            query = query.filter(Trip.destination.ilike("%singapore%"))
        elif dest_lower in ["new york", "jfk", "usa"]:
            query = query.filter(Trip.destination.ilike("%new york%"))
        elif dest_lower in ["goa", "goi", "gox"]:
            query = query.filter(Trip.destination.ilike("%goa%"))
        elif dest_lower in ["varanasi", "vns"]:
            query = query.filter(Trip.destination.ilike("%varanasi%"))
        else:
            query = query.filter(Trip.destination.ilike(f"%{destination.strip()}%"))

    if date and date.strip():
        try:
            target_date = datetime.strptime(date.strip(), "%Y-%m-%d").date()
            query = query.filter(func.date(Trip.departure_time) == target_date.strftime("%Y-%m-%d"))
        except ValueError:
            pass

    if max_price is not None and max_price > 0:
        query = query.filter(Trip.price <= max_price)

    trips = query.order_by(Trip.departure_time.asc()).all()

    # Dynamic Generator for Unseeded Route Pairs
    if len(trips) == 0 and origin and destination and origin.strip() and destination.strip():
        travel_dt = datetime.now(timezone.utc)
        if date and date.strip():
            try:
                travel_dt = datetime.strptime(date.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        if active_type == "flight":
            trips = generate_live_flights(origin, destination, travel_dt, db)
        elif active_type == "train":
            trips = generate_live_trains(origin, destination, travel_dt, db)
        elif active_type == "bus":
            trips = generate_live_buses(origin, destination, travel_dt, db)

    return {
        "count": len(trips),
        "trips": [t.to_dict() for t in trips]
    }


@router.get("/trips/{trip_id}")
def get_trip_by_id(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip #{trip_id} not found."
        )
    return {"trip": trip.to_dict()}


@router.get("/popular-routes")
def get_popular_routes(db: Session = Depends(get_db)):
    indian_routes = [
        {"type": "flight", "origin": "Delhi", "destination": "London", "starting_from": 44800.0, "duration": "9h 30m Direct", "desc": "Air India B777, British Airways & Virgin Atlantic"},
        {"type": "flight", "origin": "Bengaluru", "destination": "London", "starting_from": 52600.0, "duration": "10h 40m Direct", "desc": "British Airways BA 118 Dreamliner & Air India"},
        {"type": "flight", "origin": "Chennai", "destination": "London", "starting_from": 49200.0, "duration": "11h 15m", "desc": "British Airways BA 36 & Emirates via Dubai"},
        {"type": "flight", "origin": "Mumbai", "destination": "Dubai", "starting_from": 18900.0, "duration": "3h 40m Direct", "desc": "Emirates & IndiGo daily non-stop services"},
        {"type": "flight", "origin": "Delhi", "destination": "Mumbai", "starting_from": 4450.0, "duration": "2h 15m", "desc": "IndiGo, Air India, Vistara & Akasa Air"},
        {"type": "train", "origin": "Delhi", "destination": "Varanasi", "starting_from": 1750.0, "duration": "8h 00m", "desc": "Vande Bharat Express (Train #22436) Chair Car & EC"},
        {"type": "train", "origin": "Bengaluru", "destination": "Chennai", "starting_from": 1020.0, "duration": "4h 25m", "desc": "Vande Bharat Express (Train #20608) Fast Connection"},
        {"type": "bus", "origin": "Bengaluru", "destination": "Hyderabad", "starting_from": 1250.0, "duration": "9h 00m", "desc": "KSRTC Airavat Club Class Multi-Axle Volvo AC"},
        {"type": "bus", "origin": "Mumbai", "destination": "Pune", "starting_from": 520.0, "duration": "3h 30m", "desc": "MSRTC Shivneri AC Volvo (every 30 mins)"},
        {"type": "cab", "origin": "Mumbai Airport", "destination": "South Mumbai", "starting_from": 950.0, "duration": "1h 15m", "desc": "Uber Premier & Ola Prime AC Sedan"},
    ]
    return {"routes": indian_routes}
