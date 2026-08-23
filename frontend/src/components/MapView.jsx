import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";

function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(event) {
      onLocationSelect(event.latlng.lat, event.latlng.lng);
    },
  });
  return null;
}

function MapView({ trucks, centerLat, centerLng, onLocationSelect, isPinDropMode }) {
  return (
    <MapContainer
      center={[centerLat, centerLng]}
      zoom={13}
      style={{ height: "400px", width: "100%" }}
      className={isPinDropMode ? "map--pin-drop-mode" : ""}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapClickHandler onLocationSelect={onLocationSelect} />

      <Marker position={[centerLat, centerLng]}>
        <Popup>Search center</Popup>
      </Marker>

      {trucks.map((truck) => {
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