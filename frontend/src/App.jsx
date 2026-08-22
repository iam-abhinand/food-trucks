import { useEffect, useState } from "react";
import SearchBar from "./components/SearchBar";
import TruckList from "./components/TruckList";
import MapView from "./components/MapView";
import { fetchNearbyTrucks, searchTrucks } from "./api/trucks";
import "./App.css";

const DEFAULT_LAT = 37.7955;
const DEFAULT_LNG = -122.3937;

function App() {
  const [trucks, setTrucks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [centerLat, setCenterLat] = useState(DEFAULT_LAT);
  const [centerLng, setCenterLng] = useState(DEFAULT_LNG);

  useEffect(() => {
    if (!navigator.geolocation) {
      loadNearbyTrucks(DEFAULT_LAT, DEFAULT_LNG);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCenterLat(latitude);
        setCenterLng(longitude);
        loadNearbyTrucks(latitude, longitude);
      },
      (geoError) => {
        // Permission denied or unavailable — fall back to the default point
        console.warn("Geolocation unavailable, using default location:", geoError.message);
        loadNearbyTrucks(DEFAULT_LAT, DEFAULT_LNG);
      },
    );
  }, []);

  async function loadNearbyTrucks(lat = centerLat, lng = centerLng) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchNearbyTrucks(lat, lng, 3);
      setTrucks(data);
    } catch (err) {
      setError("Failed to load nearby trucks. Is the backend running?");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSearch(query) {
    if (!query.trim()) {
      loadNearbyTrucks();
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await searchTrucks(query);
      setTrucks(data);
    } catch (err) {
      setError("Search failed. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>SF Food Trucks</h1>
      <SearchBar onSearch={handleSearch} />

      {isLoading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && !error && (
        <>
          <MapView trucks={trucks} centerLat={DEFAULT_LAT} centerLng={DEFAULT_LNG} />
          <TruckList trucks={trucks} />
        </>
      )}
    </div>
  );
}

export default App;