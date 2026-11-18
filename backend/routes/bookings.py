"""
backend/routes/bookings.py - Bookings REST API Endpoints
Endpoints:
- POST /api/bookings (reduces trips.seats_available inside one transaction; reject if not enough seats)
- GET /api/my-bookings
- GET /api/bookings/{id}
- POST /api/bookings/{id}/cancel (returns seats to trip inside one transaction)
"""

from datetime import datetime, timezone
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Booking, Trip, User
from backend.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Bookings"])


class CreateBookingSchema(BaseModel):
    trip_id: int = Field(..., description="Target trip ID")
    passenger_names: Union[str, List[str]] = Field(..., description="Passenger full name(s)")
    seats_booked: int = Field(..., ge=1, le=20, description="Number of seats or vehicles booked")


@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(
    req: CreateBookingSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new booking within a single atomic database transaction:
    1. Locks and verifies trip existence.
    2. Verifies seats_available >= seats_booked (rejects if insufficient).
    3. Decrements trip.seats_available.
    4. Calculates total_price.
    5. Saves booking record with status='confirmed'.
    6. Commits transaction so live changes appear on the admin monitor immediately.
    """
    # Normalize passenger_names
    if isinstance(req.passenger_names, list):
        names_str = ", ".join([n.strip() for n in req.passenger_names if n.strip()])
    else:
        names_str = req.passenger_names.strip()

    if not names_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one passenger name must be provided."
        )

    try:
        # Fetch trip inside transaction
        trip = db.query(Trip).filter(Trip.id == req.trip_id).with_for_update().first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip #{req.trip_id} not found."
            )

        # Seat availability check
        if trip.seats_available < req.seats_booked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough seats available. Only {trip.seats_available} seat(s) remaining for this trip."
            )

        # Atomic seat decrement
        trip.seats_available -= req.seats_booked

        # Price calculation
        total_price = round(trip.price * req.seats_booked, 2)

        booking = Booking(
            user_id=current_user.id,
            trip_id=trip.id,
            passenger_names=names_str,
            seats_booked=req.seats_booked,
            total_price=total_price,
            status="confirmed",
            booked_at=datetime.now(timezone.utc)
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "message": "Booking confirmed successfully.",
            "booking": booking.to_dict()
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction failed: {str(e)}"
        )


@router.get("/my-bookings")
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all bookings for the currently authenticated customer,
    ordered by booking date descending.
    """
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).order_by(Booking.booked_at.desc()).all()

    return {
        "count": len(bookings),
        "bookings": [b.to_dict() for b in bookings]
    }


@router.get("/bookings/{booking_id}")
def get_booking_details(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full booking details for ticket rendering.
    Enforces authorization: users can only view their own bookings unless admin.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking #{booking_id} not found."
        )

    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this booking."
        )

    return {"booking": booking.to_dict()}


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancels a booking inside an atomic transaction:
    1. Validates ownership and state.
    2. Marks status = 'cancelled'.
    3. Returns booked seats back to the trip (seats_available += seats_booked).
    4. Commits transaction so live seat counts reflect on admin monitor and search.
    """
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).with_for_update().first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking #{booking_id} not found."
            )

        if booking.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this booking."
            )

        if booking.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This booking has already been cancelled."
            )

        # Fetch trip and restore seats
        trip = db.query(Trip).filter(Trip.id == booking.trip_id).with_for_update().first()
        if trip:
            trip.seats_available = min(trip.seats_total, trip.seats_available + booking.seats_booked)

        booking.status = "cancelled"
        db.commit()
        db.refresh(booking)

        return {
            "message": "Booking successfully cancelled. Seats have been returned to the trip.",
            "booking": booking.to_dict()
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cancellation transaction failed: {str(e)}"
        )
