"""
backend/main.py - Main FastAPI Application Server
Serves REST API endpoints and static frontend pages (11 pages in total).
Handles CORS, database lifecycle, and friendly routing.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.routes import auth, trips, bookings, admin

# Create database tables if not already existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ticket Booking - Transport Booking & Database Monitor System",
    description="Full-stack transport ticket booking platform with real-time Database Monitor.",
    version="1.0.0"
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST API routers
app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(bookings.router)
app.include_router(admin.router)

# Paths for static assets and frontend HTML pages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CSS_DIR = os.path.join(FRONTEND_DIR, "css")
JS_DIR = os.path.join(FRONTEND_DIR, "js")
ADMIN_DIR = os.path.join(FRONTEND_DIR, "admin")

# Mount CSS and JS static asset directories
if os.path.exists(CSS_DIR):
    app.mount("/css", StaticFiles(directory=CSS_DIR), name="css")
if os.path.exists(JS_DIR):
    app.mount("/js", StaticFiles(directory=JS_DIR), name="js")

# Mount entire frontend directory for direct file serving
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Customer Pages Routes
@app.get("/", response_class=FileResponse)
@app.get("/index.html", response_class=FileResponse)
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/search", response_class=FileResponse)
@app.get("/search.html", response_class=FileResponse)
def serve_search():
    return FileResponse(os.path.join(FRONTEND_DIR, "search.html"))


@app.get("/login", response_class=FileResponse)
@app.get("/login.html", response_class=FileResponse)
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/booking", response_class=FileResponse)
@app.get("/booking.html", response_class=FileResponse)
def serve_booking():
    return FileResponse(os.path.join(FRONTEND_DIR, "booking.html"))


@app.get("/ticket", response_class=FileResponse)
@app.get("/ticket.html", response_class=FileResponse)
def serve_ticket():
    return FileResponse(os.path.join(FRONTEND_DIR, "ticket.html"))


@app.get("/my-bookings", response_class=FileResponse)
@app.get("/my-bookings.html", response_class=FileResponse)
def serve_my_bookings():
    return FileResponse(os.path.join(FRONTEND_DIR, "my-bookings.html"))


# Admin Database Monitor Pages Routes
@app.get("/admin", response_class=FileResponse)
@app.get("/admin/index.html", response_class=FileResponse)
@app.get("/admin/dashboard", response_class=FileResponse)
@app.get("/admin/dashboard.html", response_class=FileResponse)
def serve_admin_dashboard():
    return FileResponse(os.path.join(ADMIN_DIR, "dashboard.html"))


@app.get("/admin/users", response_class=FileResponse)
@app.get("/admin/users.html", response_class=FileResponse)
def serve_admin_users():
    return FileResponse(os.path.join(ADMIN_DIR, "users.html"))


@app.get("/admin/login-logs", response_class=FileResponse)
@app.get("/admin/login-logs.html", response_class=FileResponse)
def serve_admin_login_logs():
    return FileResponse(os.path.join(ADMIN_DIR, "login-logs.html"))


@app.get("/admin/trips", response_class=FileResponse)
@app.get("/admin/trips.html", response_class=FileResponse)
def serve_admin_trips():
    return FileResponse(os.path.join(ADMIN_DIR, "trips.html"))


@app.get("/admin/bookings", response_class=FileResponse)
@app.get("/admin/bookings.html", response_class=FileResponse)
def serve_admin_bookings():
    return FileResponse(os.path.join(ADMIN_DIR, "bookings.html"))
