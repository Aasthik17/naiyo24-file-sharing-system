# 📁 Naiyo24 File Sharing System

A full-stack, cross-platform file sharing application built with **Flutter** (frontend) and **FastAPI** (backend). Users can register, log in, upload files, and share them via expiring short links — all served through a Docker-composed microservice stack.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure register & login with token persistence
- 📤 **File Upload** — Pick and upload any file via a native file picker
- 🔗 **Expiring Share Links** — Generate short links with configurable expiry (10–60 minutes)
- 📥 **File Download** — Download files via share links without authentication
- 🎨 **Dark-themed UI** — Custom brand design system with Google Fonts
- ⚡ **Background Tasks** — Celery workers handle async processing (e.g. link cleanup)
- 📊 **Task Monitoring** — Flower dashboard for Celery worker visibility
- 🗄️ **Object Storage** — MinIO (S3-compatible) for file persistence
- 🔄 **Nginx Reverse Proxy** — Routes all traffic through a single entry point

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Flutter App (Client)         │
│  Android · iOS · Web · Desktop      │
└────────────────┬────────────────────┘
                 │ HTTP / REST
                 ▼
┌─────────────────────────────────────┐
│           Nginx (Port 80)            │  ← Reverse Proxy
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       FastAPI Backend (Port 8000)    │
│  /api/auth · /api/upload            │
│  /api/share · /api/download         │
└──────┬───────────────┬──────────────┘
       │               │
       ▼               ▼
┌────────────┐  ┌─────────────┐
│ PostgreSQL  │  │    Redis     │
│ (Port 5432) │  │ (Port 6379)  │
└────────────┘  └──────┬───────┘
                        │
                        ▼
               ┌─────────────────┐
               │  Celery Worker   │
               │  + Flower :5555  │
               └─────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  MinIO Storage   │
               │  API  :9000      │
               │  UI   :9001      │
               └─────────────────┘
```

---

## 🗂️ Project Structure

```
naiyo24-file-sharing-system/
├── lib/                          # Flutter frontend
│   ├── main.dart                 # App entry point & routing
│   ├── providers/
│   │   ├── auth_provider.dart    # Authentication state (Riverpod)
│   │   └── file_provider.dart    # File upload state (Riverpod)
│   ├── screens/
│   │   ├── login_screen.dart     # Login UI
│   │   ├── register_screen.dart  # Registration UI
│   │   └── upload_screen.dart    # File upload & share link UI
│   ├── services/
│   │   └── api_service.dart      # Dio HTTP client
│   ├── theme/
│   │   └── app_theme.dart        # Dark theme definition
│   └── widgets/
│       └── brand_kit.dart        # Reusable UI components
│
├── test/
│   └── widget_test.dart          # Widget tests
│
├── filesharingbackend/           # Backend services
│   ├── docker-compose.yml        # Service orchestration
│   ├── nginx/
│   │   └── nginx.conf            # Nginx config
│   └── backend/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── alembic.ini           # DB migration config
│       ├── migrations/           # Alembic migration scripts
│       └── app/
│           ├── main.py           # FastAPI app factory
│           ├── api/
│           │   ├── router.py     # Root API router
│           │   └── routes/
│           │       ├── auth.py       # /api/auth
│           │       ├── upload.py     # /api/upload
│           │       ├── share.py      # /api/share
│           │       └── download.py   # /api/download
│           ├── core/             # Config, DB engine, security
│           ├── models/           # SQLAlchemy ORM models
│           ├── schemas/          # Pydantic request/response schemas
│           ├── services/         # Business logic & storage service
│           ├── workers/          # Celery tasks
│           └── utils/            # Logging, helpers
│
├── pubspec.yaml
└── analysis_options.yaml
```

---

## 🧰 Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| Flutter 3 (Dart ≥ 3.2.5) | Cross-platform UI framework |
| flutter_riverpod `^2.5.1` | State management |
| dio `^5.4.0` | HTTP client |
| file_picker `^8.0.0` | Native file selection |
| shared_preferences `^2.2.2` | JWT token persistence |
| google_fonts `^6.3.2` | Typography |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI 0.111 | Async REST API |
| SQLAlchemy 2 + asyncpg | Async ORM / PostgreSQL |
| Alembic | Database migrations |
| Redis + Celery | Background task queue |
| Flower | Celery task monitoring |
| MinIO (boto3) | S3-compatible file storage |
| python-jose + passlib | JWT auth & password hashing |
| Nginx | Reverse proxy |

---

## 🚀 Getting Started

### Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) ≥ 3.2.5
- [Docker](https://www.docker.com/get-started) & Docker Compose
- An Android/iOS emulator or physical device (for mobile targets)

---

### 1. Start the Backend

```bash
cd filesharingbackend

# Copy and configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Build and start all services
docker compose up --build -d
```

**Service URLs once running:**

| Service | URL |
|---|---|
| FastAPI (via Nginx) | http://localhost |
| FastAPI (direct) | http://localhost:8000 |
| FastAPI Swagger Docs | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |
| Flower (Celery Monitor) | http://localhost:5555 |
| Health Check | http://localhost:8000/health |

---

### 2. Run the Flutter App

```bash
# From the project root
flutter pub get

# Run on a connected device or emulator
flutter run

# Or target a specific platform
flutter run -d chrome       # Web
flutter run -d macos        # macOS desktop
flutter run -d android      # Android device/emulator
```

> **Note:** The app points to your backend host. Update the base URL in `lib/services/api_service.dart` if running on a physical device (replace `localhost` with your machine's local IP, e.g. `192.168.1.x`).

---

### 3. Run Tests

```bash
flutter test
```

All tests should pass with no analysis issues:

```bash
flutter analyze   # No issues found
flutter test      # 2/2 tests passed
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | ❌ | Register a new user |
| `POST` | `/api/auth/login` | ❌ | Login and receive JWT token |
| `POST` | `/api/upload` | ✅ | Upload a file to MinIO |
| `POST` | `/api/share` | ✅ | Create an expiring share link |
| `GET` | `/api/download/{token}` | ❌ | Download file via share token |
| `GET` | `/health` | ❌ | Backend health check |

---

## ⚙️ Environment Variables

Create `filesharingbackend/backend/.env` based on the following:

```env
# App
APP_NAME=FileSharingSystem
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/filesharingsystem

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=filesharingsystem
MINIO_USE_SSL=false
```

---

## 📦 Database Migrations

```bash
# Enter the backend container
docker exec -it filesharesystem_backend bash

# Run migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "your migration message"
```

---

## 🧪 Backend Tests

```bash
# Run pytest inside the backend container
docker exec -it filesharesystem_backend pytest
```

---

## 🐳 Docker Services Overview

| Container | Image | Port(s) |
|---|---|---|
| `filesharesystem_backend` | Custom (FastAPI) | 8000 |
| `filesharesystem_db` | postgres:16-alpine | 5432 |
| `filesharesystem_redis` | redis:7-alpine | 6379 |
| `filesharesystem_minio` | minio/minio:latest | 9000, 9001 |
| `filesharesystem_nginx` | nginx:alpine | 80 |
| `filesharesystem_celery` | Custom (Celery worker) | — |
| `filesharesystem_flower` | Custom (Flower) | 5555 |

---

## 📄 License

This project is private and not published to pub.dev. All rights reserved.
