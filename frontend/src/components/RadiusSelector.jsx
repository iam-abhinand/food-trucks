/**
 * Simple dropdown to choose the search radius in km.
 * Fully controlled: the parent owns the actual value.
 */
function RadiusSelector({ radiusKm, onChange }) {
  const options = [1, 3, 5, 10, 20];

  return (
    <div className="radius-selector">
      <label htmlFor="radius-select">Radius:</label>
      <select
        id="radius-select"
        value={radiusKm}
        onChange={(event) => onChange(Number(event.target.value))}
      >
        {options.map((km) => (
          <option key={km} value={km}>
            {km} km
          </option>
        ))}
      </select>
    </div>
  );
}

export default RadiusSelector;