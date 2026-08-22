import { useState } from "react";

/**
 * A search input that calls onSearch(query) whenever the user submits.
 *
 * `query` is local state — it only matters to this component (what's
 * currently typed). `onSearch` is a prop: a function passed down from
 * the parent, which is how this component "reports back" without needing
 * to know anything about what happens with the search results.
 */
function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");

  function handleSubmit(event) {
    event.preventDefault(); // stop the browser from doing a full page reload on form submit
    onSearch(query);
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search by truck name or food type..."
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;