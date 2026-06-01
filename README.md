# Inventory & Order Management System

## Prerequisites

Make sure the following are installed:

* Docker
* Docker Compose

---

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd inventory-management-system
```

### 2. Configure Environment Variables

#### Backend (`backend/.env`)

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/inventory
```

#### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

### 3. Build and Start the Application

```bash
docker compose up --build
```

To run in detached mode:

```bash
docker compose up -d --build
```

---

## Access the Application

| Service           | URL                        |
| ----------------- | -------------------------- |
| Frontend          | http://localhost:3000      |
| Backend API       | http://localhost:8000      |
| API Documentation | http://localhost:8000/docs |

---

## Stop the Application

```bash
docker compose down
```

To remove containers and volumes:

```bash
docker compose down -v
```

---

## Troubleshooting

If you encounter container name conflicts:

```bash
docker rm -f inventory_db inventory_backend
docker compose up --build
```

To view container logs:

```bash
docker logs inventory_backend
docker logs inventory_db
```
