# GoTix — Your Journey. Your Way.

Every Journey Starts with GoTix.

GoTix is an educational travel booking platform that allows users to search and simulate bookings for buses, trains, flights, and cabs. This is a full-stack application built with the MERN stack (MongoDB, Express, React, Node.js).

**Note:** This is a demonstration project. All transport schedules, fares, and bookings are simulated demo data. No actual reservations are made with transport operators, and no payments are processed.

## 🚀 Features

- **Multi-Transport Search**: Search for Buses, Trains, Flights, and Cabs.
- **Simulated Inventory**: Centralized demo data for various routes and services.
- **User Authentication**: Secure registration and login using JWT and bcrypt.
- **Booking Flow**: Complete flow from search to passenger details and confirmation.
- **Booking History**: View your past and upcoming simulated bookings.
- **Print Confirmation**: Generate a print-friendly booking confirmation.
- **Responsive Design**: Modern UI that works on desktop, tablet, and mobile.

## 🛠️ Technology Stack

- **Frontend**: React (Vite), JavaScript, Tailwind CSS, Lucide React, Axios.
- **Backend**: Node.js, Express.js.
- **Database**: MongoDB Atlas with Mongoose.
- **Authentication**: JWT (JSON Web Tokens) and bcryptjs.

## 📂 Project Structure

```
gotix/
├── client/              # Frontend React application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── context/     # Auth and state management
│   │   ├── pages/       # Page components
│   │   └── services/    # API communication
├── server/              # Backend Node.js application
│   ├── config/          # Database configuration
│   ├── models/          # Mongoose models
│   ├── routes/          # API routes
│   └── utils/           # Helper functions and sample data
└── README.md
```

## ⚙️ Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- MongoDB Atlas account (or local MongoDB)

## 🛠️ Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd gotix
```

### 2. Backend Setup
1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables:
   - Create a `.env` file in the `server` directory.
   - Use the following template (update with your credentials):
   ```env
   PORT=5000
   MONGODB_URI=your_mongodb_connection_string
   JWT_SECRET=your_long_random_secret
   CLIENT_URL=http://localhost:5173
   ```
4. Start the backend server:
   ```bash
   npm start
   ```

### 3. Frontend Setup
1. Navigate to the client directory:
   ```bash
   cd ../client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 🧪 Testing the Application

1. **Register**: Create a new account.
2. **Search**: Go to the homepage and search for a journey (e.g., Mumbai to Pune).
3. **Select**: Choose a transport service from the results.
4. **Book**: Enter passenger details and confirm.
5. **History**: Go to "My Bookings" to view your saved booking.

## ⚠️ Demo Limitations
- No actual payment gateway is integrated.
- Seat availability is simulated and does not reflect real-time data.
- Cabs use estimated fares based on category.

---
Built for educational purposes as part of the GoTix project.
