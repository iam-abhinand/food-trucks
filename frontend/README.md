# SF Food Trucks — Frontend

Minimal React SPA for browsing SF food trucks on a map, built with Vite + Leaflet.

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`. Requires the Django backend running at
`http://localhost:8000` (see the root README for backend setup).

## Features
- Geolocates the user (falls back to SF's Ferry Building if permission is denied)
- Shows nearby trucks on a map with popups
- Search by truck name or food type (Elasticsearch-backed autocomplete)

## Structure
- `src/api/` — API client and endpoint-specific functions
- `src/components/` — SearchBar, MapView, TruckList, TruckCard
- `src/App.jsx` — top-level state and data-fetching orchestration