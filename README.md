# Trekking Management Application - MAD2 Project

This is my Modern Application Development 2 (MAD2) project on a Trekking Management Application.  
**(Roll No.: 23f2003086)**

---

## Project Architecture

```text
├── backend
│   ├── api/              # API endpoints for admin, staff, and trekkers
│   ├── auth/             # Authentication, role-based access, and JWT logic
│   ├── core/             # Application configuration and security settings
│   ├── database/         # SQLAlchemy models and database session management
│   ├── db/               # SQLite database file (trekking.sqlite3)
│   ├── service/          # Core business logic used by routes and tasks
│   ├── tasks/            # Celery workers for background jobs (emails, payments)
│   ├── app.py            # Main Flask application entry point
│   ├── cache.py          # Caching instance initialization (Redis)
│   ├── celery_app.py     # Celery instance and scheduler setup
│   ├── requirements.txt  # Python dependencies
│   └── start.bat|.sh   # Startup script for backend services
└── frontend
    ├── src/
    │   ├── components/   # Reusable UI components (admin, user, shared)
    │   ├── routers/      # Vue Router configuration and navigation guards
    │   ├── views/        # Page-level layouts categorized by portals (admin, auth, staff, user)
    │   ├── App.vue       # Root Vue component and layout wrapper
    │   └── main.js       # Main Vue app entry point and plugin initialization
    ├── index.html        # Main HTML template
    ├── package.json      # Node.js dependencies and scripts
    └── vite.config.js    # Vite build tool and dev server configuration
```

---

## Challenges Faced

* **Setting up Celery and Redis:** Configuring the background workers and Redis database required studying documentation and utilizing AI (Gemini) to get both running smoothly.
* **Email Service Integration:** Implementing the SMTP protocol to send automated emails to specific users was a new concept to learn and integrate into the Flask app.
* **Frontend Routing:** Figuring out the proper way to configure Vue Router so that all components navigate and work seamlessly across different role-based views.
* **Chart.js Integration:** Being new to both Chart.js and Vue.js, I relied on documentation, video lectures, and Gemini to build the analytical dashboards.

---

## How to Run the Project

### 1. Frontend Setup

Navigate to the frontend directory, install the required npm packages, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

### 2. Backend Setup

Navigate to the backend directory and create a Python virtual environment.

**For Linux / macOS:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

*(Alternatively, use `uv init` if you prefer using uv).*

**For Windows:**

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
```

*(Alternatively, use `uv init` if you prefer using uv).*

### 3. Redis Setup (Required for Celery & Caching)

Redis must be running in the background before you start the backend server.

**For Linux (Ubuntu/Debian):**

1. Install Redis:
```bash
sudo apt update
sudo apt install redis-server
```


2. Start the Redis service:
```bash
sudo systemctl start redis-server
```


*(To ensure it's running, you can type `redis-cli ping`. It should reply with `PONG`).*

**For Windows:**
Since Redis doesn't officially support Windows natively, you have two options:

* **Option A (WSL - Recommended):** Open your Windows Subsystem for Linux (WSL) terminal and run the exact same commands listed in the Linux section above.
* **Option B (Native Windows Port):** 1. Go to [https://github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases).
2. Download the latest `.msi` file and install it.
3. Once installed, Redis automatically runs as a background Windows service (you don't need to start it manually). You can verify it's working by opening Command Prompt, typing `redis-cli`, and then typing `ping`.

### 4. Environment Variables (`.env`)

Create a `.env` file in the root of your `backend` folder and add the following configuration:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-secret-key-jwt
API_BASE=/api
API_SERVER_URL=http://localhost:8000

REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=RedisCache
CACHE_DEFAULT_TIMEOUT=300

EMAIL_USER=example@gmail.com
EMAIL_PASS=hykc scbc dksi ksok
EMAIL_OTP_SALT=email-otp-salt
```

> **Note on `EMAIL_PASS`:** This is your 16-character Google App Password. You can generate it by navigating to your Google Account -> Security -> 2-Step Verification -> App Passwords, or you can go directly to this link to generate it: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### 5. Start the Backend Server

Once your virtual environment is active, Redis is running, and the `.env` file is set up, run the startup script to boot the backend services (Flask and Celery).

**For Linux / macOS:**

```bash
./start.sh
```

**For Windows:**

```cmd
start.bat
```

---

## Accessing the Application

Once both the frontend and backend servers are running, you can access the application using the links below:

* **Frontend:** [http://localhost:5173/](https://www.google.com/search?q=http://localhost:5173/)
* **Backend:** [http://localhost:8000/](https://www.google.com/search?q=http://localhost:8000/)

### Default Admin Credentials

To access the administrator dashboard, use the following credentials:
* **Email:** `admin@tma.com`
* **Password:** `Admin@1234`
