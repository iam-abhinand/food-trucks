import TruckCard from "./TruckCard";

/**
 * Renders a list of trucks. Receives the array via props and maps
 * over it, rendering one TruckCard per truck.
 */
function TruckList({ trucks }) {
  if (trucks.length === 0) {
    return <p className="truck-list__empty">No trucks found.</p>;
  }

  return (
    <div className="truck-list">
      {trucks.map((truck) => (
        <TruckCard key={truck.id ?? truck.db_id} truck={truck} />
      ))}
    </div>
  );
}

export default TruckList;