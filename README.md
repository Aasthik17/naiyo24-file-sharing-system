# 📁 Naiyo24 File Sharing System

A full-stack, cross-platform file sharing application built with **Flutter** (frontend) and **FastAPI** (backend). Users can pick and upload any file — no login required — and instantly receive an expiring share link. The backend runs as a simple two-container Docker stack (FastAPI + PostgreSQL) with local disk storage.

---

## ✨ Features

- 📤 **No-Auth Upload** — Pick and upload any file instantly, no account needed
- 🔗 **Expiring Share Links** — Generate short links with configurable expiry (10–60 minutes)
- 📥 **File Download** — Stream files directly via share link URL (no authentication)
- 🔄 **HTTP Range Support** — Resume-download support via `Accept-Ranges` / `Range` headers
- 🔒 **Optional Password Protection** — Share links can be password-protected
- 🎨 **Dark-themed UI** — Custom brand design system with Google Fonts
- 💾 **Local Disk Storage** — Files persisted in a Docker volume (`/app/uploads`)
- 🐳 **Docker-first** — One `docker compose up --build` starts everything

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Flutter App (Client)            │
│   Android · iOS · Web · Desktop         │
│                                         │
│   UploadScreen                          │
│     └─ FileProvider (Riverpod)          │
│         └─ ApiService (Dio)             │
└──────────────────┬──────────────────────┘
                   │ HTTP / REST (Port 8000)
                   ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                  │
│                                         │
│  POST /api/upload/simple   (no auth)    │
│  POST /api/share/create    (auth req.)  │
│  GET  /api/share/{token}/info           │
│  GET  /api/download/{token}/{filename}  │
│  GET  /health                           │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌──────────────┐  ┌──────────────────────┐
│  PostgreSQL  │  │  Local Disk          │
│  (Port 5432) │  │  /app/uploads/       │
│              │  │                      │
│  users       │  │  files/simple/       │
│  files       │  │  <uuid>_filename     │
│  shares      │  │                      │
│  downloads   │  └──────────────────────┘
└──────────────┘
```

---

## 🗂️ Project Structure

```
naiyo24-file-sharing-system/
├── lib/                              # Flutter frontend
│   ├── main.dart                     # App entry point & routing
│   ├── providers/
│   │   └── file_provider.dart        # File upload state (Riverpod)
│   ├── screens/
│   │   └── upload_screen.dart        # Upload UI & share link display
│   ├── services/
│   │   └── api_service.dart          # Dio HTTP client (base URL config)
│   ├── theme/
│   │   └── app_theme.dart            # Dark theme definition
│   └── widgets/
│       └── brand_kit.dart            # Reusable UI components
│
├── test/
│   └── widget_test.dart              # Widget tests
│
├── filesharingbackend/               # Backend services
│   ├── docker-compose.yml            # Service orchestration (backend + db)
│   ├── nginx/
│   │   └── nginx.conf                # Reverse proxy config (optional)
│   └── backend/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── .env                      # Environment variables
│       ├── alembic.ini               # DB migration config
│       ├── migrations/               # Alembic migration scripts
│       └── app/
│           ├── main.py               # FastAPI app factory & lifespan
│           ├── api/
│           │   ├── router.py         # Root API router
│           │   └── routes/
│           │       ├── upload.py     # POST /api/upload/simple
│           │       ├── share.py      # POST /api/share/create · GET info · DELETE
│           │       └── download.py   # GET /api/download/{token}/{filename}
│           ├── core/                 # Config, DB engine, security, dependencies
│           ├── models/               # SQLAlchemy ORM models (user, file, share, download)
│           ├── schemas/              # Pydantic request/response schemas
│           ├── services/             # Business logic & local storage
│           │   ├── storage_service.py
│           │   ├── upload_service.py
│           │   ├── share_service.py
│           │   └── download_service.py
│           ├── workers/              # Background task utilities
│           └── utils/                # Logging, file helpers
│
├── pubspec.yaml
└── analysis_options.yaml
```

---

## 🧰 Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Flutter (Dart) | ≥ 3.2.5 | Cross-platform UI framework |
| flutter_riverpod | ^2.5.1 | State management |
| dio | ^5.4.0 | HTTP client |
| file_picker | ^8.0.0 | Native file selection |
| google_fonts | ^6.3.2 | Typography |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.111.0 | Async REST API |
| SQLAlchemy 2 + asyncpg | 2.0.30 / 0.29.0 | Async ORM / PostgreSQL |
| Alembic | 1.13.1 | Database migrations |
| aiofiles | 23.2.1 | Async local file I/O |
| python-jose + passlib | 3.3.0 / 1.7.4 | JWT auth & password hashing |
| uvicorn | 0.29.0 | ASGI server |

### Infrastructure
| Component | Image / Tool | Purpose |
|---|---|---|
| PostgreSQL | postgres:16-alpine | Relational database |
| Docker Compose | — | Service orchestration |
| Local Volume (`uploads_data`) | — | Persistent file storage |

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

# Build and start backend + database
docker compose up --build -d
```

