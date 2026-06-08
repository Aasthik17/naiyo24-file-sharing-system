# 📁 Naiyo24 File Sharing System

A full-stack, cross-platform file sharing application built with **Flutter** (frontend) and **FastAPI** (backend). Users can register, log in, upload files, and share them via expiring short links — all served through a simple, robust Docker-composed backend using local filesystem storage.

---

## ✨ Features

- 📤 **File Upload** — Pick and upload any file via a native file picker, supporting large files.
- 🔗 **Expiring Share Links** — Generate short links with configurable expiry (e.g., 10–60 minutes).
- 📥 **File Download** — Download files via share links without authentication.
- 🎨 **Modern UI** — Custom brand design system with Google Fonts and responsive layouts.
- 🗄️ **Local File Storage** — Simple, reliable file storage on the server's filesystem.
- 🚀 **Dockerized Backend** — Easy deployment with Docker Compose (FastAPI + PostgreSQL).

---

## 🏗️ Architecture

```text
┌───────────────────────────────────────┐
│          Flutter App (Client)         │
│    Android · iOS · Web · Desktop      │
└───────────────────┬───────────────────┘
                    │ HTTP / REST API
                    ▼
┌───────────────────────────────────────┐
│         FastAPI Backend (API)         │
│  Port: 8000                           │
│  Routes: /upload, /share, /download...│
└─────────┬───────────────────┬─────────┘
          │                   │
  SQL/ORM ▼                   ▼ File I/O
┌─────────────────┐   ┌─────────────────┐
│   PostgreSQL    │   │ Local Storage   │
│   (Database)    │   │  (Filesystem)   │
│   Port: 5432    │   │  ./uploads/     │
└─────────────────┘   └─────────────────┘
```

---

## 🗂️ Project Structure

```
naiyo24-file-sharing-system/
├── lib/                          # Flutter frontend
│   ├── main.dart                 # App entry point & routing
│   ├── providers/                # Riverpod state management
│   ├── screens/                  # Application screens (Login, Upload, etc.)
│   ├── services/                 # API client (Dio)
│   ├── theme/                    # App styling and themes
│   └── widgets/                  # Reusable UI components
│
├── filesharingbackend/           # Backend services
│   ├── docker-compose.yml        # Docker service orchestration
│   └── backend/
│       ├── Dockerfile            # API Docker configuration
│       ├── requirements.txt      # Python dependencies
│       ├── alembic.ini           # DB migration config
│       ├── migrations/           # Alembic migration scripts
│       ├── uploads/              # Local file storage directory
│       └── app/
│           ├── main.py           # FastAPI app entry point
│           ├── api/              # API routes (/upload, /share, /download)
│           ├── core/             # Configuration & Security
│           ├── models/           # SQLAlchemy models
│           ├── schemas/          # Pydantic validation schemas
│           └── services/         # Business logic & Storage operations
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

### Backend
| Technology | Purpose |
|---|---|
| FastAPI 0.111 | Async REST API framework |
| SQLAlchemy 2 + asyncpg | Async ORM / PostgreSQL |
| Alembic | Database migrations |
| aiofiles | Asynchronous local file operations |

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
# Edit backend/.env with your settings (optional for local dev)

# Build and start all services
docker compose up --build -d
```

**Service URLs once running:**

| Service | URL |
|---|---|
| FastAPI API | http://localhost:8000 |
| FastAPI Swagger Docs | http://localhost:8000/docs |
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

### 3. Run Tests (Frontend)

```bash
flutter test
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a file to local storage |
| `POST` | `/api/share` | Create an expiring share link |
| `GET` | `/api/download/{token}` | Download file via share token |
| `GET` | `/health` | Backend health check |

---

## ⚙️ Environment Variables

Create `filesharingbackend/backend/.env` with the following:

```env
# App
APP_NAME=FileSharingSystem
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/filesharingsystem
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

## 🐳 Docker Services Overview

| Container | Image | Port(s) | Volume |
|---|---|---|---|
| `filesharesystem_backend` | Custom (FastAPI) | 8000 | `./backend:/app`, `upload_data:/app/uploads` |
| `filesharesystem_db` | postgres:16-alpine | 5432 | `postgres_data:/var/lib/postgresql/data` |

---

## 📄 License

This project is private. All rights reserved.
