# SF Food Trucks API

A backend service that helps users find food trucks near a specific location in San Francisco, built with Django REST Framework. Data is sourced from [DataSF's Mobile Food Facility Permit dataset](https://data.sfgov.org/Economy-and-Community/Mobile-Food-Facility-Permit/rqzj-sfat).



**Live demo:** [https://food-trucks-olive.vercel.app](https://food-trucks-olive.vercel.app)
**Live API:** [https://food-trucks-api.onrender.com/api/docs/](https://food-trucks-api.onrender.com/api/docs/)
**Demo video:** _[link added after recording]_

## Table of Contents
- [Architecture](#architecture)
- [Tech Stack & Experience Notes](#tech-stack--experience-notes)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Design Decisions](#design-decisions)
- [Developer](#developer)

## Architecture

The system is split into focused Django apps, each with a single responsibility:

- **`trucks/`** — the `FoodTruck` model and the core read-only REST API (list, detail, filter, nearby-search)
- **`ingestion/`** — the DataSF client, data mapper, and Celery task that syncs data into Postgres and Elasticsearch; also exposes an authenticated endpoint to trigger a manual sync
- **`search/`** — Elasticsearch index definition, indexing logic, and the autocomplete search endpoint
- **`core/`** — cross-cutting concerns: custom exception handling, structured logging, the health check endpoint, and geo-distance utilities

**Data flow:** DataSF (Socrata API) → `ingestion` client fetches raw JSON → `mappers.py` transforms it into clean model fields, skipping malformed records → a Celery task upserts into PostgreSQL (source of truth) and indexes into Elasticsearch (search layer) → the API layer (`trucks`, `search`) serves reads from Postgres and Elasticsearch respectively, with Redis caching the geo-search endpoint.

```
┌─────────────┐      ┌────────────────┐      ┌─────────────┐
│   DataSF    │─────▶│  Celery Task   │─────▶│  PostgreSQL │ (source of truth)
│  (Socrata)  │      │ (fetch + map + │      └──────┬──────┘
└─────────────┘      │     upsert)    │             │
                     └───────┬────────┘             │
                             │                      ▼
                             ▼                 ┌─────────────┐
                     ┌──────────────┐          │  DRF API    │
                     │Elasticsearch │◀─────────│ (trucks,    │
                     │  (search)    │          │  search,    │
                     └──────────────┘          │  nearby)    │
                                               └──────┬──────┘
                                                      │
                                               ┌──────▼──────┐
                                               │    Redis    │
                                               │ (cache +    │
                                               │  celery     │
                                               │  broker)    │
                                               └─────────────┘
```

## Tech Stack & Experience Notes

| Technology | Role in this project | Experience level |
|---|---|---|
| Python / Django / DRF | Core framework | Strong — primary daily-use stack |
| PostgreSQL | Primary data store | Strong |
| Redis | Caching + Celery broker | Strong |
| Celery | Async task queue (data ingestion) | Strong |
| Elasticsearch | Autocomplete search | Have working experience — first time configuring a custom edge-ngram analyzer, learned it for this project |
| Docker / docker-compose | Local dev environment + deployment | Comfortable |
| JWT (SimpleJWT) | API authentication | Comfortable |
| pytest / pytest-django | Testing | Strong |
| GitHub Actions | CI | Comfortable |
| React (Vite) | Minimal frontend | Basic — enough to build a functional SPA, backend is the focus of this submission |
| Sentry | Error tracking | Basic, integrated and verified working for this project |

**Deliberately not used, and why:**
- **Kafka / Kong / HashiCorp Nomad / full microservices** — this is a single bounded-context service; introducing a message broker topology or an API gateway for one internal API would be over-engineering for a project this size and would hurt code clarity, not help it. I know these tools and would reach for them if the problem called for multiple independently-deployed services or multiple real-time producers — that's not the case here.
- **PostGIS** — used the Haversine formula with a bounding-box DB pre-filter instead. At this dataset's scale (under 1000 records), it's simpler to set up (no GDAL system dependency), fully correct, and easy to unit test against known real-world coordinates. I'd reach for PostGIS at a larger scale or if more advanced spatial queries (polygons, intersections) were needed.

## Project Structure

```
sf-food-trucks/
├── config/                  # Django project settings, URLs, Celery app config
│   └── settings/
│       ├── base.py          # shared settings
│       ├── dev.py           # local development overrides
│       └── prod.py          # production overrides (Sentry, security headers)
├── trucks/                  # FoodTruck model, serializers, filters, core API
├── ingestion/                # DataSF client, mapper, Celery task, sync endpoint
├── search/                   # Elasticsearch index, indexing logic, search endpoint
├── core/                     # logging, exception handling, health check, geo utils
├── frontend/                 # React (Vite) SPA
├── docs/postman/              # Postman collection
├── .github/workflows/         # CI pipeline
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Setup

### Prerequisites
- Python 3.12
- Docker & Docker Compose
- Node.js 18+ (only needed for the frontend, in `frontend/`)
- **Note:** if you have a local PostgreSQL service already running on port 5432, stop it first
  (`sudo systemctl stop postgresql`) so Docker's Postgres container can bind the port.

### Backend Setup

1. Clone the repo and create your env file:
   ```bash
   cp .env.example .env
   ```

2. Start the infrastructure services:
   ```bash
   docker-compose up -d db redis elasticsearch
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (needed for the authenticated `/sync/` endpoint):
   ```bash
   python manage.py createsuperuser
   ```

6. Create the Elasticsearch index and pull real data from DataSF:
   ```bash
   python manage.py index_trucks
   python manage.py sync_food_trucks --limit 1000
   ```

7. Start the dev server:
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000/api/docs/` for interactive Swagger docs.

### Running the full backend stack via Docker only

```bash
docker-compose up --build
```

This runs Django, Postgres, Redis, Elasticsearch, and the Celery worker/beat together.

### Running the async ingestion pipeline locally

```bash
# In one terminal
celery -A config worker -l info

# In another
python manage.py sync_food_trucks --limit 1000
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`. Requires the backend running at `http://localhost:8000`.

## Running Tests

```bash
pytest -v --cov=. --cov-report=term-missing
```

Current coverage: **100%** (77 tests) across models, serializers, views, the ingestion pipeline, geo utilities, search, and authentication.

## API Documentation

Interactive docs, live: **[https://food-trucks-api.onrender.com/api/docs/](https://food-trucks-api.onrender.com/api/docs/)** (Swagger UI) and `/api/redoc/` (ReDoc).

Locally: `http://localhost:8000/api/docs/`

A Postman collection is also available at [`docs/postman/SF_Food_Trucks_API.postman_collection.json`](docs/postman/SF_Food_Trucks_API.postman_collection.json).

### Key Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/trucks/` | Paginated list, filterable by `status`, `facility_type`, `applicant` | No |
| GET | `/api/v1/trucks/{id}/` | Single truck detail | No |
| GET | `/api/v1/trucks/nearby/?lat=&lng=&radius_km=` | Trucks near a point, sorted by distance, Redis-cached | No |
| GET | `/api/v1/search/?q=` | Elasticsearch-backed autocomplete search | No |
| POST | `/api/v1/auth/token/` | Obtain JWT access/refresh tokens | No |
| POST | `/api/v1/auth/token/refresh/` | Refresh an access token | No |
| POST | `/api/v1/sync/` | Manually trigger a DataSF sync | Yes (JWT), rate-limited |
| GET | `/health/` | Checks DB, cache, and Elasticsearch connectivity | No |

## Deployment

- **Backend:** [Render](https://render.com) (Docker-based web service), PostgreSQL and Redis also on Render (free tier)
- **Search:** [Elastic Cloud](https://cloud.elastic.co) free trial (real Elasticsearch, not a fork)
- **Frontend:** [Vercel](https://vercel.com)

**Known free-tier constraint:** Render's free tier doesn't offer a dedicated Background Worker service or shell access. To keep the deployed demo fully functional without a paid plan, two adaptations were made, both clearly gated by environment configuration rather than silently changing behavior:
- Migrations and a one-time idempotent superuser creation run automatically on container startup (`Dockerfile`'s `CMD`), since there's no pre-deploy hook available on the free tier.
- The `/api/v1/sync/` endpoint runs synchronously (`SYNC_RUNS_SYNCHRONOUSLY=true`) on this deployment, since no Celery worker process is running continuously. Locally, and in the codebase itself, the full async pipeline (Celery + Redis broker + dedicated worker) is implemented and tested — see the demo video for it running live via `celery -A config worker`.

## Design Decisions

A few choices worth calling out, since they were deliberate tradeoffs rather than defaults:

- **Read-only trucks API** — all writes happen through the ingestion pipeline, not the API. This matches the actual data ownership model (DataSF is the source of truth, not API consumers).
- **Haversine over PostGIS** — see [Tech Stack & Experience Notes](#tech-stack--experience-notes).
- **Elasticsearch indexing failures don't fail the sync** — Postgres is the source of truth; a transient ES issue shouldn't block the DB from staying current. Indexing errors are logged and counted (`index_errors` in the sync summary) for visibility.
- **Custom exception handler** — every API error returns a consistent `{"error": {"message", "details"}}` shape, rather than DRF's default inconsistent per-exception-type formats.
- **Scoped rate limiting on `/sync/`** — separate from general API throttling, since this endpoint triggers a real external HTTP call and a DB write.

## Developer

Abhinand Satheesh — iam.abhinandsatheesh@gmail.com
