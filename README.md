# SF - Food Trucks API

A backend service that helps users find food trucks near a specific location in San Francisco,
built with Django REST Framework. Data is sourced from [DataSF's Mobile Food Facility Permit dataset](https://data.sfgov.org/Economy-and-Community/Mobile-Food-Facility-Permit/rqzj-sfat).



## Table of Contents
- [Architecture](#architecture)
- [Tech Stack & Experience Notes](#tech-stack--experience-notes)
- [Setup](#setup)
- [API Documentation](#api-documentation)
- [Developer](#developer)

## Architecture


## Tech Stack & Experience Notes


## Setup

### Prerequisites
- Python 3.12
- Docker & Docker Compose
- **Note:** if you have a local PostgreSQL service already running on port 5432, stop it first
  (`sudo systemctl stop postgresql`) so Docker's Postgres container can bind the port.

### Steps

1. Clone the repo and create your env file:
   \```bash
   cp .env.example .env
   \```

2. Start the infrastructure services:
   \```bash
   docker-compose up -d db redis elasticsearch
   \```

3. Create a virtual environment and install dependencies:
   \```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   \```

4. Run migrations:
   \```bash
   python manage.py migrate
   \```

5. Start the dev server:
   \```bash
   python manage.py runserver
   \```

   Visit `http://localhost:8000`.

### Running the full stack via Docker only

\```bash
docker-compose up --build
\```

This runs Django, Postgres, Redis, Elasticsearch, and the Celery worker/beat together.



## API Documentation


## Developer
Abhinand Satheesh - iam.abhinandsatheesh@gmail.com
