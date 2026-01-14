# RideShare API

A **scalable and real-time ride-sharing backend** built with **Django**, **Django REST Framework**, and **Django Channels**.
The system is designed to support **REST APIs** and **real-time WebSocket communication** using **Redis**, enabling features like live ride updates, notifications, and asynchronous events.

---

## Project Overview

The RideShare API handles:

* User authentication and account management
* Ride lifecycle management
* Real-time notifications
* Ratings and reviews
* Payment handling
* Frontend integration support
* Redis-powered WebSocket communication

---

## Tech Stack

* **Backend:** Django, Django REST Framework
* **Real-Time:** Django Channels, WebSockets
* **Message Broker:** Redis
* **Database:** SQLite (development)
* **Language:** Python 3.x

---

## Folder Structure

```
rideshare/
│
├── accounts/        # User authentication & profiles
├── config/          # Project settings (ASGI, URLs, settings)
├── frontend/        # Frontend integration (if applicable)
├── notifications/  # Real-time notifications (WebSockets)
├── payments/       # Ride payment handling
├── ratings/        # Driver & rider ratings
├── rides/           # Ride booking & lifecycle logic
│
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## Setup & Run Instructions

Follow these steps to run the project locally.

---

### 1. Clone the Repository

```bash
git clone https://github.com/israr-ax/rideshare-api.git
cd rideshare
```

---

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install & Run Redis Server

Redis is **mandatory** for WebSockets and Django Channels.

**Windows (WSL recommended)**

```bash
redis-server
```

**Linux**

```bash
sudo apt install redis
redis-server
```

**macOS**

```bash
brew install redis
brew services start redis
```

Verify Redis:

```bash
redis-cli ping
```

Expected output:

```
PONG
```

---

### 5. Configure Django Channels

Ensure the following settings exist in `config/settings.py`:

```python
ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

---

### 6. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

---

### 8. Run the Server

**Development Server**

```bash
python manage.py runserver
```

**WebSocket-Friendly (Recommended)**

```bash
daphne config.asgi:application
```

Server will be available at:

```
http://127.0.0.1:8000/
```

---

## API & WebSocket Usage

### REST APIs

* User registration & authentication
* Ride creation and status updates
* Ratings and payments APIs

### WebSockets

* Real-time ride status updates
* Instant notifications
* Async events using Redis

Example WebSocket endpoint:

```
ws://127.0.0.1:8000/ws/rides/<ride_id>/
```

---

## Important Notes

* Redis **must be running** before starting the server
* Do not commit `venv/` or `.env` files
* SQLite is for development only
* Use PostgreSQL for production
* Secrets should be stored in environment variables

---

## Future Enhancements

* Live GPS tracking
* Push notifications
* Payment gateway integration
* Driver matching algorithm
* Docker & CI/CD support

