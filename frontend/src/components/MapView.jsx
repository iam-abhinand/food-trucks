import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

/**
 * Renders trucks as pins on a map, centered on the given lat/lng.
 * Each pin shows a popup with the truck's name and address when clicked.
 */
function MapView({ trucks, centerLat, centerLng }) {
  return (
    <MapContainer
      center={[centerLat, centerLng]}
      zoom={14}
      style={{ height: "400px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {trucks.map((truck) => {
        // Skip trucks with missing/invalid coordinates rather than crashing the map
        if (!truck.latitude || !truck.longitude) return null;

        return (
          <Marker key={truck.id ?? truck.db_id} position={[truck.latitude, truck.longitude]}>
            <Popup>
              <strong>{truck.applicant}</strong>
              <br />
              {truck.food_items}
              <br />
              {truck.address}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}

export default MapView;