**Service URLs once running:**

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
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

> **Note:** Update the base URL in `lib/services/api_service.dart` if running on a physical device (replace `localhost` with your machine's local IP, e.g. `192.168.1.x:8000`).

---

### 3. Run Tests

```bash
flutter test       # Widget tests
flutter analyze    # Static analysis
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/upload/simple` | ❌ | Upload a file; returns an expiring share link |
| `POST` | `/api/share/create` | ✅ | Create a share link for an existing file |
| `GET` | `/api/share/{token}/info` | ❌ | Get public info about a share link |
| `GET` | `/api/share/my` | ✅ | List all share links for the current user |
| `DELETE` | `/api/share/{token}` | ✅ | Revoke (deactivate) a share link |
| `GET` | `/api/download/{token}/{filename}` | ❌ | Download file (filename shown in URL) |
| `GET` | `/api/download/{token}` | ❌ | Download file via token (backward-compat) |
| `HEAD` | `/api/download/{token}` | ❌ | File metadata for resume-download clients |
| `GET` | `/health` | ❌ | Backend health check |

> **Upload flow (primary):** `POST /api/upload/simple` — a single call that saves the file to disk, creates a DB record under a guest user, generates a share link, and returns `{ "link": "...", "expiry_time": "..." }`.

---

## ⚙️ Environment Variables

`filesharingbackend/backend/.env`:

```env
# App
APP_NAME=FileShareSystem
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=filesharingsystem
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/filesharingsystem

# Local Storage
UPLOAD_DIR=/app/uploads

# File Settings
MAX_FILE_SIZE_BYTES=5368709120   # 5 GB
CHUNK_SIZE_BYTES=5242880         # 5 MB per chunk
SHARE_LINK_EXPIRY_HOURS=72       # 3 days default
UPLOAD_SESSION_TTL_SECONDS=3600  # 1 hour to complete upload
```

---

## 🗄️ Database Models

| Model | Table | Key Fields |
|---|---|---|
| `User` | `users` | `id`, `email`, `password` |
| `File` | `files` | `id`, `filename`, `original_filename`, `size`, `mime_type`, `storage_url`, `uploaded_by` |
| `Share` | `shares` | `id`, `token`, `file_id`, `expiry_time`, `password`, `download_limit`, `download_count` |
| `Download` | `downloads` | `id`, `share_id`, `ip_address`, `user_agent`, `downloaded_at` |

> Files uploaded via `/api/upload/simple` are attributed to a built-in `guest@naiyo24.local` user to satisfy the FK constraint.

---

## 📦 Database Migrations

```bash
# Enter the backend container
docker exec -it filesharesystem_backend bash

# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "your migration message"
```

---

## 🧪 Backend Tests

```bash
docker exec -it filesharesystem_backend pytest
```

---

## 🐳 Docker Services

| Container | Image | Port(s) | Purpose |
|---|---|---|---|
| `filesharesystem_backend` | Custom (FastAPI + uvicorn) | 8000 | REST API |
| `filesharesystem_db` | postgres:16-alpine | 5432 | Database |

**Volumes:**
- `postgres_data` → PostgreSQL data directory
- `uploads_data` → `/app/uploads` inside the backend container (uploaded files)

**Network:** Both services share the `filesharenet` bridge network.

---

## 📄 License

This project is private and not published to pub.dev. All rights reserved.
