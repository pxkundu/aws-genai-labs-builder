## Minimal Starter (FastAPI Backend)

A minimal, production-leaning FastAPI backend starter with Docker for quick local runs.

### Features

- FastAPI with a simple health endpoint
- Uvicorn server configuration
- Dockerfile and docker-compose for local dev
- `.env` example for basic configuration

### Quickstart

1. Create a `.env` file based on `.env.example`.
2. Run with Docker Compose:

```bash
docker compose up --build
```

3. Visit `http://localhost:8000/health` to verify.

### Project Structure

```
minimal-starter/
  ├── Dockerfile
  ├── docker-compose.yml
  ├── .env.example
  ├── backend/
  │   ├── main.py
  │   └── requirements.txt
  └── docs/
      └── README.md
```


