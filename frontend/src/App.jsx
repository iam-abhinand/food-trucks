import { useCallback, useEffect, useState } from "react";
import { MapPin } from "lucide-react";
import SearchBar from "./components/SearchBar";
import TruckList from "./components/TruckList";
import MapView from "./components/MapView";
import RadiusSelector from "./components/RadiusSelector";
import { fetchNearbyTrucks, searchTrucks } from "./api/trucks";
import "./App.css";

const DEFAULT_LAT = 37.7955;
const DEFAULT_LNG = -122.3937;
const DEFAULT_RADIUS_KM = 3;

function App() {
  const [trucks, setTrucks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [centerLat, setCenterLat] = useState(DEFAULT_LAT);
  const [centerLng, setCenterLng] = useState(DEFAULT_LNG);
  const [radiusKm, setRadiusKm] = useState(DEFAULT_RADIUS_KM);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [isPinDropMode, setIsPinDropMode] = useState(false);

  const loadNearbyTrucks = useCallback(async (lat, lng, radius) => {
    setIsLoading(true);
    setError(null);
    setIsSearchMode(false);
    try {
      const data = await fetchNearbyTrucks(lat, lng, radius);
      setTrucks(data);
    } catch (err) {
      setError("Failed to load nearby trucks. Is the backend running?");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) {
      setIsSearchMode(false);
      loadNearbyTrucks(centerLat, centerLng, radiusKm);
      return;
    }

    setIsLoading(true);
    setError(null);
    setIsSearchMode(true);
    try {
      const data = await searchTrucks(query);
      setTrucks(data);
    } catch (err) {
      setError("Search failed. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [centerLat, centerLng, radiusKm]);

  // Only acts on map clicks while pin-drop mode is active; automatically
  // exits pin-drop mode after a location is picked, so clicking around
  // the map afterward (e.g. to pan) doesn't accidentally trigger new searches.
  function handleLocationSelect(lat, lng) {
    if (!isPinDropMode) return;

    setCenterLat(lat);
    setCenterLng(lng);
    setIsSearchMode(false);
    setIsPinDropMode(false);
    loadNearbyTrucks(lat, lng, radiusKm);
  }

  function handleRadiusChange(newRadius) {
    setRadiusKm(newRadius);
    loadNearbyTrucks(centerLat, centerLng, newRadius);
  }

  useEffect(() => {
    if (!navigator.geolocation) {
      loadNearbyTrucks(DEFAULT_LAT, DEFAULT_LNG, DEFAULT_RADIUS_KM);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCenterLat(latitude);
        setCenterLng(longitude);
        loadNearbyTrucks(latitude, longitude, DEFAULT_RADIUS_KM);
      },
      (geoError) => {
        console.warn("Geolocation unavailable, using default location:", geoError.message);
        loadNearbyTrucks(DEFAULT_LAT, DEFAULT_LNG, DEFAULT_RADIUS_KM);
      },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app">
      <header className="app__header">
        <h1>SF Food Trucks</h1>
        <p className="app__subtitle">Find food trucks near you, or search by name and cuisine.</p>
      </header>

      <section className="panel panel--search">
        <h2 className="panel__title">Search by name or food</h2>
        <SearchBar onSearch={handleSearch} />
      </section>

      {!isSearchMode && (
        <section className="panel panel--location">
          <h2 className="panel__title">Browse by location</h2>
          <div className="location-controls">
            <button
              type="button"
              className={`pin-drop-button ${isPinDropMode ? "pin-drop-button--active" : ""}`}
              onClick={() => setIsPinDropMode((prev) => !prev)}
              title="Click a spot on the map to search that location"
            >
              <MapPin size={18} />
              {isPinDropMode ? "Click anywhere on the map..." : "Choose location on map"}
            </button>
            <RadiusSelector radiusKm={radiusKm} onChange={handleRadiusChange} />
          </div>
        </section>
      )}

      {isLoading && <p className="status status--loading">Loading trucks...</p>}
      {error && <p className="status status--error">{error}</p>}

      {!isLoading && !error && (
        <>
          <section className="panel panel--map">
            <MapView
              trucks={trucks}
              centerLat={centerLat}
              centerLng={centerLng}
              onLocationSelect={handleLocationSelect}
              isPinDropMode={isPinDropMode}
            />
          </section>

          <section className="panel panel--results">
            <h2 className="panel__title">
              {trucks.length} truck{trucks.length !== 1 ? "s" : ""} found
            </h2>
            <TruckList trucks={trucks} />
          </section>
        </>
      )}
    </div>
  );
}

export default App;