# EventFlow: Asynchronous Event-Driven Microservices Platform

EventFlow is a scalable, distributed backend platform architected around an **Event-Driven Architecture (EDA)**. It illustrates asynchronous communication, message streaming with JetStream, decoupled microservices, database transactions, reverse-proxy API Gateway routing, and containerized deployment with Docker Compose.

---

## 🏛️ System Architecture

```text
                    Client (Web / Mobile / Postman)
                                   │
                                   ▼ HTTP (Port 8003)
                         ┌──────────────────┐
                         │   API Gateway    │
                         │    (FastAPI)     │
                         └────────┬─────────┘
                                  │
                                  ▼ Async Reverse Proxy
                         ┌──────────────────┐
                         │   User Service   │
                         │   (Django DRF)   │
                         └────┬────────┬────┘
                              │        │
             SQL Transactions │        │ Publishes: "user.created"
                              ▼        ▼
                       ┌──────────┐  ┌───────────────┐
                       │PostgresDB│  │ NATS JetStream│
                       │ (:5433)  │  │    (:4222)    │
                       └──────────┘  └───────┬───────┘
                                             │
                                             ▼ Subscribes & ACKs
                                     ┌──────────────────────┐
                                     │ Notification Service │
                                     │   (Event Consumer)   │
                                     └──────────────────────┘
```

---

## 🌟 Key Features

- **API Gateway Routing:** Built with **FastAPI** to provide a single, non-blocking entry point for external traffic, forwarding requests asynchronously to internal services using `httpx`.
- **Event-Driven & Loosely Coupled:** Microservices communicate asynchronously via **NATS JetStream** messaging rather than direct synchronous HTTP calls.
- **Reliable Message Delivery:** Employs NATS JetStream persistent streams (`USER_EVENTS`) with durable consumer subscriptions and explicit acknowledgements (`msg.ack()`) for at-least-once delivery guarantees.
- **Relational Persistence:** **PostgreSQL 16** with persistent Docker volumes ensures robust data integrity and transactional safety.
- **Containerized Orchestration:** Full multi-service infrastructure defined with **Docker Compose**, including health dependencies, volume management, and port mapping.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
|---|---|---|
| **API Gateway** | FastAPI, Uvicorn, HTTPX | Central entrypoint & reverse proxy |
| **User Service** | Django 6.x, Django REST Framework, Psycopg | User lifecycle management & event publishing |
| **Notification Service** | Python, NATS-Py | Event consumer & notification dispatcher |
| **Message Broker** | NATS 2.11 (JetStream enabled) | Distributed event streaming broker |
| **Database** | PostgreSQL 16 | Relational database storage |
| **Orchestration** | Docker & Docker Compose | Containerization and networking |

---

## 📂 Project Structure

```text
.
├── api-gateway/               # FastAPI reverse proxy gateway
│   ├── main.py                # Gateway routing logic & proxy handlers
│   ├── requirements.txt       # Gateway dependencies (FastAPI, uvicorn, httpx)
│   └── Dockerfile             # Container definition for API Gateway
├── user-service/              # Django REST Framework user management
│   ├── users/                 # Users Django app (models, serializers, views)
│   │   ├── nats_client.py     # Background thread NATS publisher
│   │   ├── views.py           # User list and create API endpoints
│   │   └── models.py          # User model (name, email, created_at)
│   ├── Dockerfile             # Container definition for User Service
│   └── test_publisher.py      # Standalone testing script for NATS publishing
├── notification-service/      # Background event processing worker
│   ├── notifications/         # Worker consumer logic
│   │   └── nats_consumer.py   # JetStream consumer with durable subscription & ACK
│   └── Dockerfile             # Container definition for Notification Service
├── docker-compose.yml         # Multi-container orchestration definition
└── .env                       # Environment configuration variables
```

---

## 🔄 End-to-End Workflow

1. **Client Request:** Client sends a `POST` request to `http://localhost:8003/users/` with user details (`name`, `email`).
2. **Gateway Proxy:** FastAPI Gateway intercepts the request and proxies it asynchronously to User Service at `http://user-service:8000/api/users/`.
3. **Database Write:** User Service validates the payload and commits the record into PostgreSQL.
4. **Publish Event:** User Service immediately publishes a `user.created` event containing `{ "event": "user.created", "user_id": ..., "name": ..., "email": ... }` to NATS JetStream.
5. **Immediate Response:** User Service returns HTTP `201 Created` back through the Gateway to the client without blocking.
6. **Consumer Execution:** Notification Service receives the message, processes the notification, and sends an explicit `ack()` to NATS.

---

## ⚙️ Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- (Optional for local non-Docker development) Python 3.12+, PostgreSQL, and NATS CLI.

### 1. Environment Configuration

Ensure a `.env` file exists in the root directory:

```env
USER_SECRET_KEY="django-insecure-key-here"
SECRET_KEY="production-secret-key-here"
DB_NAME=microservices_db
DB_USER=postgres
DB_PASSWORD=postgres_password
DB_HOST=postgres
DB_PORT=5432
NATS_URL=nats://nats:4222
```

### 2. Start Services via Docker Compose

Run the following command in the project root:

```bash
docker compose up --build
```

To run in detached (background) mode:
```bash
docker compose up -d
```

### 3. Service Ports Mapping

| Service | Internal Port | Host Port | Purpose |
|---|---|---|---|
| **API Gateway** | `8000` | `8003` | Primary external API entrypoint |
| **User Service** | `8000` | `8001` | Internal user CRUD service |
| **Notification Service** | `8000` | `8002` | Event consumer service |
| **PostgreSQL** | `5432` | `5433` | Database access |
| **NATS Broker** | `4222` | `4222` | Message queue protocol |
| **NATS Dashboard** | `8222` | `8222` | NATS HTTP monitoring console |

---

## 📡 API Endpoints

### 1. Health Check
* **Endpoint:** `GET http://localhost:8003/health`
* **Response:**
  ```json
  {
    "status": "ok",
    "service": "api-gateway"
  }
  ```

### 2. Create User
* **Endpoint:** `POST http://localhost:8003/users/`
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "name": "Alex Johnson",
    "email": "alex.johnson@example.com"
  }
  ```
* **Response:** `201 Created`
  ```json
  {
    "id": 1,
    "name": "Alex Johnson",
    "email": "alex.johnson@example.com",
    "created_at": "2026-10-21T01:30:00Z"
  }
  ```

### 3. List Users
* **Endpoint:** `GET http://localhost:8003/users/`
* **Response:** `200 OK`
  ```json
  [
    {
      "id": 1,
      "name": "Alex Johnson",
      "email": "alex.johnson@example.com",
      "created_at": "2026-10-21T01:30:00Z"
    }
  ]
  ```

---

## 🧪 Testing Event Streaming

You can test the NATS JetStream event publishing independently using the included test publisher:

```bash
# Activate your local virtual environment
.\venv\Scripts\activate

# Run the test publisher script
python user-service/test_publisher.py
```
Check the Notification Service terminal logs to observe the received and acknowledged payload.
