/**
 * Displays a single food truck's details.
 * Pure "presentational" component — it just receives data via props
 * and renders it. No state, no API calls here.
 */
function TruckCard({ truck }) {
  return (
    <div className="truck-card">
      <h3>{truck.applicant}</h3>
      <p className="truck-card__status">{truck.status}</p>
      {truck.food_items && <p className="truck-card__food">{truck.food_items}</p>}
      <p className="truck-card__address">{truck.address}</p>
      {truck.distance_km !== undefined && (
        <p className="truck-card__distance">{truck.distance_km} km away</p>
      )}
    </div>
  );
}

export default TruckCard;