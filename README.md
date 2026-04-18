# 📁 File Sharing System

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production--Ready-success" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-blue" />
  <img src="https://img.shields.io/badge/Frontend-Flutter-02569B" />
  <img src="https://img.shields.io/badge/Storage-AWS%20S3-orange" />
</p>

A **production-grade file sharing platform** (WeTransfer-style) built for **high scalability, secure transfers, and fast delivery**.

---

## ✨ Features

* 📦 Upload large files (5GB+)
* 🔁 Chunk-based upload with resume support
* 🔗 Secure shareable links
* ⏳ Expiry-based access control
* ⚡ CDN-powered fast downloads
* 👥 Designed for 100K+ users

---

## 🏗️ Architecture Overview

```text
Flutter App → FastAPI Backend → Redis (Cache) → PostgreSQL (DB)
                         ↓
                     S3 Storage
                         ↓
                        CDN
```

---

## 🧰 Tech Stack

**Frontend**

* Flutter
* Riverpod
* Dio

**Backend**

* FastAPI
* JWT Authentication
* Celery (Background Jobs)

**Database & Storage**

* PostgreSQL
* Redis
* AWS S3 / MinIO

**DevOps & Infra**

* Docker & Docker Compose
* Nginx
* Cloudflare / AWS CloudFront

---

## ⚙️ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/file-sharing-system.git
cd file-sharing-system
```

### 2. Setup environment

Create a `.env` file and configure:

* Database URL
* Redis URL
* S3 credentials
* JWT secret

### 3. Run with Docker

```bash
docker compose up -d --build
```

### 4. Run migrations

```bash
# Example (adjust as needed)
alembic upgrade head
```

---

## 🔄 System Flow

1. User selects file
2. Backend creates upload session
3. File split into chunks
4. Chunks uploaded sequentially
5. Stored in S3
6. Upload finalized
7. Share link generated
8. File downloaded via CDN

---

## 📦 Core Modules

* **Upload Service** → Chunking, resume
* **Share Service** → Secure links
* **Expiry System** → Auto expiration
* **Download Service** → CDN delivery
